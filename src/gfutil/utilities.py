import gdsfactory as gf
import numpy as np
import pandas as pd
from gdsfactory.typings import (
    ComponentSpec, LayerSpecs, ComponentSpecOrList
)



def add_sref(c: ComponentSpec,
             component: ComponentSpec,
             specs: tuple | list | pd.Series = (0., 0.)
             ) -> ComponentSpec:
    # ref = ref() if callable(ref) else ref
    ref = gf.get_component(component)
    inst = c << ref
    if isinstance(specs, pd.Series):
        x, y = specs["X"], specs["Y"]
        a = None or specs["A"]
        m = False or specs["M"]
    else:
        x, y, *other = specs
        a = other[0] if len(other) > 0 else None
        m = other[1] if len(other) > 1 else False
    if a is not None:
        inst.drotate(a)
    if m:
        inst.mirror_y()
    inst.dmove((x, y))
    return inst


def add_sref_list(c: ComponentSpec,
                  components: ComponentSpecOrList,
                  specs: list | None = None
                  ):
    return [add_sref(c, component, spec) for component, spec in zip(components, specs)]



def array_coordinates(shape: tuple, pitch: tuple, by_row: bool = True):
    nx, ny = shape
    dx, dy = pitch
    if by_row:
        return [(n * dx, m * dy) for n in range(nx) for m in range(ny)]
    else:
        return [(n * dx, m * dy) for m in range(ny) for n in range(nx)]


@gf.cell
def add_text(c: ComponentSpec,
             text: str,
             position: tuple[float, float] = (0., 0.),
             layers: LayerSpecs = ("TEXT",),
             bg_layers: LayerSpecs = ("NO_TILE_SI"),
             bg_margin: float = 2,
             size: float = 25,
             text_component: ComponentSpec = gf.components.text,
             drc_resize: float = 0.8,
             **text_kwargs
             ) -> ComponentSpec:
    t = gf.Component()
    cref = t << gf.get_component(c)
    bbox = np.zeros((2, 2))
    for layer in layers:
        text_c = text_component(text=text, layer=layer, size=size, **text_kwargs)
        if drc_resize:
            text_c = text_c.dup()
            text_c.over_under(layer=layer, distance=int(drc_resize*1000)) # Concave angles
            text_c.over_under(layer=layer, distance=int(-drc_resize * 1000)) # Convex angles
        r = t << text_c
        r.dmove(position)
        bbox = np.array(((r.dxmin, r.dymin), (r.dxmax, r.dymax)))

    for bg_layer in bg_layers:
        r = t << gf.components.rectangle(
            size=(bbox[1, 0] - bbox[0, 0] + 2*bg_margin, bbox[1, 1] - bbox[0, 1] + 2*bg_margin),
            layer=bg_layer)
        r.dmovey(bbox[0, 1] - bg_margin)
        r.dmovex(bbox[0, 0] - bg_margin)

    t.add_ports(cref.ports)

    return t

def add_text_wrapper(*pos_add_text_arguments, **add_text_arguments):
    def decorator(f):
        def wrapper(*args, **kwargs):
            c = f(*args, **kwargs)
            return add_text(c, *pos_add_text_arguments, **add_text_arguments)
        return wrapper
    return decorator


def max_width(c) -> float:
    xs = gf.get_cross_section(c)
    return max([xs.width] + [s.width for s in xs.sections])



# if __name__ == "__main__":
#     from sin_pdk import sin_pdk_loaded
#     sin_pdk_loaded()
#     import string
#
#     def main():
#         s = string.hexdigits + string.ascii_letters
#         comps = [add_text(gf.Component(), s + f" resize={rs}, size={sz}, text", drc_resize=rs, size=sz) for rs in np.linspace(0, 2, 11) for sz in [10, 20, 30, 40, 50]]
#         # comps += [add_text(gf.Component(), s + f" resize {rs} size {sz} text_rectangular", drc_resize=rs, size=sz, text_component=gf.components.text_rectangular) for rs in np.linspace(0, 2, 11) for sz in [10, 20, 30, 40, 50]]
#         # comps += [add_text(gf.Component(), s + f" resize {rs} size {sz} text_lines", drc_resize=rs, size=sz, text_component=gf.components.text_lines) for rs in np.linspace(0, 2, 11) for sz in [10, 20, 30, 40, 50]]
#         grid = gf.grid(comps, shape=(len(comps)//5, 10))
#
#         grid.show()
#         grid.write_gds('text_drc_test.gds', with_metadata=False)
#
#     main()
