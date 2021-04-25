import sys
import pytest
import unittest

sys.path.append("../")

from plugins.lookup.auto_absent import LookupModule


class MyTestCase(unittest.TestCase):
    def test_auto_absent(self):

        exp = [
            {
                "data": [
                    {"name": "foo", "state": "present"},
                    {"name": "bar", "state": "absent"},
                ]
            }
        ]

        r = LookupModule.run(
            "",
            "",
            "",
            new="new.yml",
            old="old.yml",
        )

        assert r == exp

        with self.assertRaises(Exception) as context:
            f = LookupModule.run(
                "",
                "",
                "",
                new="neww.yml",
                old="old.yml",
            )

        self.assertTrue(
            "No such file or directory: 'neww.yml'" in str(context.exception)
        )

        with self.assertRaises(Exception) as context:
            f = LookupModule.run(
                "",
                "",
                "",
                new="new.yml",
                old="oldd.yml",
            )

        self.assertTrue(
            "No such file or directory: 'oldd.yml'" in str(context.exception)
        )


if __name__ == "__main__":
    unittest.main()
