try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

def readme():
	with open('README.rst') as f:
		return f.read()

setup(
    name = 'Mage2Gen',
    packages = ['mage2gen', 'mage2gen.snippets', 'mage2gen.core'],
    package_data={'mage2gen': ['templates/**/*.j2', 'templates/**/*.tmpl', 'licenses/*.txt']},
    scripts=['bin/mage2gen'],
    version = '3.0.0',
    description = 'Magento 2 module generator',
	long_description=readme(),
	classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Code Generators',
      ],
	author = 'Maikel Martens',
	author_email = 'maikel@martens.me',
	license='GPL3',
	url = 'https://github.com/krukas/Mage2Gen',
	download_url = 'https://github.com/krukas/Mage2Gen/releases/tag/2.3.3',
	keywords = ['Magento', 'Magento2', 'module', 'generator', 'mage2gen'],
	install_requires=[
        'Jinja2>=3.1.2',
        'typer>=0.9.0'
    ],
)
