# PyQtImageViewer

* `QtImageViewer`: Yet another [PyQt5](https://www.riverbankcomputing.com/software/pyqt/intro) image viewer widget. Comes prepackaged with several easily configurable options for display (aspect ratio, scroll bars) and mouse interaction (zoom, pan, click signals). Also has limited support for ROIs. Displays a *QImage*, *QPixmap*, or *NumPy 2D array* (requires [qimage2ndarray](https://github.com/hmeine/qimage2ndarray)). To display any other image format, you must first convert it to one of the supported formats (e.g., see [PIL](https://github.com/python-pillow/Pillow) and [ImageQt](https://github.com/python-pillow/Pillow/blob/master/PIL/ImageQt.py)).
* `QtImageStackViewer`: Multi-page image stack viewer similar to [ImageJ](https://imagej.nih.gov/ij/). Based off of QtImageViewer with sliders for traversing frames and/or channels and a titlebar that displays the current frame in the stack and mouse position coordinates like in ImageJ.

**Author**: Marcel Goldschen-Ohm  
**Email**:  <marcel.goldschen@gmail.com>  
**License**: MIT  
Copyright (c) 2022 Marcel Goldschen-Ohm  

# INSTALL

Everything's in `QtImageViewer.py` and `QtImageStackViewer.py`. Just put these somewhere where your project can find them.

### Requirements:

* [PyQt5](https://www.riverbankcomputing.com/software/pyqt/intro)
* [NumPy](https://numpy.org/)
* [qimage2ndarray](https://github.com/hmeine/qimage2ndarray)
* [Pillow](https://python-pillow.org)

## `QtImageViewer` Example

```python
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from QtImageViewer import QtImageViewer


# Custom slot for handling mouse clicks in our viewer.
# This example just prints the (row, column) matrix index
# of the image pixel that was clicked on.
def handleLeftClick(x, y):
    row = int(y)
    column = int(x)
    print("Pixel (row="+str(row)+", column="+str(column)+")")
    

if __name__ == '__main__':
    # Create the QApplication.
    app = QApplication(sys.argv)
        
    # Create an image viewer widget.
    viewer = QtImageViewer()
        
    # Set viewer's aspect ratio mode.
    # !!! ONLY applies to full image view.
    # !!! Aspect ratio always ignored when zoomed.
    #   Qt.IgnoreAspectRatio: Fit to viewport.
    #   Qt.KeepAspectRatio: Fit in viewport using aspect ratio.
    #   Qt.KeepAspectRatioByExpanding: Fill viewport using aspect ratio.
    viewer.aspectRatioMode = Qt.KeepAspectRatio
    
    # Set the viewer's scroll bar behaviour.
    #   Qt.ScrollBarAlwaysOff: Never show scroll bar.
    #   Qt.ScrollBarAlwaysOn: Always show scroll bar.
    #   Qt.ScrollBarAsNeeded: Show scroll bar only when zoomed.
    viewer.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    viewer.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    
    # Allow zooming by draggin a zoom box with the left mouse button.
    # !!! This will still emit a leftMouseButtonReleased signal if no dragging occured,
    #     so you can still handle left mouse button clicks in this way.
    #     If you absolutely need to handle a left click upon press, then
    #     either disable region zooming or set it to the middle or right button.
    viewer.regionZoomButton = Qt.LeftButton  # set to None to disable
    
    # Pop end of zoom stack (double click clears zoom stack).
    viewer.zoomOutButton = Qt.RightButton  # set to None to disable
    
    # Mouse wheel zooming.
    viewer.wheelZoomFactor = 1.25  # Set to None or 1 to disable
    
    # Allow panning with the middle mouse button.
    viewer.panButton = Qt.MiddleButton  # set to None to disable
        
    # Load an image file to be displayed (will popup a file dialog).
    viewer.open()
    
    # Handle left mouse clicks with your own custom slot
    # handleLeftClick(x, y). (x, y) are image coordinates.
    # For (row, col) matrix indexing, row=y and col=x.
    # ImageViewerQt also provides similar signals for
    # left/right mouse button press, release and doubleclick.
    # Here I bind the slot to leftMouseButtonReleased only because
    # the leftMouseButtonPressed signal will not be emitted due to
    # left clicks being handled by the regionZoomButton.
    viewer.leftMouseButtonReleased.connect(handleLeftClick)
        
    # Show the viewer and run the application.
    viewer.show()
    sys.exit(app.exec_())
```
