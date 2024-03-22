"""Setup of package_foobar."""

from setuptools import find_packages, setup

setup(
    name="package_foobar",  # Replace by the actual name
    version="0.0.0",
    packages=find_packages(),
    entry_points={"console_scripts": ["package_foobar = package_foobar.main:main"]},
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
