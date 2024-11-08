# HOW TO RUN BERT BENCHMARKS

## Prerequisites

1. Spin up a new VM in paperspace and make sure you select "Ubuntu 22" for the OS

2. SSH into your machine and install drivers

```sh
# Grab compatible drivers
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt-get update

# Install drivers and update machine
sudo apt update
ubuntu-drivers devices
sudo ubuntu-drivers install
sudo reboot
```

3. Copy the `setup.sh` script to your machine and run it.

4. Run a quick test to make sure there are no red warnings:

```sh
cm run script --tags=generate-run-cmds,inference,\_find-performance,\_all-scenarios \
 --adr.python.name=mlperf-cuda --model=bert-99 --implementation=reference \
 --device=cuda --backend=onnxruntime --quiet
```

5. Run the benchmarks (This could take a an hour or more depending on your machine)

https://github.com/mlcommons/ck/blob/master/cm-mlops/project/mlperf-inference-v3.0-submissions/docs/crowd-benchmark-mlperf-bert-inference-cuda.md

a. Do a full accuracy run for all the scenarios
b. Do a full performance run for all the scenarios
c. Populate the README files
d. Generate MLPerf submission tree

For step D, take out the last two commands `--hw_notes_extra="Result taken by <YOUR NAME>" --quiet`

6. Run the dump your hardware info script located in the /inference directory
```sh
sh dump-hardware-info.sh
```

7. The submission result will be stored in `inference_submission_tree/`

8. Grab your linux aws credentials from https://uillinoisedu.sharepoint.com/:t:/s/CS598ResearchGroup79/EeGvJadKOgFBov5_1lE8AfQBDRLlrbJpzwLi6Kyxl3oudg?e=oL85da . Then run the `sh submit-results.sh` script to submit your results.


```sh
scp -r paperspace@<IP>:/home/paperspace/inference_submission_tree/ .
```

Issues?
Web UI to create your own cm CLI commands:
https://access.cknowledge.org/playground/?action=howtorun
