"""Unit tests for the stimulus/record pydantic models in ``elektro.neuron.simulate``.

These models carry pint-backed unit quantities (via ``kanne.scalars``); the tests
mirror how the user's script constructs them with pint quantities.
"""

import pytest
from pint import UnitRegistry

from elektro.api.schema import RecordingKind, StimulusKind
from elektro.neuron.simulate import (
    CurrentClampStimulus,
    SineWaveStimulus,
    VRecord,
    WhiteNoiseStimulus,
)

ureg = UnitRegistry()
pA = ureg.picoampere
Hz = 1 / ureg.second
ms = ureg.millisecond


def test_vrecord_defaults():
    rec = VRecord(cell="cell_1", location="soma")
    assert rec.position == 0.5
    assert rec.kind == RecordingKind.VOLTAGE
    assert rec.id  # auto-generated


def test_unique_ids():
    a = VRecord(cell="c", location="soma")
    b = VRecord(cell="c", location="soma")
    assert a.id != b.id


def test_current_clamp_defaults_and_units():
    stim = CurrentClampStimulus(cell="cell_1", location="soma")
    assert stim.kind == StimulusKind.VOLTAGE
    # Defaults carry explicit units (not dimensionless), so .to(...) works.
    assert stim.amp.to("nanoampere").magnitude == pytest.approx(0.1)
    assert stim.delay.to("millisecond").magnitude == pytest.approx(100.0)


def test_current_clamp_with_pint_quantities():
    stim = CurrentClampStimulus(
        cell="cell_1", location="soma", position=0.5, amp=100 * pA, delay=20 * ms
    )
    # 100 pA == 0.1 nA
    assert stim.amp.to("nanoampere").magnitude == pytest.approx(0.1)
    assert stim.delay.to("millisecond").magnitude == pytest.approx(20.0)


def test_current_clamp_plain_number_delay_is_milliseconds():
    # A bare number is interpreted as milliseconds by the Millisecond validator
    # (this is the path the simulation script uses, e.g. ``delay=100``).
    stim = CurrentClampStimulus(cell="cell_1", location="soma", delay=100)
    assert stim.delay.to("millisecond").magnitude == pytest.approx(100.0)


def test_sine_wave_stimulus_units():
    stim = SineWaveStimulus(
        cell="cell_1", location="soma", amplitude=80 * pA, frequency=200 * Hz
    )
    assert stim.amplitude.to("nanoampere").magnitude == pytest.approx(0.08)
    assert stim.frequency.to("hertz").magnitude == pytest.approx(200.0)


def test_sine_wave_stimulus_defaults():
    stim = SineWaveStimulus(cell="cell_1", location="soma")
    # Default frequency carries explicit hertz units.
    assert stim.frequency.to("hertz").magnitude == pytest.approx(10.0)
    assert stim.amplitude.to("nanoampere").magnitude == pytest.approx(0.1)


def test_white_noise_stimulus_defaults():
    stim = WhiteNoiseStimulus(cell="cell_1", location="soma")
    assert stim.noise_level.to("nanoampere").magnitude == pytest.approx(0.05)
