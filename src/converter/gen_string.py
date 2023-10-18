
import os


def tagfile_md(tag_file):
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
    result += " " + tag.text + "\n"
    return result


# TODO: добавить распознавание заголовков
# TODO: добавить метки для источников (Panitch L., Gindin S. The Making of Global Capitalism - выходит и без источника и без меток)
def sourcefile_md(sourcefile, tagfiles):
    """
    Return the contents of a file formatted in .md
    """
    if "Panitch" in sourcefile.address:
        stuff = ""

    # header
    result = "---\ncssclass: sourcefile\n---"

    # the source
    for source in sourcefile.sources:
        result += _source_str(source, tagfiles)

    # every entry, separated by an empty line
    if sourcefile.entries:
        result += "\n"
    for entry in sourcefile.entries:
        result += _entry_str(entry, tagfiles)

    return result


def _source_str(source, tagfiles):
    result = ""

    text = source.text.strip(" \n")
    result += f"\n## {text}"

    # if the source has got tags, they're listed after it on separate lines
    for tag in source.tags:
        result += _tag_str(tag, tagfiles)
    return result


def _tag_str(tag, tagfiles):
    result = ""
    file = _find_tagfile_for_tag(tag, tagfiles)
    if file is not None:
        filename = _get_tagfilename(file)
        result += f"\n[[{filename}#{tag.text}]]"
    else:
        result += f"\n{tag.text}"
    return result


def _entry_str(entry, tagfiles):
    result = ""

    text = entry.text.strip(" \n")
    result += "\n\n" + text

    # if the entry has got tags, they're listed after it on separate lines
    for tag in entry.tags:
        result += _tag_str(tag, tagfiles)

    return result


def _find_tagfile_for_tag(tag, tagfiles):
    for tagfile in tagfiles:
        if tag in tagfile.tag_nest.tags:
            return tagfile
    return None


def _get_tagfilename(tagfile):
    filename = os.path.basename(tagfile.address)
    name = os.path.splitext(filename)[0]
    return name
