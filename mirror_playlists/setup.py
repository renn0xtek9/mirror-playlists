"""Setup of mirror_playlists."""

from setuptools import find_packages, setup

setup(
    name="mirror_playlists",
    version="0.0.1",
    packages=find_packages(),
    entry_points={"console_scripts": ["mirror_playlists = mirror_playlists.main:main"]},
    author="Maxime Haselbauer",
    author_email="maxime.haselbauer@googlemail.com",
    description="A tool to mirror playlists on devices",
    license="MIT",
    keywords="keywords ",
    url="https://github.com/renn0xtek9/mirror-playlists",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
