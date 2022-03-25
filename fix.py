import os
import sys
import re
from collections import defaultdict
from typing import List, Optional

from absl import flags

_PATH = flags.DEFINE_string("path", None, "Path to header.")
_ROOT = flags.DEFINE_string("root", None, "Root path to normalize against.")


def format_guard(header_path: str, root_path: str) -> str:
    """Formats a header guard symbol given a header path and the root directory.

    Args:
      header_path: Location of the header file.
      root_path: Root path (portion of `header_path` to omit from the guard).

    Returns:
      A screaming snake case string with a trailing underscore containing the
      truncated header path components.
    """
    print(header_path, root_path)
    if os.path.commonpath([header_path, root_path]) != root_path:
        raise ValueError("Header path does not include root path")

    header_subpath = os.path.relpath(header_path, root_path)

    transformed = re.sub(r'(\.|\/)', '_', header_subpath.upper()) + '_'
    stripped = re.sub('[^A-Z0-9_]', '', transformed)
    return stripped


def format_file(contents: str, guard: str) -> str:
    return (f'#ifndef {guard:s}\n#define {guard:s}\n\n{contents:s}\n'
            f'#endif  // {guard:s}\n')


def fix_file(contents: str, guard: str) -> str:
    ifndef_re = re.compile(r'^\s*#ifndef\s+(?P<expression>[^\s]*)\s*$')
    define_re = re.compile(r'^\s*#define\s+(?P<expression>[^\s]*)\s*$')
    endif_re = re.compile(r'^\s*#endif(\s*\/\/\s*(?P<expression>[^\s]*))?\s*$')

    symbols = defaultdict(lambda: 0)

    for line in contents.split('\n'):
        for r in [ifndef_re, define_re, endif_re]:
            m = r.match(line)
            if m and m.groupdict()['expression']:
                symbols[m.groupdict()['expression']] += 1

    if not symbols:
        return format_file(contents, guard)

    max_symbol_pair = (sorted(symbols.items(), key=(lambda x: x[1]))[-1])

    if max_symbol_pair[1] < 2:
        return format_file(contents, guard)

    return re.sub(max_symbol_pair[0], guard, contents)


def main():
    header = _PATH.value
    contents = open(header).read()
    open(header, 'w').write(
        fix_file(contents, format_guard(header, _ROOT.value)))


if __name__ == '__main__':
    flags.mark_flag_as_required(_PATH.name)
    flags.FLAGS(sys.argv)
    main()
