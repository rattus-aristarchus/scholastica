import os
import yaml
import sys

import storage.tagfile as tagfile
import storage.storage as storage
from storage.sourcefile import SourceFile
from util import DOCS_DIR


def convert_tagfile(tagfile, output_path):
    output = get_md_tagfile(tagfile)
    storage.write_safe(output_path, output)


def convert_sourcefile(sourcefile, output_path, tagfile):
    sourcefile.read_sources(tagfile)
    sourcefile.read(tagfile)
    output = get_md_sourcefile(sourcefile, [tagfile])
    storage.write_safe(output_path, output)


def get_md_tagfile(tag_file):
    """
    Write a linked structure of tags with their contents as a file.
    """
    output = "---\ncssclass: tagfile\n---"
    level = 1
    written_tags = []

    if tag_file.tag_nest.roots:
        output += "\n\n"

    # Traverse the roots; for each of them call a recursive function to get
    # their string representation
    for root in tag_file.tag_nest.roots:
        output += _tag_to_string_deep(root,
                                      level,
                                      written_tags,
                                      tag_file)

    return output


# TODO: добавить распознавание заголовков
def get_md_sourcefile(sourcefile, tagfiles):
    result = "---\ncssclass: sourcefile\n---"

    if sourcefile.sources:
        result += "\n"
    for source in sourcefile.sources:
        result += f"\n## {source.text}"

    if sourcefile.entries:
        result += "\n"
    for entry in sourcefile.entries:
        if entry.text[-1] == "\n":
            text = entry.text[:-1]
        else:
            text = entry.text

        result += "\n\n" + text

        for tag in entry.tags:
            file = find_tagfile_for_tag(tag, tagfiles)
            link = tag.text.replace(" ", "-")
            if file is not None:
                filename = get_tagfilename(file)
                result += f"\n[[{filename}#{link}]]"
            else:
                result += f"\n{link}"
    return result


def find_tagfile_for_tag(tag, tagfiles):
    for tagfile in tagfiles:
        if tag in tagfile.tag_nest.tags:
            return tagfile
    return None


def get_tagfilename(tagfile):
    filename = os.path.basename(tagfile.address)
    name = os.path.splitext(filename)[0]
    return name


def _tag_to_string_deep(tag, level, written_tags, tag_file):
    """
    Returns the string representation of a tag, its content and its children
    """
    # First, the tag itself
    result = _tag_to_string(tag, level)

    # Then, its content and children, recursively - unless they've already been
    # written down elsewhere in the file
    if tag not in written_tags:
        written_tags.append(tag)
        for child in tag.children:
            result += _tag_to_string_deep(child,
                                          level + 1,
                                          written_tags,
                                          tag_file)
    return result


def _tag_to_string(tag, level):
    """
    Returns the string representation of a tag
    """
    result = ""
    for i in range(level):
        result += "#"
    text = tag.text.replace(" ", "-")
    result += " " + text + "\n"
    return result


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


run()


"""
if len(sys.argv) > 1:
    tagfile_path = sys.argv[1]
else:
    print("file not supplied")
"""
