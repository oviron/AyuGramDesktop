import tempfile
import unittest
from pathlib import Path

from ninja_log_stats import human, main, markdown_report, parse_log, summarize, target_of, text_report

LOG = """# ninja log v5
0\t1000\t0\tTelegram/CMakeFiles/Telegram.dir/SourceFiles/main.cpp.o\taaaa
1000\t4000\t0\tTelegram/CMakeFiles/Telegram.dir/SourceFiles/apiwrap.cpp.o\tbbbb
0\t500\t0\tTelegram/lib_ui/CMakeFiles/lib_ui.dir/ui/rp_widget.cpp.o\tcccc
"""


class ParseTest(unittest.TestCase):
    def test_reads_every_edge(self):
        self.assertEqual(len(parse_log(LOG)), 3)

    def test_skips_comments_and_short_lines(self):
        self.assertEqual(parse_log("# ninja log v5\nnot\ta\tlog\n"), {})

    def test_last_entry_of_a_rebuilt_output_wins(self):
        repeated = LOG + "9000\t9100\t0\tTelegram/CMakeFiles/Telegram.dir/SourceFiles/main.cpp.o\taaaa\n"
        self.assertEqual(parse_log(repeated)["Telegram/CMakeFiles/Telegram.dir/SourceFiles/main.cpp.o"], (9000, 9100))

    def test_negative_duration_ignored(self):
        self.assertEqual(parse_log("# ninja log v5\n500\t100\t0\tout.o\tdddd\n"), {})


class TargetTest(unittest.TestCase):
    def test_cmake_target_directory(self):
        self.assertEqual(target_of("Telegram/lib_ui/CMakeFiles/lib_ui.dir/ui/rp_widget.cpp.o"), "lib_ui")

    def test_output_without_target_directory(self):
        self.assertEqual(target_of("cmake_install.cmake"), "cmake_install.cmake")

    def test_windows_separators(self):
        self.assertEqual(target_of("Telegram\\CMakeFiles\\Telegram.dir\\Release\\main.cpp.obj"), "Telegram")

    def test_windows_absolute_path(self):
        output = "D:/a/AyuGramDesktop/TBuild/out/Telegram/CMakeFiles\\Telegram.dir\\Release\\main.cpp.obj"
        self.assertEqual(target_of(output), "Telegram")

    def test_absolute_path_without_target_directory(self):
        self.assertEqual(target_of("D:/a/TBuild/out/Release/AyuGram.exe"), "Release")


class SummaryTest(unittest.TestCase):
    def setUp(self):
        self.stats = summarize(parse_log(LOG))

    def test_totals(self):
        self.assertEqual(self.stats["edges"], 3)
        self.assertEqual(self.stats["work"], 4500)
        self.assertEqual(self.stats["span"], 4000)
        self.assertAlmostEqual(self.stats["parallelism"], 1.125)

    def test_slowest_edge_first(self):
        self.assertEqual(self.stats["slowest"][0][1], "Telegram/CMakeFiles/Telegram.dir/SourceFiles/apiwrap.cpp.o")

    def test_targets_are_aggregated(self):
        self.assertEqual(self.stats["targets"][0], (4000, 2, "Telegram"))

    def test_top_limits_both_tables(self):
        limited = summarize(parse_log(LOG), top=1)
        self.assertEqual(len(limited["slowest"]), 1)
        self.assertEqual(len(limited["targets"]), 1)


class FormatTest(unittest.TestCase):
    def test_human(self):
        self.assertEqual(human(1500), "1.5s")
        self.assertEqual(human(95000), "1m 35s")
        self.assertEqual(human(3725000), "1h 02m 05s")

    def test_reports_mention_the_title_and_targets(self):
        stats = summarize(parse_log(LOG))
        self.assertIn("macOS arm64", text_report(stats, "macOS arm64"))
        self.assertIn("| `Telegram` | 2 |", markdown_report(stats, "macOS arm64"))


class MainTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name)

    def test_missing_log_is_not_an_error(self):
        self.assertEqual(main([str(self.path / "absent"), "--title", "Build"]), 0)

    def test_markdown_is_appended(self):
        log = self.path / ".ninja_log"
        log.write_text(LOG)
        summary = self.path / "summary.md"
        summary.write_text("before\n")
        self.assertEqual(main([str(log), "--markdown-file", str(summary)]), 0)
        self.assertTrue(summary.read_text().startswith("before\n### Build"))

    def test_empty_log_is_not_an_error(self):
        log = self.path / ".ninja_log"
        log.write_text("# ninja log v5\n")
        self.assertEqual(main([str(log)]), 0)


if __name__ == "__main__":
    unittest.main()
