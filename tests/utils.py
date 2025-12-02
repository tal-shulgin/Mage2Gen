import json
import os
import random
import string
import shutil
from glob import glob

from subprocess import Popen, PIPE

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
PHPCS_PATH = os.path.join(os.path.dirname(BASE_PATH), 'phpcs.phar')


def tmp_path():
    return 'tmp_{}'.format(
        ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
    )


class CodeSniffer:
    class CodeStyleException(Exception):
        def __init__(self, message):
            self.message = message

    @staticmethod
    def cleanup():
        for path in glob(os.path.join(BASE_PATH, 'tmp_*')):
            shutil.rmtree(path)

    @staticmethod
    def generate_and_test(module, *args):
        path = os.path.join(BASE_PATH, tmp_path())

        os.mkdir(path)
        module.generate_module(path)

        results = CodeSniffer(path).test(path, *args)
        CodeSniffer.cleanup()

        return results

    def __init__(self, path):
        self.path = path

    @staticmethod
    def execute(*args):
        # Use php explicitly
        command = ['php', PHPCS_PATH]
        for arg in args:
            command.append(arg)

        process = Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        return stdout, stderr

    @staticmethod
    def test(*args):
        # Run phpcs with JSON report
        json_encoded, stderr = CodeSniffer.execute('--report=json', '--standard=PSR12', *args)

        # Debugging: Print raw output if decoding fails
        try:
            output = json.loads(json_encoded.decode())
        except json.decoder.JSONDecodeError as e:
            print("\n\n--- PHPCS FAILED TO OUTPUT JSON ---")
            print("STDOUT:", json_encoded.decode())
            print("STDERR:", stderr.decode())
            print("-----------------------------------\n")
            raise e

        total_errors = output.get('totals', {}).get('errors', 0)
        if total_errors:
            exception_message = "\n"
            for file_name, file in output.get('files', {}).items():
                
                file_errors = ""
                for message in file.get('messages', []):
                    if message['type'] == 'ERROR':
                        file_errors += "{message[line]: <5} {message[message]}\n".format(message=message)
                
                if file_errors:
                    exception_message += "FILE: {}\n".format(file_name)
                    exception_message += file_errors
                    exception_message += "\n"
            raise CodeSniffer.CodeStyleException(exception_message)

        return True
