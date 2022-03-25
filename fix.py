import os
import sys
import re
from typing import List, Optional

from absl import flags

_PATH = flags.DEFINE_string(
    "path", None,
    "Path to find headers in. Also used as the root path to normalize guards "
    "against.")


def format_guard(header_path: str, root_path: str) -> str:
    """Formats a header guard symbol given a header path and the root directory.

    Args:
      header_path: Location of the header file.
      root_path: Root path (portion of `header_path` to omit from the guard).

    Returns:
      A screaming snake case string with a trailing underscore containing the
      truncated header path components.
    """
    if os.path.commonpath([header_path, root_path]) != root_path:
        raise ValueError("Header path does not include root path")

    header_subpath = os.path.relpath(header_path, root_path)

    transformed = re.sub(r'(\.|\/)', '_', header_subpath.upper()) + '_'
    stripped = re.sub('[^A-Z0-9_]', '', transformed)
    return stripped


def get_headers(root_dir: str) -> List[str]:
    header_re = re.compile(r'.*\.h$')
    files: List[str] = []
    for file in os.listdir(root_dir):
        print(file)
        if os.path.isdir(file):
            files.extend(get_headers(file))
        elif header_re.fullmatch(file):
            files.append(file)
    return files


def fix_file(contents: str, guard: str) -> str:
    state = 0

    ifndef_re = re.compile(r'^\s*#ifndef (?P<expression>[^\s]*)\s*$')
    define_re = re.compile(r'^\s*#define (?P<expression>[^\s]*)\s*$')
    endif_re = re.compile(r'^\s*#endif(\s*\/\/\s*(?P<expression>[^\s]*))?\s*$')

    before_guard: List[str] = []
    between_guard: List[str] = []
    after_guard: List[str] = []

    expression: Optional[str] = None

    for line in contents.split('\n'):
        if state == 0:
            m = ifndef_re.match(line)
            if not m:
                before_guard.append(line)
                continue
            expression = m.groupdict()['expression']
            state = 1
            continue

        if state == 1:
            m = define_re.match(line)
            if not m:
                return contents
            if expression != m.groupdict()['expression']:
                return contents
            state = 2
            continue

        if state == 2:
            m = endif_re.match(line)
            if not m:
                between_guard.append(line)
                continue
            endif_expression = m.groupdict()['expression']
            if endif_expression and endif_expression != expression:
                return contents
            state = 3
            continue

        if state == 3:
            after_guard.append(line)
            continue

    if 0 < state and state < 3:
        return contents

    before = '\n'.join(before_guard).strip()
    if before:
        before = before + '\n'

    between = '\n'.join(between_guard).strip()

    after = '\n'.join(after_guard).strip()
    if after:
        after = '\n' + after

    print(before, between, after)

    if state > 0:
      return (
          f'{before:s}#ifndef {guard:s}\n#define {guard:s}\n\n{between:s}\n\n#endif  // {guard:s}{after:s}\n'
      )

    return (
        f'#ifndef {guard:s}\n#define {guard:s}\n\n{before:s}\n\n#endif  // {guard:s}\n'
    )


def main():
    headers = get_headers(_PATH.value)


if __name__ == '__main__':
    flags.mark_flag_as_required(_PATH.name)
    flags.FLAGS(sys.argv)
    main()
