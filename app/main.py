import numpy as np

from bokeh.events import MouseWheel, Tap
from bokeh.io import curdoc
from bokeh.layouts import column, row, widgetbox
from bokeh.models import ColumnDataSource
from bokeh.models.glyphs import Image, MultiLine
from bokeh.models.mappers import LinearColorMapper
from bokeh.models.ranges import Range1d
from bokeh.plotting import figure, Figure
from bokeh.models.widgets import (
    CheckboxButtonGroup,
    RangeSlider,
    Select,
    Slider,
    Toggle,
)
from functools import partial
from utils.crosshair import (
    CrosshairLines,
    crosshair_colors,
    crosshair_line_dict,
    DEFAULT_CROSSHAIR_COLOR,
)
from utils.palettes import DEFAULT_PALETTE, get_default_palette, palette_dict
from utils.plane import Plane

data = np.load('data.npy')

figures = {
    Plane.TRANSVERSE: None,
    Plane.SAGITTAL: None,
    Plane.CORONAL: None,
}

sources = {
    Plane.TRANSVERSE: {
        'image': ColumnDataSource(data=dict(image=[], dw=[], dh=[])),
        'crosshair': ColumnDataSource(data=dict(x=[], y=[])),
    },
    Plane.SAGITTAL: {
        'image': ColumnDataSource(data=dict(image=[], dw=[], dh=[])),
        'crosshair': ColumnDataSource(data=dict(x=[], y=[])),
    },
    Plane.CORONAL: {
        'image': ColumnDataSource(data=dict(image=[], dw=[], dh=[])),
        'crosshair': ColumnDataSource(data=dict(x=[], y=[])),
    },
}


def get_image_data(plane: Plane, index: int) -> np.ndarray:
    """
    Returns the 2D matrix representing a single slice at a particular plane.
    
    Parameters
    ----------
    plane : Plane
        One of the three planes of the 3D data.
    index : int
        The index of the desired slice.
    
    Returns
    -------
    np.ndarray
        A 2D array of data.
    """

    image = np.take(data, index, axis=plane.value)
    if plane in (Plane.CORONAL, Plane.SAGITTAL):
        return np.transpose(image)
    return image


def get_image_from_source(plane: Plane) -> np.ndarray:
    """
    Returns the image that is currently "loaded" to the desired plane's source.
    
    Parameters
    ----------
    plane : Plane
        One of the three planes of the 3D data.
    
    Returns
    -------
    np.ndarray
        Current image data.
    """

    try:
        return sources[plane]['image'].data['image'][0]
    # If not image is loaded, returns None
    except IndexError:
        pass


def fix_index(plane: Plane, index: int) -> int:
    """
    If the chosen is index is larger than the size of the image in the chosen
    plane, returns 0 instead of the given index.
    
    Parameters
    ----------
    plane : Plane
        One of the three planes of the 3D data.
    index : int
        The index to be tested against the image's shape.
    
    Returns
    -------
    int
        A fixed index value to use.
    """

    axis_size = data.shape[plane.value]
    if index >= axis_size:
        index = 0
    elif index < 0:
        index = axis_size - 1
    return index


def create_figure_model(plane: Plane) -> Figure:
    """
    Creates an instance of the Figure model for the given plane.
    
    Parameters
    ----------
    plane : Plane
        One of the three planes of the 3D data.
    
    Returns
    -------
    Figure
        A Figure instance for the given plane.
    """

    figure_model = figure(
        plot_width=100,
        plot_height=100,
        x_range=[0, 100],
        y_range=[0, 100],
        title=f'{plane.name.capitalize()} View',
        name=plane.name,
    )
    figure_model.xaxis.visible = False
    figure_model.yaxis.visible = False
    return figure_model


def create_image_model(plane: Plane) -> Image:
    """
    Create an instance of the Image model for the given plane.
    
    Parameters
    ----------
    plane : Plane
        One of the three planes of the 3D data.
    
    Returns
    -------
    Image
        The created Image instace for the given plot.
    """

    plot = figures[plane].image(
        image='image',
        x=0,
        y=0,
        dw='dw',
        dh='dh',
        source=sources[plane]['image'],
        palette=get_default_palette(),
        name=f'{plane.name}_image',
    )
    return plot


