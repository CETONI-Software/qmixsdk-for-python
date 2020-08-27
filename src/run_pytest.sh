#!/bin/sh

LD_LIBRARY_PATH=$(pwd)/../lib:"$LD_LIBRARY_PATH"
echo "$LD_LIBRARY_PATH"
export LD_LIBRARY_PATH 

python3 $1 ../config/testconfig_qmixsdk
