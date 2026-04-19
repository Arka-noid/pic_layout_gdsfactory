import gdsfactory as gf

@gf.cell
def dircoup(length: float = 10,
            gap: float = 0.8,
            **kwargs):
    return gf.components.coupler(length=length, gap=gap, dx=30., dy=10., **kwargs)


@gf.cell
def coupler_ring(
        gap=0.8,
        length_x=0.1,
        *args,
        **kwargs):
    return gf.components.coupler_ring(gap=gap,
                                      length_x=length_x,
                                      *args,
                                      **kwargs)


if __name__ == '__main__':
    from gfutil import pdk

    gf.pack([
        dircoup,
        coupler_ring,
    ])[0].show()


