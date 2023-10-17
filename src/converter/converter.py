import os
import yaml

import storage.tagfile as tagfile
import storage.storage as storage
from storage.sourcefile import SourceFile
from util import DOCS_DIR
import gen_string


def convert_tagfile(tagfile, output_path):
    output = gen_string.tagfile_md(tagfile)
    storage.write_safe(output_path, output)


def convert_sourcefile(sourcefile, output_path, tagfile):
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

    for source_dir in source_dirs:
        for address, dirs, files in os.walk(source_dir):
            for filename in files:
                if not os.path.splitext(filename)[1] == ".scla":
                    source_path = os.path.join(address, filename)
                    s_file = SourceFile(source_path, t_file.backup_location)
                    sourcefiles.append(s_file)

    return t_file, sourcefiles


def write(tagfile, sourcefiles, output_dir):
    tagfile_name = os.path.basename(tagfile.address)
    tagfile_new_path = os.path.join(output_dir, tagfile_name)
    tagfile_new_path = get_md_name(tagfile_new_path)
    convert_tagfile(tagfile, tagfile_new_path)

    for sourcefile in sourcefiles:
        sourcefile_name = os.path.basename(sourcefile.address)
        sourcefile_dir = os.path.dirname(sourcefile.address)
        just_dir = os.path.split(sourcefile_dir)[1]
        new_dir = os.path.join(output_dir, just_dir)
        if not os.path.exists(new_dir):
            os.makedirs(new_dir)
        sourcefile_new_path = os.path.join(output_dir, just_dir, sourcefile_name)
        sourcefile_new_path = get_md_name(sourcefile_new_path)
        convert_sourcefile(sourcefile, sourcefile_new_path, tagfile)


def run():
    yaml_path = os.path.join(DOCS_DIR, "convert.yml")
    paths = yaml.safe_load(open(yaml_path, "r", encoding="utf-8"))[0]

    if not os.path.exists(paths["output"]):
        os.makedirs(paths["output"])

    t_file, s_files = read(paths["tagfile"], paths["sourcefiles"])
    write(t_file, s_files, paths["output"])
