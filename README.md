# PyQtImageViewer

Yet another [PyQt](https://www.riverbankcomputing.com/software/pyqt/intro) (version 5) image viewer widget. Comes prepackaged with several configurable options for display (aspect ratio, scroll bars) and mouse interaction (zoom, pan, click signals). Also has limited support for ROIs.

Displays a *QImage*, *QPixmap*, or *NumPy 2D array* (later requires [qimage2ndarray](https://github.com/hmeine/qimage2ndarray)). To display any other image format, you must first convert it to one of the supported formats. Some useful image format conversion utilities:

* [qimage2ndarray](https://github.com/hmeine/qimage2ndarray): [NumPy](http://www.numpy.org) *ndarray* <==> *QImage*
* [ImageQt](https://github.com/python-pillow/Pillow/blob/master/PIL/ImageQt.py): [PIL](https://github.com/python-pillow/Pillow) *Image* <==> *QImage*

**Author**: Marcel Goldschen-Ohm  
**Email**:  <marcel.goldschen@gmail.com>  
**License**: MIT  
Copyright (c) 2015 Marcel Goldschen-Ohm  

## INSTALL

Everything's in `QtImageViewer.py`. Just put it somewhere where your project can find it.

### Requires:

* [PyQt](https://www.riverbankcomputing.com/software/pyqt/intro) (version 5)

If you want to display NumPy 2D arrays:

* [NumPy](https://numpy.org/)
* [qimage2ndarray](https://github.com/hmeine/qimage2ndarray)

## A Simple Example

```python
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import QApplication, QFileDialog
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
        
    # Load an image to be displayed.
    fileName, dummy = QFileDialog.getOpenFileName(None, "Open image file...")
    image = QImage(fileName)
    
    # Display the image in the viewer.
    viewer.setImage(image)
    
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
