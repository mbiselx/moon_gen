import os
import sys
import argparse

import pyqtgraph as pg

from .surface_plotter import SurfacePlotter


parser = argparse.ArgumentParser()
parser.add_argument('FILE', nargs='?', type=str, help='input file')
parser.add_argument('-n', '--newest', action='store_true',
                    help='use the most recently modified file in the module\'s `surfaces` folder')
args = parser.parse_args()


def get_most_recent_file() -> str:
    surfaces_dir = os.path.join(os.path.dirname(__file__), 'surfaces')
    print(surfaces_dir)
    print(*os.listdir(surfaces_dir), sep='\n')

    files = filter(
        os.path.isfile,
        map(
            lambda p: os.path.join(surfaces_dir, p),
            os.listdir(surfaces_dir)
        )
    )
    files = sorted(files, key=os.path.getmtime)
    return files[0]


pg.mkQApp("GLSurfacePlot Example")
with SurfacePlotter() as w:
    if args.FILE is not None:
        w.plotSurfaceFromFile(args.FILE)
    elif args.newest:
        file = get_most_recent_file()
        print(f"using {file}")
        w.plotSurfaceFromFile(file)

    sys.exit(pg.exec())
