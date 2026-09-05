import json
import tempfile
import unittest
from pathlib import Path

from check_macos_release import check


class ReleaseCheckTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.build = Path(self.directory.name)
        (self.build / "build.ninja").write_text("libQt6Widgets.a")
        self.command = {
            "file": "/src/Telegram/SourceFiles/core/application.cpp",
            "command": "clang++ -O3 -DNDEBUG -arch arm64 -c application.cpp",
        }

    def run_check(self, architectures=("arm64",)):
        (self.build / "compile_commands.json").write_text(json.dumps([self.command]))
        check(self.build, architectures)

    def test_release(self):
        self.run_check()

    def test_debug_optimization_rejected(self):
        self.command["command"] += " -O0"
        with self.assertRaises(ValueError):
            self.run_check()

    def test_debug_defines_rejected(self):
        self.command["command"] += " -D_DEBUG"
        with self.assertRaises(ValueError):
            self.run_check()

    def test_intel_rejected(self):
        self.command["command"] = self.command["command"].replace("arm64", "x86_64")
        with self.assertRaises(ValueError):
            self.run_check()

    def test_debug_qt_rejected(self):
        (self.build / "build.ninja").write_text("libQt6Widgets_debug.a")
        with self.assertRaises(ValueError):
            self.run_check()

    def test_each_target(self):
        for architectures in (("x86_64",), ("x86_64", "arm64")):
            with self.subTest(architectures=architectures):
                self.command["command"] = "clang++ -O3 -DNDEBUG " + " ".join("-arch " + arch for arch in architectures)
                self.run_check(architectures)

    def test_extra_architecture_rejected(self):
        self.command["command"] += " -arch x86_64"
        with self.assertRaises(ValueError):
            self.run_check()

    def test_debug_define_with_value_rejected(self):
        self.command["command"] += " -D_DEBUG=1"
        with self.assertRaises(ValueError):
            self.run_check()

    def test_undefined_ndebug_rejected(self):
        self.command["command"] += " -UNDEBUG"
        with self.assertRaises(ValueError):
            self.run_check()

if __name__ == "__main__":
    unittest.main()
