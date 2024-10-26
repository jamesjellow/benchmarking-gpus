# HOW TO RUN RESET BENCHMARKS

1. Spin up a new VM in paperspace and make sure you select "ML in a box" for the OS

2. SSH into your machine and Setup CM

```
python3 -m pip install cmind -U

cm init

cm test core

Run test
```

2. Update environment

```
sudo apt update
echo 'export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc
```

2. Install cuDNN

```
#Ubuntu 22
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt-get update
sudo apt-get -y install cudnn


#Ubuntu 20
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt-get update
sudo apt-get -y install cudnn
```

2. Install TensorRT

```
sudo apt update
sudo apt install tensorrt
```

3. Run a quick test to make sure there are no red warnings:

```
cm run script --tags=generate-run-cmds,inference,_find-performance,_all-scenarios \
    --adr.python.name=mlperf-cuda --model=bert-99 --implementation=reference \
    --device=cuda --backend=onnxruntime --quiet
#sudo apt install tensorrt --fix-missing
```

4. Run the benchmarks (This could take a an hour or more depending on your machine)

   a. Do a full accuracy run for all the scenarios
   b. Do a full performance run for all the scenarios
   c. Populate the README files
   d. Generate MLPerf submission tree

For step D, take out the last two commands `--hw_notes_extra="Result taken by <YOUR NAME>" --quiet`

5. The submission result will be stored in `inference_submission_tree/`

6. Grab that submission, scp it from your machine to your machine. Create a pull request.

```
scp -r paperspace@<IP>:/home/paperspace/inference_submission_tree/ .
```

Issues?
Try this guide:
https://github.com/mlcommons/ck/blob/master/cm-mlops/project/mlperf-inference-v3.0-submissions/docs/crowd-benchmark-mlperf-bert-inference-cuda.md

Web UI to create your own cm CLI commands:
https://access.cknowledge.org/playground/?action=howtorun
