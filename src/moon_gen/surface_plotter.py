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
            shader='shaded'
        )
        self.vw.addItem(self.surf)

        self.setAcceptDrops(True)

        self._reloadAction = QtGui.QAction('&Regenerate surface', self)
        self._reloadAction.setIcon(self.style().standardIcon(
            QtWidgets.QStyle.StandardPixmap.SP_BrowserReload))
        self._reloadAction.setShortcut(QtGui.QKeySequence('Ctrl+R'))
        self._reloadAction.triggered.connect(self.reloadSurface)
        self.addAction(self._reloadAction)

        self._gridVizAction = QtGui.QAction('&Toggle grid on/off', self)
        self._gridVizAction.setCheckable(True)
        self._gridVizAction.setChecked(self.grid.visible())
        self._gridVizAction.setShortcut(QtGui.QKeySequence('Ctrl+G'))
        self._gridVizAction.toggled.connect(self.grid.setVisible)
        self.addAction(self._gridVizAction)

        self._shaderAction = QtGui.QAction('&Shader on/off', self)
        self._shaderAction.setCheckable(True)
        self._shaderAction.setChecked(self.surf.shader().name == 'normalColor')
        self._shaderAction.toggled.connect(self.toggleShader)
        self.addAction(self._shaderAction)

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

    def toggleShader(self, active: bool):
        self.surf.setShader('normalColor' if active else 'shaded')

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
        self.plotSurfaceFromFile(filename)

    def plotSurfaceFromFile(self, filename: str):

        if filename.casefold().endswith('.py'):
            self.plotSurfaceFromModule(filename)
        elif filename.casefold().endswith(('.png', '.jpg', '.jepg', '.tif', '.tiff')):
            self.plotSurfaceFromHeightmap(filename)
        else:
            ermsg = f"unsupported filetype `{filename.rsplit('.', 1)[-1]}`"
            self._err_message.showMessage(ermsg, 'warning')
            self._logger.warning(ermsg)

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
            surface_image.convertTo(
                QtGui.QImage.Format.Format_Grayscale8,
                QtCore.Qt.ImageConversionFlag.MonoOnly
            )
            w = surface_image.width()
            h = surface_image.height()
            ptr = surface_image.constBits()
            ptr.setsize(surface_image.sizeInBytes())

            # QImage has some end-of-line padding, so that each line is word-aligned
            padding = surface_image.sizeInBytes()//w - h

            x_range, _ = QtWidgets.QInputDialog.getDouble(
                self,
                "X range", "please input width of heightmap image (in meters)",
                20, 0, 10000
            )
            y_range, _ = QtWidgets.QInputDialog.getDouble(
                self,
                "Y range", "please input height of heightmap image (in meters)",
                x_range/w*h, 0, 10000
            )
            z_range, _ = QtWidgets.QInputDialog.getDouble(
                self,
                "Z range", "please input depth of heightmap image (in meters)",
                1, 0, 10000
            )

            x = np.linspace(-x_range/2, x_range/2, w)
            y = np.linspace(-y_range/2, y_range/2, h)

            zz = np.asarray(ptr, dtype=np.uint8).reshape((h, w+padding))
            if padding:
                zz = zz[:, :-padding]
            z = np.flipud(zz.T).astype(float)*(z_range/(2**8-1))

            self._surfaceData = x, y, z
            self.surf.setData(*self._surfaceData)
            self._module = None

        except Exception as e:
            ermsg = f"failed to load heightmap image ({e})"
            self._err_message.showMessage(ermsg, 'error')
            self._logger.error(ermsg)
            self._logger.exception(e)

    def reloadSurface(self):
        if self._module is not None:
            self.reloadSurfaceModule()
        elif self._surfaceData is not None:
            self.reloadSurfaceImage()
        else:
            ermsg = f"No surface to reload"
            self._err_message.showMessage(ermsg, 'warning')
            self._logger.warn(ermsg)

    def reloadSurfaceModule(self):
        '''reload the surface defined in the current python file'''
        if self._module is None:
            return

        # try to reload the module if it exists
        module = importlib.reload(self._module)

        # try to retrieve a surface from the module
        self._surfaceData = module.surface()
        self.surf.setData(*self._surfaceData)

    def reloadSurfaceImage(self):
        x, y, z = self._surfaceData

        x_range, _ = QtWidgets.QInputDialog.getDouble(
            self,
            "X range", "please input width of heightmap image (in meters)",
            x.ptp(), 0, 10000
        )
        y_range, _ = QtWidgets.QInputDialog.getDouble(
            self,
            "Y range", "please input height of heightmap image (in meters)",
            y.ptp(), 0, 10000
        )
        z_range, _ = QtWidgets.QInputDialog.getDouble(
            self,
            "Z range", "please input depth of heightmap image (in meters)",
            z.ptp(), 0, 10000
        )

        x = np.linspace(-x_range/2, x_range/2, len(x))
        y = np.linspace(-y_range/2, y_range/2, len(y))
        z *= (z_range/z.ptp())

        self._surfaceData = x, y, z
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

        # zz: np.ndarray = (1000*(z - z.min())).astype(np.uint16)
        zz: np.ndarray = ((z - z.min())*(255/z.ptp())).astype(np.uint8)
        zz = np.flipud(zz).transpose()

        img = QtGui.QImage(
            zz.data.tobytes(),
            z.shape[0],
            z.shape[1],
            # z.shape[0]*2,  # 16 bits == 2 bytes
            # QtGui.QImage.Format.Format_Grayscale16
            z.shape[0],  # 8 bits == 1 byte
            QtGui.QImage.Format.Format_Grayscale8
        )

        img.save(filename)
