# PyQtImageViewer

Yet another [PyQt](https://www.riverbankcomputing.com/software/pyqt/intro) (version 4 or 5) image viewer widget. Comes prepackaged with several configurable options for display (aspect ratio, scroll bars) and mouse interaction (zoom, pan, click signals).

Displays a *QImage* or *QPixmap*. To display any other image format, you must first convert it to a *QImage* or *QPixmap*. Some useful image format conversion utilities:

* [qimage2ndarray](https://github.com/hmeine/qimage2ndarray): [NumPy](http://www.numpy.org) *ndarray* <==> *QImage*
* [ImageQt](https://github.com/python-pillow/Pillow/blob/master/PIL/ImageQt.py): [PIL](https://github.com/python-pillow/Pillow) *Image* <==> *QImage*

**Author**: Marcel Goldschen-Ohm  
**Email**:  <marcel.goldschen@gmail.com>  
**License**: MIT  
Copyright (c) 2015 Marcel Goldschen-Ohm  

## INSTALL

Everything's in `QtImageViewer.py`. Just put it somewhere where your project can find it.

### Requires:

* [PyQt](https://www.riverbankcomputing.com/software/pyqt/intro) (version 4 or 5)

## A Simple Example

```python
import sys
try:
    from PyQt5.QtCore import Qt, QT_VERSION_STR
    from PyQt5.QtGui import QImage
    from PyQt5.QtWidgets import QApplication, QFileDialog
except ImportError:
    try:
        from PyQt4.QtCore import Qt, QT_VERSION_STR
        from PyQt4.QtGui import QImage, QApplication, QFileDialog
    except ImportError:
        raise ImportError("Requires PyQt5 or PyQt4.")
from QtImageViewer import QtImageViewer


# Custom slot for handling mouse clicks in our viewer.
# Just prints the (row, column) matrix index of the 
# image pixel that was clicked on.
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
    viewer.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    viewer.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    
    # Allow zooming with right mouse button.
    # Drag for zoom box, doubleclick to view full image.
    viewer.canZoom = True
    
    # Allow panning with left mouse button.
    viewer.canPan = True
        
    # Load an image to be displayed.
    if QT_VERSION_STR[0] == '4':
        fileName = QFileDialog.getOpenFileName(None, "Open image file...")
    elif QT_VERSION_STR[0] == '5':
        fileName, dummy = QFileDialog.getOpenFileName(None, "Open image file...")
    image = QImage(fileName)
    
    # Display the image in the viewer.
    viewer.setImage(image)
    
    # Handle left mouse clicks with your own custom slot
    # handleLeftClick(x, y). (x, y) are image coordinates.
    # For (row, col) matrix indexing, row=y and col=x.
    # ImageViewerQt also provides similar signals for
    # left/right mouse button press, release and doubleclick.
    viewer.leftMouseButtonPressed.connect(handleLeftClick)
        
    # Show the viewer and run the application.
    viewer.show()
    sys.exit(app.exec_())
```
