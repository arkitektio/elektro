"""Offline tests: table and sparse declarations are checked before any bytes move."""

import numpy as np
import pytest
import scipy.sparse as sp
from pydantic import ValidationError

from elektro.api.schema import (
    AxisType,
    ColumnInput,
    CreateSparseDatasetInput,
    CreateTableDatasetInput,
    SparseAxisInput,
    TableIdentifiesInput,
)
from elektro.scalars import ParquetLike, SporadikLike

UNITS = TableIdentifiesInput(table="1")


def _raster() -> sp.csr_matrix:
    return sp.csr_matrix(np.eye(3, 10, dtype=np.float32))


def _sparse(*axes: SparseAxisInput) -> CreateSparseDatasetInput:
    return CreateSparseDatasetInput(name="raster", store=_raster(), axes=list(axes))


def test_raster_with_one_time_axis_is_accepted() -> None:
    model = _sparse(
        SparseAxisInput(name="unit", identified_by=[UNITS]),
        SparseAxisInput(name="t", type=AxisType.TIME),
    )
    assert isinstance(model.store, SporadikLike)


def test_identified_time_axis_is_refused() -> None:
    with pytest.raises(ValidationError, match="samples, not ids"):
        _sparse(
            SparseAxisInput(name="unit", identified_by=[UNITS]),
            SparseAxisInput(name="t", type=AxisType.TIME, identified_by=[UNITS]),
        )


def test_unidentified_index_axis_is_refused() -> None:
    with pytest.raises(ValidationError, match="empty `identified_by`"):
        _sparse(SparseAxisInput(name="unit"), SparseAxisInput(name="t", type=AxisType.TIME))


def test_two_time_axes_are_refused() -> None:
    with pytest.raises(ValidationError, match="all TIME"):
        CreateSparseDatasetInput(
            name="raster",
            store=_raster(),
            axes=[
                SparseAxisInput(name="unit", identified_by=[UNITS]),
                SparseAxisInput(name="t", type=AxisType.TIME),
                SparseAxisInput(name="t2", type=AxisType.TIME),
            ],
        )


def test_rank_disagreeing_with_the_matrix_is_refused() -> None:
    with pytest.raises(ValidationError, match="has shape"):
        CreateSparseDatasetInput(
            name="raster",
            store=_raster(),
            axes=[
                SparseAxisInput(name="unit", identified_by=[UNITS]),
                SparseAxisInput(name="t", type=AxisType.TIME),
                SparseAxisInput(name="channel", identified_by=[UNITS]),
            ],
        )


def test_single_identification_instead_of_list_is_named() -> None:
    with pytest.raises(ValidationError, match="is a list"):
        SparseAxisInput(name="unit", identified_by=UNITS)  # type: ignore[arg-type]


def test_table_columns_are_resolved_from_a_dict() -> None:
    model = CreateTableDatasetInput(
        name="events",
        data={"t": np.array([0.25, 0.5]), "label": ["on", "off"]},
        columns=[ColumnInput(name="t", axis_type=AxisType.TIME, unit="second")],
    )
    assert isinstance(model.data, ParquetLike)
    # Every column of the file, in its order, with the DuckDB type the server reads back.
    assert [(c.name, c.dtype) for c in model.columns] == [("t", "DOUBLE"), ("label", "VARCHAR")]
    assert "columns" in model.model_fields_set
