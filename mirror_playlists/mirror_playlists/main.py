#!/usr/bin/env python3
"""Main script."""

import argparse
import sys
from pathlib import Path
from typing import List

from mirror_playlists.mirror_playlists.mirror_playlists_utils import mirror_all_playlist


# pylint: disable=(unused-argument)
def main(argv: List[str]):
    """Implement main function of the script.

    Args:
        argv (List[str]): list of arguments
    """
    ap = argparse.ArgumentParser(description="Mirror the content of playlist files to a given destination")
    ap.add_argument(
        "-m",
        "--music-folder",
        help="path of the root folder of the music directory. Default is Music directory under the home folder",
        required=True,
    )
    ap.add_argument("-p", "--playlist-root", help="Root folder of where playlist are located", required=True)
    ap.add_argument("-d", "--destination", help="destination where the music should be mirrored", required=True)
    args = ap.parse_args()
    mirror_all_playlist(Path(args.music_folder), Path(args.playlist_root), Path(args.destination))


if __name__ == "__main__":
    main(sys.argv)
