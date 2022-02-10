from distutils.core import setup
from setuptools import find_packages
import pathlib

# The directory containing this file
HERE = pathlib.Path(__file__).parent
# The text of the README file
README = (HERE / "README.md").read_text()

"""
setup is the main function that describes all the package
"""

version = "1.3.11"

setup(
    name='rustress',
    packages=['rustress'],
    version=version,
    description='A tiny module for offline stress detection in russian words.',
    author='aishutin',
    long_description=README,
    long_description_content_type="text/markdown",
    author_email='hazmozavr@gmail.com',
    url='https://github.com/aishutin/rustress',
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
    ],
    download_url='https://github.com/aishutin/rustress/archive/{}.tar.gz'.format(version),
    keywords=['ru', 'stress', 'rustress', 'poetry', 'linguistic', 'python'],
    data_files=['rustress/back.json', 'rustress/c2id.json', 'rustress/model.h5'],
    include_package_data=True,
    install_requires=['pymorphy2==0.8', 'tensorflow==2.5.3', 'keras==2.2.4']
)