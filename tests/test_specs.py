"""The spec vocabulary, the descriptors it matches against, and the composer.

mikro's ``tests/test_specs.py``, for time series. ``elektro.specs`` imports
``rekuest`` at module level, and rekuest is not an install requirement -- hence
the skip, and why the module is not exported from ``elektro/__init__.py``.

Everything here is server-free by construction: `compose` is the reference
implementation a frontend mirrors to decide, for a dropped dataset and a port's
requires, whether to filter it out, pass it through, or offer a picker.
"""

from types import SimpleNamespace
from typing import Any

import pytest

# Not `pytest.importorskip`: it imports under `simplefilter("error")`, and
# rekuest emits a DeprecationWarning on import, which would skip the whole
# module on every machine rather than only where rekuest is absent.
try:
    import rekuest  # noqa: F401 -- presence is the question
except ImportError:  # pragma: no cover -- depends on the install
    pytest.skip("rekuest is an optional dependency", allow_module_level=True)

from elektro.specs import (
    N_CHANNELS,
    N_SAMPLES,
    VALUE_DIMENSION,
    VALUE_KIND,
    Categorical,
    CurrentTrace,
    MultichannelTrace,
    SingleChannelTrace,
    SingleSweep,
    SpecMismatch,
    Spectrogram,
    Spectrum,
    Sweeps,
    Trace,
    VoltageTrace,
    axes_of_type,
    axis_types,
    compose,
    ensure,
    exactly,
    fit_lens,
    fulfills,
    lens_descriptors,
    refine,
    selections_for,
    spec_constraints,
    unfulfilled,
    value_dimension,
)
from elektro.vocabulary import UnknownAxisName


def system(names: list[str], types: list[str]) -> SimpleNamespace:
    """A typed coordinate system: one axis per name, in order."""
    return SimpleNamespace(
        axes=[
            SimpleNamespace(order=i, name=n, type=t) for i, (n, t) in enumerate(zip(names, types))
        ]
    )


def candidate(
    names: list[str],
    shape: tuple[int, ...],
    types: list[str] | None = None,
    value_unit: str | None = None,
) -> SimpleNamespace:
    """A stand-in for a dataset: axis names, a shape, optionally typed axes and a value unit."""
    return SimpleNamespace(
        axis_names=names,
        shape=shape,
        coordinate_system=None,
        intrinsic_system=system(names, types) if types is not None else None,
        value_unit=value_unit,
    )


VM = candidate(["t"], (30_000,), ["TIME"], "mV")
ARRAY = candidate(["t", "c"], (30_000, 32), ["TIME", "CHANNEL"], "microvolt")
CLAMP = candidate(["t", "c"], (30_000, 1), ["TIME", "CHANNEL"], "pA")
EPISODIC = candidate(["sweep", "t", "c"], (20, 5_000, 2), ["INDEX", "TIME", "CHANNEL"], "mV")
SPECTROGRAM = candidate(["t", "f"], (2_000, 64), ["TIME", "FREQUENCY"], "dB")
PSD = candidate(["f"], (512,), ["FREQUENCY"], "V**2/Hz")
UNITLESS = candidate(["t"], (100,), ["TIME"])


class TestDescriptors:
    """The candidate side: what a lens or dataset carries to be matched."""

    def test_a_typed_system_wins_over_the_convention(self) -> None:
        """A typed system wins over the convention."""
        odd = candidate(["time", "electrode"], (10, 4), ["TIME", "CHANNEL"])
        assert axis_types(odd) == ("TIME", "CHANNEL")

    def test_the_bare_name_convention_is_the_fallback(self) -> None:
        """The bare name convention is the fallback."""
        assert axis_types(candidate(["sweep", "t", "c"], (2, 3, 4))) == ("INDEX", "TIME", "CHANNEL")

    def test_an_unconventional_untyped_name_is_refused_not_guessed(self) -> None:
        """Nothing in an array says whether a second dimension is channels or sweeps."""
        with pytest.raises(UnknownAxisName):
            axis_types(candidate(["t", "electrode"], (10, 4)))

    def test_a_lens_is_typed_through_its_dataset_when_fetched_without_a_system(self) -> None:
        """A lens is typed through its dataset when fetched without a system."""
        lens = SimpleNamespace(
            axis_names=["t", "c"], shape=(100, 1), coordinate_system=None, dataset=ARRAY
        )
        assert axis_types(lens) == ("TIME", "CHANNEL")
        assert lens_descriptors(lens)[VALUE_DIMENSION] == "voltage", "and measured through it"

    def test_every_count_key_is_emitted_including_the_zeroes(self) -> None:
        """`Trace` and `SingleChannel` match on absence, so a missing key and a zero count differ."""
        descriptors = lens_descriptors(VM)
        assert descriptors["@elektro/n_time_axes"] == 1
        assert descriptors["@elektro/n_channel_axes"] == 0
        assert descriptors["@elektro/n_index_axes"] == 0

    def test_adjustable_keys_are_total_extents(self) -> None:
        """Adjustable keys are total extents."""
        descriptors = lens_descriptors(EPISODIC)
        assert (
            descriptors[N_CHANNELS],
            descriptors[N_SAMPLES],
            descriptors["@elektro/n_indices"],
        ) == (2, 5_000, 20)

    def test_value_kind_is_never_computed(self) -> None:
        """It is provenance: only a producer that made ids can vouch for it."""
        assert VALUE_KIND not in lens_descriptors(ARRAY)


