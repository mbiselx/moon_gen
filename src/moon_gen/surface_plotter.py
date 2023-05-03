#!/usr/bin/env python
'''
A widget for interactively plotting surfaces.
'''

import os
import sys
import importlib

import numpy as np

import pyqtgraph.opengl as gl
from PyQt5 import QtCore, QtGui, QtWidgets


class SurfacePlotter(QtWidgets.QFrame):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._module = None

        self.vw = gl.GLViewWidget(self)

        self.grid = gl.GLGridItem()
        self.vw.addItem(self.grid)

        self.surf = gl.GLSurfacePlotItem(
            x=np.arange(0, 2),
            y=np.arange(0, 2),
            z=np.zeros((2, 2)),
            shader='normalColor'
        )
        self.vw.addItem(self.surf)

        self.setAcceptDrops(True)

        self._reloadAction = QtWidgets.QAction('&Regenerate surface', self)
        self._reloadAction.setIcon(self.style().standardIcon(
            QtWidgets.QStyle.StandardPixmap.SP_BrowserReload))
        self._reloadAction.setShortcut(
            QtCore.Qt.Modifier.CTRL + QtCore.Qt.Key.Key_R)
        self._reloadAction.triggered.connect(self.reloadSurface)
        self.addAction(self._reloadAction)

        self._gridVizAction = QtWidgets.QAction('&Toggle grid on/off', self)
        self._gridVizAction.setCheckable(True)
        self._gridVizAction.setChecked(self.grid.visible())
        self._gridVizAction.setShortcut(
            QtCore.Qt.Modifier.CTRL + QtCore.Qt.Key.Key_G)
        self._gridVizAction.toggled.connect(self.grid.setVisible)
        self.addAction(self._gridVizAction)

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
        self.surf.setData(*module.surface())
        self._module = module

    def reloadSurface(self):
        '''reload the surface defined in the current python file'''
        if self._module is None:
            return

        # try to reload the module if it exists
        module = importlib.reload(self._module)

        # try to retrieve a surface from the module
        self.surf.setData(*module.surface())
