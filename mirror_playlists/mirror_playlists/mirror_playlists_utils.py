"""Utility to mirror content of playlist with playlist file themselves a new destination."""

import logging
import os
import shutil
from pathlib import Path
from typing import List

logging.basicConfig(level=logging.INFO)


def is_folder_existing(path: Path) -> bool:
    """Return true if folder exist.

    Args:
        path: Path: path to the folder
    Returns: True if folder exists
    """
    return path.is_dir()


def get_all_playlist_files(playlist_root_path: Path) -> List[Path]:
    """List all .m3u files stored under the playlist root path.

    Args:
        playlist_root_path (Path): path of where all files are located
    Returns:
        List[Path]: list of path to all files
    """
    playlist_files = list(playlist_root_path.glob("**/*.m3u"))
    return playlist_files


def get_list_of_song_path_from_playlist_content(content: List[str], playlist_path: Path) -> List[Path]:
    """Get a list of song path contained in the playlist content.

    Args:
        content (List[str]): content of the playlist file
        playlist_path (Path): path to a given playlist file
    Return:
        List[Path]: list of resolved song path
    """
    file_paths = []
    for line in content:
        line = line.strip()
        if line and not line.startswith("#"):
            file_path = Path(line)
            if not file_path.is_absolute():
                file_path = Path(playlist_path.parent) / Path(file_path)
                file_path = file_path.resolve()
            if not file_path.exists():
                logging.warning("Song file %s does not exist", file_path)
            else:
                file_paths.append(file_path)
    return file_paths


def parse_playlist(playlist_path: Path) -> List[Path]:
    """Parse a playlist file.

    Args:
        playlist_path (Path): path to a given playlist file
    Returns:
        List[Path]: list of file contains in the m3u file
    """
    if not playlist_path.exists():
        logging.warning("Playlist file %s does not exist", playlist_path)
        return []
    with open(playlist_path, "r", encoding="utf-8") as content:
        return get_list_of_song_path_from_playlist_content(content, playlist_path)


def create_destination_file(
    source_song_path: Path, music_root_folder_path: Path, destination_folder_path: Path
) -> Path:
    """Create the destination path for a song.

    Create path being given the source path by replacing the music root folder with the destination folder.
    Example:
        source_song_path=/home/foo/Music/Artist/bar.mp3
        music_root_folder_path=/home/foo/Music
        destination_folder_path=/mnt/music will point
    The function will return /mnt/music/Artist/bar.mp3
    Args:
        source_song_path (Path): path of the song
        music_root_folder_path (Path): path of the root of music collection
        destination_folder_path (Path): path of mirroring destination
    Return:
        Path: destination of song path
    """
    relative_path = source_song_path.relative_to(music_root_folder_path)
    destination_path = destination_folder_path / relative_path
    return destination_path


def copy_song_file_if_not_existing_and_create_necessary_parent_folder(
    source_song_path: Path, destination_song_path: Path
):
    """Copy source_song_path into destination_song_path if destination_song_path does not already exist.

    If necessary, create parent folders of the destination_song_path.
    Args:
        source_song_path (Path): Path to the source song file.
        destination_song_path (Path): Path to the destination song file.
    """
    if not destination_song_path.exists():
        destination_song_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_song_path, destination_song_path)
        logging.info("New file %s copied on mirror side", str(destination_song_path))
    else:
        logging.info("File %s already exist on mirror side", str(destination_song_path))


def get_relative_path_to_song_from_playlist_file(playlist_file_path: Path, song_file_path: Path) -> str:
    """Get the reatlive path to the song from the playlist file.

    Example with
    playlist_file_path = /home/foo/music/Playlists/myplaylist.m3u and
    song_file = /home/foo/music/bar.mp3
    the function will return ../bar.mp3
    Args:
        playlist_file_path (Path): path of the playlist file that we want to mirror
        song_file_path (Path): path to the song file
    Return:
        str: relative path to reacht the song file from the playlist file
    """
    if playlist_file_path == song_file_path:
        raise ValueError("Song file and playlist file identical {song_file}")
    playlist_file_path_list = list(playlist_file_path.parts)
    song_file_path_list = list(song_file_path.parts)

    common_part_index = 0
    while common_part_index < len(playlist_file_path_list) and common_part_index < len(song_file_path_list):
        if playlist_file_path_list[common_part_index] != song_file_path_list[common_part_index]:
            break
        common_part_index = common_part_index + 1

    number_of_subfolder_remaining_to_playlist_file = len(playlist_file_path_list) - 1 - common_part_index
    relative_path_list = []
    relative_path_list = relative_path_list + ["../" for i in range(0, number_of_subfolder_remaining_to_playlist_file)]
    relative_path_list = relative_path_list + song_file_path_list[common_part_index:]
    return os.path.join(*relative_path_list)


