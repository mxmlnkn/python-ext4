#!/usr/bin/env python3

import bz2
import os
import tempfile

import ext4


SCRIPT_FOLDER = os.path.dirname(os.path.realpath(__file__))


def test_path_tuple():
    path_tuple = ext4.Volume.path_tuple

    assert path_tuple("/") == ()
    assert path_tuple(b"/") == ()
    assert path_tuple("/test") == (b"test",)
    assert path_tuple(b"/test") == (b"test",)
    assert path_tuple("/test/test") == (b"test", b"test")
    assert path_tuple(b"/test/test") == (b"test", b"test")


def test_image():
    with (
        tempfile.NamedTemporaryFile(suffix=".test.ext4") as image,
        bz2.open(os.path.join(SCRIPT_FOLDER, "nested-tar-and-symlink-1M.ext4.bz2"), "rb") as compressed_image,
    ):
        image.write(compressed_image.read())
        image.seek(0)
        volume = ext4.Volume(compressed_image)

        # Expect FileNotFoundError for wrong path.
        got_exception = False
        try:
            volume.inode_at("/non-existing")
        except FileNotFoundError:
            got_exception = True
        assert got_exception

        # Root should return a directory object
        root = volume.inode_at("/")
        assert isinstance(root, ext4.Directory)
        # Not sure whether the special folders .. and . should be returned in the future.
        # Returning paths and names as bytes avoids having to assume an encoding.
        assert {entry.name for entry, _ in root.opendir()} == {b'..', b'.', b'foo', b'foo.tar'}

        # Open a regular file via its inode.
        file_node = volume.inode_at("/foo/bar")
        # TODO: Would be nice if this was possible.
        # assert file_node.i_no in volume.inodes
        file_node = volume.inodes[file_node.i_no]
        with file_node.open() as file:
            assert file.tell() == 0
            assert file.seek(0) == 0
            assert file.read() == b"Hi\n"
            assert file.read() == b""

            assert file.seek(1) == 1
            assert file.read() == b"i\n"

            assert file.seek(1) == 1
            assert file.read(1) == b"i"
            assert file.read(1) == b"\n"
            assert file.read(1) == b""
