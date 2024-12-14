# HOW TO RUN BERT BENCHMARKS

## Prerequisites

1. Spin up a new VM in paperspace and make sure you select "Ubuntu 22" for the OS

2. Clone the repository into your home directory
```sh
git clone git@github.com:jamesjellow/benchmarking-gpus.git 
```

3. SSH into your machine and install drivers

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

4. Move all the scripts to your home directory
```sh
cp benchmarking-gpus/inference/bert99/*.sh benchmarking-gpus/inference/bert99/*.py benchmarking-gpus/inference/dump-hardware-info.sh .

```

5. Make all the scripts executable and change the ownership
```sh
chmod +x *.sh
sudo chown $USER:$USER -R .
```

6. Run the setup script
```sh
./setup.sh
```

7. Run a quick test to make sure there are no red warnings:

```sh
source cm/bin/activate
cm run script --tags=generate-run-cmds,inference,\_find-performance,\_all-scenarios \
 --adr.python.name=mlperf-cuda --model=bert-99 --implementation=reference \
 --device=cuda --backend=onnxruntime --quiet
```

8. Run the dump your hardware info script
```sh
./dump-hardware-info.sh
```

9. Run the benchmarks (This could take a couple hours or more depending on your machine)
```sh
for i in {1..9}; do 
./run_tests.sh; 
done
```

10. Run the `sh submit-results.sh` script to submit your results.
```sh
./submit-results.sh
```