# Whistler-Blackcomb Lift Prediction

XXXXXX

## Overview

XXXXXX

### Key Repo Locations

XXXXX

## Setting Up Environment

1. Clone this repo, instructions found [HERE](https://docs.github.com/en/free-pro-team@latest/github/creating-cloning-and-archiving-repositories/cloning-a-repository)
2. Open a command prompt and navigate to the newly cloned repo
3. Create a virtual environment by executing `python -m venv YOUR-ENV-NAME` in a command prompt. Replace `YOUR-EVN-NAME` with whatever you like, instructions found [HERE](https://docs.python.org/3/library/venv.html)
4. Activate the virtual environment, in Linux and Mac this is `source YOUR-ENV-NAME/bin/activate` and Windows this is `./YOUR-ENV-NAME/bin/activate`

If you plan to run `nam_model_download.py` you need download `pygrib`, otherwise this can be skipped. Instructions can be found [HERE](https://jswhit.github.io/pygrib/docs/)

In Linux:
This works for Ubuntu and is only necessary if you want to run NAM_model_download.py
- In a virtual environment execute `sudo apt-get update` and `sudo apt-get install -y libeccodes-dev gcc`
- Install dependencies by executing `pip install -r requirements.txt` in a command prompt 

In Mac:
- `brew install eccodes` untested

In Windows:
You will need to install Cygwin
