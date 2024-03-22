"""Unit test ofr mirror_playlists"""

import os
import unittest
from pathlib import Path
from typing import List
from unittest.mock import patch

from parameterized import parameterized

from mirror_playlists.mirror_playlists.main import main
from mirror_playlists.mirror_playlists.mirror_playlists_utils import (
    copy_song_file_if_not_existing_and_create_necessary_parent_folder,
    create_destination_file,
    get_all_playlist_files,
    get_destination_path_of_playlist_file,
    get_list_of_song_path_from_playlist_content,
    get_new_content_of_playlist_file,
    get_relative_path_to_song_from_playlist_file,
    is_folder_existing,
    mirror_all_playlist,
    parse_playlist,
    write_content_of_playlist_to_file,
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

    @patch("mirror_playlists.mirror_playlists.main.mirror_all_playlist")
    def test_main_call_mirror_all_playlist_with_correct_arguments(self, mock_mirror_all_playlist):
        mock_mirror_all_playlist.return_value = None
        argv = ["mirror_all_playlist.py", "-m", "/home/foo/Music", "-p", "/home/foo/Music/Playlists", "-d", "/mnt/bar"]
        music_folder_path = Path(argv[2])
        playlist_folder_path = Path(argv[4])
        destination_folder_path = Path(argv[6])
        main(argv)
        mock_mirror_all_playlist.assert_called_once_with(
            music_folder_path, playlist_folder_path, destination_folder_path
        )


class TestMirrorAllPlaylist(unittest.TestCase):
    def setUp(self):
        self.non_existing_path = None

    def mock_is_folder_existing(self, mocked_path: Path) -> bool:
        """mock of function"""
        if mocked_path == self.non_existing_path:
            return False
        return True

    @patch("mirror_playlists.mirror_playlists.mirror_playlists_utils.is_folder_existing")
    def test_mirror_all_playlist_throws_if_non_existing_music_folder(self, mock_is_folder_existing):
        music_folder = Path("/music")
        playlist_folder = Path("/music/playlists")
        destination_folder = Path("/destination")
        self.non_existing_path = music_folder

        mock_is_folder_existing.side_effect = self.mock_is_folder_existing

        with self.assertRaises(FileNotFoundError):
            mirror_all_playlist(music_folder, playlist_folder, destination_folder)

    @patch("mirror_playlists.mirror_playlists.mirror_playlists_utils.is_folder_existing")
    def test_mirror_all_playlist_throws_if_non_existing_playlist_folder(self, mock_is_folder_existing):
        music_folder = Path("/music")
        playlist_folder = Path("/music/playlists")
        destination_folder = Path("/destination")
        self.non_existing_path = playlist_folder

        mock_is_folder_existing.side_effect = self.mock_is_folder_existing

        with self.assertRaises(FileNotFoundError):
            mirror_all_playlist(music_folder, playlist_folder, destination_folder)

    @patch("mirror_playlists.mirror_playlists.mirror_playlists_utils.is_folder_existing")
    def test_mirror_all_playlist_throws_if_non_existing_destination_folder(self, mock_is_folder_existing):
        music_folder = Path("/music")
        playlist_folder = Path("/music/playlists")
        destination_folder = Path("/destination")
        self.non_existing_path = destination_folder

        mock_is_folder_existing.side_effect = self.mock_is_folder_existing

        with self.assertRaises(FileNotFoundError):
            mirror_all_playlist(music_folder, playlist_folder, destination_folder)

    @patch("mirror_playlists.mirror_playlists.mirror_playlists_utils.is_folder_existing")
    @patch("os.access")
    def test_mirror_all_playlist_throws_if_no_write_permission_on_destination(
        self, mock_access, mock_is_folder_existing
    ):
        mock_access.return_value = False
        mock_is_folder_existing.return_value = True

        music_folder = Path("/path/to/music_folder")
        playlist_root = Path("/path/to/playlist_root")
        destination_folder = Path("/path/to/destination_folder")

        with self.assertRaises(PermissionError):
            mirror_all_playlist(music_folder, playlist_root, destination_folder)

        mock_access.assert_called_once_with(str(destination_folder), os.W_OK)

    @patch("os.access")
    @patch("mirror_playlists.mirror_playlists.mirror_playlists_utils.is_folder_existing")
    @patch("mirror_playlists.mirror_playlists.mirror_playlists_utils.write_content_of_playlist_to_file")
    @patch("mirror_playlists.mirror_playlists.mirror_playlists_utils.get_destination_path_of_playlist_file")
    @patch("mirror_playlists.mirror_playlists.mirror_playlists_utils.get_new_content_of_playlist_file")
    # pylint: disable=(line-too-long)
    @patch(
        "mirror_playlists.mirror_playlists.mirror_playlists_utils.copy_song_file_if_not_existing_and_create_necessary_parent_folder"
    )
    @patch("mirror_playlists.mirror_playlists.mirror_playlists_utils.create_destination_file")
    @patch("mirror_playlists.mirror_playlists.mirror_playlists_utils.parse_playlist")
    @patch("mirror_playlists.mirror_playlists.mirror_playlists_utils.get_all_playlist_files")
    def test_mirror_all_playlists_make_right_calls(
        self,
        mock_get_all_playlist,
        mock_parse_playlist,
        mock_create_file,
        mock_copy_song,
        mock_get_new_content,
        mock_get_destination,
        mock_write_content,
        mock_is_folder_exist,
        mock_os_access,
    ):
        mock_get_all_playlist.return_value = [
            Path("/home/foo/Music/Playlists/one.m3u"),
            Path("/home/foo/Music/Playlists/two.m3u"),
        ]
        mock_parse_playlist.return_value = [Path("/home/foo/Music/song_one.mp3"), Path("/home/foo/Music/song_two.mp3")]
        mock_copy_song.return_value = True
        mock_create_file.return_value = Path("/mnt/foo/playlist.m3u")
        mock_get_new_content.return_value = ["#EXTM3U", "/home/foo/bar.mp3"]
        mock_get_destination.return_value = Path("/mnt/foo/playlist.m3u")
        mock_write_content.return_value = True
        mock_is_folder_exist.return_value = True
        mock_os_access.return_value = True

        mirror_all_playlist(Path("/home/foo/Music"), Path("/home/foo/Music/Playlists"), Path("/mnt/foo"))

        self.assertEqual(mock_get_all_playlist.call_count, 1)
        self.assertEqual(mock_create_file.call_count, 4)
        self.assertEqual(mock_parse_playlist.call_count, 2)
        self.assertEqual(mock_get_new_content.call_count, 2)
        self.assertEqual(mock_get_destination.call_count, 2)
        self.assertEqual(mock_write_content.call_count, 2)


class TestIsfolderExisting(unittest.TestCase):
    @patch("pathlib.Path.is_dir")
    def test_is_folder_existing(self, mock_is_dir):
        mock_is_dir.return_value = True
        self.assertTrue(is_folder_existing(Path("/foo")))
        mock_is_dir.return_value = False
        self.assertFalse(is_folder_existing(Path("/foo")))


class TestGetAllPlaylistFiles(unittest.TestCase):
    @patch("pathlib.Path.glob")
    def test_get_all_playlist_files(self, mock_glob):
        mock_glob.return_value = [Path("/home/foo/bar.mp3"), Path("/home/foo/bar2.mp3")]
        all_file_path = get_all_playlist_files(Path("/home/foo"))
        expected_files_list = [Path("/home/foo/bar.mp3"), Path("/home/foo/bar2.mp3")]
        self.assertEqual(expected_files_list, all_file_path)


class TestWriteContentOfPlaylist(unittest.TestCase):
    @patch("builtins.open", new_callable=unittest.mock.mock_open)
    @patch("pathlib.Path.mkdir")
    def test_write_content_of_playlist_to_file(self, mock_mkdir, mock_open):
        # Prepare mock content
        content = ["song1.mp3", "song2.mp3", "song3.mp3"]
        new_playlist_file_path = Path("/path/to/playlist.m3u")

        # Call the write_content_of_playlist_to_file function
        write_content_of_playlist_to_file(content, new_playlist_file_path)

        # Assert that mkdir was called with the correct arguments
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

        # Assert that open was called with the correct arguments
        mock_open.assert_called_once_with(new_playlist_file_path, "w", encoding="utf-8")

        # Assert that write was called with the correct content
        mock_open().write.assert_called_once_with("\n".join(content))


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


class TestParsePlaylist(unittest.TestCase):
    @patch("pathlib.Path.exists")
    def test_parse_playlist_when_file_does_not_exists(self, mock_exists):
        mock_exists.return_value = False
        self.assertEqual([], parse_playlist(Path("/home/foo/playlist.m3u")))

    @patch("builtins.open")
    @patch("pathlib.Path.exists")
    def test_parse_playlist_when_file_exists(self, mock_exists, mock_open):
        mock_exists.return_value = True
        mock_content = ["/home/foo/song1.mp3", "/home/foo/song2.mp3", "/home/foo/song3.mp3"]
        mock_open.return_value.__enter__.return_value = mock_content

        playlist_path = Path("/home/foo/playlist.m3u")
        expected_content = [Path(song_path_str) for song_path_str in mock_content]
        self.assertEqual(expected_content, parse_playlist(playlist_path))
        mock_open.assert_called_once_with(playlist_path, "r", encoding="utf-8")


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


class TestGetListOfSongPathFromPlaylistContent(unittest.TestCase):

    @patch("pathlib.Path.exists")
    def test_get_list_of_song_path_from_playlist_content(self, mock_exists):
        mock_exists.return_value = True
        content = ["#EXTM3U", "/home/foo/Music/Artist/foobar.mp3", "../Artist2/foobar2.mp3"]
        expected_path_list = [Path("/home/foo/Music/Artist/foobar.mp3"), Path("/home/foo/Music/Artist2/foobar2.mp3")]
        path_list = get_list_of_song_path_from_playlist_content(content, Path("/home/foo/Music/Playlists/playlist.m3u"))
        self.assertEqual(expected_path_list, path_list)
        # when files already exists
        mock_exists.return_value = False
        path_list = get_list_of_song_path_from_playlist_content(content, Path("/home/foo/Music/Playlists/playlist.m3u"))
        self.assertEqual([], path_list)


class TestCopySongFileIfNotExistingAndCreateNecessaryParentFolder(unittest.TestCase):
    @patch("pathlib.Path.mkdir")
    @patch("shutil.copy2")
    @patch("pathlib.Path.exists")
    def test_copy_song_file_if_not_existing_and_create_necessary_parent_folder_when_file_does_not_exist(
        self, mock_exists, mock_copy, mock_mkdir
    ):
        mock_exists.return_value = False
        mock_copy.return_value = True
        mock_mkdir.return_value = True

        source_song_path = Path("/home/foo/Music/Artist/foo.mp3")
        destination_song_path = Path("/mnt/Music/Artist/foo.mp3")

        copy_song_file_if_not_existing_and_create_necessary_parent_folder(source_song_path, destination_song_path)
        mock_copy.assert_called_once_with(source_song_path, destination_song_path)
        mock_mkdir.assert_called_once()

    @patch("pathlib.Path.mkdir")
    @patch("shutil.copy2")
    @patch("pathlib.Path.exists")
    def test_copy_song_file_if_not_existing_and_create_necessary_parent_folder_when_file_exists(
        self, mock_exists, mock_copy, mock_mkdir
    ):
        mock_exists.return_value = True
        mock_copy.return_value = True
        mock_mkdir.return_value = True

        source_song_path = Path("/home/foo/Music/Artist/foo.mp3")
        destination_song_path = Path("/mnt/Music/Artist/foo.mp3")

        copy_song_file_if_not_existing_and_create_necessary_parent_folder(source_song_path, destination_song_path)
        mock_copy.assert_not_called()
        mock_mkdir.assert_not_called()
