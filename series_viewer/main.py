import numpy as np

from bokeh.layouts import column, row, widgetbox
from series_viewer.utils.sources_manager import SourcesManager
from series_viewer.utils.figures_manager import FiguresManager
from series_viewer.utils.widgets_manager import WidgetsManager


class SeriesViewer:
    def __init__(self, data: np.ndarray):
        self.sources_manager = SourcesManager(data)
        self.widgets_manager = WidgetsManager()
        self.figures_manager = FiguresManager(
            sources_manager=self.sources_manager, widgets_manager=self.widgets_manager
        )
        self.figures_manager.create_figures()
        self.figures_row = row(*self.figures_manager.figures.values())

    def create_visibility_checkbox(self):
        visibility_checkbox = self.widgets_manager.create_visibility_checkbox()
        visibility_checkbox.on_change("active", self.figures_manager.handle_checkbox)
        return visibility_checkbox

    def create_palette_select(self):
        palette_select = self.widgets_manager.create_palette_select()
        palette_select.on_change("value", self.figures_manager.handle_palette_change)
        return palette_select

    def create_crosshair_color_select(self):
        crosshair_color_select = self.widgets_manager.create_crosshair_color_select()
        crosshair_color_select.on_change(
            "value", self.figures_manager.change_crosshair_color
        )
        return crosshair_color_select

    def create_extra_widgets(self):
        return widgetbox(
            self.create_visibility_checkbox(),
            self.create_palette_select(),
            self.create_crosshair_color_select(),
        )

    def create_main_layout(self):
        return row(
            self.figures_row,
            column(
                self.widgets_manager.create_index_sliders_toggle(),
                widgetbox(*self.widgets_manager.index_sliders.values()),
                self.widgets_manager.create_displayed_values_toggle(),
                widgetbox(*self.widgets_manager.range_sliders.values()),
                self.create_extra_widgets(),
            ),
            name="main",
        )

