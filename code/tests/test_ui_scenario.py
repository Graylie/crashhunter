import unittest
import xml.etree.ElementTree as ET

from code.src.crash_hunter.ui_scenario import center, match_node


class ScenarioSelectorTests(unittest.TestCase):
    def test_combined_selector_avoids_wrong_settings_label(self):
        root = ET.fromstring('<hierarchy><node text="Server" resource-id="title" enabled="true" bounds="[2,4][10,20]"/><node text="Server" resource-id="editor" enabled="true"/></hierarchy>')
        node = match_node(root, {"text": "Server", "resource-id": "title"})
        self.assertEqual(center(node), (6, 12))
        with self.assertRaises(RuntimeError):
            match_node(root, {"text": "Server"})

    def test_missing_control_does_not_trigger_arbitrary_tap(self):
        root = ET.fromstring('<hierarchy><node text="OK" enabled="false"/></hierarchy>')
        self.assertIsNone(match_node(root, {"text": "OK"}))
        with self.assertRaises(RuntimeError):
            center(ET.fromstring('<node bounds="[1,1][1,1]"/>'))


if __name__ == "__main__":
    unittest.main()
