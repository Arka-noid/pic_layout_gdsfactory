import gdsfactory as gf
import numpy
from .layer_map import LAYER
from gdsfactory.cross_section import (CrossSection,
                                      cross_section,
                                      xsection,
                                      )
from gdsfactory.typings import LayerSpec
from functools import partial


clad_dict = {
    "WG": "WGCLD",
    "SIN": "SINCLAD",
}

WG_LAYER = "WG"
SIN_LAYER = "SIN"
SLAB_LAYER = "SLAB150"
STRIP_WIDTH = 0.45
RIB_WIDTH = 5.0
SLAB_WIDTH = 10.0
HEATER_LAYER = "HEATER"
HEATER_WIDTH = 0.6
UCUT_LAYER = "UNDERCUT"
M1_LAYER = "M1"
M2_LAYER = "M2"
METAL_LAYER = M1_LAYER
M1_WIDTH = 10
M2_WIDTH = 10

"""Return strip with full etch cladding cross_section."""


@xsection
def strip(
        layer: LayerSpec = WG_LAYER,
        offset: float = 0.,
        cladding_layer: LayerSpec | None = None,
        cladding_offset: float = 14.,
        width: float = STRIP_WIDTH,
        radius: float = 60.0,
        radius_min: float = 5,
        add_cladding: bool = False,
        **kwargs,
) -> CrossSection:
    sections = []
    if add_cladding:
        cladding_layer = cladding_layer or clad_dict[layer]
        sections.append(gf.Section(layer=cladding_layer, width=width + cladding_offset, name="cladding", simplify=50e-3))
    
    return cross_section(
        layer=layer,
        offset=offset,
        width=width,
        radius=radius,
        radius_min=radius_min,
        sections=sections,
        **kwargs
    )


@xsection
def rib(
        layer: LayerSpec = WG_LAYER,
        slab_layer: LayerSpec = SLAB_LAYER,
        cladding_layer: LayerSpec | None = None,
        cladding_offset: float = 14.,
        width: float = 1.5,
        width_slab: float = 15,
        slab_cladding_offset: float = 6.4,
        radius: float = 50.0,
        radius_min: float = 1000.,
        cladding_insets: tuple[float, float] = (0., 0.),
        add_cladding: bool = False,
        **kwargs,
) -> CrossSection:
    sections = [
        gf.Section(layer=slab_layer, width=width_slab, name="slab"),
        ]

    if add_cladding:
        cladding_layer = cladding_layer or clad_dict[layer]
        sections.append(gf.Section(layer=cladding_layer, width=width + cladding_offset, name="cladding", simplify=50e-3)) 

    return cross_section(
        width=width,
        layer=layer,
        radius=radius,
        radius_min=radius_min,
        sections=tuple(sections),
        **kwargs,
    )




@xsection
def metal_routing(
        layer=METAL_LAYER,
        *args, **kwargs
):
    return gf.cross_section.metal_routing(layer=layer, *args, **kwargs)

@xsection
def heater_metal(
        layer: LayerSpec = HEATER_LAYER,
        width: float = HEATER_WIDTH,
        *args, **kwargs
):
    return gf.cross_section.heater_metal(
        width=width,
        layer=layer,
        *args, **kwargs
    )


@xsection
def strip_heater_metal(
        width=STRIP_WIDTH,
        layer=WG_LAYER,
        heater_width=HEATER_WIDTH,
        layer_heater=HEATER_LAYER,
        *args, **kwargs,
):
    return gf.cross_section.strip_heater_metal(
        width=width,
        layer=layer,
        heater_width=heater_width,
        layer_heater=layer_heater,
        *args, **kwargs
    )

@xsection
def strip_metal_heater_undercut(
        layer=WG_LAYER,
        width=STRIP_WIDTH,
        layer_heater=HEATER_LAYER,
        heater_width=HEATER_WIDTH,
        layer_trench=UCUT_LAYER,
        trench_width=1.0,
        trench_gap=5.0,
        *args, **kwargs
):
    return gf.cross_section.strip_heater_metal_undercut(
        layer=layer,
        width=width,
        layer_heater=layer_heater,
        heater_width=heater_width,
        layer_trench=layer_trench,
        trench_width=trench_width,
        trench_gap=trench_gap,
        *args, **kwargs
    )



BASE_CROSS_SECTIONS = dict(
    SWG_CTE=partial(strip, layer=WG_LAYER, width=0.45),
    SWG_OTE=partial(strip, layer=WG_LAYER, width=0.40),
    MWG_CTE=partial(strip, layer=WG_LAYER, width=1.5),
    MWG_OTE=partial(strip, layer=WG_LAYER, width=1.4),

    SSIN_CTE=partial(strip, layer=SIN_LAYER, width=1),
    SSIN_OTE=partial(strip, layer=SIN_LAYER, width=0.8),
    MSIN_CTE=partial(strip, layer=SIN_LAYER, width=2.5),
    MSIN_OTE=partial(strip, layer=SIN_LAYER, width=2.2),

)



CROSS_SECTIONS = dict(
    **BASE_CROSS_SECTIONS,
    strip=strip,
    rib=rib,


    metal_routing=metal_routing,
    m1_routing=partial(metal_routing, layer=M1_LAYER),
    m2_routing=partial(metal_routing, layer=M2_LAYER),

    heater_metal=heater_metal,
    strip_heater_metal=strip_heater_metal,
    strip_heater_metal_undercut=strip_metal_heater_undercut,
)

TRANSITIONS = {
    LAYER.WG: "taper",
    LAYER.SIN: "taper",

}
