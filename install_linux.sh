#!/bin/bash

export HF_HOME=/workspace/local_ssd/huggingface
export NO_PROXY=localhost,.woa.com,.oa.com,.tencent.com
export HTTP_PROXY=$ENV_VENUS_PROXY
export HTTPS_PROXY=$ENV_VENUS_PROXY
export no_proxy=$NO_PROXY
export http_proxy=$ENV_VENUS_PROXY
export https_proxy=$ENV_VENUS_PROXY

pip install torch==2.2.0 torchvision==0.17.0 --extra-index-url https://download.pytorch.org/whl/cu121
pip install bitsandbytes==0.41.1
pip install deepspeed==0.11.2
pip install -r ./requirements.txt

if [ $? -ne 0 ]; then
    echo "Deps install failed"
    exit 1
fi

echo Install completed

ln -s /dockerdata/ /workspace/local_ssd
mkdir -p /workspace/local_ssd/models
ln -s /group/30188/ /workspace/falcon_folder
cp -r /workspace/falcon_folder/models/cogagent-vqa-hf /workspace/local_ssd/models/cogagent-vqa-hf

echo ""