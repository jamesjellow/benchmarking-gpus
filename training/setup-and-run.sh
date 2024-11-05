#!/bin/bash

sudo apt update
sudo apt install ubuntu-drivers-common
ubuntu-drivers devices
sudo ubuntu-drivers install
sudo reboot
sudo apt update -y
sudo apt install -y python3.7 python3.7-pip python3.7-venv python3.7-dev git git-lfs wget curl
python3.7 -m venv tf_env
source tf_env/bin/activate

git clone https://github.com/mlcommons/training.git
cd training

sh install_cuda_docker.sh

pip3 install protobuf==3.19.6
pip3 install absl-py
pip3 install tensorflow-gpu==1.14.0 protobuf==3.19.6
####python3 -m pip install tensorflow[and-cuda]

export CUDA_VISIBLE_DEVICES=0

cd language_model/tensorflow/bert
sudo -v ; curl https://rclone.org/install.sh | sudo bash
rclone config create mlc-training s3 provider=Cloudflare access_key_id=76ea42eadb867e854061a1806220ee1e secret_access_key=a53625c4d45e3ca8ac0df8a353ea3a41ffc3292aa25259addd8b7dc5a6ce2936 endpoint=https://c2686074cb2caf5cbaf6d134bdba8b47.r2.cloudflarestorage.com
rclone copy mlc-training:mlcommons-training-wg-public/wikipedia_for_bert/input_files ./input_files -P
rclone copy mlc-training:mlcommons-training-wg-public/wikipedia_for_bert/processed_dataset ./processed_dataset -P
mv processed_dataset input_files
mkdir output_data

cd input_files/processed_dataset
sudo apt install unzip
unzip results_text.zip
cd ../../

INPUT_DIR="input_files/processed_dataset/results4"          # Path to the input directory
OUTPUT_DIR="output_data"    # Path to the output TFRecord directory
VOCAB_FILE="input_files/vocab.txt"       # Path to the downloaded vocab.txt file
BERT_CONFIG="input_files/bert_config.json" # Path to bert config

chmod 777 output_data
mv cleanup_scripts/*.* .

for i in $(seq -w 0 499); do
  INPUT_DIR="input_files/processed_dataset/results4"      
  OUTPUT_DIR="output_data"
  INPUT_FILE="${INPUT_DIR}/part-00${i}-of-00500"
  OUTPUT_FILE="${OUTPUT_DIR}/part-00${i}-of-00500"
  VOCAB_FILE="input_files/vocab.txt"


  python3 create_pretraining_data.py \
    --input_file=${INPUT_FILE} \
    --output_file=${OUTPUT_FILE} \
    --vocab_file=${VOCAB_FILE} \
    --do_lower_case=True \
    --max_seq_length=512 \
    --max_predictions_per_seq=76 \
    --masked_lm_prob=0.15 \
    --random_seed=12345 \
    --dupe_factor=3

  echo "Processed file part-00${i}-of-00500"
done
echo "Pretraining data creation completed for all 500 parts."

## Pretraining and generating TF records
python3 create_pretraining_data.py \
  --input_file=${INPUT_DIR}/eval.txt \
  --output_file=${OUTPUT_DIR}/eval_intermediate \
  --vocab_file=${VOCAB_FILE} \
  --do_lower_case=True \
  --max_seq_length=512 \
  --max_predictions_per_seq=76 \
  --masked_lm_prob=0.15 \
  --random_seed=12345 \
  --dupe_factor=3

  python3 pick_eval_samples.py \
  --input_tfrecord=${OUTPUT_DIR}/eval_intermediate \
  --output_tfrecord=${OUTPUT_DIR}/eval_10k \
  --num_examples_to_pick=10000

pip install mlperf_logging

## Training
TF_XLA_FLAGS='--tf_xla_auto_jit=2' \
python3 run_pretraining.py \
  --bert_config_file=${BERT_CONFIG} \
  --output_dir="/tmp/output/parts" \
  --input_file="${OUTPUT_DIR}/part*" \
  --nodo_eval \
  --do_train \
  --eval_batch_size=8 \
  --learning_rate=0.0001 \
  --init_checkpoint=input_files/tf2_ckpt/model.ckpt-28252 \
  --iterations_per_loop=1000 \
  --max_predictions_per_seq=76 \
  --max_seq_length=512 \
  --num_train_steps=107538 \
  --num_warmup_steps=1562 \
  --optimizer=lamb \
  --save_checkpoints_steps=6250 \
  --start_warmup_step=0 \
  --num_gpus=1 \
  --train_batch_size=24

## Evaluation
TF_XLA_FLAGS='--tf_xla_auto_jit=2' \
python3 run_pretraining.py \
  --bert_config_file=${BERT_CONFIG} \
  --output_dir="tmp/output/eval_10k" \
  --input_file="${OUTPUT_DIR}/eval_10k" \
  --do_eval \
  --nodo_train \
  --eval_batch_size=8 \
  --init_checkpoint=input_files/tf2_ckpt/model.ckpt-28252 \
  --iterations_per_loop=1000 \
  --learning_rate=0.0001 \
  --max_eval_steps=1250 \
  --max_predictions_per_seq=76 \
  --max_seq_length=512 \
  --num_gpus=1 \
  --num_train_steps=107538 \
  --num_warmup_steps=1562 \
  --optimizer=lamb \
  --save_checkpoints_steps=1562 \
  --start_warmup_step=0 \
  --train_batch_size=24 \
  --nouse_tpu




