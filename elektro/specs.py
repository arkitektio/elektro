"""Spec types: what a lens structurally *is*, as importable Annotated aliases.

mikro's ``mikro.specs``, for time series. An action that detects spikes does not
accept "a Lens" -- it accepts a single-channel voltage trace. These aliases say
so in the signature, in the same vocabulary ``ArrayDatasetSpec`` uses
server-side::

    from elektro.specs import SingleChannelTrace, VoltageTrace, Spectrogram

    @register
    def spectrogram(trace: SingleChannelTrace) -> Spectrogram: ...

Each alias wraps :class:`~elektro.api.schema.Lens` in a mirrored
``Requires``/``Provides`` pair over the descriptor vocabulary below. Rekuest
keeps only the side a port can carry -- ``requires`` on arguments, ``provides``
on returns -- so the same alias works in both positions, and the constraints
become wiring information: a ``Trace`` argument only matches candidates whose
descriptors satisfy it, and a ``Spectrogram`` return advertises what it produced.

The vocabulary counts axes by :class:`~elektro.api.schema.AxisType` rather than
naming positions, because elektro declares axes in the order the data has them
and finds its time and channel axes by type, never by position. Counts make
specs stack the way ``ArrayDatasetSpec`` says they do -- a ``(t, c)`` recording
is SCALAR, TIMESERIES and MULTICHANNEL at once::

    MultichannelTrace = Annotated[Trace, *at_least(N_CHANNEL_AXES, 1)]

A lens never drops or reorders an axis -- it only crops, steps and pins -- so it
changes *extents*, and only ever downward. That splits the vocabulary into two
kinds of keys with different wiring meaning:

- **Invariant** (the ``n_*_axes`` counts, ``VALUE_DIMENSION``): no lens over a
  dataset can change them. A mismatch filters the dataset out -- it is
  fundamentally not that kind of data.
- **Adjustable** (the extents in ``ADJUSTABLE_KEYS``: ``n_channels``,
  ``n_samples``, ``n_indices``): a mismatch is a *conversion target*. A frontend
  can satisfy ``n_channels <= 1`` on a 32-channel recording by pinning one
  channel -- and which channel is exactly the choice to render as a picker. The
  composed Lens IS the conversion: actions take a lens, so passing the composed
  view converts on the fly without touching the data.

What is elektro's rather than mikro's:

- the axis types: ``FREQUENCY`` (a spectrogram's rows) and ``INDEX`` (sweeps,
  trials, units -- no metric) are counted; mikro's ``SPECTRUM`` / ``MICROTIME``
  are not this service's;
- ``N_SAMPLES`` is mikro's ``N_TIMEPOINTS``, named for what a TIME axis holds
  here, and ``N_INDICES`` makes one sweep of an episodic recording pinnable;
- ``VALUE_DIMENSION`` -- what the values *measure* (voltage, current, ...) -- is
  structural here, not provenance: it is read off the dataset's ``valueUnit``,
  so ``VoltageTrace`` can be matched on a candidate without its producer having
  said so. A dataset that states no unit has no such key, and fails such a spec;
- ``Categorical`` is mikro's ``LabelMask``: values that are ids (a unit
  assignment, event codes), provided by a producer and never inferred.

Three rules, each protecting against a silent failure (mikro's, unchanged):

- Aliases are plain assignments, never PEP 695 ``type`` statements. A ``type``
  alias wraps the Annotated in a ``TypeAliasType`` that rekuest's definition
  machinery does not unwrap, so every marker is dropped without an error.
- Aliases here carry no ``Description``: it is single-valued, so a base type
  that had one could never be refined ("Multiple descriptions found"). Add
  yours at the leaf: ``Annotated[Trace, Description("...")]``.
- ``Categorical`` is provenance, not structure: ``lens_descriptors`` never emits
  ``VALUE_KIND``.
"""

from __future__ import annotations

import functools
import re
from collections import Counter, abc
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import (
    Annotated,
    Any,
    Final,
    Literal,
    Protocol,
    Union,
    cast,
    get_args,
)

from rekuest.annotations import Provides, Requires
from rekuest.api.schema import DescriptorOperator, RequiresInput

from elektro.api.schema import AxisInput, AxisType, Lens
from elektro.vocabulary import (
    AxisSelection,
    AxisTypeName,
    default_axis_type,
    normalize_selection,
)

