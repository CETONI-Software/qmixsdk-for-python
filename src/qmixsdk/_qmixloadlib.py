import sys
import os
import ctypes
from ctypes import util

load_cnt = 0
libpath = None

def init_libpath_from_dir():
    """
    Helper function to return the right libpath depending on the platform
    The directory layout of the final QmixSDK package is different on Windows and Linux
    """
    if sys.platform.startswith('win32'):
        reldir = r"../../.."
    else:
        reldir = r"../.."
    return os.path.abspath(os.path.join(os.path.dirname(__file__), reldir))
    
    
def load_lib(libname):
    """
    Helper function for loading QmixSDK DLLs.
    This helper function ensures that DLL loading works for all Python 3 
    versions
    """
    global libpath
    if libpath is None:
        libpath = os.environ.get('QMIXSDK')
        
    if libpath is None:
        libpath = init_libpath_from_dir()

    if sys.platform.startswith('win32'):
        global load_cnt
        libname = os.path.join(libpath, libname + ".dll")
        # We need to extend that library search path only once, so we do it
        # only for the first call here
        if load_cnt < 1:
            # From python 3.8 on loading DLLs from folder in PATH environment
            # does not work anymore. We use os.add_dll_directory instead
            if sys.version_info >= (3, 8):
                os.add_dll_directory(libpath)
            else:
                sys.path.append(libpath)
                os.environ['PATH'] = libpath + os.pathsep + os.environ['PATH']
        load_cnt += 1
        return ctypes.windll.LoadLibrary(libname)
    else:
        # Standard solution if the shared libraries are properly installed
        # in the Linux libs folders - for debian package
        libname = ctypes.util.find_library(libname)
        # Fall back solution for the distribution via tar archive where whe
        # know the location of the shared libraries
        if libname is None:
            libname = os.path.join(libpath, "lib/lib" + libname + ".so")
        return ctypes.cdll.LoadLibrary(libname)
