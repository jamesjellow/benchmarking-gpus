# PLEASE ENSURE YOU GRAB THE AWS LINUX USER CREDENTIALS AND SET THEM
# https://uillinoisedu.sharepoint.com/:t:/s/CS598ResearchGroup79/EeGvJadKOgFBov5_1lE8AfQBDRLlrbJpzwLi6Kyxl3oudg?e=oL85da

sudo apt install unzip uuid -y
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

YOUR_RESULTS_DIR=$HOME/runs/
uuid=$(uuidgen -t)

aws s3 sync ${YOUR_RESULTS_DIR} s3://benchmarking-gpus/inference/bert99/results/${uuid}/runs
echo submission complete!