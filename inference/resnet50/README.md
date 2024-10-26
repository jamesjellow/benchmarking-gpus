# Instructions to run

1. First spin up a paperspace VM
2. ssh into your vm and clone the repo (you will need to setup an SSH key since this repo is private)

```sh
git clone git@github.com:jamesjellow/benchmarking-gpus.git
```

3. Move the script to the home directory

```sh
mv benchmarking-gpus/inference/resnet50/setup-and-run.sh .
```

4. Run the script for performance (You will need to type Y or Yes or press enter for some prompts)

```sh
sh setup-and-run.sh
```

5. Once performance is run, create a directory for your submission. I created this directory locally and will be submitting locally.
   Make sure you update the GPU_COUNT, GPU_MODEL, and VRAM

`mkdir benchmarking-gpus/inference/resnet50/results/single-stream/nvidia-GPU_COUNT-GPU_MODEL-VRAM`

6. Make sure you cloned the machine on yourlocal computer. Navigate into this directory on your local machine:

```
cd benchmarking-gpus/inference/resnet50/results/single-stream/nvidia-GPU_COUNT-GPU_MODEL-VRAM
```

7. Transfer your results from the VM to your local computer's file submission:
   scp -r paperspace@184.105.5.110:/home/paperspace/inference/vision/classification_and_detection/output/onnxruntime-gpu/resnet50/ performance/

8. Next, on the VM, let's do another run for accuracy. Add this `--accuracy` option to the last line of the `setup-and-run.sh` script

```
./run_local.sh onnxruntime resnet50 gpu --accuracy
```

9. Once it's done, on your local machine, copy the results to your local directory

```
scp -r paperspace@184.105.5.110:/home/paperspace/inference/vision/classification_and_detection/output/onnxruntime-gpu/resnet50/ accuracy/

```

10. Last but not least, we need to grab the hardware info. On the VM run:

```
sh inference/dump-hardware-info.sh
```

Then on your local machine run:

```
scp paperspace@184.105.5.110:/home/paperspace/hardware.json .
scp paperspace@184.105.5.110:/home/paperspace/hardware.txt .
```

11. Create the PR and your submission should be ready!
