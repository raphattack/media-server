import logging
from argparse import ArgumentParser, Namespace
from enum import Enum
import os
from typing import List

_LOG_FORMAT = "[%(asctime)s] [%(process)d] [%(filename)s] [%(funcName)s] [%(levelname)s] %(message)s"
logging.basicConfig(
    level=logging.DEBUG,
    format=_LOG_FORMAT,
    handlers=[logging.FileHandler("dedupe.log"), logging.StreamHandler()],
)
LOGGER = logging.getLogger(__name__)


class Mode(Enum):
    TEST = "test"
    DELETE = "delete"


"""
Directories to exclude.

Example directory structure:
    /media/Games
    /media/Movies
    /media/Pictures
    /media/Shows

Running the script with --base-dir /media will exclude these directories:
    /media/Games
    /media/Pictures
"""
EXCLUDE = {"Games", "Pictures"}

# global variables
_total_space_saved = 0
_mode = ""


def parse_args() -> Namespace:
    """
    Sets the arguments for the program.

    -b, --base-dir
        The base directory.

        Example:
            /media

    -m, --mode
        The mode that the program will execute in.

        "test" mode will not delete any files
        "delete" mode will delete duplicate files
    :return:
    """
    parser = ArgumentParser()
    parser.add_argument("-b", "--base-dir", type=str, required=True)
    parser.add_argument("-m", "--mode", choices=[e.value for e in Mode], default="test")
    return parser.parse_args()


def get_sub_dirs(base_dir: str):
    """
    Recursively walk through the base directory. If the subdirectory does not contain any other directories, it is the
    lowest-level directory, so add it to the list.
    :param base_dir: The base directory.
    :return: The list of lowest-level subdirectories.
    """
    sub_dirs = list()
    for root, dirs, files in os.walk(base_dir, topdown=True):
        dirs[:] = [d for d in dirs if d not in EXCLUDE]

        if not dirs:
            sub_dirs.append(root)
    return sub_dirs


def get_files(sub_dir: str) -> List:
    """
    Get all files in the subdirectory.
    :param sub_dir: The subdirectory.
    :return: All files in the subdirectory.
    """
    return [f for f in os.listdir(sub_dir) if os.path.isfile(os.path.join(sub_dir, f))]


def find_duplicates(subdir: str, files: List) -> dict:
    """
    For each file in the subdirectory, search for duplicate files that have the same prefix (first six characters) and
    the same suffix (last four characters). Store files with the same prefix + suffix as a key, with the list of
    filenames as the value. Only return dictionary items with two or more files for a given key.
    :param subdir: The subdirectory.
    :param files: The files in the subdirectory.
    :return: A dictionary of duplicate files.
    """
    duplicates = dict()
    for file in files:
        filename = f"{subdir}/{file}"
        search_term = file[:6].lower() + file[-4:].lower()
        if search_term not in duplicates:
            duplicates[search_term] = [filename]
        else:
            duplicates[search_term].append(filename)
    return {k: v for k, v in duplicates.items() if len(v) >= 2}


def delete_duplicates(duplicates: dict) -> None:
    """
    If there are duplicates, sort the files in descending order by file size, keep the largest file, and remove all
    other files.
    :param duplicates: Dictionary of duplicate files.
    :return: None.
    """
    if duplicates:
        for files in duplicates.values():
            sorted_files = sorted(files, key=os.path.getsize, reverse=True)
            largest_file = sorted_files[0]
            file_size = get_file_size(largest_file)
            LOGGER.info(f"Keeping file: {largest_file}, file size: {file_size}GB")
            remove_smaller_files(sorted_files)


def get_file_size(filename) -> float:
    """
    Get the file size for a given filename in GB.
    :param filename: The filename.
    :return: The file size in GB.
    """
    return round(os.path.getsize(filename) / 1024**3, 3)


def remove_smaller_files(sorted_files: List) -> None:
    """
    Remove all files from the sorted list except the largest (first) file.
    :param sorted_files: The list of files sorted in descending order by file size.
    :return: None.
    """
    global _total_space_saved
    i = 1
    while i < len(sorted_files):
        filename = sorted_files[i]
        file_size = get_file_size(filename)
        LOGGER.debug(f"filename: {filename}, file size: {file_size}GB")
        remove_file(filename, file_size)
        _total_space_saved += file_size
        i += 1


def remove_file(filename: str, file_size: float) -> None:
    """
    Remove the file if the program is running in "delete" mode.
    :param filename: The file to remove.
    :param file_size: The file size in GB.
    :return: None.
    """
    if _mode == Mode.DELETE.value:
        LOGGER.info(f"Removing file: {filename}, file size: {file_size}GB")
        os.remove(filename)


def main():
    args = parse_args()
    global _mode
    _mode = args.mode
    base_dir = args.base_dir
    sub_dirs = get_sub_dirs(base_dir)

    for sub_dir in sub_dirs:
        files = get_files(sub_dir)
        duplicates = find_duplicates(sub_dir, files)
        delete_duplicates(duplicates)
    LOGGER.info(f"Total space saved: {round(_total_space_saved, 3)}GB")


if __name__ == "__main__":
    main()
