#!/bin/bash
#MOVE THIS SCRIPT TO THE HOME DIRECTORY IN VM
#MOVE THIS SCRIPT TO THE HOME DIRECTORY IN VM
#MOVE THIS SCRIPT TO THE HOME DIRECTORY IN VM



# Function to check if a package is installed and install it if missing
check_and_install_sysstat() {
    if ! dpkg -s sysstat &>/dev/null; then
        echo "sysstat is not installed. Installing sysstat..."
        sudo apt-get update && sudo apt-get install -y sysstat
    else
        echo "sysstat is already installed."
    fi
}

# Run the function to check/install sysstat
check_and_install_sysstat


# Base directory for results
BASE_RESULTS_DIR=$HOME/inference_3.0_results
BASE_PROFILING_DIR=$HOME/profile
BASE_SUBMISSION_DIR=$HOME/inference_submission_tree

# Determine the next run number
NEXT_RUN_NUM=1
while [ -d "${BASE_RESULTS_DIR}_run_${NEXT_RUN_NUM}" ]; do
  ((NEXT_RUN_NUM++))
done

# Set the results and profiling directories with the new run number
RESULTS_DIR="${BASE_RESULTS_DIR}_run_${NEXT_RUN_NUM}"
PROFILING_DIR="${BASE_PROFILING_DIR}_run_${NEXT_RUN_NUM}"
SUBMISSION_DIR="${BASE_SUBMISSION_DIR}_run_${NEXT_RUN_NUM}"
SUBMISSION_PROFILING_DIR="${SUBMISSION_DIR}/open/cTuning/profiling" # This may only work for BERT

# Create results and profiling directories if they don't exist
mkdir -p "$RESULTS_DIR"
mkdir -p "$PROFILING_DIR"
# mkdir -p "$SUBMISSION_DIR" # no need the CM script already collects this

# Do full accuracy and performance runs
./run_tests_type.sh "$RESULTS_DIR" "$PROFILING_DIR" "$NEXT_RUN_NUM" "accuracy"
./run_tests_type.sh "$RESULTS_DIR" "$PROFILING_DIR" "$NEXT_RUN_NUM" "performance"

# Populate readme
cm run script --tags=generate-run-cmds,inference,_populate-readme,_all-scenarios \
    --adr.python.name=mlperf-cuda --model=bert-99 --device=cuda \
    --implementation=reference --backend=onnxruntime --quiet \
    --execution-mode=valid --results_dir="$RESULTS_DIR"

# Generate MLPerf submission tree ---- maybe use to capture multiple run_1s from bert, resnet50, etc
yes "" | head -n 1 | cm run script --tags=generate,inference,submission \
    --results_dir="$RESULTS_DIR"/valid_results \
    --adr.python.name=mlperf-cuda \
    --device=cuda --submission_dir="$SUBMISSION_DIR" --clean  \
    --run-checker --submitter=cTuning --adr.inference-src.version=master 


# Move profiling logs to submission tree folder
SUBMISSION_PROFILING_DIR="${SUBMISSION_DIR}/open/cTuning/profiling"
mkdir -p "$SUBMISSION_PROFILING_DIR"
cp "$PROFILING_DIR"/*.log "$SUBMISSION_PROFILING_DIR"
