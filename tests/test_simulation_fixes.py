"""Regression tests for simulator correctness fixes in ``elektro.neuron.simulate``.

Covers: unit conversion of section parameters to each mechanism's NEURON unit,
soma-referenced path distance for expression distributions, reproducible and
dt-invariant white noise, stimulus delay/duration windows, and refusing to load a
second mechanism library over already-registered mechanism names.

NEURON-gated: skipped when the optional ``neuron`` package is not installed.
"""

import platform
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

pytestmark = pytest.mark.neuron

pytest.importorskip("neuron")

from kanne.scalars import Duration, ElectricCurrent, GenericQuantity  # noqa: E402
from neuron import h  # noqa: E402

from elektro.api.schema import (  # noqa: E402
    Cell,
    CellBiophysics,
    CellTopology,
    Compartment,
    NeuronModel,
    NeuronModelConfig,
    Section,
    SectionParamMap,
    StimulusKind,
)
from elektro.neuron import simulate  # noqa: E402
from elektro.neuron.simulate import (  # noqa: E402
    SimulationResults,
    SineWaveStimulus,
    VRecord,
    WhiteNoiseStimulus,
    _to_neuron_magnitude,
    instantiate_model,
    load_compiled_mechanisms,
    run_simulation_processed,
)


def _param(param: str, mechanism: str, **distribution: object) -> SectionParamMap:
    return SectionParamMap(param=param, mechanism=mechanism, distribution=distribution)


def _config(section_params: list[SectionParamMap]) -> NeuronModelConfig:
    """A soma (20 µm, 3 segments) with one 100 µm dendrite attached at soma(1)."""
    topology = CellTopology(
        sections=[
            Section(id="soma", category="soma", nseg=3, diam="20 um", length="20 um"),
            Section(
                id="dend",
                category="dend",
                nseg=1,
                diam="2 um",
                length="100 um",
                parent={"parent": "soma", "parentLocation": 1.0, "childEnd": 0.0},
            ),
        ]
    )
    biophysics = CellBiophysics(
        compartments=[
            Compartment(id="soma", mechanisms=["pas", "hh"], sectionParams=section_params, ions=[]),
            Compartment(
                id="dend",
                mechanisms=["pas"],
                sectionParams=[_param("e_pas", "pas", kind="EXPRESSION", expression="-65 - d/100")],
                ions=[],
            ),
        ]
    )
    return NeuronModelConfig(
        vInit="-65 mV",
        temperature="310.15 K",
        cells=[Cell(id="cell_1", biophysics=biophysics, topology=topology)],
        ions=[],
        mechanismGlobals=[],
    )


def _model() -> NeuronModel:
    return NeuronModel.model_construct(
        id="local-model", name="local-test", environment=None, config=_config([])
    )


# --- Units -----------------------------------------------------------------


@pytest.mark.parametrize(
    ("name", "value", "expected"),
    [
        ("g_pas", "0.05 mS/cm2", 5e-5),  # declared S/cm2
        ("gnabar_hh", "120 mS/cm2", 0.12),  # declared S/cm2
        ("e_pas", "-0.065 V", -65.0),  # declared mV
        ("g_pas", "0.001 S/cm2", 0.001),  # already native
    ],
)
def test_values_are_converted_to_the_neuron_unit(name: str, value: str, expected: float) -> None:
    """A quantity reaches NEURON in the unit the mechanism declares, not the one typed."""
    assert _to_neuron_magnitude(h, name, GenericQuantity.validate(value)) == pytest.approx(expected)


def test_incompatible_unit_is_rejected() -> None:
    """A value whose dimension can't be the parameter's is an error, not a silent number."""
    with pytest.raises(ValueError, match="g_pas"):
        _to_neuron_magnitude(h, "g_pas", GenericQuantity.validate("5 mV"))


def test_section_params_are_converted_end_to_end() -> None:
    """Uniform and linear distributions both reach the segments in NEURON units."""
    config = _config(
        [
            _param("g_pas", "pas", kind="UNIFORM", value="0.05 mS/cm2"),
            _param(
                "gnabar_hh",
                "hh",
                kind="LINEAR",
                proximalValue="120 mS/cm2",
                distalValue="0.06 S/cm2",
            ),
        ]
    )
    sections = instantiate_model(h, config).cell_h_sections["cell_1"]
    soma = sections["soma"]

    assert all(seg.g_pas == pytest.approx(5e-5) for seg in soma)
    gna = [seg.gnabar_hh for seg in soma]
    assert gna[0] < 0.12 + 1e-12 and gna[-1] == pytest.approx(0.06)
    assert all(0.06 - 1e-12 <= g <= 0.12 + 1e-12 for g in gna)


