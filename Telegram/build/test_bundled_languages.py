import json
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


class BundledLanguagesTest(unittest.TestCase):
    def test_every_bundle_is_valid_and_registered(self):
        resources = Path(__file__).resolve().parents[1] / "Resources"
        qrc = resources / "qrc/telegram/telegram.qrc"
        registered = {
            entry.attrib["alias"]: (qrc.parent / entry.text).resolve()
            for group in ET.parse(qrc).getroot()
            if group.attrib.get("prefix") == "/ayu/languages"
            for entry in group
        }
        bundled = {path.name: path.resolve() for path in (resources / "ayu/languages").glob("*.json")}
        self.assertTrue(bundled)
        self.assertEqual(registered, bundled)
        for name, path in bundled.items():
            with self.subTest(language=name):
                data = json.loads(path.read_text())
                self.assertIsInstance(data, dict)
                self.assertTrue(data)
                self.assertTrue(all(isinstance(value, str) for value in data.values()))
