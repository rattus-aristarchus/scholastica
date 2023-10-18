import os
import yaml
import shutil

from kivy.logger import Logger, LOG_LEVELS

import storage.tagfile as tagfile
import storage.storage as storage
from storage.sourcefile import SourceFile
from util import DOCS_DIR
import converter.gen_string as gen_string


def convert_tagfile(tagfile, output_path):
    Logger.info(f"Converting file {tagfile.address}")

    output = gen_string.tagfile_md(tagfile)
    storage.write_safe(output_path, output)


def convert_sourcefile(sourcefile, output_path, tagfile):
    Logger.info(f"Converting file {sourcefile.address}")

    sourcefile.read_sources(tagfile)
    sourcefile.read(tagfile)
    output = gen_string.sourcefile_md(sourcefile, [tagfile])
    storage.write_safe(output_path, output)


def get_md_name(old_name):
    no_ext = os.path.splitext(old_name)[0]
    return no_ext + ".md"


def read(tagfile_path, source_dirs):
    t_file, messages = tagfile.read(tagfile_path)
    sourcefiles = []
    other_stuff = []

    for source_dir in source_dirs:
        for address, dirs, files in os.walk(source_dir):
            if has_dot(address):
                Logger.info(f"Skipping dir {address}")
                continue

            for filename in files:
                if starts_with_dot(filename):
                    Logger.info(f"Skipping file {filename}")
                    continue

                source_path = os.path.join(address, filename)
                ext = os.path.splitext(filename)[1]
                if ext not in [".txt", ".md", ""]:
                    other_stuff.append(source_path)
                    continue

                s_file = SourceFile(source_path, t_file.backup_location)
                sourcefiles.append(s_file)

    return t_file, sourcefiles, other_stuff


def starts_with_dot(address):
    if os.path.isdir(address):
        name = os.path.basename(os.path.normpath(address))
    else:
        name = os.path.split(address)[1]
    if len(name) > 0 and name[0] == ".":
        return True
    else:
        return False


def has_dot(address):
    normalized = os.path.normpath(address)
    parts = normalized.split(os.sep)
    for part in parts:
        if len(part) > 0 and part[0] == ".":
            return True
    return False


def write(tagfile, sourcefiles, stuff, output_dir):
    convert_tagfile(tagfile, t_path(tagfile, output_dir))

    for sourcefile in sourcefiles:
        source_dir = os.path.join(output_dir, "выписки")
        dir = new_dir(sourcefile.address,
                      tagfile.address,
                      source_dir)
        if not os.path.exists(dir):
            os.makedirs(dir)
        path = new_path(sourcefile.address, dir)
        md_path = get_md_name(path)
        convert_sourcefile(sourcefile, md_path, tagfile)

    for address in stuff:
        stuff_dir = os.path.join(output_dir, "не-текст")
        dir = new_dir(address,
                      tagfile.address,
                      stuff_dir)
        if not os.path.exists(dir):
            os.makedirs(dir)
        path = new_path(address, dir)
        shutil.copy(address, path)


def t_path(tagfile, output_dir):
    tagfile_name = os.path.basename(tagfile.address)
    tagfile_new_path = os.path.join(output_dir, tagfile_name)
    tagfile_new_path = get_md_name(tagfile_new_path)
    return tagfile_new_path


def new_dir(old_path, tagfile_path, output_dir):
    tagfile_dir = os.path.dirname(tagfile_path)
    rel_path = os.path.relpath(old_path, tagfile_dir)
    rel_dir = os.path.dirname(rel_path)
    new_dir = os.path.join(output_dir, rel_dir)
    return new_dir


def new_path(address, output_dir):
    name = os.path.basename(address)
    result = os.path.join(output_dir, name)
    return result


class Converter:

    def __init__(self, load_what):
        """
        load_what - which combination of files from convert.yml to load
        """
        self.load_what = load_what

    def run(self):
        yaml_path = os.path.join(DOCS_DIR, "convert.yml")
        paths = yaml.safe_load(open(yaml_path, "r", encoding="utf-8"))[self.load_what]

        if not os.path.exists(paths["output"]):
            os.makedirs(paths["output"])

        t_file, s_files, stuff = read(paths["tagfile"], paths["sourcefiles"])
        write(t_file, s_files, stuff, paths["output"])
