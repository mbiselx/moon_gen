#!/usr/bin/env python
'''
A widget for interactively plotting surfaces.
'''

import os
import sys
from typing import TYPE_CHECKING
import importlib

import numpy as np

import pyqtgraph.opengl as gl
if TYPE_CHECKING:
    from PyQt6 import QtCore, QtGui, QtWidgets
else:
    from pyqtgraph.Qt import QtCore, QtGui, QtWidgets


class SurfacePlotter(QtWidgets.QFrame):

    def __init__(self, parent=None):
        super().__init__(parent)
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
        self._reloadAction.triggered.connect(self.reloadSurface)
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
            if txt.startswith('file:'):
                txt = txt[8:]
            print(txt)
            if os.path.isfile(txt) and txt.endswith('.py'):
                return a0.accept()

        return a0.ignore()

    def dropEvent(self, a0: QtGui.QDropEvent) -> None:
        '''
        Run the files dropped onto this widget and plot the resulting surface.
        '''
        filename = a0.mimeData().text()
        self.plotSurfaceFromFile(filename)

    def plotSurfaceFromFile(self, filename: str):
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
        self._surfaceData = module.surface()
        self.surf.setData(*self._surfaceData)
        self._module = module

    def reloadSurface(self):
        '''reload the surface defined in the current python file'''
        if self._module is None:
            return

        # try to reload the module if it exists
        module = importlib.reload(self._module)

        # try to retrieve a surface from the module
        self._surfaceData = module.surface()
        self.surf.setData(*self._surfaceData)

    def exportSurface(self,  *, filename: str | None = None):
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

        x, y, z = self._surfaceData

        zz: np.ndarray = (1000*(z - z.min())).astype(np.uint16)

        img = QtGui.QImage(
            zz.data,
            z.shape[0],
            z.shape[1],
            z.shape[0]*2,  # 16 bits == 2 bytes
            QtGui.QImage.Format.Format_Grayscale16
        )

        img.save(filename)
