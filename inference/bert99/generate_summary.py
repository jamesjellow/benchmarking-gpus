import os
import sys
import json
from summarize_profiles import getSummary

def main():
    if len(sys.argv) < 2:
        profiling_dir = input("Enter path to profiling subdirectory for run of interest: ").strip()
    else:
        profiling_dir = sys.argv[1]
    
    if not os.path.isdir(profiling_dir):
        print(f"Error: The directory '{profiling_dir}' does not exist.")
        return

    # Change to the profiling directory
    os.chdir(profiling_dir)
    print(f"Changed directory to: {os.getcwd()}")

    # get summarized dataframes per log
    dfCpuAcc = getSummary('cpu_metrics_accuracy.log')
    dfCpuPerf = getSummary('cpu_metrics_performance.log')
    dfGpuAcc = getSummary('gpu_metrics_accuracy.log')
    dfGpuPerf = getSummary('gpu_metrics_performance.log')
    dfMemAcc = getSummary('memory_metrics_accuracy.log')
    dfMemPerf = getSummary('memory_metrics_performance.log')
    dfDiskAcc = getSummary('disk_metrics_accuracy.log')
    dfDiskPerf = getSummary('disk_metrics_performance.log')
    
    # convert dataframes to dictionaries
    cpuAccuracy = dfCpuAcc.to_dict()
    cpuPerformance = dfCpuPerf.to_dict()
    gpuAccuracy = dfGpuAcc.to_dict()
    gpuPerformance = dfGpuPerf.to_dict()
    memoryAccuracy = dfMemAcc.to_dict()
    memoryPerformance = dfMemPerf.to_dict()
    diskAccuracy = dfDiskAcc.to_dict()
    diskPerformance = dfDiskPerf.to_dict()

    finalJson = {
        "cpu": {
            "accuracy": cpuAccuracy,
            "performance": cpuPerformance
        },
        "gpu": {
            "accuracy": gpuAccuracy,
            "performance": gpuPerformance
        },
        "memory": {
            "accuracy": memoryAccuracy,
            "performance": memoryPerformance
        },
        "disk": {
            "accuracy": diskAccuracy,
            "performance": diskPerformance
        }
    }

    with open('metrics_summary.json', 'w') as jsonFile:
        json.dump(finalJson, jsonFile, indent=4)

    print("JSON file 'metrics_summary.json' created successfully!")

if __name__ == "__main__":
    main()
