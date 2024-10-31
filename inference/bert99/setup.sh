# Setup common linux tools
sudo apt update -y
sudo apt install -y python3 python3-pip python3-venv git git-lfs wget curl

# Install CUDA Ubuntu 22
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt-get update
sudo apt-get -y install cuda-toolkit-12-6

# Env setup
sudo apt update
echo "
# Set the CUDA paths
export PATH=/usr/local/cuda-12.6/bin:\$PATH
export LD_LIBRARY_PATH=/usr/local/cuda-12.6/lib64:\$LD_LIBRARY_PATH
" >> ~/.bashrc
source ~/.bashrc

# Setup cudnn Ubuntu 22
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt-get update
sudo apt-get -y install cudnn

# Install TensorRT
sudo apt update
sudo apt install tensorrt -y
    

# Setup CM
python3 -m venv cm
source cm/bin/activate

python3 -m pip install cmind -U

cm init 

cm test core