# Descriptor keys, namespaced like the other @elektro structure identifiers.
# One vocabulary drives both sides: the aliases below constrain on these keys,
# and `lens_descriptors` computes them for a candidate lens.
N_SPACE_AXES: Final = "@elektro/n_space_axes"
N_TIME_AXES: Final = "@elektro/n_time_axes"
N_CHANNEL_AXES: Final = "@elektro/n_channel_axes"
N_FREQUENCY_AXES: Final = "@elektro/n_frequency_axes"
N_INDEX_AXES: Final = "@elektro/n_index_axes"
N_CHANNELS: Final = "@elektro/n_channels"
N_SAMPLES: Final = "@elektro/n_samples"
N_INDICES: Final = "@elektro/n_indices"
VALUE_DIMENSION: Final = "@elektro/value_dimension"
VALUE_KIND: Final = "@elektro/value_kind"

#: The closed set of descriptor keys this vocabulary defines. A key outside it
#: is not a typo the server will catch -- nothing on either side computes it, so
#: the constraint would simply never be satisfiable.
DescriptorKey = Literal[
    "@elektro/n_space_axes",
    "@elektro/n_time_axes",
    "@elektro/n_channel_axes",
    "@elektro/n_frequency_axes",
    "@elektro/n_index_axes",
    "@elektro/n_channels",
    "@elektro/n_samples",
    "@elektro/n_indices",
    "@elektro/value_dimension",
    "@elektro/value_kind",
]

#: What a descriptor key can be constrained to. The counts are ints; the value
#: keys are strings; the set operators (IN, NOT_IN) take a sequence of either.
DescriptorValue = Union[int, str, bool, Sequence[int | str]]

#: The matching operators, as they read back off a `RequiresInput`. A Literal
#: rather than `DescriptorOperator` because `use_enum_values=True` means the
#: model stores the plain value -- annotating a read as the enum would be a lie.
ConstraintOperator = Literal[
    "EQUALS",
    "NOT_EQUALS",
    "GTE",
    "LTE",
    "IN",
    "NOT_IN",
    "CONTAINS",
    "MATCHES",
    "EXISTS",
]

_KEY_BY_AXIS_TYPE: Final[Mapping[AxisTypeName, DescriptorKey]] = {
    "SPACE": N_SPACE_AXES,
    "TIME": N_TIME_AXES,
    "CHANNEL": N_CHANNEL_AXES,
    "FREQUENCY": N_FREQUENCY_AXES,
    "INDEX": N_INDEX_AXES,
}

# The adjustability contract, mirrored by frontend composers: each key measures
# the total extent along one axis type, so a lens can shrink it (pin, crop) but
# never grow it. Every key not listed here is lens-invariant.
ADJUSTABLE_KEYS: Final[Mapping[DescriptorKey, AxisTypeName]] = {
    N_CHANNELS: "CHANNEL",
    N_SAMPLES: "TIME",
    N_INDICES: "INDEX",
}

#: What `VALUE_DIMENSION` can say, and the unit each is recognised by. A unit of
#: another dimension reads as ``"other"``; ``"a.u."`` (arbitrary units) as
#: ``"arbitrary"``; no stated unit leaves the key absent.
ValueDimension = Literal[
    "voltage",
    "current",
    "conductance",
    "resistance",
    "capacitance",
    "charge",
    "time",
    "frequency",
    "concentration",
    "dimensionless",
    "arbitrary",
    "other",
]

_REFERENCE_UNITS: Final[Mapping[ValueDimension, str]] = {
    "voltage": "volt",
    "current": "ampere",
    "conductance": "siemens",
    "resistance": "ohm",
    "capacitance": "farad",
    "charge": "coulomb",
    "time": "second",
    "frequency": "hertz",
    "concentration": "mole / liter",
    "dimensionless": "dimensionless",
}


def constrain(
    key: DescriptorKey, operator: ConstraintOperator, value: DescriptorValue
) -> tuple[Requires, Provides]:
    """A mirrored Requires/Provides pair for one constraint.

    Both directions carry the same statement so one alias serves argument and
    return positions; the port converter keeps the applicable side and drops
    the other.
    """
    return (
        Requires(key=key, operator=DescriptorOperator(operator), value=value),
        Provides(key=key, operator=DescriptorOperator(operator), value=value),
    )


