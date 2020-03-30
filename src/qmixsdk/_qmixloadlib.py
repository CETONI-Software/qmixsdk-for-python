import sys
import os
import ctypes

load_cnt = 0
libpath = None

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
        libpath = os.path.abspath(os.path.join(os.path.dirname(__file__), r"../../.."))

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
        libname = os.path.join(libpath, "lib" + libname + ".so")
        return ctypes.cdll.LoadLibrary(libname)