def get_figure_model(plane: Plane) -> Figure:
    """
    Returns the existing Figure instance for the desired plane from the document.
    
    Parameters
    ----------
    plane : Plane
        One of the three planes of the 3D data.
    
    Returns
    -------
    Figure
        The Figure instance for the given plane.
    """

    return curdoc().get_model_by_name(plane.name)


def get_image_model(plane: Plane) -> Image:
    """
    Returns the existing Image instance for the desired plane from the document.
    
    Parameters
    ----------
    plane : Plane
        One of the three planes of the 3D data.
    
    Returns
    -------
    Image
        The Image instance for the given plane.
    """

    return curdoc().get_model_by_name(f'{plane.name}_image')


def toggle_index_sliders_visibility(active):
    """
    Shows or hides the index sliders.
    
    Parameters
    ----------
    active : bool
        Index sliders' visiblity toggle button state.
    """

    for slider in index_sliders.values():
        slider.visible = active


def create_index_sliders_toggle() -> Toggle:
    """
    Create the index sliders' visibility toggle button.
    
    Returns
    -------
    Toggle
        A Toggle type button instance to control index sliders' visibility.
    """

    sliders_toggle = Toggle(label='Plane Indices', active=False)
    sliders_toggle.on_click(toggle_index_sliders_visibility)
    return sliders_toggle


def toggle_range_sliders_visibility(active):
    """
    Shows or hides the range sliders.
    
    Parameters
    ----------
    active : bool
        Range sliders' visiblity toggle button state.
    """

    for slider in range_sliders.values():
        slider.visible = active


def create_displayed_values_toggle():
    """
    Create the range sliders' visibility toggle button.
    
    Returns
    -------
    Toggle
        A Toggle type button instance to control range sliders' visibility.
    """

    displayed_values_toggle = Toggle(label='Displayed Values')
    displayed_values_toggle.on_click(toggle_range_sliders_visibility)
    return displayed_values_toggle


def create_palette_select() -> Select:
    """
    Create a Select widget instance to choose the palette of the figures.
    
    Returns
    -------
    Select
        A widget to choose the desired palette for the figures.
    """

    select = Select(
        title='Palette',
        value=DEFAULT_PALETTE,
        options=list(palette_dict.keys()),
    )
    select.on_change('value', handle_palette_change)
    return select


def handle_palette_change(attr, old, new):
    """
    Changes the figures' palette according to the user's selection.
    """

    palette = palette_dict[new]
    for plane in figures:
        image_model = get_image_model(plane)
        image_model.glyph.color_mapper = LinearColorMapper(palette=palette)


def create_crosshair_model(plane: Plane) -> MultiLine:
    """
    Creates an instance of the MultiLine model for the given plane to display a
    crosshair.
    
    Parameters
    ----------
    plane : Plane
        One of the three planes of the 3D data.
    
    Returns
    -------
    MultiLine
        A model used to display the crosshair for the given plane.
    """

    crosshair = figures[plane].multi_line(
        'x',
        'y',
        source=sources[plane]['crosshair'],
        color='lime',
        alpha=0.4,
        line_width=1,
        name=f'{plane.name}_crosshair',
    )
    return crosshair


def get_crosshair_model(plane: Plane) -> MultiLine:
    """
    Returns the existing MultiLine model used to display the crosshair for the
    given plane.
    
    Parameters
    ----------
    plane : Plane
        One of the three planes of the 3D data.
    
    Returns
    -------
    MultiLine
        The crosshair model for the given plane.
    """

    return curdoc().get_model_by_name(f'{plane.name}_crosshair')


