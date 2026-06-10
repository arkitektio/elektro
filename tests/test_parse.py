"""Unit tests for ``elektro.neuron.parse`` (pure, no NEURON / no network)."""

import zipfile

import pytest

from elektro.neuron.parse import build_and_zip_environment, parse_mod_file_to_schema


SUFFIX_MOD = """
TITLE Delayed rectifier potassium channel

NEURON {
    SUFFIX kdr
    USEION k READ ek WRITE ik
}

PARAMETER {
    gbar = 0.05 (S/cm2)
    tau = 1.2
    novalue
}
"""

POINT_PROCESS_MOD = """
NEURON {
    POINT_PROCESS MyShunt
}

PARAMETER {
    e = -70 (mV)
}
"""

NO_TITLE_MOD = """
NEURON {
    SUFFIX leak
}

PARAMETER {
    g = 0.001
}
"""


def _write(tmp_path, name: str, content: str):
    path = tmp_path / name
    path.write_text(content, encoding="utf-8")
    return path


def test_parse_suffix_mechanism(tmp_path):
    mech = parse_mod_file_to_schema(_write(tmp_path, "kdr.mod", SUFFIX_MOD))

    assert mech.name == "kdr"
    assert mech.description == "Delayed rectifier potassium channel"

    by_key = {p.key: p for p in mech.parameters}
    # Parameter keys are suffixed with the mechanism name to match NEURON's namespace.
    assert "gbar_kdr" in by_key
    assert "tau_kdr" in by_key
    assert "novalue_kdr" in by_key

    gbar = by_key["gbar_kdr"]
    assert gbar.label == "gbar"  # UI label stays the raw name
    assert gbar.default == pytest.approx(0.05)
    # A parameter declared without a default value parses to ``None``.
    assert by_key["novalue_kdr"].default is None


def test_parse_point_process_mechanism(tmp_path):
    mech = parse_mod_file_to_schema(_write(tmp_path, "shunt.mod", POINT_PROCESS_MOD))

    assert mech.name == "MyShunt"
    # No TITLE -> fallback description references the file name.
    assert mech.description == "Parsed from shunt.mod"
    assert mech.parameters[0].key == "e_MyShunt"
    assert mech.parameters[0].default == pytest.approx(-70.0)


def test_build_and_zip_environment(tmp_path):
    model_dir = tmp_path / "models"
    model_dir.mkdir()

    _write(model_dir, "kdr.mod", SUFFIX_MOD)
    _write(model_dir, "leak.mod", NO_TITLE_MOD)
    # Files that must be skipped from the zip.
    (model_dir / "kdr.o").write_bytes(b"\x00")
    (model_dir / "libnrnmech.so").write_bytes(b"\x00")
    # An architecture build folder that must be excluded entirely.
    arch = model_dir / "x86_64"
    arch.mkdir()
    (arch / "special").write_bytes(b"\x00")

    out_zip = tmp_path / "mechanisms.zip"
    zip_path, mechanisms = build_and_zip_environment(
        str(model_dir), output_zip_path=str(out_zip)
    )

    assert zip_path == str(out_zip)
    # One MechanismInput per .mod file.
    assert {m.name for m in mechanisms} == {"kdr", "leak"}

    with zipfile.ZipFile(zip_path) as zf:
        names = set(zf.namelist())

    assert "kdr.mod" in names
    assert "leak.mod" in names
    # Ignored extensions and the x86_64 build folder are excluded.
    assert "kdr.o" not in names
    assert "libnrnmech.so" not in names
    assert not any(n.startswith("x86_64") for n in names)


def test_build_and_zip_environment_missing_dir(tmp_path):
    with pytest.raises(FileNotFoundError):
        build_and_zip_environment(str(tmp_path / "does_not_exist"))
