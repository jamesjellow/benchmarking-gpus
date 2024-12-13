import requests
import json
import sys
import os
url = "https://henc2vuxaj.execute-api.us-east-1.amazonaws.com/default/Upload-Perf-Run"

def main():
  # inputs
  APIKEY = input("Enter API Key: ").strip()
  
  if len(sys.argv) < 2:
    runs_dir = input("Enter path to profiling subdirectory for run of interest: ").strip()
  else:
    runs_dir = sys.argv[1]
    
  if not os.path.isdir(runs_dir):
    print(f"Error: The directory '{runs_dir}' does not exist.")
    return
  os.chdir(runs_dir)
  
  submissionName = input("[OPTIONAL]Provide name for leaderboard!: ").strip()
  
  # file locations
  profling_metrics_directory = 'profiling/metrics_summary.json'
  results_directory = 'results/performance/run_1/mlperf_log_summary.txt'
  hardware_directory = 'systems'
  
  payloadVector = []
  
  # get payload data in JSON schema
  for thisRun in sorted(os.listdir(".")):
    if os.path.isdir(thisRun):
      os.chdir(thisRun)
      # print(f"Changed directory to: {os.getcwd()}")
      
      # work
      profilingMetrics = getProfilingMetrics(profling_metrics_directory)
      hardwareMetrics = getHardwareMetrics(hardware_directory)
      resultsMetrics = getResultsMetrics(results_directory)
      
      thisRunsDict = {
        "my_name_is": submissionName,
        "accelerator_memory_capacity": hardwareMetrics["accelerator_memory_capacity"],
        "accelerator_model_name": hardwareMetrics["accelerator_model_name"],
        "avg_cpu_usage": profilingMetrics["avg_cpu_usage"],
        "avg_gpu_mem_usage": profilingMetrics["avg_gpu_mem_usage"],
        "avg_gpu_usage": profilingMetrics["avg_gpu_usage"],
        "avg_mem_usage": profilingMetrics["avg_mem_usage"],
        "host_memory_capacity": hardwareMetrics["host_memory_capacity"],
        "host_processor_core_count": hardwareMetrics["host_processor_core_count"],
        "host_processor_model_name": hardwareMetrics["host_processor_model_name"],
        "host_processors_per_node": hardwareMetrics["host_processors_per_node"],
        "host_storage_type": hardwareMetrics["host_storage_type"],
        "latency_m": resultsMetrics["latency_m"],
        "operating_system": hardwareMetrics["operating_system"],
        "samples_ps": resultsMetrics["samples_ps"]
      }
      
      payloadVector.append(thisRunsDict)
      os.chdir("..")
    
  payload = json.dumps(payloadVector)
  
  headers = {
    'Content-Type': 'application/json',
    'x-api-key': APIKEY
  }
  
  print(payload)
  response = requests.request("POST", url, headers=headers, data=payload)
  print(response.text)
  

  
def getProfilingMetrics(file):
  with open(file, 'r') as file:
    profilingMetrics = json.load(file)
    
  cpu_performance = profilingMetrics.get("cpu", {}).get("performance", {})
  avg_cpu_usage = cpu_performance.get("cpu_all usage (%)", {}).get("mean", None)
  avg_gpu_mem_usage = profilingMetrics.get("gpu", {}).get("performance", {}).get("GPU memory usage (%)", {}).get("mean", None)
  avg_gpu_usage = profilingMetrics.get("gpu", {}).get("performance", {}).get("GPU usage (%)", {}).get("mean", None)
  avg_mem_usage = profilingMetrics.get("memory", {}).get("performance", {}).get("cache, RAM cache usage (KB)", {}).get("mean", None)
  
  profilingJson = {
      "avg_cpu_usage": avg_cpu_usage,
      "avg_gpu_mem_usage": avg_gpu_mem_usage,
      "avg_gpu_usage": avg_gpu_usage,
      "avg_mem_usage": avg_mem_usage
  }

  return profilingJson

def getHardwareMetrics(directory):
  hardWareFile = ''
  for thisFile in sorted(os.listdir(directory)):
    if thisFile == 'hardware.json' or thisFile == 'hardware.txt':
      continue
    hardWareFile = os.path.join(directory, thisFile)

  with open(hardWareFile, 'r') as file:
    hardwareMetrics = json.load(file)

  hardwareJson = {
      "accelerator_memory_capacity": hardwareMetrics.get("accelerator_memory_capacity", None),
      "accelerator_model_name": hardwareMetrics.get("accelerator_model_name", None),
      "host_memory_capacity": hardwareMetrics.get("host_memory_capacity", None),
      "host_processor_core_count": hardwareMetrics.get("host_processor_core_count", None),
      "host_processor_model_name": hardwareMetrics.get("host_processor_model_name", None),
      "host_processors_per_node": hardwareMetrics.get("host_processors_per_node", None),
      "host_storage_type": hardwareMetrics.get("host_storage_type", None),
      "operating_system": hardwareMetrics.get("operating_system", None)
  }

  return hardwareJson

def getResultsMetrics(file):
  resultsJson = {}
  targetList = ['Mean latency (ns)', 'samples_per_query']
  latency_m = None
  samples_ps = None
  
  with open(file, 'r') as file:
    for line in file:
      line = line.strip()
      keyValues = line.split(":")
      for i in range(0, len(keyValues)):
        keyValues[i] = keyValues[i].strip()
        
      if len(keyValues) != 2:
        continue
      
      key, value =  keyValues
      
      if key in targetList:
        thisKey = "latency_m" if key == targetList[0] else "samples_ps"
        resultsJson[thisKey] = value
  
  return resultsJson

if __name__ == "__main__":
  main()