def get_crosshair_line_plane(plane: Plane, line: CrosshairLines) -> Plane:
    """
    Returns the orientation of the desired line (horizontal or vertical) for the
    given plane.
    
    Parameters
    ----------
    plane : Plane
        One of the three planes of the 3D data.
    line : CrosshairLines
        One of the two orientations of the crosshair lines.
    
    Returns
    -------
    Plane
        The plane of the crosshair line in the given plane and orientation.
    """

    return crosshair_line_dict[plane][line]


def get_crosshair_index(plane: Plane, line: CrosshairLines) -> int:
    """
    Returns the index of the crosshair line in the given plane and orientation.
    
    Parameters
    ----------
    plane : Plane
        One of the three planes of the 3D data.
    line : CrosshairLines
        One of the two possible crosshair line orientations.
    
    Returns
    -------
    int
        The current index of the crosshair line.
    """

    crosshair_line_plane = get_crosshair_line_plane(plane, line)
    return index_sliders[crosshair_line_plane].value


def get_crosshair_indices(plane: Plane):
    """
    Returns the indices of the crosshair lines in the given plane.
    
    Parameters
    ----------
    plane : Plane
        One of the three planes of the 3D data.
    
    Returns
    -------
    tuple
        The indices of the crosshair lines for x and y.
    """

    x = get_crosshair_index(plane, CrosshairLines.VERTICAL)
    y = get_crosshair_index(plane, CrosshairLines.HORIZONTAL)
    return x, y


def update_crosshair_source(
        plane: Plane,
        vertical_line: list,
        horizontal_line: list,
):
    """
    Updates the crosshair's MultiLine model's source with the desired line values.

    Parameters
    ----------
    plane : Plane
        One of the three planes of the 3D data.
    vertical_line : list
        List of values to represent the vertical crosshair line.
    horizontal_line : list
        List of values to represent the horizontal crosshair line.
    """

    crosshair_model = get_crosshair_model(plane)
    crosshair_model.data_source.data = dict(
        x=[np.arange(len(horizontal_line)), vertical_line],
        y=[horizontal_line, np.arange(len(vertical_line))],
    )


def update_crosshair(plane: Plane):
    """
    Updates the crosshair for the given plane.
    
    Parameters
    ----------
    plane : Plane
        One of the three planes of the 3D data.
    """

    x, y = get_crosshair_indices(plane)
    image = get_image_from_source(plane)
    horizontal_line = [y] * image.shape[1]
    vertical_line = [x] * image.shape[0]
    update_crosshair_source(plane, vertical_line, horizontal_line)


def update_crosshairs(skip: Plane = None):
    """
    Updates the crosshair for all planes, except for the "skip" plane if provided.
    
    Parameters
    ----------
    skip : Plane, optional
        A plane to skip when updating crosshair indices, by default None
    """

    for plane in figures:
        if plane is not skip and isinstance(
                get_image_from_source(plane), np.ndarray):
            update_crosshair(plane)


def add_wheel_interaction(plane: Plane):
    """
    Adds the wheel interactivity to easily browse a plane with the mouse.
    
    Parameters
    ----------
    plane : Plane
        One of the three planes of the 3D data.
    """

    figures[plane].on_event(MouseWheel, partial(
        handle_mouse_wheel, plane=plane))


def add_click_interaction(plane: Plane):
    """
    Adds the click interactivity to easily browse a plane with the mouse.
    
    Parameters
    ----------
    plane : Plane
        One of the three planes of the 3D data.
    """

    figures[plane].on_event(Tap, partial(handle_tap, plane=plane))


def handle_mouse_wheel(event: MouseWheel, plane: Plane):
    """
    Changes the current plane's index interactively in response to a MouseWheel
    event.
    
    Parameters
    ----------
    event : MouseWheel
        Rolling the mouse wheel up or down.
    plane : Plane
        One of the three planes of the 3D data.
    """

    current_value = index_sliders[plane].value
    if event.delta > 0:
        index_sliders[plane].value = current_value + 1
    elif event.delta < 0:
        index_sliders[plane].value = current_value - 1