class TestValueDimension:
    """What the values measure, read off the dataset's value unit."""

    @pytest.mark.parametrize(
        ("unit", "dimension"),
        [
            ("mV", "voltage"),
            ("microvolt", "voltage"),
            ("pA", "current"),
            ("nS", "conductance"),
            ("MΩ", "resistance"),
            ("pF", "capacitance"),
            ("ms", "time"),
            ("Hz", "frequency"),
            ("mM", "concentration"),
            ("a.u.", "arbitrary"),
            ("V**2/Hz", "other"),
            (None, None),
        ],
    )
    def test_a_unit_is_read_as_what_it_measures(
        self, unit: str | None, dimension: str | None
    ) -> None:
        """Read with the registry the server validated the unit against."""
        assert value_dimension(unit) == dimension

    def test_an_unstated_unit_leaves_the_key_absent(self) -> None:
        """So `VoltageTrace` fails on it, rather than a guess passing it."""
        assert VALUE_DIMENSION not in lens_descriptors(UNITLESS)
        (failure,) = unfulfilled(UNITLESS, VoltageTrace)
        assert "key absent" in failure


class TestFulfilment:
    """Whether a candidate satisfies a spec, and what it misses."""

    @pytest.mark.parametrize(
        ("dataset", "spec", "fits"),
        [
            (VM, Trace, True),
            (ARRAY, Trace, True),
            (VM, SingleChannelTrace, True),
            (ARRAY, MultichannelTrace, True),
            (VM, MultichannelTrace, False),
            (VM, VoltageTrace, True),
            (CLAMP, VoltageTrace, False),
            (CLAMP, CurrentTrace, True),
            (EPISODIC, Trace, False),
            (EPISODIC, Sweeps, True),
            (SPECTROGRAM, Spectrogram, True),
            (SPECTROGRAM, Trace, False),
            (SPECTROGRAM, Spectrum, False),
            (PSD, Spectrum, True),
            (PSD, Spectrogram, False),
        ],
    )
    def test_the_electrophysiology_stacks(
        self, dataset: SimpleNamespace, spec: object, fits: bool
    ) -> None:
        """Each stack holds of exactly the recordings it names."""
        assert fulfills(dataset, spec) is fits, unfulfilled(dataset, spec)

    def test_every_unmet_constraint_is_reported_not_just_the_first(self) -> None:
        """Every unmet constraint is reported not just the first."""
        failures = unfulfilled(SPECTROGRAM, VoltageTrace)
        assert len(failures) == 2, "a FREQUENCY axis, and decibels are not a voltage"
        assert "@elektro/value_dimension EQUALS 'voltage'" in failures[-1]

    def test_provenance_must_be_declared(self) -> None:
        """Provenance must be declared."""
        (failure,) = unfulfilled(VM, Categorical)
        assert "key absent" in failure
        assert fulfills(VM, Categorical, {VALUE_KIND: "categorical"})

    def test_refine_stacks_constraints_onto_a_base(self) -> None:
        """Refine stacks constraints onto a base."""
        stereo = refine(Trace, *exactly(N_CHANNELS, 2))
        assert len(spec_constraints(stereo)) == len(spec_constraints(Trace)) + 1

    def test_ensure_guards_a_promise(self) -> None:
        """Ensure guards a promise."""
        assert ensure(SPECTROGRAM, Spectrogram) is SPECTROGRAM
        with pytest.raises(SpecMismatch, match="does not fulfil"):
            ensure(VM, Spectrogram)


