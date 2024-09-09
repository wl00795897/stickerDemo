# stickerDemo

## Environment set up

### Frontend
**If not install node.js yet, please install node.js first.**

Link: https://nodejs.org/en/download/package-manager

```
npm install
```
We only use Tailwind css for faster edit of css.

Docs: https://tailwindcss.com/docs/installation

### Backend

**We recommand using virtual environment.** The following is set up on Anaconda:

#### Install PyTorch
**First option:** Go to PyTorch for latest version: https://pytorch.org/get-started/locally/

**Second option (Recommand):** Since install latest version of PyTorch may encounter **UserWarning: 1Torch was not compiled with flash attention**, we use the following installation instead:
```
pip install torch==2.1.2 torchvision==0.16.2 torchaudio==2.1.2 --index-url https://download.pytorch.org/whl/cu121
pip install xformers==0.0.23.post1 --index-url https://download.pytorch.org/whl/cu121 // not sure need or not
```
Source: https://github.com/oobabooga/text-generation-webui/issues/5705

#### Install diffusers
```
conda install -c conda-forge diffusers
```
Also, we may encounter some problem while executing server.py, please execute the following commands also:
```
pip install --upgrade diffusers transformers accelerate safetensors
pip install -U peft
```
Source1: https://github.com/huggingface/safetensors/issues/128

Source2: https://stackoverflow.com/questions/78056541/how-do-i-resolve-this-lora-loading-error

#### Install huggingface CLI
```
pip install -U "huggingface_hub[cli]"
```

#### Install Flask, Flask-socketio, Flask-cors
```
pip install flask flask-socketio flask-cors
```
#### (Optional) Windows-build triton
For running zero-shot classifier, one may encounter **A matching Triton is not available, some optimizations will not be enabled. Error caught was: No module named 'triton'** on Windows.
To solve this, please run the following command:
```
pip install https://huggingface.co/madbuda/triton-windows-builds/resolve/main/triton-2.1.0-cp311-cp311-win_amd64.whl
```
Source1: https://huggingface.co/madbuda/triton-windows-builds/tree/main
Source2: https://github.com/triton-lang/triton/issues/1057
## Running
```
python server.py
```
Then go to localhost:5002 (or http://127.0.0.1:5002) for using interface.

## (Optional) Editing CSS
If you need to edit css, please run this command first:
```
npm run watch-tailwind
```
Then please edit css on static/css/input.css only
