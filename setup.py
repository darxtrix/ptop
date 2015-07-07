from setuptools import setup
from ptop import __version__

setup(
    name='ptop',
    version=__version__,
    description='A task manager written in Python',
    long_description=open('README.md').read(),
    keywords='top ptop task manager python',
    author='Ankush Sharma',
    author_email='ankprashar@gmail.com',
    url='https://github.com/black-perl/ptop',
    license='MIT',
    download_url= 'https://github.com/black-perl/ptop/tarball/0.0.6',
    packages=['ptop', 'ptop.core', 'ptop.plugins', 'ptop.interfaces','ptop.statistics','ptop.utils'],
    install_requires=[
        "npyscreen>=4.9.1",
        "psutil>=3.0.1",
        "argparse>=1.2.1",
        "drawille>=0.0.4"
    ],
    entry_points={
        'console_scripts': ['ptop = ptop.main:main']
    },

)