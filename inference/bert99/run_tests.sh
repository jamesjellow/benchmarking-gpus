#!/bin/bash
#MOVE SCRIPT TO HOME DIRECTORY
#MOVE SCRIPT TO HOME DIRECTORY
#MOVE SCRIPT TO HOME DIRECTORY

source ${HOME}/cm/bin/activate

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
BASE_RESULTS_DIR=$HOME/inference_results
BASE_PROFILING_DIR="profile"
BASE_SUBMISSION_DIR=$HOME/inference_submission_tree

# Determine the next run number
NEXT_RUN_NUM=1
while [ -d "${BASE_RESULTS_DIR}_run_${NEXT_RUN_NUM}" ]; do
  ((NEXT_RUN_NUM++))
done

# Set the results and profiling directories with the new run number
RESULTS_DIR="${BASE_RESULTS_DIR}_run_${NEXT_RUN_NUM}"
PROFILING_DIR="${RESULTS_DIR}/${BASE_PROFILING_DIR}"
SUBMISSION_DIR="${BASE_SUBMISSION_DIR}_run_${NEXT_RUN_NUM}"
INFERENCE_SUBMISSION="${SUBMISSION_DIR}/open/cTuning"

# Create results and profiling directories if they don't exist
mkdir -p "$RESULTS_DIR" "$PROFILING_DIR"
# mkdir -p "$SUBMISSION_DIR" # no need the CM scrip already collects this

# Do full accuracy and performance runs
./run_tests_type.sh "$RESULTS_DIR" "$PROFILING_DIR" "$NEXT_RUN_NUM" "accuracy"
./run_tests_type.sh "$RESULTS_DIR" "$PROFILING_DIR" "$NEXT_RUN_NUM" "performance"

# Populate readme
cm run script --tags=generate-run-cmds,inference,_populate-readme \
    --device=cuda \
    --model=bert-99 \
    --implementation=reference \
    --backend=onnxruntime \
    --scenario=Offline \
    --execution-mode=valid \
    --adr.python.name=mlperf-cuda \
    --quiet \
    --results_dir="$RESULTS_DIR"

# Generate MLPerf submission tree ---- maybe use to capture multiple run_1s from bert, resnet50, etc
cm run script --tags=generate,inference,submission \
    --results_dir="$RESULTS_DIR"/valid_results \
    --adr.python.name=mlperf-cuda \
    --device=cuda \
    --submission_dir="$SUBMISSION_DIR" \
    --clean \
    --run-checker \
    --submitter=cTuning \
    --quiet \
    --adr.inference-src.version=master

# Copy profiling logs and hardware summry to submission tree folder
SUBMISSION_PROFILING_DIR="${INFERENCE_SUBMISSION}/profiling"
SUBMISSION_SYSTEMS_DIR="${INFERENCE_SUBMISSION}/systems"


mkdir -p "$SUBMISSION_PROFILING_DIR"
./generate_summary.sh "$PROFILING_DIR"
cp "$PROFILING_DIR"/*.log "$SUBMISSION_PROFILING_DIR"
cp "$PROFILING_DIR"/*.json "$SUBMISSION_PROFILING_DIR"

## requires hardware to have have been run.....
cp "$HOME/hardware.txt" "$SUBMISSION_SYSTEMS_DIR"
cp "$HOME/hardware.json" "$SUBMISSION_SYSTEMS_DIR"


# get other relevant directories to report
SUBMISSION_MEASUREMENTS_DIR=$(find "${INFERENCE_SUBMISSION}/measurements" -type d -name "offline" -print -quit)
SUBMISSION_ACCURACY_DIR=$(find "${INFERENCE_SUBMISSION}/results" -type d -name "accuracy" -print -quit)
SUBMISSION_PERFORMANCE_DIR=$(find "${INFERENCE_SUBMISSION}/results" -type d -name "run_1" -print -quit)

# make runs directory if not already there to package this run
BASE_RUN_DIR="run"
RUN_DIR="${BASE_RUN_DIR}_${NEXT_RUN_NUM}"
mkdir -p "$HOME/runs/$RUN_DIR"/{measurements,profiling,results/{accuracy,performance},systems}

# package this run into runs directory
# cp -r "${SUBMISSION_PROFILING_DIR}" "$HOME/runs/${RUN_DIR}/profiling" # profiling here is redundant
cp -r "${SUBMISSION_PROFILING_DIR}" "$HOME/runs/${RUN_DIR}" # use this for profiling
# cp -r "${SUBMISSION_SYSTEMS_DIR}" "$HOME/runs/${RUN_DIR}/systems" # systems here is redundant
cp -r "${SUBMISSION_SYSTEMS_DIR}" "$HOME/runs/${RUN_DIR}" # use this for systems

if [ -n "${SUBMISSION_MEASUREMENTS_DIR}" ]; then
    cp -r "${SUBMISSION_MEASUREMENTS_DIR}" "$HOME/runs/${RUN_DIR}/measurements" # offline directory is kept here, maybe remove?
fi

if [ -n "${SUBMISSION_ACCURACY_DIR}" ]; then
    # cp -r "${SUBMISSION_ACCURACY_DIR}" "$HOME/runs/${RUN_DIR}/results/accuracy" # accuracy here is redundant
    cp -r "${SUBMISSION_ACCURACY_DIR}" "$HOME/runs/${RUN_DIR}/results" # use this for accuracy
fi

if [ -n "${SUBMISSION_PERFORMANCE_DIR}" ]; then
    cp -r "${SUBMISSION_PERFORMANCE_DIR}" "$HOME/runs/${RUN_DIR}/results/performance" # run_1 is kept here, maybe remove
fi