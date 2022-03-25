import unittest
import parameterized
from fix_guards import fix

TEST_FILE_CONTENTS = ("""#ifndef FOO_H_
#define FOO_H_

some
file
contents

#endif  // FOO_H_
""")

TEST_FILE_CONTENTS_MALFORMED_1 = ("""#ifndef FOO_H_
#define FOO_H_

some
file
contents

#endif//FOO_H_
""")

TEST_FILE_CONTENTS_MALFORMED_2 = ("""#ifndef FOO_H_
#define FOO_H_

some
file
contents

#endif
""")

TEST_FILE_CONTENTS_MALFORMED_3 = ("""
some
file
contents
""")

TEST_FILE_CONTENTS_MALFORMED_4 = ("""#ifndef SOME_OTHER_TEST

some
file
contents

#endif
""")

EXPECTED_TEST_FILE_CONTENTS_4 = ("""#ifndef FOO_H_
#define FOO_H_

#ifndef SOME_OTHER_TEST

some
file
contents

#endif

#endif  // FOO_H_
""")


class TestFix(unittest.TestCase):
    @parameterized.parameterized.expand([
        ("foo/bar/baz/bux.h", "foo", "BAR_BAZ_BUX_H_"),
        ("foo/bar/baz/bux.h", "foo/bar", "BAZ_BUX_H_"),
        ("this/is/a_file/with_some_underscores.h", "",
         "THIS_IS_A_FILE_WITH_SOME_UNDERSCORES_H_"),
        ("maybe_99_words.h", "", "MAYBE_99_WORDS_H_"),
        ("path/containing/speી°cial/characters.h", "",
         "PATH_CONTAINING_SPECIAL_CHARACTERS_H_"),
    ])
    def test_format_guard(self, header_path, root_path, expected_guard):
        guard = fix.format_guard(header_path, root_path)
        self.assertEqual(guard, expected_guard)

    def test_format_guard_not_common_path_raises_exception(self):
        with self.assertRaisesRegex(ValueError, "does not include root"):
            fix.format_guard("a/b/c", "d/e/f")

    @parameterized.parameterized.expand([
        (TEST_FILE_CONTENTS_MALFORMED_1, "FOO_H_", TEST_FILE_CONTENTS),
        (TEST_FILE_CONTENTS_MALFORMED_2, "FOO_H_", TEST_FILE_CONTENTS),
        (TEST_FILE_CONTENTS_MALFORMED_3, "FOO_H_", TEST_FILE_CONTENTS),
        (TEST_FILE_CONTENTS_MALFORMED_4, "FOO_H_",
         EXPECTED_TEST_FILE_CONTENTS_4),
    ])
    def test_format_guard(self, contents, guard, expected_contents):
        self.assertEqual(fix.fix_file(contents, guard), expected_contents)

    def test_format_guard_not_common_path_raises_exception(self):
        with self.assertRaisesRegex(ValueError, "does not include root"):
            fix.format_guard("a/b/c", "d/e/f")


if __name__ == '__main__':
    unittest.main()
