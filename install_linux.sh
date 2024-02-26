#!/bin/bash

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