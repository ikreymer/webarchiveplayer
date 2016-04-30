#!/bin/bash

ENV=`python -c "import sys; print(sys.prefix)"`
PYTHON=`python -c "import sys; print(sys.real_prefix)"`/bin/python3
export PYTHONHOME=$ENV
exec $PYTHON "$@"

