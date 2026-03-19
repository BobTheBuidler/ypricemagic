import os

import brownie

brownie.network.connect(os.environ["BROWNIE_NETWORK"])
brownie._config.CONFIG.settings["autofetch_sources"] = False


# Monkeypatch brownie's _get_ast_hash to skip compiled .so/.pyd files.
# Without this, brownie's test runner crashes with UnicodeDecodeError when
# it follows imports into compiled Cython extensions (e.g.,
# brownie.convert.datatypes.cpython-312-darwin.so) that happen to be inside
# the project directory (because .venv is under the project root).
import brownie.project.scripts as _bps
import brownie.test.managers.base as _btmb

_orig_get_ast_hash = _bps._get_ast_hash


def _safe_get_ast_hash(path):
    path_str = str(path)
    if path_str.endswith((".so", ".pyd", ".o", ".dylib")):
        from hashlib import sha1

        return sha1(path_str.encode()).hexdigest()
    try:
        return _orig_get_ast_hash(path)
    except UnicodeDecodeError:
        from hashlib import sha1

        return sha1(path_str.encode()).hexdigest()


# Patch both the source module AND the already-imported reference in base.py
_bps._get_ast_hash = _safe_get_ast_hash
_btmb._get_ast_hash = _safe_get_ast_hash