def exactly(key: DescriptorKey, value: DescriptorValue) -> tuple[Requires, Provides]:
    """Constrain a descriptor key to exactly a value."""
    return constrain(key, "EQUALS", value)


def at_least(key: DescriptorKey, value: DescriptorValue) -> tuple[Requires, Provides]:
    """Constrain a descriptor key to at least a value."""
    return constrain(key, "GTE", value)


def at_most(key: DescriptorKey, value: DescriptorValue) -> tuple[Requires, Provides]:
    """Constrain a descriptor key to at most a value."""
    return constrain(key, "LTE", value)


def refine(base: Any, *markers: Any) -> Any:  # noqa: ANN401 -- see `Spec` below
    """Stack more markers onto a spec type, building it dynamically.

    ``Annotated`` flattens on nesting and Requires/Provides accumulate, so a
    refined spec carries the base's constraints plus the new ones. For an alias
    you will write in signatures, prefer the literal spelling -- static checkers
    reject a call result in type position but accept the literal::

        StereoTrace = Annotated[Trace, *exactly(N_CHANNELS, 2)]
    """
    if not markers:
        return base
    return Annotated[base, *markers]


# --- Spatial specs: exactly one of these holds for any lens. ----------------

Scalar = Annotated[Lens, *exactly(N_SPACE_AXES, 0)]
"""No spatial extent: no SPACE axis at all. What nearly every electrophysiology
array is."""

Profile = Annotated[Lens, *exactly(N_SPACE_AXES, 1)]
"""One spatial axis -- a depth profile along a probe."""

Image = Annotated[Lens, *exactly(N_SPACE_AXES, 2)]
"""Two spatial axes: a plane -- a current-source density map over a probe's
face, an imaging-derived array."""

Volume = Annotated[Lens, *exactly(N_SPACE_AXES, 3)]
"""Three spatial axes."""

Hypervolume = Annotated[Lens, *at_least(N_SPACE_AXES, 4)]
"""Four or more spatial axes."""

# --- Presence modifiers: any subset may hold alongside a spatial spec. ------

Timeseries = Annotated[Lens, *at_least(N_TIME_AXES, 1)]
"""Carries a TIME axis. Presence only: a single-sample time axis counts."""

Multichannel = Annotated[Lens, *at_least(N_CHANNEL_AXES, 1)]
"""Carries a CHANNEL axis. Presence only: a one-channel axis counts."""

Spectral = Annotated[Lens, *at_least(N_FREQUENCY_AXES, 1)]
"""Carries a FREQUENCY axis: a spectrum or a spectrogram."""

Indexed = Annotated[Lens, *at_least(N_INDEX_AXES, 1)]
"""Carries an INDEX axis: sweeps, trials or units -- positions with no metric."""

SingleChannel = Annotated[Lens, *at_most(N_CHANNELS, 1)]
"""At most one channel's worth of data -- no channel axis, or one pinned to a
single position. Extent-based on purpose: a multichannel recording satisfies it
after a composer pins a channel -- which channel is the frontend's picker.
Action code must tolerate a surviving size-1 channel axis (squeeze it)."""

SingleSweep = Annotated[Lens, *at_most(N_INDICES, 1)]
"""At most one position along INDEX axes -- one sweep, one trial, one unit.
Pinnable like ``SingleChannel``: which sweep is the frontend's picker."""

# --- Electrophysiology stacks. ----------------------------------------------

Trace = Annotated[
    Scalar,
    *exactly(N_TIME_AXES, 1),
    *exactly(N_FREQUENCY_AXES, 0),
    *exactly(N_INDEX_AXES, 0),
]
"""A continuous signal: one TIME axis, any channels, no spatial, spectral or
sweep axis. ``(t)`` and ``(t, c)`` both qualify."""

SingleChannelTrace = Annotated[Trace, *at_most(N_CHANNELS, 1)]
"""A signal with at most one channel's worth of data -- "a Vm trace".
Composable: any multichannel recording fits after pinning a channel."""

MultichannelTrace = Annotated[Trace, *at_least(N_CHANNEL_AXES, 1)]
"""A signal with a channel axis -- an electrode array's recording."""

