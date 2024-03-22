"""Unit test ofr mirror_playlists"""

import unittest
from pathlib import Path
from typing import List
from unittest.mock import patch

from parameterized import parameterized

from mirror_playlists.mirror_playlists.main import main
from mirror_playlists.mirror_playlists.mirror_playlists_utils import (
    create_destination_file,
    get_destination_path_of_playlist_file,
    get_new_content_of_playlist_file,
    get_relative_path_to_song_from_playlist_file,
    mirror_all_playlist,
)


class TestMain(unittest.TestCase):
    def test_main_throws_if_help(self):
        argv = ["mirror_all_playlist.py", "-h"]
        with self.assertRaises(SystemExit):
            main(argv)

    def test_main_throws_if_destination_not_supplied(self):
        argv = ["mirror_all_playlist.py", "-m", "foo"]
        with self.assertRaises(SystemExit):
            main(argv)

    def test_main_throws_if_music_folder_not_supplied(self):
        argv = ["mirror_all_playlist.py"]
        with self.assertRaises(SystemExit):
            main(argv)


class TestMirrorAllPlaylist(unittest.TestCase):
    def setUp(self):
        self.non_existing_path = None

    def mock_is_folder_existing(self, mocked_path: Path) -> bool:
        """mock of function"""
        if mocked_path == self.non_existing_path:
            return False
        return True

    @patch("mirror_playlists.mirror_playlists.mirror_playlists_utils.is_folder_existing")
    def test_non_existing_music_folder(self, mock_is_folder_existing):
        music_folder = Path("/music")
        playlist_folder = Path("/music/playlists")
        destination_folder = Path("/destination")
        self.non_existing_path = music_folder

        mock_is_folder_existing.side_effect = self.mock_is_folder_existing

        with self.assertRaises(FileNotFoundError):
            mirror_all_playlist(music_folder, playlist_folder, destination_folder)

    @patch("mirror_playlists.mirror_playlists.mirror_playlists_utils.is_folder_existing")
    def test_non_existing_playlist_folder(self, mock_is_folder_existing):
        music_folder = Path("/music")
        playlist_folder = Path("/music/playlists")
        destination_folder = Path("/destination")
        self.non_existing_path = playlist_folder

        mock_is_folder_existing.side_effect = self.mock_is_folder_existing

        with self.assertRaises(FileNotFoundError):
            mirror_all_playlist(music_folder, playlist_folder, destination_folder)

    @patch("mirror_playlists.mirror_playlists.mirror_playlists_utils.is_folder_existing")
    def test_non_existing_destination_folder(self, mock_is_folder_existing):
        music_folder = Path("/music")
        playlist_folder = Path("/music/playlists")
        destination_folder = Path("/destination")
        self.non_existing_path = destination_folder

        mock_is_folder_existing.side_effect = self.mock_is_folder_existing

        with self.assertRaises(FileNotFoundError):
            mirror_all_playlist(music_folder, playlist_folder, destination_folder)


class TestCreateDestinationFile(unittest.TestCase):
    def test_create_destination_file(self):
        destination_path = create_destination_file(
            Path("/home/foo/Music/Artist/bar.mp3"), Path("/home/foo/Music/"), Path("/mnt/Music")
        )
        self.assertEqual(destination_path, Path("/mnt/Music/Artist/bar.mp3"))


class TestGetRelativePathToSongFromPlaylistFile(unittest.TestCase):
    @parameterized.expand(
        [
            [
                "song plain in music root dir",
                Path("/home/foo/music/Playlists/myplaylist.m3u"),
                Path("/home/foo/music/bar.mp3"),
                "../bar.mp3",
            ],
            [
                "song plain in a subfolder",
                Path("/home/foo/music/Playlists/myplaylist.m3u"),
                Path("/home/foo/music/Artist1/bar.mp3"),
                "../Artist1/bar.mp3",
            ],
            [
                "playlist file in subfolder",
                Path("/home/foo/music/Playlists/Subfolder/myplaylist.m3u"),
                Path("/home/foo/music/bar.mp3"),
                "../../bar.mp3",
            ],
            [
                "no common part",
                Path("/home/foo/music/Playlists/myplaylist.m3u"),
                Path("/media/foo/music/bar.mp3"),
                "../../../../media/foo/music/bar.mp3",
            ],
        ]
    )
    # pylint: disable=(unused-argument)
    def test_get_correct_relative_path(self, name, playlist_file, song_file, expected_path_string):
        self.assertEqual(expected_path_string, get_relative_path_to_song_from_playlist_file(playlist_file, song_file))

    def test_get_correct_relative_path_raises_if_both_path_are_identical(self):
        path = Path("/home/foo/bar.mp3")
        with self.assertRaises(ValueError):
            get_relative_path_to_song_from_playlist_file(path, path)


class TestGetNewContentOfPlaylistFile(unittest.TestCase):
    def mock_parse_playlist(self, _) -> List[Path]:
        """mock the parse playlist function"""
        return [Path("/home/foo/Music/bar.mp3"), Path("/home/foo/Music/Artist1/bar1.mp3")]

    @patch("mirror_playlists.mirror_playlists.mirror_playlists_utils.parse_playlist")
    def test_get_new_content_of_playlist_file(self, patch_parse_playlist):
        patch_parse_playlist.side_effect = self.mock_parse_playlist

        playlist_path = Path("/home/foo/Music/Playlist/playlist.m3u")
        expected_content = ["#EXTM3U", "../bar.mp3", "../Artist1/bar1.mp3"]

        self.assertEqual(expected_content, get_new_content_of_playlist_file(playlist_path))


class TestGetDestinationPathOfPlaylistFile(unittest.TestCase):
    def test_get_destination_path_of_playlist_file(self):
        music_folder = Path("/home/foo/Music/")
        playlist_file_path = Path("/home/foo/Music/Playlists/playlist.m3u")
        destination_folder = Path("/mnt/Music")
        expected_path = Path("/mnt/Music/Playlists/playlist.m3u")
        self.assertEqual(
            expected_path, get_destination_path_of_playlist_file(music_folder, playlist_file_path, destination_folder)
        )