def get_new_content_of_playlist_file(playlist_file_path: Path) -> List[str]:
    """Return the new content of the playlist that should be written on destination device.

    All song path are relative to the playlist file
    Args:
        playlist_file_path (Path): path of the playlist file that we want to mirror
    Return:
        List[str]: line by line content of the new file
    """
    list_of_song_path = parse_playlist(playlist_file_path)
    content = ["#EXTM3U"]
    for song_path in list_of_song_path:
        content.append(get_relative_path_to_song_from_playlist_file(playlist_file_path, song_path))
    return content


def get_destination_path_of_playlist_file(
    music_root_folder_path: Path, playlist_file_path: Path, destination_folder_path: Path
) -> Path:
    """Get the path of the new playlist (on destination device).

    Example:
        music_root_folder_path = /home/foo/Music/
        playlist_file_path = /home/foo/Music/Playlists/playlist.m3u
        destination_folder_path = /mnt/Music
    The function will return /mnt/Music/Playlists/playlist.m3u
    Args:
        music_root_folder_path (Path): root folder of the music repository to be mirror
        playlist_file_path (Path): path of the playlist file
        destination_folder_path (Path): destination where we should mirror files
    Return
        Path: path of the playlist file where the new playlist shall be saved
    """
    relative_path = playlist_file_path.relative_to(music_root_folder_path)
    return destination_folder_path / relative_path


def write_content_of_playlist_to_file(content: List[str], new_playlist_file_path: Path) -> None:
    """Write the content of the playlist into the new file.

    If needed, parent directory will be created.
    Args:
        content (List[str]): List of string line by line of the new content of playlist
        new_playlist_file_path (Path): path of the playlist file (absolute path, in destination folder)
    """
    new_playlist_file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(new_playlist_file_path, "w", encoding="utf-8") as new_file:
        new_file.write("\n".join(content))


def mirror_all_playlist(
    music_root_folder_path: Path, playlist_root_folder_path: Path, destination_folder_path: Path
) -> None:
    """Mirror all playlist and there content to the given destination.

    Args:
        music_root_folder_path (Path): root folder of the music repository to be mirror
        playlist_root_folder_path (Path): root folder of the playlist files
        destination_folder_path (Path): destination where we should mirror files
    Raises:
        FileNotFoundError: if the music folder or the playlist root or the destination folder does not exist.
        PermissionError: if no write permission to destination.
    """
    if not is_folder_existing(music_root_folder_path):
        raise FileNotFoundError("Music root folder not existing {music_root_folder_path}")
    if not is_folder_existing(playlist_root_folder_path):
        raise FileNotFoundError("Playlist root folder not existing {playlist_root_folder_path}")
    if not is_folder_existing(destination_folder_path):
        raise FileNotFoundError("Destination fodler not existing {destination_folder_path}")
    if not os.access(str(destination_folder_path), os.W_OK):
        raise PermissionError("No write access to {destination_folder_path}")

    playlist_files = get_all_playlist_files(playlist_root_folder_path)
    for playlist_file in playlist_files:
        logging.info("Mirroring: %s", str(playlist_file))
        list_of_song_path = parse_playlist(playlist_file)
        for song_path in list_of_song_path:
            destination_path = create_destination_file(song_path, music_root_folder_path, destination_folder_path)
            copy_song_file_if_not_existing_and_create_necessary_parent_folder(song_path, destination_path)
        new_content = get_new_content_of_playlist_file(playlist_file)
        new_playlist_file_path = get_destination_path_of_playlist_file(
            music_root_folder_path, playlist_file, destination_folder_path
        )
        write_content_of_playlist_to_file(new_content, new_playlist_file_path)
