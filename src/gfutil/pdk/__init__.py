pdk_name = "pdk_v0.1"


from gdsfactory import Pdk
from .layer_map import LAYER, LAYER_VIEWS
from .xsections import CROSS_SECTIONS, TRANSITIONS
from .components import COMPONENTS

pdk = Pdk(
    name=pdk_name,
    layers=LAYER,
    layer_views=LAYER_VIEWS,
    cross_sections=CROSS_SECTIONS,
    cells=COMPONENTS,
    layer_transitions=TRANSITIONS,
)


pdk.activate()

print(f"Activated {pdk_name}")

