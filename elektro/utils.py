from typing import Dict, Any, List
import math
from .vars import current_ontology, current_graph


def create_linked_expression(expression, graph=None):
    from elektro.api.schema import link_expression

    if graph is None:
        graph = current_graph.get()

    assert graph is not None, "Graph must be set"

    return link_expression(expression=expression, graph=graph)


def v(name, description=None):
    from elektro.api.schema import create_expression, ExpressionKind

    exp = create_expression(
        label=name,
        ontology=current_ontology.get(),
        kind=ExpressionKind.ENTITY,
        description=description,
    )
    return create_linked_expression(exp)


def e(name, description=None):
    from elektro.api.schema import create_expression, ExpressionKind

    exp = create_expression(
        label=name,
        ontology=current_ontology.get(),
        kind=ExpressionKind.RELATION,
        description=description,
    )
    return create_linked_expression(exp)


def m(name, metric_kind, description=None):
    from elektro.api.schema import create_expression, ExpressionKind, MetricDataType

    exp = create_expression(
        label=name,
        ontology=current_ontology.get(),
        kind=ExpressionKind.METRIC,
        metric_kind=metric_kind,
        description=description,
    )
    return create_linked_expression(exp)


def rm(name, metric_kind, description=None):
    from elektro.api.schema import create_expression, ExpressionKind, MetricDataType

    exp = create_expression(
        label=name,
        ontology=current_ontology.get(),
        kind=ExpressionKind.RELATION_METRIC,
        metric_kind=metric_kind,
        description=description,
    )
    return create_linked_expression(exp)


def rechunk(
    sizes: Dict[str, int], itemsize: int = 8, chunksize_in_bytes: int = 20_000_000
) -> Dict[str, int]:
    """Calculates Chunks for a given size

    Args:
        sizes (Dict): The sizes of the image

    Returns:
        The chunks(dict): The chunks
    """
    assert "c" in sizes, "c must be in sizes"
    assert "z" in sizes, "z must be in sizes"
    assert "y" in sizes, "y must be in sizes"
    assert "x" in sizes, "x must be in sizes"
    assert "t" in sizes, "t must be in sizes"

    all_size = sizes["c"] * sizes["z"] * sizes["y"] * sizes["x"] * sizes["t"]

    # We will not rechunk if the size is smaller than 1MB
    if all_size < 1 * 2048 * 2048:
        return sizes

    x = (
        sizes["x"] if not sizes["x"] > 2048 else 2048
    )  # Biggest X but not bigger than 1024
    y = (
        sizes["y"] if not sizes["y"] > 2048 else 2048
    )  # Biggest Y but not bigger than 1024

    best_z = math.ceil(chunksize_in_bytes / (x * y * itemsize))
    z = best_z if best_z < sizes["z"] else sizes["z"]

    best_t = math.ceil(chunksize_in_bytes / (x * y * z * itemsize))
    t = best_t if best_t < sizes["t"] else sizes["t"]

    chunk = {
        "c": 1,
        "z": z,
        "y": y,
        "x": x,
        "t": t,
    }

    return chunk