VoltageTrace = Annotated[Trace, *exactly(VALUE_DIMENSION, "voltage")]
"""A signal whose values are voltages: a membrane potential, an LFP, an
extracellular recording. Read off the dataset's ``valueUnit``."""

CurrentTrace = Annotated[Trace, *exactly(VALUE_DIMENSION, "current")]
"""A signal whose values are currents: a clamp current, an injected stimulus."""

Sweeps = Annotated[
    Scalar,
    *exactly(N_TIME_AXES, 1),
    *exactly(N_INDEX_AXES, 1),
    *exactly(N_FREQUENCY_AXES, 0),
]
"""An episodic recording: one INDEX axis (sweeps, trials) against one TIME axis,
any channels. Structurally also what unit waveform templates ``(unit, c, w)``
are; which one a dataset is, is its provenance (a template set derives from a
spike raster), not its shape."""

Spectrogram = Annotated[Scalar, *exactly(N_TIME_AXES, 1), *at_least(N_FREQUENCY_AXES, 1)]
"""Power over time and frequency: one TIME axis and a FREQUENCY axis."""

Spectrum = Annotated[Scalar, *exactly(N_TIME_AXES, 0), *at_least(N_FREQUENCY_AXES, 1)]
"""Power over frequency alone: a FREQUENCY axis and no TIME axis -- a PSD."""

Categorical = Annotated[Lens, *exactly(VALUE_KIND, "categorical")]
"""A lens whose values are ids, not magnitudes -- a unit assignment, event codes.
Never structurally inferred: only a producer that *made* ids provides this, and
only an action that requires it will be offered them."""


# --- The candidate side: the same vocabulary, computed from a lens. ---------


class _TypedAxis(Protocol):
    """One axis of a coordinate system, as `_axis_table` reads it."""

    @property
    def order(self) -> int: ...

    @property
    def type(self) -> AxisType: ...


class _HasCoordinateSystem(Protocol):
    """A lens: it names the space it frames its data in its *coordinate* system."""

    @property
    def axis_names(self) -> Sequence[str]: ...

    @property
    def shape(self) -> Sequence[int]: ...

    @property
    def coordinate_system(self) -> _HasAxes | None: ...


class _HasIntrinsicSystem(Protocol):
    """A dataset: it calls the space of its own sample grid *intrinsic*."""

    @property
    def axis_names(self) -> Sequence[str]: ...

    @property
    def shape(self) -> Sequence[int]: ...

    @property
    def intrinsic_system(self) -> _HasAxes | None: ...


class _HasAxes(Protocol):
    """Whichever system a candidate carries, all this side needs is its axes."""

    @property
    def axes(self) -> Sequence[_TypedAxis]: ...


Candidate = Union[_HasCoordinateSystem, _HasIntrinsicSystem]
"""Anything with ``axis_names``, ``shape`` and a typed system -- a Lens
(``coordinate_system``, else its ``dataset``'s intrinsic system) or an
ArrayDataset (``intrinsic_system``)."""


def _typed_system(candidate: Candidate) -> _HasAxes | None:
    """The system whose axes type the candidate's: its own, else its dataset's.

    A lens selects without dropping or reordering an axis, so its dataset's
    intrinsic axes type it exactly when the lens was fetched without a system.
    """
    system = getattr(candidate, "coordinate_system", None) or getattr(
        candidate, "intrinsic_system", None
    )
    if system is None:
        dataset = getattr(candidate, "dataset", None)
        system = getattr(dataset, "intrinsic_system", None) if dataset is not None else None
    return system


def _axis_table(candidate: Candidate) -> tuple[tuple[str, AxisTypeName, int], ...]:
    """``(name, axis_type, extent)`` per axis, in array order.

    Types come from the candidate's typed system when it was fetched with one;
    otherwise the bare-name convention (``t`` -> TIME, ``c`` -> CHANNEL,
    ``sweep`` -> INDEX, ...), which refuses a name it has no entry for rather
    than guess (``vocabulary.UnknownAxisName``).
    """
    names = tuple(candidate.axis_names)
    shape = tuple(candidate.shape)
    system = _typed_system(candidate)
    types: tuple[AxisTypeName, ...]
    if system is not None:
        axes = sorted(system.axes, key=lambda axis: axis.order)
        # `use_enum_values` means the field may hold either the enum or its value.
        types = tuple(str(getattr(axis.type, "value", axis.type)) for axis in axes)  # type: ignore[assignment]
    else:
        types = tuple(default_axis_type(name) for name in names)
    return tuple(zip(names, types, shape))


