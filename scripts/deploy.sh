DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"/../package_foobar/

python3 setup.py sdist bdist_wheel
twine upload dist/*
