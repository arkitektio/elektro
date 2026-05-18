import os
import re
import json
import zipfile
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Tuple
from elektro.api.schema import CreateModEnvironmentInput, MechanismInput, ArgPortInput


# ==========================================
# 2. Parsing & Packaging Logic
# ==========================================


def parse_mod_file_to_schema(file_path: Path) -> MechanismInput:
    """
    Parses a single .mod file and returns a populated MechanismInput schema.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Extract Mechanism Name
    name_match = re.search(r"(?:SUFFIX|POINT_PROCESS)\s+([a-zA-Z0-9_]+)", content)
    mechanism_name = name_match.group(1) if name_match else file_path.stem

    # 2. Extract Description (Look for TITLE)
    title_match = re.search(r"TITLE\s+([^\n]+)", content)
    description = (
        title_match.group(1).strip() if title_match else f"Parsed from {file_path.name}"
    )

    # 3. Extract PARAMETER block
    param_block_match = re.search(r"PARAMETER\s*\{([^}]*)\}", content)

    ports = []
    if param_block_match:
        param_block = param_block_match.group(1)

        for line in param_block.split("\n"):
            line = line.strip()
            if not line or line.startswith(":"):
                continue

            # Regex captures the variable name (Group 1) and an optional default value (Group 2)
            # e.g., "gbar = 0.05 (S/cm2)" -> Group 1: "gbar", Group 2: "0.05"
            var_match = re.match(
                r"^([a-zA-Z0-9_]+(?:\[\d+\])?)\s*(?:=\s*([\d\.\-eE]+))?", line
            )

            if var_match:
                raw_param_name = var_match.group(1)
                default_val_str = var_match.group(2)

                # Convert default to float if it exists
                default_val = float(default_val_str) if default_val_str else None

                # Append the suffix to the parameter to match NEURON's Python namespace
                # e.g., "gbar" in "NaTs2_t" becomes "gbar_NaTs2_t"
                key_name = f"{raw_param_name}_{mechanism_name}"

                ports.append(
                    ArgPortInput(
                        key=key_name,
                        label=raw_param_name,  # Keep UI label clean
                        kind="FLOAT",
                        nullable=False,
                        default=default_val,
                        description=f"Parameter {raw_param_name} for {mechanism_name}",
                    )
                )

    return MechanismInput(
        name=mechanism_name, description=description, parameters=ports
    )


def build_and_zip_environment(
    directory_path: str, output_zip_path: str = "/tmp/mechanisms.zip"
) -> Tuple[str, List[MechanismInput]]:
    """
    Zips the directory, parses all .mod files, and returns the zip path
    along with the list of extracted mechanism schemas.
    """
    model_dir = Path(directory_path)
    if not model_dir.exists() or not model_dir.is_dir():
        raise FileNotFoundError(f"Directory {directory_path} does not exist.")

    mechanisms_schema: List[MechanismInput] = []
    ignored_folders = {"x86_64", "arm64", "i686", "powerpc", "umac"}
    ignored_extensions = {".o", ".c", ".so", ".dll", ".dylib"}

    # 1. Parse and Zip
    with zipfile.ZipFile(output_zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(model_dir):
            dirs[:] = [d for d in dirs if d not in ignored_folders]

            for file in files:
                file_path = Path(root) / file

                # Parse .mod files into Pydantic models
                if file_path.suffix == ".mod":
                    try:
                        mech_input = parse_mod_file_to_schema(file_path)
                        mechanisms_schema.append(mech_input)
                    except Exception as e:
                        print(f"Error parsing {file.name}: {e}")

                # Zip all safe files
                if file_path.suffix not in ignored_extensions:
                    arcname = file_path.relative_to(model_dir)
                    zipf.write(file_path, arcname)

    return output_zip_path, mechanisms_schema
