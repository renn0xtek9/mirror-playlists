#!/usr/bin/env python3
"""Main script."""

import argparse
from pathlib import Path

from .mirror_playlists_utils import mirror_all_playlist


# pylint: disable=(unused-argument)
def main():
    """Implement main function of the script."""
    parser = argparse.ArgumentParser(description="Mirror the content of playlist files to a given destination")
    parser.add_argument(
        "-m",
        "--music-folder",
        help="path of the root folder of the music directory. Default is Music directory under the home folder",
        required=True,
    )
    parser.add_argument("-p", "--playlist-root", help="Root folder of where playlist are located", required=True)
    parser.add_argument("-d", "--destination", help="destination where the music should be mirrored", required=True)
    args = parser.parse_args()
    mirror_all_playlist(Path(args.music_folder), Path(args.playlist_root), Path(args.destination))


if __name__ == "__main__":
    main()  # pragma nocover
