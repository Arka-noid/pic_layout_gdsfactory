import gdsfactory as gf
from gdsfactory.typings import CrossSectionSpec



def mmi1x2(*args, **kwargs):
    return gf.components.mmi_tapered(inputs=1, 
                                     outputs=2, 
                                     length_taper_start=2.,
                                     length_taper_end=2.,
                                     #width_taper=1.,
                                     width_taper_in=1.,
                                     width_taper_out=1.,
                                     length_taper_in=20.,
                                     *args, 
                                     **kwargs)



def mmi2x2(*args, **kwargs):
    return gf.components.mmi_tapered(inputs=2, outputs=2,*args, **kwargs)





if __name__ == '__main__':

    # from import_pdk import *
    # from .. import pdk
    import sys
    from pathlib import Path

    sys.path.append(Path(__file__).parents[2].as_posix())

    from src.gfutil.pdk import pdk

    c = gf.pack([
        mmi1x2,
        mmi2x2,
    ])[0]
    c.show()
