#!/bin/bash
#MOVE THIS SCRIPT TO THE HOME DIRECTORY IN VM
#MOVE THIS SCRIPT TO THE HOME DIRECTORY IN VM
#MOVE THIS SCRIPT TO THE HOME DIRECTORY IN VM



# Assign variables from command-line arguments
RESULTS_DIR=$1
PROFILING_DIR=$2
NEXT_RUN_NUM=$3
TEST_TYPE=$4

echo "Starting $TEST_TYPE metrics logging for run $NEXT_RUN_NUM..."

# Start logging GPU, CPU, disk, and memory usage
nvidia-smi --query-gpu=timestamp,utilization.gpu,utilization.memory,memory.used,memory.total --format=csv -l 1 > gpu_metrics_$TEST_TYPE.log &
GPU_LOG_PID=$!

mpstat -P ALL 1 > cpu_metrics_$TEST_TYPE.log &
CPU_LOG_PID=$!

iostat -x 1 > disk_metrics_$TEST_TYPE.log &
DISK_LOG_PID=$!

vmstat 1 > memory_metrics_$TEST_TYPE.log &
MEMORY_LOG_PID=$!

# Run the MLCommons benchmark - $TEST_TYPE (accuracy or performance)
echo "Running MLCommons benchmark for run $NEXT_RUN_NUM..."
cm run script --tags=generate-run-cmds,inference,_"$TEST_TYPE"-only,_all-scenarios \
    --adr.python.name=mlperf-cuda --model=bert-99 --device=cuda \
    --implementation=reference --backend=onnxruntime --quiet \
    --execution-mode=valid --results_dir="$RESULTS_DIR"

echo "Benchmark completed. Stopping $TEST_TYPE metrics logging for run $NEXT_RUN_NUM..."

# Stop the logging processes
kill $GPU_LOG_PID $CPU_LOG_PID $DISK_LOG_PID $MEMORY_LOG_PID

# Move the logs to the profiling directory
echo "Saving logs to profiling directory for run $NEXT_RUN_NUM..."
mv gpu_metrics_$TEST_TYPE.log "$PROFILING_DIR"
mv cpu_metrics_$TEST_TYPE.log "$PROFILING_DIR"
mv disk_metrics_$TEST_TYPE.log "$PROFILING_DIR"
mv memory_metrics_$TEST_TYPE.log "$PROFILING_DIR"

echo "All logs saved to $PROFILING_DIR"
