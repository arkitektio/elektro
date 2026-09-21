"""Checking a sparse dataset's declaration against the matrix it is made of, before it moves.

Vendored from mikro's ``mikro.sparse``, with elektro's one divergence: **a sparse axis may be
TIME**. A spike raster is ``(unit: INDEX, t: TIME)`` -- its sample axis has a metric, because it
was sampled exactly as the recording it was sorted from, and a sampling law
(``createSamplingLaw``) places it on a clock once the dataset exists::

    raster = create_sparse_dataset(
        name="spikes",
        store=[spikes.tocsr(), spikes.tocsc()],
        axes=[
            SparseAxisInput(name="unit", identified_by=[TableIdentifiesInput(table=units.id)]),
            SparseAxisInput(name="t", type=AxisType.TIME),
        ],
    )

Every refusal below mirrors one the server makes (``core/mutations/sparse_dataset.py``), and
none is stricter. What the client's copy buys is *order*: ``Elektro.execute`` validates before the
upload middleware runs, so a refusal raised here comes before the bytes move.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from sporadik import Layout

    from elektro.api.schema import SparseAxisInput

#: The lowest rank a sparse dataset can have: a compressed axis needs another to hold positions.
MIN_RANK: Final[int] = 2

#: The axis types a sparse matrix admits: it enumerates (INDEX) and may have one sample axis.
SPARSE_AXIS_TYPES: Final[frozenset[str]] = frozenset({"INDEX", "TIME"})


class SparseDeclarationError(ValueError):
    """Raised when a declaration cannot describe the matrix it is made for."""


def _enum_value(value: object) -> str:
    """An enum-valued field's value, however it is spelled."""
    return str(getattr(value, "value", value) or "")


def _axis_type(axis: SparseAxisInput) -> str:
    """The declared type, INDEX when unset -- the server's default."""
    return _enum_value(getattr(axis, "type", None)) or "INDEX"


def _identifications(axis: SparseAxisInput) -> tuple:
    """The identifications on one axis, under either spelling of the field."""
    entries = getattr(axis, "identified_by", None)
    if entries is None:
        entries = getattr(axis, "identifiedBy", None)
    return tuple(entries or ())


def check_axes(axes: Sequence[SparseAxisInput]) -> None:
    """Refuse a set of axes that could not describe any matrix.

    In the order the server makes them, none of which needs the store:

    1. fewer than :data:`MIN_RANK` axes;
    2. a duplicate axis name;
    3. a type other than INDEX or TIME, more than one TIME axis, or no INDEX axis at all;
    4. a TIME axis that is identified (its positions are samples, not ids);
    5. an INDEX axis that is not (no source could ever key it);
    6. more than one table identifying one axis.

    Raises:
        SparseDeclarationError: If any of them holds.
    """
    names = [axis.name for axis in axes]
    if len(axes) < MIN_RANK:
        raise SparseDeclarationError(
            f"A sparse dataset declares at least {MIN_RANK} axes and this one declares "
            f"{len(axes)} {names}: a single compressed axis needs at least one other to hold "
            "the positions."
        )
    duplicates = sorted({name for name in names if names.count(name) > 1})
    if duplicates:
        raise SparseDeclarationError(
            f"The axis {duplicates} is declared more than once. An axis name is how a "
            "colouring names a position along it, so it has to pick one axis."
        )

    types = {axis.name: _axis_type(axis) for axis in axes}
    wrong = sorted(name for name, kind in types.items() if kind not in SPARSE_AXIS_TYPES)
    if wrong:
        raise SparseDeclarationError(
            f"{wrong} declare a type other than INDEX or TIME. A sparse matrix enumerates "
            "(INDEX) and may have one sample axis (TIME); nothing else."
        )
    timed = [name for name, kind in types.items() if kind == "TIME"]
    if len(timed) > 1:
        raise SparseDeclarationError(
            f"{timed} are all TIME. A spike raster has one sample axis, and one sampling law "
            "places it; a second would be a second clock."
        )
    if len(timed) == len(axes):
        raise SparseDeclarationError(
            "There is no INDEX axis. A sparse matrix enumerates something -- units, channels "
            "-- along at least one axis."
        )

    identified_time = [axis.name for axis in axes if _axis_type(axis) == "TIME" and _identifications(axis)]
    if identified_time:
        raise SparseDeclarationError(
            f"The TIME axis {identified_time} is identified, but a TIME axis' positions are "
            "samples, not ids. Leave `identified_by` empty and place the axis on a clock with "
            "`create_sampling_law` once the dataset exists."
        )
    empty = [axis.name for axis in axes if _axis_type(axis) == "INDEX" and not _identifications(axis)]
    if empty:
        raise SparseDeclarationError(
            f"The INDEX axes {empty} have an empty `identified_by`. An axis of a sparse matrix "
            "is positions and nothing else, so one that does not say what they are is one no "
            "source could ever key. Name the table whose rows the positions are (a units "
            "table), or a dataset whose contents are the ids."
        )

    for axis in axes:
        tables = [entry for entry in _identifications(axis) if _enum_value(entry.kind) == "TABLE"]
        if len(tables) > 1:
            raise SparseDeclarationError(
                f"Axis {axis.name!r} is identified by more than one table. An axis enumerates "
                "one thing: two tables would be two different answers to what a position is."
            )


def check_against_store(
    axes: Sequence[SparseAxisInput],
    layouts: Mapping[int, Layout],
) -> None:
    """Refuse a declaration that disagrees with the matrix's own shape.

    The one refusal the server cannot make first: it reads the shape off a row written at
    ``finishSparseUpload``, after the bytes have landed. Here the matrix is in hand, and a
    declaration that disagrees with it places every lookup one position out and raises nothing.

    Raises:
        SparseDeclarationError: If the axis count disagrees with the matrix's rank.
    """
    if not layouts:
        return
    shape = tuple(int(size) for size in next(iter(layouts.values())).shape)
    if len(shape) != len(axes):
        names = [axis.name for axis in axes]
        raise SparseDeclarationError(
            f"{len(axes)} axes {names} are declared, but the matrix has shape {list(shape)}. "
            "The axes describe the store, in the order its shape is written, so there are the "
            "same number of them."
        )
