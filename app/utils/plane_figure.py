import numpy as np

from bokeh.io import curdoc
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
from .crosshair import crosshair_line_dict
from .palettes import get_default_palette
from .plane import Plane


class PlaneFigure:
    _image = None
    model = None
    image_model = None
    crosshair_model = None

    def __init__(self, plane: Plane, image=None, index=0):
        self.plane = plane
        self.index = index

        self.crosshair_dict = crosshair_line_dict[self.plane]

        self.source = ColumnDataSource()
        self.crosshair_source = ColumnDataSource()

        if image:
            self.image = image

    def _update_image_source(self, image: np.ndarray):
        self.source.data['image'] = [image]
        self.source.data['dw'] = [image.shape[1]]
        self.source.data['dh'] = [image.shape[0]]

    def _update_crosshair_source(self, vertical_line: list,
                                 horizontal_line: list):
        self.crosshair_source.data = dict(
            x=[self.x_range, vertical_line],
            y=[horizontal_line, self.y_range],
        )

    def generate_model(self):
        return figure(
            plot_width=self.width * 2,
            plot_height=self.height * 2,
            x_range=[0, self.width],
            y_range=[0, self.height],
            title=f'{self.plane.name.capitalize()} View',
            name=self.plane.name.lower(),
        )

    def plot_image(self):
        self.image_model = self.model.image(
            image='image',
            x=0,
            y=0,
            dw='dw',
            dh='dh',
            source=self.source,
            palette=get_default_palette(),
            name=f'{self.plane.name.lower()}_plot',
        )
        return self.image_model

    def plot_crosshair(self):
        self.model.multi_line(
            'x',
            'y',
            source=self.crosshair_source,
            color='black',
            alpha=0.4,
            line_width=1,
            name=f'{self.plane.name}_crosshair',
        )

    def get_crosshair_model(self):
        return curdoc().get_model_by_name(f'{self.plane.name}_crosshair')

    def update_crosshair(self, x: int, y: int):
        horizontal_line = [y] * self.width
        vertical_line = [x] * self.height
        self._update_crosshair_source(vertical_line, horizontal_line)

    def plot_figure(self):
        self.plot_image()
        self.plot_crosshair()

    @property
    def width(self) -> int:
        return self.image.shape[1]

    @property
    def x_range(self) -> np.ndarray:
        return np.arange(self.width)

    @property
    def height(self) -> int:
        return self.image.shape[0]

    @property
    def y_range(self) -> np.ndarray:
        return np.arange(self.height)

    @property
    def image(self) -> np.ndarray:
        return self._image

    @image.setter
    def image(self, value: np.ndarray) -> None:
        self._update_image_source(value)
        self._image = value
        if not self.model:
            self.model = self.generate_model()

    @property
    def crosshair_model(self):
        return self.get_crosshair_model()
