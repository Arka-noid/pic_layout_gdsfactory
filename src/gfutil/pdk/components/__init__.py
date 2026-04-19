import gdsfactory as gf
from functools import partial

from .dircoup import (
    dircoup,
)




from .mmi import (
    mmi1x2,
    mmi2x2,
)



from .grating_coupler import (
    dummy_fgc
)

from .transitions import (
    taper_cross_section,
    strip_to_rib,
)


from .floorplan import floorplan


COMPONENTS = dict(
    straight=gf.components.straight,

    bend_euler=gf.components.bend_euler,
    bend_circular=gf.components.bend_circular,
    bend_euler180=gf.components.bend_euler180,
    bend_s=gf.components.bend_s,


    dummy_fgc=dummy_fgc,

    taper_cross_section=taper_cross_section,
    strip_to_rib=strip_to_rib,


    floorplan=floorplan,

    mmi1x2=mmi1x2,
    mmi2x2=mmi2x2,



)
