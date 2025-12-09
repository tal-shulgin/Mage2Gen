import unittest

try:
    from typer.testing import CliRunner
    from mage2gen.app import app
    HAS_TYPER = True
except ImportError:
    HAS_TYPER = False

class TestCli(unittest.TestCase):

    def setUp(self):
        if not HAS_TYPER:
            self.skipTest("Typer not installed")
        self.runner = CliRunner()

    def test_hello(self):
        result = self.runner.invoke(app, ["hello", "World"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Hello World", result.stdout)

    def test_module_command(self):
        result = self.runner.invoke(app, ["module", "--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Create a new Magento 2 module", result.stdout)

    def test_observer_command(self):
        result = self.runner.invoke(app, ["observer", "--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Create an Observer", result.stdout)

if __name__ == '__main__':
    unittest.main()