#!/bin/bash
set -euxo pipefail
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y
python3 -m pip install -r requirements.txt
