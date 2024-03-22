"""Unit test of main."""

import unittest

from mirror_playlists.mirror_playlists.main import main


class TestMain(unittest.TestCase):
    def test_main(self):
        with self.assertRaises(NotImplementedError):
            main()
