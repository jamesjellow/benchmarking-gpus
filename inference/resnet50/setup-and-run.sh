#!/bin/bash


# TODO: Modify paths to use $HOME variable instead of static path
# TODO: See if we want to use this script as an entry point for other models ./setup-and-run.sh modelName for example
# Comment: Move this script to the home directory of your machine to run it.

sudo apt update && sudo apt upgrade
sudo apt install python3 python3-pip python3-venv git wget curl
python3 -m venv cm
source cm/bin/activate
python3 -m pip install cmind
pip install cm4mlops
git clone --recurse-submodules https://github.com/mlcommons/inference.git --depth 1
sudo apt-get install libgl1-mesa-glx libegl1-mesa libxrandr2 libxrandr2 libxss1 libxcursor1 libxcomposite1 libasound2 libxi6 libxtst6
curl -O https://repo.anaconda.com/archive/Anaconda3-2023.09-0-Linux-x86_64.sh
bash Anaconda3-2023.09-0-Linux-x86_64.sh
source /home/paperspace/anaconda3/bin/activate
conda init
source ~/.bashrc
pip install onnxruntime pycocotools opencv-python
cd inference/vision/classification_and_detection
wget -q https://zenodo.org/record/2592612/files/resnet50_v1.onnx
tools/make_fake_imagenet.sh
pip install onnxruntime
export MODEL_DIR="/home/paperspace/inference/vision/classification_and_detection"
export DATA_DIR="/home/paperspace/inference/vision/classification_and_detection/fake_imagenet"
pip install pybind11
cd ../../loadgen; CFLAGS="-std=c++14" python setup.py develop --user; cd ../vision/classification_and_detection
python setup.py develop
pip install cython
pip install pycocotools
./run_local.sh onnxruntime resnet50 gpu
