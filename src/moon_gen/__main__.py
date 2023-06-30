import os
import sys
import argparse

import pyqtgraph as pg

from moon_gen.surface_plotter import SurfacePlotter


parser = argparse.ArgumentParser()
parser.add_argument('FILE', nargs='?', type=str, help='input file')
args = parser.parse_args()

pg.mkQApp("GLSurfacePlot Example")
with SurfacePlotter() as w:
    if args.FILE is not None:
        w.plotSurfaceFromFile(args.FILE)
    sys.exit(pg.exec())
