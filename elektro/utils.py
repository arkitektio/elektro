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
    assert "t" in sizes, "t must be in sizes"

    all_size = sizes["c"] * sizes["t"]

    # We will not rechunk if the size is smaller than 1MB
    if all_size < 1 * 2048 * 2048:
        return sizes

    best_t = math.ceil(chunksize_in_bytes / (all_size * itemsize))
    t = best_t if best_t < sizes["t"] else sizes["t"]


    chunk = {
        "c": 1,
        "t": t,
    }

    return chunk
