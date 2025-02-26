
from rekuest_next.structures.default import (
    get_default_structure_registry,
    id_shrink,
)
from rekuest_next.api.schema import PortScope
from rekuest_next.widgets import SearchWidget
from elektro.api.schema import *

structure_reg = get_default_structure_registry()

structure_reg.register_as_structure(
    Trace,
    identifier="@elektro/trace",
    aexpand=aget_trace,
    ashrink=id_shrink,
    scope=PortScope.GLOBAL,
    default_widget=SearchWidget(
        query=SearchTracesQuery.Meta.document, ward="elektro"
    ),
)