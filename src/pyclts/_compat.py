"""
Backwards compatibility with supported python versions.
"""
import sys


if (sys.version_info.major, sys.version_info.minor) >= (3, 14):  # pragma: no cover
    def get_annotations(obj, is_instance=True):
        """Use annotationlib.get_annotations."""
        import annotationlib  # pylint: disable=C0415,E0401

        print(annotationlib.get_annotations(obj.__class__ if is_instance else obj))
        return annotationlib.get_annotations(obj.__class__ if is_instance else obj)
else:
    def get_annotations(obj, is_instance=True):  # pylint: disable=W0613
        """Access the __annotations__ attribute directly."""
        return obj.__annotations__
