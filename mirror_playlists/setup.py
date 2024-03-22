"""Setup of mirror_playlists."""

from setuptools import find_packages, setup

setup(
    name="mirror_playlists",  # Replace by the actual name
    version="0.0.0",
    packages=find_packages(),
    entry_points={"console_scripts": ["mirror_playlists = mirror_playlists.main:main"]},
    author="Your Name",
    author_email="your.email@example.com",
    description="A tool to mirror playlists on devices",
    license="MIT",
    keywords="keywords ",
    url="https://github.com/username/reponame",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