def test_expression_distance_is_measured_from_the_soma() -> None:
    """``d`` in an expression is the path distance from soma(0.5), not the section start."""
    sections = instantiate_model(h, _config([])).cell_h_sections["cell_1"]
    # dend(0.5) sits 10 µm (half the soma) + 50 µm (half the dendrite) from soma(0.5).
    assert sections["dend"](0.5).e_pas == pytest.approx(-65 - 60 / 100)


# --- Stimuli ---------------------------------------------------------------


DT_MS = 0.025


def _run(stims: list, dt_ms: float = DT_MS, duration_ms: float = 200.0) -> SimulationResults:
    return run_simulation_processed(
        model=_model(),
        duration=Duration(f"{duration_ms} ms"),
        stims=stims,
        records=[VRecord(cell="cell_1", location="soma", position=0.5)],
        name="fixes-sim",
        dt=Duration(f"{dt_ms} ms"),
    )


def _noise(**kwargs: object) -> WhiteNoiseStimulus:
    return WhiteNoiseStimulus(
        cell="cell_1", location="soma", noise_level=ElectricCurrent("0.02 nanoampere"), **kwargs
    )


def test_stimuli_are_current_kind() -> None:
    """Every current stimulus declares itself as a CURRENT stimulus."""
    assert _noise().kind == StimulusKind.CURRENT
    assert SineWaveStimulus(cell="c", location="soma").kind == StimulusKind.CURRENT


def test_seeded_noise_is_reproducible() -> None:
    """The same seed gives the same realization; different seeds give different ones."""
    a = _run([_noise(seed=1)]).stimuli[0].values
    b = _run([_noise(seed=1)]).stimuli[0].values
    c = _run([_noise(seed=2)]).stimuli[0].values
    np.testing.assert_array_equal(a, b)
    assert not np.array_equal(a, c)


def test_unseeded_noise_reports_its_seed() -> None:
    """An unseeded run records the seed it drew, and replaying that seed reproduces it."""
    first = _run([_noise()])
    (played,) = first.stims
    assert played.seed is not None
    replay = _run([_noise(seed=played.seed)])
    np.testing.assert_array_equal(first.stimuli[0].values, replay.stimuli[0].values)


def test_noise_power_is_dt_invariant() -> None:
    """Per-sample SD scales with sqrt(reference_dt / dt), keeping sigma**2 * dt fixed."""
    reference = _noise(seed=3, reference_dt=Duration("0.05 ms"))
    coarse = np.std(_run([reference], dt_ms=0.05, duration_ms=2000).stimuli[0].values)
    fine = np.std(_run([reference], dt_ms=0.0125, duration_ms=2000).stimuli[0].values)
    assert coarse == pytest.approx(0.02, rel=0.02)
    assert fine == pytest.approx(0.02 * 2.0, rel=0.02)


def test_time_varying_stimuli_honour_delay_and_duration() -> None:
    """Sine and noise are zero outside [delay, delay + duration)."""
    sine = SineWaveStimulus(
        cell="cell_1",
        location="soma",
        frequency="100 Hz",
        amplitude="0.1 nanoampere",
        delay="50 ms",
        duration="100 ms",
    )
    result = _run([sine, _noise(seed=4, delay="50 ms", duration="100 ms")])
    times = np.asarray(result.time_trace)
    waveform = np.asarray(result.stimuli[0].values)

    assert len(waveform) == len(times)
    assert np.all(waveform[times < 50.0] == 0.0)
    assert np.all(waveform[times >= 150.0] == 0.0)
    assert np.any(waveform[(times >= 50.0) & (times < 150.0)] != 0.0)


# --- Mechanism libraries ---------------------------------------------------


def test_refuses_to_shadow_another_environments_mechanisms(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Loading a second library whose mechanisms already exist raises instead of
    silently simulating the first library's definitions."""
    environment = SimpleNamespace(id="2", store=SimpleNamespace(key="env-b"))
    ext = "dylib" if platform.system() == "Darwin" else "so"
    dll = tmp_path / "env-b" / platform.machine() / f"libnrnmech.{ext}"
    dll.parent.mkdir(parents=True)
    dll.touch()

    def already_registered(path: str) -> None:
        raise RuntimeError("The user defined name already exists: cad")

    fake_h = SimpleNamespace(nrn_load_dll=already_registered)
    monkeypatch.setattr(simulate, "_LOADED_DLLS", {"/elsewhere/env-a/libnrnmech.so"})

    with pytest.raises(RuntimeError, match="already registered"):
        load_compiled_mechanisms(fake_h, environment, base_cache_dir=str(tmp_path))
