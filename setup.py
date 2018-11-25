from distutils.core import setup
from setuptools import find_packages

"""
setup is the main function that describes all the package
"""
setup(
    name='rustress',
    packages=find_packages(exclude=['stressdb.json', 'stressdb.zip', 'Model_creation.h5']),
    version='1.1',
    description='A tiny module for offline stress detection in russian words.',
    author='aishutin',
    author_email='hazmozavr@gmail.com',
    url='https://github.com/aishutin/rustress',
    download_url='https://github.com/aishutin/rustress/archive/1.1.tar.gz',
    keywords=['ru', 'stress', 'rustress', 'poetry', 'linguistic', 'python'],
    scripts=[],
    install_requires=['requests==2.20.1', 'bs4==0.0.1', 'pymorphy2==0.8', 'tensorflow==1.12.0', 'keras==2.2.4']
)