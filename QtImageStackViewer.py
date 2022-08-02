""" QtImageStackViewer.py: PyQt image stack viewer similar to that in ImageJ.

"""

import numpy as np
from PIL import Image
import os.path

try:
    from PyQt6.QtCore import Qt, QSize
    from PyQt6.QtGui import QImage, QPixmap
    from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy, QScrollBar, QToolBar, QLabel, QFileDialog, QStyle
except ImportError:
    try:
        from PyQt5.QtCore import Qt, QSize
        from PyQt5.QtGui import QImage, QPixmap
        from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSizePolicy, QScrollBar, QToolBar, QLabel, QFileDialog, QStyle
    except ImportError:
        raise ImportError("Requires PyQt (version 5 or 6)")

from QtImageViewer import QtImageViewer


__author__ = "Marcel Goldschen-Ohm <marcel.goldschen@gmail.com>"
__version__ = '0.1.0'


def isDarkColor(qcolor):
    darkness = 1 - (0.299 * qcolor.red() + 0.587 * qcolor.green() + 0.114 * qcolor.blue()) / 255
    return darkness >= 0.5


def invertIconColors(qicon, w, h):
    qimage = QImage(qicon.pixmap(w, h))
    qimage.invertPixels()
    pixmap = QPixmap.fromImage(qimage)
    qicon.addPixmap(pixmap)


