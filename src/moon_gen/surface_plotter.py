#!/usr/bin/env python
'''
A widget for interactively plotting surfaces.
'''

import os
import sys
import logging
import importlib
from typing import TYPE_CHECKING

import numpy as np

import pyqtgraph.opengl as gl
if TYPE_CHECKING:
    from PyQt6 import QtCore, QtGui, QtWidgets
else:
    from pyqtgraph.Qt import QtCore, QtGui, QtWidgets


class SurfacePlotter(QtWidgets.QFrame):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._logger = logging.getLogger(self.__class__.__name__)
        self._module = None

        self.vw = gl.GLViewWidget(self)

        self.grid = gl.GLGridItem()
        self.vw.addItem(self.grid)

        self._surfaceData = (
            np.arange(0, 2),
            np.arange(0, 2),
            np.zeros((2, 2))
        )

        self.surf = gl.GLSurfacePlotItem(
            *self._surfaceData,
            shader='normalColor'
        )
        self.vw.addItem(self.surf)

        self.setAcceptDrops(True)

        self._reloadAction = QtGui.QAction('&Regenerate surface', self)
        self._reloadAction.setIcon(self.style().standardIcon(
            QtWidgets.QStyle.StandardPixmap.SP_BrowserReload))
        self._reloadAction.setShortcut(QtGui.QKeySequence('Ctrl+R'))
        self._reloadAction.triggered.connect(self.reloadSurfaceModule)
        self.addAction(self._reloadAction)

        self._gridVizAction = QtGui.QAction('&Toggle grid on/off', self)
        self._gridVizAction.setCheckable(True)
        self._gridVizAction.setChecked(self.grid.visible())
        self._gridVizAction.setShortcut(QtGui.QKeySequence('Ctrl+G'))
        self._gridVizAction.toggled.connect(self.grid.setVisible)
        self.addAction(self._gridVizAction)

        self._sep = QtGui.QAction(self)
        self._sep.setSeparator(True)
        self.addAction(self._sep)

        self._exportAction = QtGui.QAction('&Export surface', self)
        self._exportAction.setIcon(self.style().standardIcon(
            QtWidgets.QStyle.StandardPixmap.SP_ToolBarHorizontalExtensionButton))
        self._exportAction.setShortcut(QtGui.QKeySequence('Ctrl+S'))
        self._exportAction.triggered.connect(self.exportSurface)
        self.addAction(self._exportAction)

        self.setContextMenuPolicy(
            QtCore.Qt.ContextMenuPolicy.ActionsContextMenu)

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().addWidget(self.vw)
        self.layout().setContentsMargins(*4*[0])

        # error message
        self._err_message = QtWidgets.QErrorMessage(self)

    def minimumSizeHint(self) -> QtCore.QSize:
        return QtCore.QSize(100, 100)

    def sizeHint(self) -> QtCore.QSize:
        return QtCore.QSize(500, 300)

    def __enter__(self) -> 'SurfacePlotter':
        self.setWindowFlag(QtCore.Qt.WindowType.WindowStaysOnTopHint)
        self.show()
        return self

    def __exit__(self, *args):
        pass

    def dragEnterEvent(self, a0: QtGui.QDragEnterEvent) -> None:
        '''accept any .py files dragged into this widget'''
        if a0.mimeData().hasText():
            txt = a0.mimeData().text()
            self._logger.info(txt)

            if os.path.isfile(txt.removeprefix('file:///')):
                return a0.accept()

        return a0.ignore()

    def dropEvent(self, a0: QtGui.QDropEvent) -> None:
        '''
        Run the files dropped onto this widget and plot the resulting surface.
        '''
        filename = a0.mimeData().text().removeprefix('file:///')

        if filename.casefold().endswith('.py'):
            self.plotSurfaceFromModule(filename)
            a0.accept()
        elif filename.casefold().endswith(('.png', '.jpg', '.jepg', '.tif', '.tiff')):
            self.plotSurfaceFromHeightmap(filename)
            a0.accept()
        else:
            ermsg = f"unsupported filetype `{filename.rsplit('.', 1)[-1]}`"
            self._err_message.showMessage(ermsg, 'warning')
            self._logger.warning(ermsg)
            a0.ignore()

    def plotSurfaceFromModule(self, filename: str):
        '''plot the surface defined in a python file'''
        modulepath = os.path.dirname(filename)
        modulename = os.path.basename(filename)[:-3]

        try:
            # try to reload the module if it exists
            module = importlib.reload(sys.modules[modulename])
        except KeyError:
            # otherwise load it for the first time
            sys.path.append(modulepath)
            module = importlib.import_module(modulename)

        # try to retrieve a surface from the module
        try:
            self._surfaceData = module.surface()
            self.surf.setData(*self._surfaceData)
            self._module = module
        except Exception as e:
            ermsg = f"failed to plot surface from module ({e})"
            self._err_message.showMessage(ermsg, 'error')
            self._logger.error(ermsg)
            self._logger.exception(e)

    def plotSurfaceFromHeightmap(self, filename: str):
        '''plot the surface defined in a heightmap image file'''
        try:
            surface_image = QtGui.QImage(filename)
            surface_image.convertTo(QtGui.QImage.Format.Format_Grayscale16)
            w = surface_image.width()
            h = surface_image.height()
            ptr = surface_image.constBits()
            ptr.setsize(w*h*2)

            x_range, _ = QtWidgets.QInputDialog.getInt(
                self,
                "X range", "please input width of heightmap image (in meters)",
                20, 0, 1000
            )
            y_range, _ = QtWidgets.QInputDialog.getInt(
                self,
                "Y range", "please input height of heightmap image (in meters)",
                x_range, 0, 1000
            )

            x = np.linspace(-x_range/2, x_range/2, w)
            y = np.linspace(-y_range/2, y_range/2, h)
            zz = np.frombuffer(ptr,
                               dtype=np.uint16).reshape((h, w))
            z = zz.astype(float)/1000

            self._surfaceData = x, y, z
            self.surf.setData(*self._surfaceData)
            self._module = None

        except Exception as e:
            ermsg = f"failed to load heightmap image`{e}`"
            self._err_message.showMessage(ermsg, 'error')
            self._logger.error(ermsg)
            self._logger.exception(e)

    def reloadSurfaceModule(self):
        '''reload the surface defined in the current python file'''
        if self._module is None:
            self._logger.warning("no module to reload")
            return

        # try to reload the module if it exists
        module = importlib.reload(self._module)

        # try to retrieve a surface from the module
        self._surfaceData = module.surface()
        self.surf.setData(*self._surfaceData)

    def exportSurface(self, *, filename: str | None = None):
        '''export a surface to a PNG image file'''
        if filename is None:
            filename, _ = QtWidgets.QFileDialog.getSaveFileName(
                self,
                'save heightmap',
                '.',
                'PNG (*.png)'
            )

        if filename in ('', None):
            return

        if not filename.casefold().endswith('.png'):
            filename += '.png'

        _, _, z = self._surfaceData

        zz: np.ndarray = (1000*(z - z.min())).astype(np.uint16)

        img = QtGui.QImage(
            zz.data,
            z.shape[0],
            z.shape[1],
            z.shape[0]*2,  # 16 bits == 2 bytes
            QtGui.QImage.Format.Format_Grayscale16
        )

        img.save(filename)
