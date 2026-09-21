"""elektro must stay importable, and correct, without arkitekt.

arkitekt is an optional integration. Two places may know about it: the integration
module ``elektro/arkitekt.py``, and ``elektro/__init__.py``, which imports that module
behind ``try/except ImportError``. Everything else, and above all the code
that decides which client answers a call, takes references instead of importing.
"""

import ast
import subprocess
import sys
from pathlib import Path

import elektro

PACKAGE = Path(elektro.__file__).parent
MAY_KNOW_ARKITEKT = {PACKAGE / "arkitekt.py", PACKAGE / "__init__.py"}


def _module_scope_imports(tree: ast.Module) -> list[str]:
    """Names imported where they run at import time: not inside a function body.

    ``if TYPE_CHECKING:`` blocks never run, so they do not count either.
    """
    found: list[str] = []

    def visit(nodes: list[ast.stmt]) -> None:
        for node in nodes:
            if isinstance(node, ast.Import):
                found.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                found.append(node.module)
            elif isinstance(node, ast.If):
                if "TYPE_CHECKING" not in ast.unparse(node.test):
                    visit(node.body)
                visit(node.orelse)
            elif isinstance(node, (ast.Try, ast.With, ast.ClassDef)):
                for field in ("body", "orelse", "finalbody"):
                    visit(getattr(node, field, []))
                for handler in getattr(node, "handlers", []):
                    visit(handler.body)

    visit(tree.body)
    return found


def test_only_the_integration_module_imports_arkitekt() -> None:
    """No module but the two that may know arkitekt imports it where it runs at import time."""
    offenders = []
    for path in sorted(PACKAGE.rglob("*.py")):
        if path in MAY_KNOW_ARKITEKT:
            continue
        imports = _module_scope_imports(ast.parse(path.read_text()))
        if any(name == "arkitekt" or name.startswith("arkitekt.") for name in imports):
            offenders.append(str(path.relative_to(PACKAGE)))

    assert not offenders, (
        f"{offenders} import arkitekt at module scope. elektro works without arkitekt: "
        "take a reference (the `Elektro` client) instead of importing it."
    )


def test_elektro_imports_and_builds_a_client_with_arkitekt_unavailable() -> None:
    """In a fresh interpreter where ``import arkitekt`` fails, as on a bare install."""
    script = (
        "import sys\n"
        "sys.modules['arkitekt'] = None\n"  # makes every `import arkitekt` raise ImportError
        "import elektro, elektro.client, elektro.io.download\n"
        "from elektro.elektro import Elektro\n"
        "client = Elektro.model_construct(rath=object(), datalayer=object(), task_token=None)\n"
        "assert elektro.client.client_of(None, client) is client\n"
        "assert callable(client.aget_lens)\n"
        "print('ok')\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", script], capture_output=True, text=True, cwd=PACKAGE.parent
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip().endswith("ok")
