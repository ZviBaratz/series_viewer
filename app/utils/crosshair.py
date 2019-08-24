from enum import Enum
from .plane import Plane


class CrosshairLines(Enum):
    HORIZONTAL = 'h'
    VERTICAL = 'v'


crosshair_line_dict = {
    Plane.TRANSVERSE: {
        CrosshairLines.HORIZONTAL: Plane.CORONAL,
        CrosshairLines.VERTICAL: Plane.SAGITTAL
    },
    Plane.SAGITTAL: {
        CrosshairLines.HORIZONTAL: Plane.TRANSVERSE,
        CrosshairLines.VERTICAL: Plane.CORONAL
    },
    Plane.CORONAL: {
        CrosshairLines.HORIZONTAL: Plane.TRANSVERSE,
        CrosshairLines.VERTICAL: Plane.SAGITTAL
    },
}

crosshair_colors = [
    'Lime',
    'Green',
    'Black',
    'White',
    'Red',
    'Cyan',
    'Yellow',
    'Blue',
    'Orange',
    'Purple',
    'Pink',
    'Brown',
    'Indigo',
    'Grey',
]

DEFAULT_CROSSHAIR_COLOR = crosshair_colors[0]
