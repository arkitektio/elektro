"""An axis may be named by anything xarray names a dim with: any hashable."""

from enum import Enum
from types import SimpleNamespace

import pytest

from elektro import specs
from elektro.api.schema import AxisInput, AxisType
from elektro.scalars import axis_name


class Dim(str, Enum):
    """A hashable dim that is not a plain ``str``."""

    T = "t"


def test_an_axis_is_called_by_its_name_or_its_enum_value() -> None:
    """``str()`` of a str-valued enum member is ``'Dim.T'``; its name is its value."""
    assert axis_name("c") == "c"
    assert axis_name(Dim.T) == "t"


def test_a_bare_axis_name_may_be_any_hashable() -> None:
    """A str, a str-valued enum member, or an AxisInput itself."""
    assert AxisInput.model_validate("t").type == AxisType.TIME
    assert AxisInput.model_validate(Dim.T).name == "t"
    assert AxisInput.model_validate(AxisInput(name="c", type=AxisType.CHANNEL)).name == "c"


def test_carried_axes_take_the_dims_xarray_reports(monkeypatch: pytest.MonkeyPatch) -> None:
    """Known dims keep their source type; a new one falls back to its name."""
    monkeypatch.setattr(specs, "axis_types", lambda lens: ("TIME", "CHANNEL"))
    lens = SimpleNamespace(axis_names=("t", "c"))
    axes = specs.carried_axes(lens, (Dim.T, "c"))  # type: ignore[arg-type]
    assert [(a.name, a.type) for a in axes] == [("t", AxisType.TIME), ("c", AxisType.CHANNEL)]
