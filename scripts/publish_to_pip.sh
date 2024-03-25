DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"/../mirror_playlists/

python3 setup.py sdist bdist_wheel
twine upload dist/*
