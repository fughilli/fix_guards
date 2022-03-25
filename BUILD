load("@py_deps//:requirements.bzl", "requirement")

py_binary(
    name = "fix",
    srcs = ["fix.py"],
    python_version = "PY3",
    deps = [
        requirement("absl-py"),
    ],
)

py_test(
    name = "fix_test",
    srcs = ["fix_test.py"],
    deps = [
        ":fix",
        requirement("parameterized"),
    ],
)