def axis_types(candidate: Candidate) -> tuple[AxisTypeName, ...]:
    """Per-axis semantic types in array order, as AxisType value strings."""
    return tuple(axis_type for _, axis_type, _ in _axis_table(candidate))


@functools.lru_cache(maxsize=256)
def value_dimension(unit: str | None) -> ValueDimension | None:
    """What a value unit measures, in the ``VALUE_DIMENSION`` vocabulary.

    Read with kanne's registry -- the one the server validated the unit
    against. ``None`` for no unit (the key is then absent); ``"arbitrary"`` for
    ``a.u.``, checked first because pint would read it as *atomic* units;
    ``"other"`` for a unit of a dimension this vocabulary does not name, or one
    that does not parse.
    """
    if unit is None or not unit.strip():
        return None
    if unit.strip() == "a.u.":
        return "arbitrary"
    from kanne.registry import get_global_registry

    registry = get_global_registry()
    try:
        dimensionality = registry.Unit(unit).dimensionality
    except Exception:  # noqa: BLE001 -- pint raises several unrelated types for an unknown unit
        return "other"
    for dimension, reference in _REFERENCE_UNITS.items():
        if registry.Unit(reference).dimensionality == dimensionality:
            return dimension
    return "other"


def _value_unit(candidate: Candidate) -> str | None:
    """The dataset-wide value unit of a lens (through its dataset) or a dataset."""
    unit = getattr(candidate, "value_unit", None)
    if unit is None:
        dataset = getattr(candidate, "dataset", None)
        unit = getattr(dataset, "value_unit", None) if dataset is not None else None
    return unit


def lens_descriptors(candidate: Candidate) -> dict[DescriptorKey, DescriptorValue]:
    """The descriptor key/value pairs a lens (or dataset) carries as a match candidate.

    Emits every count key of the vocabulary (zero included -- ``Trace`` and
    ``SingleChannel`` match on absence) plus the adjustable extent keys (total
    extent across axes of that type), and ``VALUE_DIMENSION`` when the dataset
    states a value unit. ``VALUE_KIND`` is deliberately absent: it is
    provenance, carried only by a producer's ``Provides``.
    """
    table = _axis_table(candidate)
    counts = Counter(axis_type for _, axis_type, _ in table)
    descriptors: dict[DescriptorKey, DescriptorValue] = {
        key: counts.get(axis_type, 0) for axis_type, key in _KEY_BY_AXIS_TYPE.items()
    }
    for key, wanted in ADJUSTABLE_KEYS.items():
        descriptors[key] = sum(extent for _, axis_type, extent in table if axis_type == wanted)
    dimension = value_dimension(_value_unit(candidate))
    if dimension is not None:
        descriptors[VALUE_DIMENSION] = dimension
    return descriptors


def axes_of_type(lens: Lens, axis_type: AxisType | AxisTypeName) -> tuple[str, ...]:
    """The names of the lens' axes of one AxisType, in array order.

    The runtime counterpart of the spec vocabulary: a function typed over
    ``Trace`` should find its sample axis with ``axes_of_type(trace, AxisType.TIME)``
    rather than hard-coding ``"t"`` -- the spec guarantees the axis exists, not
    what it is called.
    """
    wanted = str(getattr(axis_type, "value", axis_type))
    return tuple(name for name, found in zip(lens.axis_names, axis_types(lens)) if found == wanted)


def carried_axes(lens: Lens, dims: Sequence[str]) -> list[AxisInput]:
    """AxisInput for a derived array's dims, types carried from the source lens.

    For ``create_array_dataset(axes=...)`` on a dataset computed from this lens:
    an axis that survived the computation keeps the semantic type it had at the
    source instead of being re-guessed from its name, so the derived dataset's
    descriptors -- and with them the action's Provides -- stay true even for
    unconventionally named axes. A genuinely new dim falls back to the bare-name
    convention.
    """
    types = dict(zip(lens.axis_names, axis_types(lens)))
    return [
        AxisInput(name=dim, type=AxisType(types[dim] if dim in types else default_axis_type(dim)))
        for dim in dims
    ]


