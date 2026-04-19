import functools
from typing import Callable, Literal

import gdsfactory as gf
from gdsfactory.typings import (
    ComponentSpec,
    ComponentSpecOrList,
    CrossSectionSpec,
    # PortsList
)

import numpy as np
from functools import partial, wraps
from gfutil.utilities import add_sref, add_text


gc_dict = {}


# @add_cladding()
@gf.cell
def add_fgc(component: ComponentSpec | None = None,
            io_component: ComponentSpecOrList = "dummy_fgc",
            cross_section: CrossSectionSpec | None = None,
            component_specs: tuple | None = None,
            input_ports: list | None = None,
            output_ports: list | None = None,
            input_distance: tuple | list = (-60., 0),
            input_distances: list | None = None,
            input_reference: tuple | str | None = None,
            output_distance: tuple | list = (60., 0),
            output_distances: list | None = None,
            output_reference: tuple | str | None = None,
            routing_function=gf.routing.route_bundle,
            **kwargs
            ) -> gf.Component:
    c = gf.Component()
    io_cell = gf.get_component(io_component)

    if cross_section is None:
        cross_section = gc_dict.get(io_component, "strip") if isinstance(io_component, str) else "strip"

    if component is None:
        io_in = c << io_cell
        io_in.dmirror_x().dmove(input_distance)
        io_out = c << io_cell
        io_out.dmove(output_distance)
        routing_function(c,
                         ports1=[io_in.ports["o1"]],
                         ports2=[io_out.ports["o1"]],
                         cross_section=cross_section,
                         **kwargs)
    else:
        cref = add_sref(c, component, component_specs or (0., 0.))
        c.add_ports(cref.ports)
        if input_ports is None:
            input_ports = list(cref.ports.filter(port_type="optical", orientation=180))
        else:
            input_ports = [cref.ports[p] for p in input_ports]

        if output_ports is None:
            output_ports = list(cref.ports.filter(port_type="optical", orientation=0))
        else:
            output_ports = [cref.ports[p] for p in output_ports]

        input_distances = input_distances or [input_distance] * len(input_ports)
        output_distances = output_distances or [output_distance] * len(output_ports)

        for n, (p, pos) in enumerate(zip(input_ports, input_distances)):
            io = add_fgc_to_port(canvas=c,
                                 port=p,
                                 io_cell=io_cell,
                                 io_spec=(*pos, 180., False),
                                 routing_function=routing_function,
                                 cross_section=cross_section,
                                 relative_to=input_reference or (p.dx, p.dy),
                                 **kwargs
                                 )
            # c.add_port(f"v_o{n + 1}", io["o2"])

        for n, (p, pos) in enumerate(zip(output_ports, output_distances)):
            io = add_fgc_to_port(canvas=c,
                                 port=p,
                                 io_cell=io_cell,
                                 io_spec=(*pos, 0., False),
                                 routing_function=routing_function,
                                 cross_section=cross_section,
                                 relative_to=output_reference or (p.dx, p.dy),
                                 **kwargs
                                 )
            # c.add_port(f"v_o{n + len(input_ports) + 1}", io["o2"])


    return c


def add_fgc_to_port(
        canvas: ComponentSpec,
        port: str | gf.Port,
        io_spec: tuple | list,
        io_cell: ComponentSpec = "dummy_fgc",
        routing_function: Callable = gf.routing.route_bundle,
        relative_to: tuple | None = None,
        taper: ComponentSpec | None = None,
        **kwargs
):
    dx, dy, *other = io_spec
    if relative_to is not None:
        if isinstance(relative_to, str):
            relative_to = canvas[relative_to].dcenter
        dx += relative_to[0]
        dy += relative_to[1]

    if taper is not None:
        tref = canvas << gf.get_component(taper)
        tref.connect("o2", port)
        port_to_connect = tref["o1"]
        dx += tref["o1"].dx - tref["o2"].dx  # Adapt to the length of the taper (assuming these ports names)
        dy += tref["o1"].dy - tref["o2"].dy
        port_to_connect.name = port.name
    else:
        port_to_connect = port

    io_component = add_sref(canvas, io_cell, (dx, dy, *other))
    io_port = io_component["o1"]

    try:
        routing_function(canvas,
                         ports1=[io_port],
                         ports2=[port_to_connect],
                         # allow_width_mismatch=True,
                         # allow_layer_mismatch=True,
                         **kwargs)
    except Exception as e:
        print(f"Error incurred: {e}")
        print(f"Impossible to connect {port_to_connect.name} to {io_cell.name}:{io_port.name} - No connection occurred")
    return io_component


def add_fgc_wrapper(
        wrapper=add_fgc,
        **settings,
):
    def decorator(func):
        @wraps(func)
        @gf.cell
        def add_io(*args, **kwargs):
            component = func(*args, **kwargs)
            return wrapper(component=component, **settings)

        return add_io

    return decorator


# @gf.cell
def add_reference_waveguide(io_component: ComponentSpec | None = "dummy_fgc",
                            length: float = 800.,
                            vertical_offset: float = 0,
                            io_port_reference: str | None = None,
                            cross_section: CrossSectionSpec | None = None,
                            routing_function: Callable = gf.routing.route_bundle):
    c = gf.Component()

    if cross_section is None:
        if isinstance(io_component, str):
            cross_section = gc_dict[io_component]
        else:
            raise RuntimeError("Unable to determine the cross section")

    io_in = add_sref(c, io_component, (0., 0., 180))
    if io_port_reference is not None:
        ref_center = io_in.ports[io_port_reference].dcenter
        io_in.dmove((-ref_center[0], -ref_center[1]))
    in_port = io_in.ports["o1"]

    io_out = add_sref(c, io_component, (0, 0., 0))
    if io_port_reference is not None:
        ref_center = io_out.ports[io_port_reference].dcenter
        io_out.dmove((-ref_center[0], -ref_center[1]))
    io_out.dmove((length, vertical_offset))
    out_port = io_out.ports["o1"]

    if vertical_offset != 0:
        sbend = c << gf.get_component("bend_s", size=(100., vertical_offset), cross_section=cross_section)
        sbend.connect("o1", io_in.ports["o1"])
        in_port = sbend.ports["o2"]

    routing_function(c, ports1=[in_port], ports2=[out_port], cross_section=cross_section)

    return c





if __name__ == "__main__":
    from gfutil import pdk


    c = add_fgc(gf.components.straight)
    c.show()