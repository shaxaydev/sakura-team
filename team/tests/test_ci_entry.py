"""Check the security boundary of the forced SSH command without a server."""
import os
from pathlib import Path
import subprocess
import unittest


ENTRY = Path(__file__).parents[1] / "deploy" / "ci-entry.sh"


class RestrictedCommandTests(unittest.TestCase):
    def test_unrelated_commands_are_rejected_before_registry_access(self):
        for command in ("", "bash", "deploy main", "deploy " + "a" * 39, "deploy " + "a" * 41,
                        "deploy " + "a" * 40 + "; id", "deploy " + "a" * 40 + "\nwhoami",
                        "deploy " + "A" * 40):
            with self.subTest(command=command):
                result = subprocess.run(
                    ["bash", str(ENTRY)], input="", capture_output=True, text=True,
                    env={**os.environ, "SSH_ORIGINAL_COMMAND": command}, timeout=5,
                )
                self.assertEqual(result.returncode, 64)
                self.assertIn("Only deploy", result.stderr)


if __name__ == "__main__":
    unittest.main()
