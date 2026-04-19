import gdsfactory as gf
import numpy as np
from gdsfactory.typings import LayerSpec


def rect_coord(size, center):
    w, h = size
    return np.array([(0., 0), (w, 0.), (w, h), (0., h)]) + np.array(center)

@gf.cell
def floorplan(
        size: tuple[float, float] = (22000., 22000.),
        margin: float = 150.,
        floorplan_layer: LayerSpec = "FLOORPLAN",
        chip_layer: LayerSpec = "PADDING",
) -> gf.Component:
    c = gf.Component()

    frame = gf.components.rectangle(size=size, layer=chip_layer, centered=False)
    c << frame
    r_inner = c << gf.components.rectangle(size=tuple(np.array(size) - 2*margin), layer=floorplan_layer, centered=False)
    r_inner.dmove((margin, margin))
    return c


if __name__ == '__main__':
    from import_pdk import *
    c = floorplan()
    c.show()