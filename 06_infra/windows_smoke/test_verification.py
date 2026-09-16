"""Prove the maintained discovery guard rejects false-green pytest runs."""
from pathlib import Path
import os
import subprocess
import sys

import pytest


@pytest.mark.parametrize("case", ["pass", "missing", "empty", "skip"])
def test_discovery_guard(tmp_path, case):
    source = {
        "pass": "def test_required(): pass\n",
        "missing": "def test_other(): pass\n",
        "empty": "# No tests\n",
        "skip": "import pytest\n@pytest.mark.skip(reason='fixture')\ndef test_required(): pass\n",
    }[case]
    (tmp_path / "test_fixture.py").write_text(source, encoding="utf-8")
    code = (
        "import sys; sys.path.insert(0,sys.argv[1]); import pytest; "
        "from run_checks import RequiredTests; "
        "raise SystemExit(pytest.main(['test_fixture.py','--rootdir','.','-q','-p','no:cacheprovider'], "
        "plugins=[RequiredTests({'test_fixture.py::test_required'})]))"
    )
    result = subprocess.run(
        [sys.executable, "-c", code, str(Path(__file__).resolve().parents[1])],
        cwd=tmp_path, env=dict(os.environ, PYTEST_DISABLE_PLUGIN_AUTOLOAD="1"),
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60,
    )
    expected = {"pass": 0, "missing": 5, "empty": 5, "skip": 1}[case]
    assert result.returncode == expected, result.stdout + result.stderr
