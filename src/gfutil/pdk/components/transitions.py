import gdsfactory as gf
from functools import partial
from gdsfactory.typings import CrossSectionSpec

# Placeholder
taper_cross_section = gf.components.taper_cross_section


@gf.cell
def strip_to_rib(
        strip_cross_section: CrossSectionSpec = "strip",
        rib_cross_section: CrossSectionSpec = "rib",
        length: float = 20,
        **kwargs,
):
    c = gf.Component()

    Xi = gf.get_cross_section(strip_cross_section)
    Xf = gf.get_cross_section(rib_cross_section)

    X1 = gf.get_cross_section(rib_cross_section, width=Xi.width + 0.1, width_slab=Xi.width)
    X2 = gf.get_cross_section(rib_cross_section, width=Xf.width)#, width_slab=Xf.width + 6.)

    straight_strip = c << gf.components.straight(length=2, cross_section=Xi)
    transition = c << gf.components.taper_cross_section(length=length, cross_section1=X1, cross_section2=X2, linear=True, **kwargs)
    straight_rib = c << gf.components.straight(length=2, cross_section=X2)
    straight_rib.connect("o1", transition["o2"], allow_width_mismatch=True)
    straight_strip.connect("o2", transition["o1"], allow_width_mismatch=True, allow_layer_mismatch=True)

    c.add_ports([straight_strip["o1"], straight_rib["o2"]])
    return c






if __name__ == '__main__':
    from gfutil import pdk

    gf.pack([
        strip_to_rib,
    ])[0].show()