# --- The fulfilment side: guarding a Provides before returning. -------------


class SpecMismatch(Exception):
    """A lens does not fulfil the spec it was about to be returned as."""


#: A spec type: one of the `Annotated` aliases above, or a refinement of one.
#: `Any` because Python has no type for "an ``Annotated`` alias carrying these
#: markers"; the alias exists so every spec-taking signature says *which* kind
#: of `Any` it means.
Spec = Any


def spec_constraints(spec: Spec) -> tuple[RequiresInput, ...]:
    """The constraints a spec type carries.

    Reads the Requires side of the mirrored pairs; since every pair states the
    same thing in both directions, this is also exactly what the spec's Provides
    promise.
    """
    args = get_args(spec)
    return tuple(marker for marker in args[1:] if isinstance(marker, RequiresInput))


def _constrained_key(constraint: RequiresInput) -> DescriptorKey:
    """The key a constraint names. A foreign key reads as absent and fails its constraint."""
    return cast(DescriptorKey, constraint.key)


def _constraint_operator(constraint: RequiresInput) -> ConstraintOperator:
    """A constraint's operator as a plain value, whichever spelling the model holds."""
    operator = constraint.operator
    return str(getattr(operator, "value", operator))  # type: ignore[return-value]


def _holds(
    operator: ConstraintOperator,
    actual: DescriptorValue | None,
    expected: DescriptorValue | None,
    present: bool,
) -> bool:
    """Evaluate one constraint operator against a descriptor value.

    ``expected`` is optional because rekuest types ``RequiresInput.value`` so;
    only EXISTS may leave it out, and any other operator without one is refused.
    """
    if operator == "EXISTS":
        return present
    if expected is None:
        raise ValueError(f"{operator} needs a value to compare against")
    if not present:
        return False
    if operator == "EQUALS":
        return bool(actual == expected)
    if operator == "NOT_EQUALS":
        return bool(actual != expected)
    if operator in ("GTE", "LTE"):
        if not isinstance(actual, int) or not isinstance(expected, int):
            raise TypeError(
                f"{operator} orders counts; {actual!r} and {expected!r} are not both counts"
            )
        return actual >= expected if operator == "GTE" else actual <= expected
    if operator in ("IN", "NOT_IN"):
        if isinstance(expected, str) or not isinstance(expected, abc.Sequence):
            raise TypeError(f"{operator} needs a sequence of allowed values, got {expected!r}")
        found = actual in expected
        return found if operator == "IN" else not found
    if operator == "CONTAINS":
        if isinstance(actual, str):
            if not isinstance(expected, str):
                raise TypeError(
                    f"CONTAINS against the string {actual!r} needs a substring, got {expected!r}"
                )
            return expected in actual
        if not isinstance(actual, abc.Sequence):
            raise TypeError(f"CONTAINS needs a sequence descriptor, got {actual!r}")
        return any(item == expected for item in actual)
    if operator == "MATCHES":
        return re.fullmatch(str(expected), str(actual)) is not None
    raise ValueError(f"Unknown constraint operator {operator!r}")


#: Provenance keys a producer vouches for, which structure cannot show.
Declarations = Mapping[DescriptorKey, DescriptorValue]


def unfulfilled(
    lens: Candidate, spec: Spec, declares: Declarations | None = None
) -> tuple[str, ...]:
    """Every constraint of `spec` this lens does not satisfy, human-readable.

    Structural keys are computed via `lens_descriptors`; provenance keys
    (``VALUE_KIND``) cannot be computed and must be stated via `declares` -- an
    absent key fails its constraint rather than being skipped.
    """
    descriptors = lens_descriptors(lens)
    if declares:
        descriptors.update(declares)
    failures: list[str] = []
    for constraint in spec_constraints(spec):
        key = _constrained_key(constraint)
        operator = _constraint_operator(constraint)
        present = key in descriptors
        actual = descriptors.get(key)
        if not _holds(operator, actual, constraint.value, present):
            failures.append(_describe(constraint, operator, actual, present))
    return tuple(failures)


def _describe(
    constraint: RequiresInput,
    operator: ConstraintOperator,
    actual: DescriptorValue | None,
    present: bool,
) -> str:
    """One unsatisfied constraint, human-readable."""
    detail = f"actual {actual!r}" if present else "key absent -- declare it if it is provenance"
    return f"{constraint.key} {operator} {constraint.value!r} ({detail})"


