#!/bin/bash
set -euxo pipefail
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"/..
pip uninstall -y mirror_playlists
pip install -e mirror_playlists
mirror_playlists -h
