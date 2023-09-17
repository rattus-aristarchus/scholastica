import os
import pytest

from conftest import TAGFILE_PATH, RESOURCES_DIR, STUFF_PATH, BACKUP_DIR, NEW_TAGFILE_PATH
from storage.tagfile import SourcePaths, TagFile
from storage.sourcefile import SourceFile
from data.base_types import Tag
import storage.tagfile as tagfile


@pytest.fixture
def source_paths():
    output = SourcePaths(RESOURCES_DIR)
    return output


@pytest.fixture
def source_file():
    output = SourceFile(STUFF_PATH, BACKUP_DIR)
    output.tags.append(Tag("qa"))
    return output


@pytest.fixture
def tag_file(source_file):
    output = TagFile(NEW_TAGFILE_PATH)
    open(NEW_TAGFILE_PATH, 'w').close()
    output.add_file(source_file)

    yield output

    if os.path.exists(NEW_TAGFILE_PATH):
        os.remove(NEW_TAGFILE_PATH)


def test_sourcepaths(source_paths, source_file):
    source_paths.add(source_file)
    assert source_paths.relpaths[source_file] == "notes/pytest/stuff.txt"
    source_paths.remove(source_file)
    assert len(source_paths.relpaths) == 0

    #scla_path = os.path.join(RESOURCES_DIR, "test.scla")
   #with open(scla_path, "r"):
    #    print("okay, i've opened the file")


def test_read():
    result, messages = tagfile.read(TAGFILE_PATH)
    print("\n")
    for message in messages:
        print(message)
    assert list(result.source_paths.relpaths.values())[0] == "notes/pytest/stuff.txt"


def test_write(tag_file):
    tagfile.write(tag_file)
    read, messages = tagfile.read(NEW_TAGFILE_PATH)
    print("\n")
    for message in messages:
        print(message)
    assert list(read.source_paths.relpaths.values())[0] == "notes/pytest/stuff.txt"
