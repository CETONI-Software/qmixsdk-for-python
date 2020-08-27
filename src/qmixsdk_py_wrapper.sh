#!/bin/bash
#
# Wrapper script for all python scripts that use the QmixSDK Python Integration
# It sets the PATH, PYTHONPATH and LD_LIBRARY_PATH environment variables so that
# python and ctypes find the necessary files and shared libraries.
#

# change this path to point to your QmixSDK installation
export QMIXSDK_PATH="$HOME/QmixSDK_Linux"

export PATH="$QMIXSDK_PATH":"$PATH"
export PYTHONPATH="$QMIXSDK_PATH/python":"$PYTHONPATH"
export LD_LIBRARY_PATH="$QMIXSDK_PATH/lib":"$LD_LIBRARY_PATH"

curr_dir=$(pwd)
cd $(dirname $1)
python3 $(basename $1) ${@:2}
cd $curr_dir
