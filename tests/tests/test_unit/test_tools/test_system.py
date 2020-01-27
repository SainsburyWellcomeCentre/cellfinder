import pytest
import random
import os

from pathlib import Path
from math import isclose
from imlib.system import ensure_directory_exists

import cellfinder.tools.system as system
from cellfinder.tools.exceptions import CommandLineInputError

data_dir = Path("tests", "data")
background_im_dir = os.path.join(data_dir, "background")


def write_n_random_files(n, dir, min_size=32, max_size=2048):
    sizes = random.sample(range(min_size, max_size), n)
    for size in sizes:
        with open(os.path.join(dir, str(size)), "wb") as fout:
            fout.write(os.urandom(size))


def test_delete_directory_contents(tmpdir):
    delete_dir = os.path.join(str(tmpdir), "delete_dir")
    os.mkdir(delete_dir)
    write_n_random_files(10, delete_dir)

    # check the directory isn't empty first
    assert not os.listdir(delete_dir) == []

    system.delete_directory_contents(delete_dir, progress=True)
    assert os.listdir(delete_dir) == []


def test_get_subdirectories():
    subdirs = system.get_subdirectories(data_dir)
    assert len(subdirs) == 9
    assert Path(data_dir / "metadata") in subdirs
    assert Path(data_dir / "nii") in subdirs

    subdir_names = system.get_subdirectories(data_dir, names_only=True)
    assert len(subdir_names) == 9
    assert "metadata" in subdir_names
    assert "nii" in subdir_names


def test_get_number_of_files_in_dir():
    assert system.get_number_of_files_in_dir(background_im_dir) == 26


def write_file_single_size(directory, file_size):
    with open(os.path.join(directory, str(file_size)), "wb") as fout:
        fout.write(os.urandom(file_size))


def test_check_path_exists(tmpdir):
    num = 10
    tmpdir = str(tmpdir)

    assert system.check_path_exists(os.path.join(tmpdir))
    no_exist_dir = os.path.join(tmpdir, "i_dont_exist")
    with pytest.raises(FileNotFoundError):
        assert system.check_path_exists(no_exist_dir)

    write_file_single_size(tmpdir, num)
    assert system.check_path_exists(os.path.join(tmpdir, str(num)))
    with pytest.raises(FileNotFoundError):
        assert system.check_path_exists(os.path.join(tmpdir, "20"))


def test_catch_input_file_error(tmpdir):
    tmpdir = str(tmpdir)
    # check no error is raised:
    system.catch_input_file_error(tmpdir)

    no_exist_dir = os.path.join(tmpdir, "i_dont_exist")
    with pytest.raises(CommandLineInputError):
        system.catch_input_file_error(no_exist_dir)


def test_ensure_directory_exists():
    home = os.path.expanduser("~")
    exist_dir = os.path.join(home, ".cellfinder_test_dir")
    ensure_directory_exists(exist_dir)
    assert os.path.exists(exist_dir)
    os.rmdir(exist_dir)


def test_memory_in_bytes():
    memory_detection_tolerance = 1  # byte

    assert isclose(
        system.memory_in_bytes(1, "kb"),
        1000,
        abs_tol=memory_detection_tolerance,
    )
    assert isclose(
        system.memory_in_bytes(1.2, "MB"),
        1200000,
        abs_tol=memory_detection_tolerance,
    )
    assert isclose(
        system.memory_in_bytes(0.00065, "gb"),
        650000,
        abs_tol=memory_detection_tolerance,
    )
    assert isclose(
        system.memory_in_bytes(0.000000000234, "TB"),
        234,
        abs_tol=memory_detection_tolerance,
    )
    assert isclose(
        system.memory_in_bytes(1000, "pb"),
        10 ** 18,
        abs_tol=memory_detection_tolerance,
    )

    with pytest.raises(NotImplementedError):
        system.memory_in_bytes(1000, "ab")


