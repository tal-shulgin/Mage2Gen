try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

def readme():
    # Fallback if README.md is missing
    if os.path.exists('README.md'):
        with open('README.md') as f:
            return f.read()
    return "Mage2Gen 6.0"

import os

setup(
    name = 'Mage2Gen',
    packages = [
        'mage2gen', 
        'mage2gen.snippets', 
        'mage2gen.core', 
        'mage2gen.features'
    ],
    package_data={'mage2gen': ['templates/**/*.j2', 'licenses/*.txt']},
    version = '6.0.0',
    description = 'Magento 2 module generator (V6)',
    long_description=readme(),
    long_description_content_type='text/markdown',
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Code Generators',
    ],
    author = 'Maikel Martens',
    author_email = 'maikel@martens.me',
    license='GPL3',
    url = 'https://github.com/krukas/Mage2Gen',
    keywords = ['Magento', 'Magento2', 'module', 'generator', 'mage2gen', 'cli'],
    install_requires=[
            'Jinja2>=3.1.2',
            'typer>=0.9.0',
            'watchdog>=3.0.0',
            'PyYAML>=6.0',
            'gitingest>=0.3.1'
        ],
    entry_points={
        'console_scripts': [
            'mage2gen=mage2gen.app:app',
        ],
    },
)