def handle_tap(event: Tap, plane: Plane):
    """
    Changes the other planes' indices interactively in response to a Tap event.
    
    Parameters
    ----------
    event : Tap
        Tapping with the mouse on a figure.
    plane : Plane
        One of the three planes of the 3D data.
    """

    x, y = int(event.x), int(event.y)
    x_plane = crosshair_line_dict[plane][CrosshairLines.VERTICAL]
    y_plane = crosshair_line_dict[plane][CrosshairLines.HORIZONTAL]
    index_sliders[x_plane].value = x
    index_sliders[y_plane].value = y


def create_index_slider(plane: Plane) -> Slider:
    """
    Creates a slider to comfortable show and change a given plane's index.
    
    Parameters
    ----------
    plane : Plane
        One of the three planes of the 3D data.
    
    Returns
    -------
    Slider
        An instance of the Slider model for the given plane.
    """

    slider = Slider(
        start=0,
        end=data.shape[plane.value] - 1,
        value=0,
        step=1,
        title=f'{plane.name.capitalize()} Index',
        name=f'{plane.name}_index_slider',
    )
    return slider


def create_range_slider(plane: Plane) -> RangeSlider:
    """
    Creates a range slider to comfortable show and change a given plane's values
    range.
    
    Parameters
    ----------
    plane : Plane
        One of the three planes of the 3D data.
    
    Returns
    -------
    RangeSlider
        An instance of the Slider model for the given plane.
    """

    range_slider = RangeSlider(
        start=0,
        end=1,
        value=(0, 1),
        step=1,
        title=f'{plane.name.capitalize()} View',
        name=f'{plane.name}_values_slider',
    )
    return range_slider


def create_image_data_source(image: np.ndarray) -> dict:
    """
    Creates a dictionary representing a single slice (index) of a plane.
    
    Parameters
    ----------
    image : np.ndarray
        A slice of the data in one of the three planes.
    
    Returns
    -------
    dict
        A dictionary representation to be used in a figure's source.
    """

    return dict(image=[image], dw=[image.shape[1]], dh=[image.shape[0]])


def update_image_source(plane: Plane, image: np.ndarray):
    """
    Updates the source of the figure for the given plane with the provided image
    data.
    
    Parameters
    ----------
    plane : Plane
        One of the three planes of the 3D data.
    image : np.ndarray
        The slice data to be displayed in the figure.        
    """

    sources[plane]['image'].data = create_image_data_source(image)


def update_figure_properties(plane: Plane):
    """
    Updates the figure's properties according to the properties of the image.
    
    Parameters
    ----------
    plane : Plane
        One of the three planes of the 3D data.
    """

    image = get_image_from_source(plane)
    width, height = image.shape[1], image.shape[0]
    fig = get_figure_model(plane)
    fig.plot_width = min(int(width * 1.8), 405)
    fig.plot_height = int(height * 1.8)
    fig.x_range = Range1d(0, width)
    fig.y_range = Range1d(0, height)


def set_image(plane: Plane, index: int):
    """
    Sets the data for the appropriate figure according to the provided plane and
    index.
    
    Parameters
    ----------
    plane : Plane
        One of the three planes of the 3D data.
    index : int
        The index of the slice to be displayed in the figure.
    """

    image = get_image_data(plane, index)
    update_image_source(plane, image)
    update_figure_properties(plane)
    update_crosshairs(skip=plane)
    update_values_range(plane)


def update_values_range(plane: Plane):
    """
    Updates min and max values of the RangeSlider which corresponds to the given
    plane's figure.
    
    Parameters
    ----------
    plane : Plane
        One of the three planes of the 3D data.
    """

    slider = range_sliders[plane]
    image = get_image_from_source(plane)
    slider.start = image.min()
    if image.max():
        slider.end = image.max()
        slider.disabled = False
    else:
        slider.end = 1
        slider.disabled = True
    slider.value = (image.min(), image.max())


