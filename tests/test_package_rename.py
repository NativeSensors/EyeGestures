import importlib
import sys
import unittest
import warnings


def _import_old_name_fresh():
    """Import `eyeGestures` from scratch, returning (module, caught warnings)."""
    for name in [
        n for n in sys.modules
        if n == "eyeGestures" or n.startswith("eyeGestures.")
    ]:
        del sys.modules[name]
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        module = importlib.import_module("eyeGestures")
    return module, caught


class TestPackageRename(unittest.TestCase):
    def test_old_name_emits_deprecation_warning(self):
        _, caught = _import_old_name_fresh()
        self.assertTrue(
            any(
                issubclass(w.category, DeprecationWarning) and
                "eye_gestures" in str(w.message)
                for w in caught
            )
        )

    def test_old_name_is_alias_of_new_package(self):
        old, _ = _import_old_name_fresh()
        new = importlib.import_module("eye_gestures")
        self.assertIs(old, new)

    def test_submodules_are_shared_objects(self):
        _import_old_name_fresh()
        old_utils = importlib.import_module("eyeGestures.utils")
        new_utils = importlib.import_module("eye_gestures.utils")
        self.assertIs(old_utils, new_utils)
        self.assertEqual(new_utils.__name__, "eye_gestures.utils")

    def test_from_import_of_public_api(self):
        _import_old_name_fresh()
        old = importlib.import_module("eyeGestures")
        new = importlib.import_module("eye_gestures")
        self.assertIs(old.EyeGestures_v4, new.EyeGestures_v4)


if __name__ == "__main__":
    unittest.main()

