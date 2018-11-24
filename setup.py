from setuptools import setup
from ptop import __version__

setup(
    name='ptop',

    version=__version__,

    description='A task manager written in Python',

    long_description=open('README.md').read(),

    keywords='top ptop task manager python',

     # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 5 - Production/Stable',

        # Indicate who your project is intended for
        'Intended Audience :: Information Technology',

        'Natural Language :: English',

        'Topic :: System :: Monitoring',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ],

    author='Ankush Sharma',

    author_email='darxtrix@gmail.com',

    url='https://github.com/darxtrix/ptop',

    license='MIT',

    download_url= 'https://github.com/darxtrix/ptop/releases/download/v1.0/ptop-1.0.tar.gz', # need to create a git tag or git release for this 

    packages=['ptop', 'ptop.core', 'ptop.plugins', 'ptop.interfaces','ptop.statistics','ptop.utils'],

    install_requires=[
        "npyscreen>=4.10.5",
        "psutil>=3.0.1",
        "argparse>=1.2.1",
        "certifi>=2018.10.15",
        "chardet>=3.0.4",
        "drawille>=0.1.0",
        "requests>=2.20.1",
        "urllib3>=1.24.1",
        "huepy>=0.9.8.1"
    ],

    data_files=['VERSION','README.md','CONTRIBUTORS.md','LICENSE'],

    include_package_data=True, # in order to have this files as part of the installation under site packages

    entry_points={
        'console_scripts': ['ptop = ptop.main:main']
    },
)