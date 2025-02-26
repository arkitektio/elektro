
from rekuest_next.structures.default import (
    get_default_structure_registry,
    id_shrink,
)
from rekuest_next.api.schema import PortScope
from rekuest_next.widgets import SearchWidget
from elektro.api.schema import (
    Image,
    aget_image,
    SearchImagesQuery,
    Dataset,
    Stage,
    aget_stage,
    File,
    Table,
    aget_file,
    SearchStagesQuery,
    SearchTablesQuery,
    SearchFilesQuery,
    aget_rgb_context,
    RGBContext,
    aget_dataset,
    aget_table,
)
from elektro.api.schema import (
    Snapshot,
    aget_snapshot,
    SearchSnapshotsQuery,
    ROI,
    aget_roi,
    aget_rendered_plot,
    RenderedPlot,
    SearchRoisQuery,
    SearchRenderedPlotsQuery,
    Mesh,
    aget_mesh,
    SearchMeshesQuery,
)

structure_reg = get_default_structure_registry()

structure_reg.register_as_structure(
    Image,
    identifier="@mikro/image",
    aexpand=aget_image,
    ashrink=id_shrink,
    scope=PortScope.GLOBAL,
    default_widget=SearchWidget(
        query=SearchImagesQuery.Meta.document, ward="mikro"
    ),
)
structure_reg.register_as_structure(
    Snapshot,
    identifier="@mikro/snapshot",
    aexpand=aget_snapshot,
    ashrink=id_shrink,
    scope=PortScope.GLOBAL,
    default_widget=SearchWidget(
        query=SearchSnapshotsQuery.Meta.document, ward="mikro"
    ),
)

structure_reg.register_as_structure(
    ROI,
    identifier="@mikro/roi",
    aexpand=aget_roi,
    ashrink=id_shrink,
    scope=PortScope.GLOBAL,
    default_widget=SearchWidget(query=SearchRoisQuery.Meta.document, ward="mikro"),
)
structure_reg.register_as_structure(
    Stage,
    identifier="@mikro/stage",
    aexpand=aget_stage,
    ashrink=id_shrink,
    scope=PortScope.GLOBAL,
    default_widget=SearchWidget(
        query=SearchStagesQuery.Meta.document, ward="mikro"
    ),
)
structure_reg.register_as_structure(
    Dataset,
    identifier="@mikro/dataset",
    aexpand=aget_dataset,
    ashrink=id_shrink,
    scope=PortScope.GLOBAL,
    default_widget=SearchWidget(
        query=SearchImagesQuery.Meta.document, ward="mikro"
    ),
)
structure_reg.register_as_structure(
    File,
    identifier="@mikro/file",
    aexpand=aget_file,
    ashrink=id_shrink,
    scope=PortScope.GLOBAL,
    default_widget=SearchWidget(query=SearchFilesQuery.Meta.document, ward="mikro"),
)
structure_reg.register_as_structure(
    RGBContext,
    identifier="@mikro/rbgcontext",
    aexpand=aget_rgb_context,
    ashrink=id_shrink,
    scope=PortScope.GLOBAL,
)

structure_reg.register_as_structure(
    RenderedPlot,
    identifier="@mikro/renderedplot",
    aexpand=aget_rendered_plot,
    ashrink=id_shrink,
    scope=PortScope.GLOBAL,
    default_widget=SearchWidget(
        query=SearchRenderedPlotsQuery.Meta.document, ward="mikro"
    ),
)

structure_reg.register_as_structure(
    Mesh,
    identifier="@mikro/mesh",
    aexpand=aget_mesh,
    ashrink=id_shrink,
    scope=PortScope.GLOBAL,
    default_widget=SearchWidget(query=SearchMeshesQuery.Meta.document, ward="mikro"),
)

structure_reg.register_as_structure(
    Table,
    identifier="@mikro/table",
    aexpand=aget_table,
    ashrink=id_shrink,
    scope=PortScope.GLOBAL,
    default_widget=SearchWidget(query=SearchTablesQuery.Meta.document, ward="mikro"),
)
