# PLEASE ENSURE YOU GRAB THE AWS LINUX USER CREDENTIALS AND SET THEM
# https://uillinoisedu.sharepoint.com/:t:/s/CS598ResearchGroup79/EeGvJadKOgFBov5_1lE8AfQBDRLlrbJpzwLi6Kyxl3oudg?e=oL85da

curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# TODO: put all results into a dir to submit to s3

# aws sync aws s3 sync ${YOUR_RESULTS_DIR}  s3://benchmarking-gpus/inference/bert99/results/${YOUR_RESULTS_DIR}
# echo submission complete!