def fulfills(lens: Candidate, spec: Spec, declares: Declarations | None = None) -> bool:
    """Whether a lens satisfies every constraint of a spec."""
    return not unfulfilled(lens, spec, declares)


def ensure(lens: Lens, spec: Spec, declares: Declarations | None = None) -> Lens:
    """Assert a lens fulfils a spec, then return it -- the produce-side guard.

    A Provides is a promise the definition makes statically; nothing checks the
    value an implementation actually returns. Returning through ``ensure``
    closes that gap::

        return ensure(result.lens(), Spectrogram)
        return ensure(assignment.lens(), Categorical, declares={VALUE_KIND: "categorical"})
    """
    failures = unfulfilled(lens, spec, declares)
    if failures:
        raise SpecMismatch("Lens does not fulfil the promised spec: " + "; ".join(failures))
    return lens


# --- The composer: fitting a dataset to a spec by lensing. ------------------


@dataclass(frozen=True)
class Pin:
    """One adjustable constraint a lens must fix, and its degrees of freedom.

    The frontend affordance follows from ``axis_type``: CHANNEL -> picker,
    INDEX -> sweep picker, TIME -> window. ``axes`` are the candidate axes
    (name, current extent); the choice is which indices of them to keep so their
    total extent meets ``target`` under ``operator``.
    """

    key: DescriptorKey
    axis_type: AxisTypeName
    axes: tuple[tuple[str, int], ...]
    operator: ConstraintOperator
    target: int


@dataclass(frozen=True)
class CompositionPlan:
    """What it takes for a candidate to fit a spec through a lens.

    ``failures`` are invariant (or ungrowable) mismatches -- nonempty means no
    lens over this candidate can ever fit; filter it out. ``pins`` are the
    adjustable fixes, each one a choice to offer the user.
    """

    failures: tuple[str, ...]
    pins: tuple[Pin, ...]

    @property
    def satisfiable(self) -> bool:
        """Whether some lens over the candidate fits the spec."""
        return not self.failures

    @property
    def already_fits(self) -> bool:
        """Whether the candidate fits as-is, no adjustment needed."""
        return not self.failures and not self.pins


def compose(
    candidate: Candidate, spec: Spec, declares: Declarations | None = None
) -> CompositionPlan:
    """Plan how a dataset (or lens) could fit a spec -- the reference composer.

    Pure and server-free: the same algorithm a frontend runs to decide, for a
    dropped dataset and a port's requires, whether to filter it out, pass it
    through, or offer pickers. A constraint that fails is a `Pin` when its key is
    in ``ADJUSTABLE_KEYS``, its operator is EQUALS/LTE, and the target is
    reachable by shrinking (each axis keeps at least one position); anything else
    that fails is a hard failure -- extents never grow, axes never vanish.
    """
    table = _axis_table(candidate)
    descriptors = lens_descriptors(candidate)
    if declares:
        descriptors.update(declares)

    failures: list[str] = []
    pins: list[Pin] = []
    for constraint in spec_constraints(spec):
        key = _constrained_key(constraint)
        operator = _constraint_operator(constraint)
        present = key in descriptors
        actual = descriptors.get(key)
        if _holds(operator, actual, constraint.value, present):
            continue
        axis_type = ADJUSTABLE_KEYS.get(key)
        axes = tuple((name, extent) for name, found, extent in table if found == axis_type)
        target = constraint.value
        if (
            axis_type is not None
            and operator in ("EQUALS", "LTE")
            and isinstance(actual, int)
            and isinstance(target, int)
            and actual > target >= len(axes)
        ):
            pins.append(
                Pin(key=key, axis_type=axis_type, axes=axes, operator=operator, target=target)
            )
        else:
            failures.append(_describe(constraint, operator, actual, present))
    return CompositionPlan(failures=tuple(failures), pins=tuple(pins))


def _selected_extent(choice: AxisSelection, extent: int, axis: str) -> int:
    """The extent an axis keeps under a selection, mirroring DatasetTrait.lens."""
    if isinstance(choice, int) and not isinstance(choice, bool):
        if not 0 <= choice < extent:
            raise ValueError(f"Index {choice} out of range for axis {axis!r} (extent {extent})")
    start, stop, step = normalize_selection(axis, choice)
    return len(range(*slice(start, stop, step).indices(extent)))


