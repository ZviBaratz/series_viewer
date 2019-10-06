import numpy as np

from series_viewer import SeriesViewer
from bokeh.io import curdoc


data = np.load("data.npy")
series_viewer = SeriesViewer(data)
main_layout = series_viewer.create_main_layout()
curdoc().add_root(main_layout)
for plane in series_viewer.figures_manager.figures:
    series_viewer.figures_manager.set_image(plane, 0)
