# mirror_playlists

Describe here what the package actually do

## Installation

```bash
python3 -m pip install mirror_playlists
```

## Usage

Assuming you have for instance a NFS share mounted under `/mnt/Music`.
You want to mirror all the playlists file located under `$HOME/Music/Playlists`.
Your music collection is located under `$HOME/Music`.

Run this command:

```bash
mirror_playlists -m $HOME/Music/ -p $HOME/Music/Playlists/ -d /mnt/Music
```

This will copy all song referred-to by your playlists.
This will also creates corresponding playlists files under `/mnt/Music/Playlists`.
The path to songs in those new playlists will be relative to the playlists file themselves.
This shall make them functional if they are embedded on an external device