def selections_for(plan: CompositionPlan, **choices: AxisSelection) -> dict[str, AxisSelection]:
    """Resolve a plan's pins into per-axis selections for ``dataset.lens(...)``.

    Each choice keyword names an axis of a pin (``c=1`` pins channel 1). Every
    pin must end up satisfied by the choices; leftover choices on axes no pin
    asked about are rejected -- they would silently change the data.
    """
    if plan.failures:
        raise SpecMismatch("Plan is unsatisfiable: " + "; ".join(plan.failures))
    remaining = dict(choices)
    selections: dict[str, AxisSelection] = {}
    for pin in plan.pins:
        names = [name for name, _ in pin.axes]
        picked = {name: remaining.pop(name) for name in names if name in remaining}
        if not picked:
            raise ValueError(
                f"{pin.key} must be reduced to {pin.operator} {pin.target}: pass a selection for one of the {pin.axis_type} axes {names}"
            )
        achieved = sum(
            _selected_extent(picked[name], extent, name) if name in picked else extent
            for name, extent in pin.axes
        )
        fits = achieved == pin.target if pin.operator == "EQUALS" else achieved <= pin.target
        if not fits:
            raise ValueError(
                f"Choices leave {pin.key} at {achieved}, need {pin.operator} {pin.target}"
            )
        selections.update(picked)
    if remaining:
        raise ValueError(
            f"Choices for axes no pin asked about: {sorted(remaining)} -- a spec-fitting lens must not silently select beyond the plan"
        )
    return selections


class LensableDataset(_HasIntrinsicSystem, Protocol):
    """A dataset `fit_lens` can both measure and lens: `DatasetTrait` satisfies it."""

    def lens(self, **selections: AxisSelection) -> Lens:
        """Frame a view of this dataset -- see `DatasetTrait.lens`."""
        ...


def fit_lens(
    dataset: LensableDataset,
    spec: Spec,
    declares: Declarations | None = None,
    **choices: AxisSelection,
) -> Lens:
    """Compose a lens over a dataset that fits a spec -- the conversion itself.

    ``fit_lens(recording, SingleChannelTrace, c=3)`` plans, validates the
    choices, creates the lens via ``dataset.lens(...)`` and re-checks the result::

        vm = fit_lens(patch_recording, SingleChannelTrace, c=0)
        one = fit_lens(episodic, SingleSweep, sweep=12)
    """
    plan = compose(dataset, spec, declares)
    if not plan.satisfiable:
        raise SpecMismatch("No lens over this dataset fits the spec: " + "; ".join(plan.failures))
    selections = selections_for(plan, **choices)
    lens = dataset.lens(**selections)
    return ensure(lens, spec, declares)


__all__ = [
    "ADJUSTABLE_KEYS",
    "N_CHANNELS",
    "N_CHANNEL_AXES",
    "N_FREQUENCY_AXES",
    "N_INDEX_AXES",
    "N_INDICES",
    "N_SAMPLES",
    "N_SPACE_AXES",
    "N_TIME_AXES",
    "VALUE_DIMENSION",
    "VALUE_KIND",
    "Candidate",
    "Categorical",
    "CompositionPlan",
    "ConstraintOperator",
    "CurrentTrace",
    "Declarations",
    "DescriptorKey",
    "DescriptorValue",
    "Hypervolume",
    "Image",
    "Indexed",
    "LensableDataset",
    "Multichannel",
    "MultichannelTrace",
    "Pin",
    "Profile",
    "Scalar",
    "SingleChannel",
    "SingleChannelTrace",
    "SingleSweep",
    "Spec",
    "SpecMismatch",
    "Spectral",
    "Spectrogram",
    "Spectrum",
    "Sweeps",
    "Timeseries",
    "Trace",
    "ValueDimension",
    "VoltageTrace",
    "Volume",
    "at_least",
    "at_most",
    "axes_of_type",
    "axis_types",
    "carried_axes",
    "compose",
    "constrain",
    "ensure",
    "exactly",
    "fit_lens",
    "fulfills",
    "lens_descriptors",
    "refine",
    "selections_for",
    "spec_constraints",
    "unfulfilled",
    "value_dimension",
]