class QtImageStackViewer(QWidget):
    """ QtImageStackViewer.py: PyQt image stack viewer similar to that in ImageJ.

    Uses a QtImageViewer with frame/channel sliders and a titlebar indicating current frame and mouse position
    similar to that in ImageJ.

    Display a multi-page image stack with a slider to traverse the frames in the stack.
    Can also optionally split color channels with a second slider.

    Image stack data can be loaded either directly as a NumPy 3D array [rows, columns, frames] or from file using PIL.

    If reading multi-page image data from file using PIL, only the currently displayed frame will be kept in memory,
    so loading and scrolling through even huge image stacks is very fast.
    """

    def __init__(self, image=None):
        QWidget.__init__(self)

        # Image data: NumPy array - OR - PIL image file object = PIL.Image.open(...)
        self._image = image

        # Store data for current frame
        self._currentFrame = None

        # Display multiple channels individually in grayscale (choose selected channel with scrollbar).
        self._separateChannels = False

        # QtImageViewer
        self.imageViewer = QtImageViewer()
        self.imageViewer.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding))

        # Scrollbars for frames/channels/etc.
        self._scrollbars = []

        # Mouse wheel behavior
        self._wheelScrollsFrame = True
        self._wheelZoomFactor = 1.25

        self.label = QLabel()
        font = self.label.font()
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed))

        self.toolbar = QToolBar()
        self.toolbar.setOrientation(Qt.Orientation.Horizontal)
        self.toolbar.setFloatable(False)
        self.toolbar.setMovable(False)
        self.toolbar.setIconSize(QSize(10, 10))
        self.toolbar.setContentsMargins(0, 0, 0, 0)
        self.toolbar.setStyleSheet("QToolBar { spacing: 2px; }")
        self.toolbar.addWidget(self.label)

        bgColor = self.palette().color(QWidget.backgroundRole(self))
        isDarkMode = isDarkColor(bgColor)

        qpixmapi = getattr(QStyle.StandardPixmap, "SP_MediaPlay")
        qicon = self.style().standardIcon(qpixmapi)
        if isDarkMode:
            invertIconColors(qicon, 10, 10)
        self.playAction = self.toolbar.addAction(qicon, "", self.play)

        qpixmapi = getattr(QStyle.StandardPixmap, "SP_MediaPause")
        qicon = self.style().standardIcon(qpixmapi)
        if isDarkMode:
            invertIconColors(qicon, 10, 10)
        self.pauseAction = self.toolbar.addAction(qicon, "", self.pause)

        vbox = QVBoxLayout(self)
        vbox.addWidget(self.toolbar)
        vbox.addWidget(self.imageViewer)
        vbox.setContentsMargins(5, 5, 5, 5)
        vbox.setSpacing(2)

        # Track mouse position on image.
        self.imageViewer.setMouseTracking(True)
        self.imageViewer.mousePositionOnImageChanged.connect(self.updateLabel)

        # For play/pause actions.
        self._isPlaying = False

        self.updateViewer()

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def image(self):
        return self._image

    def setImage(self, im):
        self._image = im
        self.updateViewer()

    def currentFrame(self):
        return self._currentFrame

    def open(self, filepath=None):
        if filepath is None:
            filepath, dummy = QFileDialog.getOpenFileName(self, "Select image file.")
        if len(filepath) and os.path.isfile(filepath):
            self.setImage(Image.open(filepath))

    def loadData(self):
        if type(self._image) is np.ndarray:
            return self._image
        else:
            # PIL Image file object = PIL.Image.open(...)
            channels = self._image.getbands()
            n_channels = len(channels)
            n_frames = self._image.n_frames
            if n_frames == 1:
                return np.array(self._image)
            if n_frames > 1:
                self._image.seek(0)
                firstFrame = np.array(self._image)
                if n_channels == 1:
                    data = np.zeros((self._image.height, self._image.width, n_frames),
                                    dtype=firstFrame.dtype)
                else:
                    data = np.zeros((self._image.height, self._image.width, n_channels, n_frames),
                                    dtype=firstFrame.dtype)
                data[:,:,:n_channels] = firstFrame
                for i in range(1, n_frames):
                    self._image.seek(i)
                    if n_channels == 1:
                        data[:,:,i] = np.array(self._image)
                    else:
                        data[:,:,i*n_channels:(i+1)*n_channels] = np.array(self._image)
                return data

    def separateChannels(self):
        return self._separateChannels

    def setSeparateChannels(self, tf):
        self._separateChannels = tf
        self.updateViewer()

    def currentIndexes(self):
        return [scrollbar.value() for scrollbar in self._scrollbars]

    def setCurrentIndexes(self, indexes):
        for i, index in enumerate(indexes):
            self._scrollbars[i].setValue(index)
        self.updateFrame()

    def wheelScrollsFrame(self):
        return self._wheelScrollsFrame

    def setWheelScrollsFrame(self, tf):
        self._wheelScrollsFrame = tf
        if tf:
            self.imageViewer.wheelZoomFactor = 1
        else:
            self.imageViewer.wheelZoomFactor = self._wheelZoomFactor

    def wheelZoomFactor(self):
        return self._wheelZoomFactor

    def setWheelZoomFactor(self, zoomFactor):
        self._wheelZoomFactor = zoomFactor
        if not self._wheelScrollsFrame:
            self.imageViewer.wheelZoomFactor = zoomFactor

    def updateViewer(self):
        if self._image is None:
            self.imageViewer.clearImage()
            del self._scrollbars[:]
            return

        if type(self._image) is np.ndarray:
            # Treat numpy.ndarray as grayscale intensity image.
            # Add scrollbars for every dimension after the first two.
            n_scrollbars = max(0, self._image.ndim - 2)
            if len(self._scrollbars) > n_scrollbars:
                for sb in self._scrollbars[n_scrollbars:]:
                    sb.deleteLater()
                del self._scrollbars[n_scrollbars:]
            while len(self._scrollbars) < n_scrollbars:
                scrollbar = QScrollBar(Qt.Horizontal)
                scrollbar.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed))
                scrollbar.valueChanged.connect(self.updateFrame)
                self.layout().addWidget(scrollbar)
                self._scrollbars.append(scrollbar)
            for i in range(n_scrollbars):
                self._scrollbars[i].setRange(0, self._image.shape[i+2])
                self._scrollbars[i].setValue(0)
        else:
            # PIL Image file object = PIL.Image.open(...)
            channels = self._image.getbands()
            n_channels = len(channels)
            n_frames = self._image.n_frames
            n_scrollbars = 0
            if n_channels > 1 and self._separateChannels:
                n_scrollbars += 1
            if n_frames > 1:
                n_scrollbars += 1
            if len(self._scrollbars) > n_scrollbars:
                for sb in self._scrollbars[n_scrollbars:]:
                    sb.deleteLater()
                del self._scrollbars[n_scrollbars:]
            while len(self._scrollbars) < n_scrollbars:
                scrollbar = QScrollBar(Qt.Orientation.Horizontal)
                scrollbar.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed))
                scrollbar.valueChanged.connect(self.updateFrame)
                self.layout().addWidget(scrollbar)
                self._scrollbars.append(scrollbar)
            i = 0
            if n_channels > 1 and self._separateChannels:
                self._scrollbars[i].setRange(0, n_channels - 1)
                self._scrollbars[i].setValue(0)
                i += 1
            if n_frames > 1:
                self._scrollbars[i].setRange(0, n_frames - 1)
                self._scrollbars[i].setValue(0)

        # mouse wheel scroll frames vs. zoom
        if len(self._scrollbars) > 0 and self._wheelScrollsFrame:
            # wheel scrolls frame (i.e., last dimension)
            self.imageViewer.wheelZoomFactor = None
        else:
            # wheel zoom
            self.imageViewer.wheelZoomFactor = self._wheelZoomFactor

        self.updateFrame()

    def updateFrame(self):
        if self._image is None:
            return

        if type(self._image) is np.ndarray:
            rows = np.arange(self._image.shape[0])
            cols = np.arange(self._image.shape[1])
            indexes = [rows, cols].extend([[i] for i in self.currentIndexes()])
            self._currentFrame = self._image[np.ix_(*indexes)]
            self.imageViewer.setImage(self._currentFrame.copy())
        else:
            # PIL Image file object = PIL.Image.open(...)
            channels = self._image.getbands()
            n_channels = len(channels)
            n_frames = self._image.n_frames
            indexes = self.currentIndexes()
            if n_frames > 1:
                frameIndex = indexes[-1]
                self._image.seek(frameIndex)
            if n_channels > 1 and self._separateChannels:
                channelIndex = indexes[0]
                self._currentFrame = np.array(self._image)[:,:,channelIndex]
                self.imageViewer.setImage(self._currentFrame.copy())
            else:
                try:
                    self._currentFrame = QImage(self._image.toqimage())
                    self.imageViewer.setImage(self._currentFrame)
                except ValueError:
                    self._currentFrame = np.array(self._image)
                    self.imageViewer.setImage(self._currentFrame.copy())

        self.updateLabel()

    def updateLabel(self, imagePixelPosition=None):
        if self._image is None:
            return

        label = ""
        for sb in self._scrollbars:
            label += str(sb.value()) + "/" + str(sb.maximum()) + "; "
        if type(self._image) is np.ndarray:
            width = self._image.shape[1]
            height = self._image.shape[0]
        else:
            # PIL Image file object = PIL.Image.open(...)
            width = self._image.width
            height = self._image.height
        label += str(width) + "x" + str(height)
        if imagePixelPosition is not None:
            x = imagePixelPosition.x()
            y = imagePixelPosition.y()
            if 0 <= x < width and 0 <= y < height:
                label += "; x=" + str(x) + ", y=" + str(y)
                if self._currentFrame is not None:
                    if type(self._currentFrame) is np.ndarray:
                        value = self._currentFrame[y, x]
                    else:
                        # PIL Image file object = PIL.Image.open(...)
                        value = self._image.getpixel((x, y))
                    label += ", value=" + str(value)
        self.label.setText(label)

    def wheelEvent(self, event):
        if len(self._scrollbars) == 0:
            return
        n_frames = self._scrollbars[-1].maximum() + 1
        if self._wheelScrollsFrame and n_frames > 1:
            i = self._scrollbars[-1].value()
            if event.angleDelta().y() < 0:
                # next frame
                if i < n_frames - 1:
                    self._scrollbars[-1].setValue(i + 1)
                    self.updateFrame()
            else:
                # prev frame
                if i > 0:
                    self._scrollbars[-1].setValue(i - 1)
                    self.updateFrame()
            return

        QWidget.wheelEvent(self, event)

    def leaveEvent(self, event):
        self.updateLabel()

    def play(self):
        if len(self._scrollbars) == 0:
            return
        self._isPlaying = True
        first = self._scrollbars[-1].value()
        last = self._scrollbars[-1].maximum()
        for i in range(first, last + 1):
            self._scrollbars[-1].setValue(i)
            self.updateFrame()
            QApplication.processEvents()
            if not self._isPlaying:
                break
        self._isPlaying = False

    def pause(self):
        self._isPlaying = False


if __name__ == '__main__':
    import sys
    try:
        from PyQt6.QtWidgets import QApplication
    except ImportError:
        from PyQt5.QtWidgets import QApplication

    # Create the application.
    app = QApplication(sys.argv)

    # Create viewer.
    viewer = QtImageStackViewer()

    # Open an image stack from file.
    # This will NOT load the entire stack into memory, only the current frame as needed.
    # This way even huge image stacks can be loaded and examined almost instantly.
    viewer.open()

    # Show viewer and run application.
    viewer.show()
    sys.exit(app.exec())
