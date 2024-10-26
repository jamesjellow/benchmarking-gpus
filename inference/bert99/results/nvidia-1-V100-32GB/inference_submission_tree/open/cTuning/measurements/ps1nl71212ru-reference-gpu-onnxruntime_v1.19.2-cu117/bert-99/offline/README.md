This experiment is generated using the [MLCommons Collective Mind automation framework (CM)](https://github.com/mlcommons/cm4mlops).

*Check [CM MLPerf docs](https://docs.mlcommons.org/inference) for more details.*

## Host platform

* OS version: Linux-5.4.0-198-generic-x86_64-with-glibc2.31
* CPU version: x86_64
* Python version: 3.9.16 (main, Dec  7 2022, 01:11:51) 
[GCC 9.4.0]
* MLCommons CM version: 3.2.8

## CM Run Command

See [CM installation guide](https://docs.mlcommons.org/inference/install/).

```bash
pip install -U cmind

cm rm cache -f

cm pull repo mlcommons@cm4mlops --checkout=2592e2bccf09e4234070e38299d9d8d697f76eda

cm run script \
	--tags=generate-run-cmds,inference,_populate-readme,_all-scenarios \
	--adr.python.name=mlperf-cuda \
	--model=bert-99 \
	--device=cuda \
	--implementation=reference \
	--backend=onnxruntime \
	--quiet \
	--execution-mode=valid \
	--results_dir=/home/paperspace/inference_3.0_results
```
*Note that if you want to use the [latest automation recipes](https://docs.mlcommons.org/inference) for MLPerf (CM scripts),
 you should simply reload mlcommons@cm4mlops without checkout and clean CM cache as follows:*

```bash
cm rm repo mlcommons@cm4mlops
cm pull repo mlcommons@cm4mlops
cm rm cache -f

```

## Results

Platform: ps1nl71212ru-reference-gpu-onnxruntime_v1.19.2-cu117

Model Precision: fp32

### Accuracy Results 
`F1`: `90.87487`, Required accuracy for closed division `>= 89.96526`

### Performance Results 
`Samples per second`: `41.4473`
