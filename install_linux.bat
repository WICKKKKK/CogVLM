@echo off

set HF_HOME=huggingface

export NO_PROXY=localhost,.woa.com,.oa.com,.tencent.com
export HTTP_PROXY=$ENV_VENUS_PROXY
export HTTPS_PROXY=$ENV_VENUS_PROXY
export no_proxy=$NO_PROXY
export http_proxy=$ENV_VENUS_PROXY
export https_proxy=$ENV_VENUS_PROXY

pip install torch==2.2.0 torchvision==0.17.0 --extra-index-url https://download.pytorch.org/whl/cu121
pip install bitsandbytes==0.42.0
pip install deepspeed==0.13.3
pip install -r ./requirements.txt
if %ERRORLEVEL% neq 0 (
    echo Deps install failed
    pause >nul
    exit /b 1
)

echo Install completed

ln -s /dockerdata/ /workspace/local_ssd
mkdir /workspace/local_ssd/models
ln -s /group/30188/ /workspace/falcon_folder
cp -r /workspace/falcon_folder/models/cogagent-vqa-hf /workspace/local_ssd/models/cogagent-vqa-hf

pause