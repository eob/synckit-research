#!/bin/bash
python ../test_runner.py basic-download basic-download-output httperf_command_file 2>&1 | tee basic-download.txt
#python test_runner.py tc3 output_tc3 2>&1 | tee tc3.txt
#python test_runner.py tcbandwidth output_tcbandwidth 2>&1 | tee tcbandwidth.txt
