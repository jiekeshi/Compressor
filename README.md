# Compressor

This replication package contains the source code for fine-tuning pre-trained models, model simplification and training, as well as all trained compressed models.

Due to the random nature of neural networks, users may obtain slightly different results via retraining the models. Please note that such results usually can be tolerated, i.e., they mostly do not conflict with the conclusions of the paper.

## Environment configuration

We provide a `Dockerfile` to help build the experimental environment. Please run the following scripts to to compile a docker image:
```
docker build -t YOUR_CUSTOM_TAG .
```
Be careful with the torch version that you need to use, modify the `Dockerfile` according to your cuda version pls.

Then, please run the docker:
```
dokcer run -it -v YOUR_LOCAL_REPO_PATH:/root/Compressor --gpus all YOUR_CUSTOM_TAG
```

GraphCodeBERT need a parser to extract data flows from the source code, please go to `./parser` to compile the parser first. Pls run:
```
cd parser
bash build.sh
```

## How to run
When searching for a tiny model's hyperparameters, please run:
```
python3 searcher.py -t YOUR_TARGET_SIZE
```
After that, please follow the `README.md` files under each subfolder to train the tiny model via knowledge distillation.

For each experiment in our paper, the scripts and instructions  are in the `README.md` files under each subfolder.

## Misc

If you meet any problems when using our code, please contact Jieke SHI by [jiekeshi@smu.edu.sg](mailto:jiekeshi@smu.edu.sg). Many thanks!

If you use any code from our repo in your paper, pls cite:

```
@misc{https://doi.org/10.48550/arxiv.2208.07120,
  url = {https://arxiv.org/abs/2208.07120},
  author = {Shi, Jieke and Yang, Zhou and Xu, Bowen and Kang, Hong Jin and Lo, David},
  title = {Compressing Pre-trained Models of Code into 3 MB},
  publisher = {arXiv},
  year = {2022}
}
```
