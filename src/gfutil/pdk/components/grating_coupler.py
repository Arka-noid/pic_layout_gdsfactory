import gdsfactory as gf

def dummy_fgc():
    return gf.components.grating_couplers.grating_coupler_elliptical(layer_slab=(1, 0))
