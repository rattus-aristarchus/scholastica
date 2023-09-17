import os
import pytest

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESOURCES_DIR = os.path.join(BASE_DIR, 'resources')
TAGFILE_PATH = os.path.join(RESOURCES_DIR, 'test.scla')
NEW_TAGFILE_PATH = os.path.join(RESOURCES_DIR, 'test1.scla')
STUFF_PATH = os.path.join(RESOURCES_DIR, 'notes', 'pytest', 'stuff.txt')
BACKUP_DIR = os.path.join(BASE_DIR, '.backup')
