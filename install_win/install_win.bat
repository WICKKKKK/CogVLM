@echo off

set HF_HOME=huggingface

pip install torch==2.2.0+cu121 torchvision==0.17.0+cu121 --extra-index-url https://download.pytorch.org/whl/cu121
pip install bitsandbytes==0.41.1 --index-url https://jihulab.com/api/v4/projects/140618/packages/pypi/simple
pip install ./install_win/deepspeed-0.11.2+cuda121-cp310-cp310-win_amd64.whl
pip install -r ./requirements.txt
if %ERRORLEVEL% neq 0 (
    echo Deps install failed
    pause >nul
    exit /b 1
)

echo Install completed

pause