from distutils.core import setup
from setuptools import find_packages

"""
setup is the main function that describes all the package
"""
setup(
    name='rustress',
    packages=find_packages(exclude=['stressdb.json', 'stressdb.zip', 'Model_creation.h5']),
    version='1.0',
    description='A tiny module for offline stress detection in russian words.',
    author='aishutin',
    author_email='hazmozavr@gmail.com',
    url='https://github.com/aishutin/rustress',
    download_url='https://github.com/aishutin/rustress/archive/1.0.tar.gz',
    keywords=['ru', 'stress', 'rustress', 'poetry', 'linguistic', 'python'],
    scripts=[],
    install_requires=['requests', 'bs4', 'pymorphy2', 'tensorflow', 'keras']
)