class TestCompose:
    """The reference composer: filter out, pass through, or pin."""

    def test_an_invariant_mismatch_is_a_hard_failure(self) -> None:
        """No lens over a spectrogram makes it a trace -- extents shrink, axes do not vanish."""
        assert not compose(SPECTROGRAM, Trace).satisfiable

    def test_a_fitting_candidate_needs_no_adjustment(self) -> None:
        """A fitting candidate needs no adjustment."""
        assert compose(VM, SingleChannelTrace).already_fits

    def test_a_channel_of_an_array_is_a_pin(self) -> None:
        """Which electrode to keep is exactly the choice to render as a picker."""
        plan = compose(ARRAY, SingleChannelTrace)
        assert plan.satisfiable and not plan.already_fits
        (pin,) = plan.pins
        assert (pin.axis_type, pin.operator, pin.target, pin.axes) == (
            "CHANNEL",
            "LTE",
            1,
            (("c", 32),),
        )

    def test_a_sweep_of_an_episodic_recording_is_a_pin(self) -> None:
        """A sweep of an episodic recording is a pin."""
        (pin,) = compose(EPISODIC, SingleSweep).pins
        assert (pin.axis_type, pin.axes) == ("INDEX", (("sweep", 20),))

    def test_a_single_sweep_of_one_channel_is_two_pins(self) -> None:
        """A single sweep of one channel is two pins."""
        spec = refine(Sweeps, *exactly(N_CHANNELS, 1), *exactly("@elektro/n_indices", 1))
        plan = compose(EPISODIC, spec)
        assert sorted(pin.axis_type for pin in plan.pins) == ["CHANNEL", "INDEX"]
        assert selections_for(plan, sweep=3, c=0) == {"sweep": 3, "c": 0}


class TestSelections:
    """Resolving a plan's pins into the selections of a lens."""

    def test_an_int_pin_satisfies_the_plan(self) -> None:
        """An int pin satisfies the plan."""
        assert selections_for(compose(ARRAY, SingleChannelTrace), c=5) == {"c": 5}

    def test_a_selection_that_keeps_too_much_is_refused(self) -> None:
        """A selection that keeps too much is refused."""
        with pytest.raises(ValueError, match="need LTE 1"):
            selections_for(compose(ARRAY, SingleChannelTrace), c=(0, 2))

    def test_an_unpinned_pin_is_refused(self) -> None:
        """An unpinned pin is refused."""
        with pytest.raises(ValueError, match="must be reduced to"):
            selections_for(compose(ARRAY, SingleChannelTrace))

    def test_a_choice_no_pin_asked_about_is_refused(self) -> None:
        """It would silently change the data the action was offered."""
        with pytest.raises(ValueError, match="no pin asked about"):
            selections_for(compose(ARRAY, SingleChannelTrace), c=0, t=(0, 10))

    def test_an_out_of_range_index_is_refused_by_axis(self) -> None:
        """An out of range index is refused by axis."""
        with pytest.raises(ValueError, match="out of range for axis 'c'"):
            selections_for(compose(ARRAY, SingleChannelTrace), c=40)

    def test_an_unsatisfiable_plan_is_refused_outright(self) -> None:
        """An unsatisfiable plan is refused outright."""
        with pytest.raises(SpecMismatch, match="unsatisfiable"):
            selections_for(compose(SPECTROGRAM, Trace))


class TestFitLens:
    """The conversion itself: plan, lens, re-check."""

    def test_fit_lens_lenses_the_dataset_with_the_chosen_pins_and_checks_the_result(self) -> None:
        """Fit lens lenses the dataset with the chosen pins and checks the result."""
        asked = {}

        def lens(**selections: Any) -> SimpleNamespace:  # noqa: ANN401
            """The dataset's `lens`, recording what it was asked for."""
            asked.update(selections)
            return SimpleNamespace(
                axis_names=["t", "c"], shape=(30_000, 1), coordinate_system=None, dataset=ARRAY
            )

        dataset = SimpleNamespace(**vars(ARRAY), lens=lens)
        fitted = fit_lens(dataset, SingleChannelTrace, c=7)
        assert asked == {"c": 7}
        assert axes_of_type(fitted, "CHANNEL") == ("c",), "a pinned channel axis survives, size one"
