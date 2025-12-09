import unittest
import os

from mage2gen import Module
from mage2gen.snippets import InstallSnippet
from tests import utils


class TestSnippetInstall(unittest.TestCase):

    def test_snippet(self):
        module = Module(package='Package', name='Name', description='Description')
        snippet = InstallSnippet(module)
        
        # Updated to provide the required 'patch_name' argument
        sample_output = snippet.add(patch_name='InitialData')

        result = utils.CodeSniffer.generate_and_test(module)
        self.assertTrue(result)

    def tearDown(self):
        utils.CodeSniffer.cleanup()
