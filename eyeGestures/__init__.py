"""Deprecated alias for :mod:`eye_gestures`.

The module was renamed from ``eyeGestures`` to ``eye_gestures``. Importing it
under the old name still works but emits a :class:`DeprecationWarning`.
"""

import importlib
import pkgutil
import sys
import warnings

warnings.warn(
    "the 'eyeGestures' package has been renamed to 'eye_gestures'; "
    "importing 'eyeGestures' is deprecated and will be removed in the future. "
    "Please update your imports to use `eye_gestures`.",
    DeprecationWarning,
    stacklevel=2,
)

import eye_gestures  # noqa: E402  # pylint: disable=wrong-import-position

# Alias `eyeGestures` to `eye_gestures`
sys.modules[__name__] = eye_gestures

# Recursively alias `eyeGestures.*` to `eye_gestures.*` (incl. subsubmodules)
for _submodule in pkgutil.walk_packages(
    eye_gestures.__path__,
    prefix="eye_gestures.",
    onerror=lambda _: None,  # otherwise swallows ImportError throws
):
    try:
        _module = importlib.import_module(_submodule.name)
    except ImportError:
        continue
    _alias = __name__ + _submodule.name.removeprefix("eye_gestures")
    sys.modules[_alias] = _module
