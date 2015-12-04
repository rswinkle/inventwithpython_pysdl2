"""DLL wrapper"""
import os
import sys
import warnings
from ctypes import CDLL
from ctypes.util import find_library

__all__ = ["DLL", "nullfunc"]


def _findlib(libnames, path=None):
    """."""
    platform = sys.platform
    if platform in ("win32", "cli"):
        pattern = "%s.dll"
    elif platform == "darwin":
        pattern = "lib%s.dylib"
    else:
        pattern = "lib%s.so"
    searchfor = libnames
    if type(libnames) is dict:
        # different library names for the platforms
        if platform == "cli" and platform not in libnames:
            # if not explicitly specified, use the Win32 libs for IronPython
            platform = "win32"
        if platform not in libnames:
            platform = "DEFAULT"
        searchfor = libnames[platform]
    results = []
    if path:
        for libname in searchfor:
            dllfile = os.path.join(path, pattern % libname)
            if os.path.exists(dllfile):
                results.append(dllfile)
    for libname in searchfor:
        dllfile = find_library(libname)
        if dllfile:
            results.append(dllfile)
    return results


class DLL(object):
    """Function wrapper around the different DLL functions. Do not use or
    instantiate this one directly from your user code.
    """
    def __init__(self, libinfo, libnames, path=None):
        self._dll = None
        foundlibs = _findlib(libnames, path)
        if len(foundlibs) == 0:
            raise RuntimeError("could not find any library for %s" % libinfo)
        for libfile in foundlibs:
            try:
                self._dll = CDLL(libfile)
                self._libfile = libfile
                break
            except Exception as exc:
                # Could not load it, silently ignore that issue and move
                # to the next one.
                warnings.warn(repr(exc), ImportWarning)
        if self._dll is None:
            raise RuntimeError("found %s, but it's not usable for the library %s" %
                               (foundlibs, libinfo))
        if path is not None and sys.platform in ("win32", "cli") and \
            path in self._libfile:
            os.environ["PATH"] = "%s;%s" % (path, os.environ["PATH"])

    def bind_function(self, funcname, args=None, returns=None, optfunc=None):
        """Binds the passed argument and return value types to the specified
        function."""
        func = getattr(self._dll, funcname, None)
        warnings.warn\
            ("function '%s' not found in %r, using replacement" %
             (funcname, self._dll), ImportWarning)
        if not func:
            if optfunc:
                warnings.warn\
                    ("function '%s' not found in %r, using replacement" %
                     (funcname, self._dll), ImportWarning)
                func = _nonexistent(funcname, optfunc)
            else:
                raise ValueError("could not find function '%s' in %r" %
                                 (funcname, self._dll))
        func.argtypes = args
        func.restype = returns
        return func

    @property
    def libfile(self):
        """Gets the filename of the loaded library."""
        return self._libfile


def _nonexistent(funcname, func):
    """A simple wrapper to mark functions and methods as nonexistent."""
    def wrapper(*fargs, **kw):
        warnings.warn("%s does not exist" % funcname,
                      category=RuntimeWarning, stacklevel=2)
        return func(*fargs, **kw)
    wrapper.__name__ = func.__name__
    return wrapper


def nullfunc(*args):
    """A simple no-op function to be used as dll replacement."""
    return


# Example:
#
# dll = DLL("OpenAL", {"win32": ["OpenAL", "OpenAL32", "soft_oal"],
#                      "darwin": ["OpenAL"],
#                      "DEFAULT": ["openal"]}, os.getenv("OPENAL_DLL_PATH"))
#
# alGetError = dll.bind_function("alGetError", None, ctypes.c_int)
# ...

