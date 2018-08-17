import numpy as np

from bokeh.io import curdoc
from bokeh.layouts import column, widgetbox
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import RangeSlider
from bokeh.plotting import figure
from .crosshair import crosshair_line_dict
from .palettes import get_default_palette
from .plane import Plane


class PlaneFigure:
    _image = None
    model = None
    image_model = None
    crosshair_model = None
    histogram = None
    layout = None

    def __init__(
            self,
            plane: Plane,
            image: np.ndarray = None,
            index: int = 0,
    ):
        self.plane = plane
        self.index = index

        self.crosshair_dict = crosshair_line_dict[self.plane]

        self.source = ColumnDataSource()
        self.crosshair_source = ColumnDataSource()

        self.create_histogram()
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
        self.model = figure(
            plot_width=self.width * 2,
            plot_height=self.height * 2,
            x_range=[0, self.width],
            y_range=[0, self.height],
            title=f'{self.plane.name.capitalize()} View',
            name=self.plane.name.lower(),
        )
        self.model.xaxis.visible = False
        self.model.yaxis.visible = False
        return self.model

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
        self.histogram.width = self.model.plot_width - 40
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

    def change_crosshair_color(self, value: str):
        crosshair = self.get_crosshair_model().glyph
        crosshair.line_color = value

    def update_crosshair(self, x: int, y: int):
        horizontal_line = [y] * self.width
        vertical_line = [x] * self.height
        self._update_crosshair_source(vertical_line, horizontal_line)

    def create_histogram(self):
        if isinstance(self.image, np.ndarray):
            min_value, max_value = self.image.min(), self.image.max()
        else:
            min_value, max_value = 0, 1
        self.histogram = RangeSlider(
            start=min_value,
            end=max_value,
            value=(min_value, max_value),
            step=1,
            title='Displayed Values',
        )
        self.histogram.on_change('value', self.change_displayed_range)
        return self.histogram

    def change_displayed_range(self, attr, old, new):
        min_value, max_value = int(new[0]), int(new[1])
        new_image = self.image.copy()
        new_image[new_image >= max_value] = max_value
        new_image[new_image <= min_value] = min_value
        self._update_image_source(new_image)

    def update_histogram_range(self):
        self.histogram.start = self.image.min()
        if self.image.max():
            self.histogram.end = self.image.max()
            self.histogram.disabled = False
        else:
            self.histogram.end = 1
            self.histogram.disabled = True
        self.histogram.value = (self.image.min(), self.image.max())

    def plot_figure(self):
        self.plot_image()
        self.plot_crosshair()

    def create_layout(self):
        self.plot_figure()
        self.layout = column([
            widgetbox(
                self.histogram, css_classes=[f'histogram_range', 'hidden']),
            self.model
        ])
        return self.layout

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
        self.update_histogram_range()
        if not self.model:
            self.generate_model()

    @property
    def crosshair_model(self):
        return self.get_crosshair_model()