def change_displayed_range(attr, old, new, plane: Plane):
    """
    Interactively changes the given plane's figure displayed range.
    """

    min_value, max_value = int(new[0]), int(new[1])
    new_image = get_image_data(plane, index_sliders[plane].value)
    new_image[new_image >= max_value] = max_value
    new_image[new_image <= min_value] = min_value
    sources[plane]['image'].data['image'] = [new_image]


CHECKBOX_LABELS = ['Crosshair', 'Axes']


def create_visibility_checkbox() -> CheckboxButtonGroup:
    """
    Toggles crosshair and axes visiblity on or off.
    
    Returns
    -------
    CheckboxButtonGroup
        A button group to change the visibility of the crosshair and axes in the
        figures.
    """

    visibility_checkbox = CheckboxButtonGroup(
        labels=CHECKBOX_LABELS, active=[0, 2])
    visibility_checkbox.on_change('active', handle_checkbox)
    return visibility_checkbox


def get_checkbox_index(label: str) -> int:
    """
    Returns the index of the given label from the CheckboxButtonGroup definition.
    
    Parameters
    ----------
    label : str
        The label for which the index is required.
    
    Returns
    -------
    int
        The index of the given label in the CheckboxButtonGroup definition.
    """

    return CHECKBOX_LABELS.index(label)


def handle_checkbox(attr, old, new):
    """
    Show or hide crosshairs and axes according to the CheckboxButtonGroup state.    
    """

    if get_checkbox_index('Crosshair') in new:
        show_crosshairs()
    else:
        hide_crosshairs()
    if get_checkbox_index('Axes') in new:
        show_plot_axes()
    else:
        hide_plot_axes()


def hide_plot_axes():
    """
    Hides the axes in all figures.
    """

    for plane in figures:
        figures[plane].xaxis.visible = False
        figures[plane].yaxis.visible = False


def show_plot_axes():
    """
    Shows the axes in all figures.
    """

    for plane in figures:
        figures[plane].xaxis.visible = True
        figures[plane].yaxis.visible = True


def hide_crosshairs():
    """
    Hides the crosshairs in all figures.
    """

    for plane in figures:
        get_crosshair_model(plane).visible = False


def show_crosshairs():
    """
    Shows the crosshairs in all figures.
    """

    for plane in figures:
        get_crosshair_model(plane).visible = True


def create_crosshair_color_select() -> Select:
    """
    Creates a widget to select the color of the crosshairs in the figures.
    
    Returns
    -------
    Select
        A Select widget to select between possible crosshair colors.
    """

    select = Select(
        title='Crosshair Color',
        value=DEFAULT_CROSSHAIR_COLOR,
        options=crosshair_colors)
    select.on_change('value', change_crosshair_color)
    return select


def change_crosshair_color(attr, old, new):
    """
    Changes the color of the crosshairs displayed in the figures.
    """

    color = new.lower()
    for plane in figures:
        get_crosshair_model(plane).glyph.line_color = color


def update_plane_index(attr, old, new, plane: Plane):
    set_image(plane, fix_index(plane, new))


index_sliders = {}
range_sliders = {}
for plane in figures:
    figures[plane] = create_figure_model(plane)
    create_image_model(plane)
    create_crosshair_model(plane)
    add_wheel_interaction(plane)
    add_click_interaction(plane)
    slider = create_index_slider(plane)
    slider.on_change('value', partial(update_plane_index, plane=plane))
    slider.visible = False
    index_sliders[plane] = slider
    range_slider = create_range_slider(plane)
    range_slider.visible = False
    range_slider.on_change('value', partial(
        change_displayed_range, plane=plane))
    range_sliders[plane] = range_slider

figures_row = row(*figures.values())

extra_widgets = widgetbox(
    create_visibility_checkbox(),
    create_palette_select(),
    create_crosshair_color_select(),
)

main_layout = row(
    figures_row,
    column(
        create_index_sliders_toggle(),
        widgetbox(*index_sliders.values()),
        create_displayed_values_toggle(),
        widgetbox(*range_sliders.values()),
        extra_widgets,
    ),
    name='main',
)
curdoc().add_root(main_layout)

for plane in figures:
    set_image(plane, 0)
