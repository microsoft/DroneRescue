#!/bin/bash
#/home/nvagent/Blocks/Blocks.sh&
python runtime_test.py

kill -SIGKILL %1 >/dev/null
echo "EXITING TEST SCRIPT"
exit `cat result.txt`
