"""Nufox setup."""

import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages


setup(
    name = 'Nufox',
    version = '0.2.0',
    description = 'Python + XUL',
    long_description = """
    Nufox is a Python XUL_ toolkit written on top of Twisted_ and Nevow_.

    .. _XUL: http://xulplanet.com/

    .. _Twisted: http://twistedmatrix.com/

    .. _Nevow: http://nevow.com/
    """,
    
    classifiers = [
    ## Fill me in.
    ],
    
    author = 'Nufox Contributors',
    author_email = 'nufox@googlegroups.com',
    url = 'http://trac.nunatak.com.au/projects/nufox',
    license = 'LGPL',
    platforms = [
    ## Fill me in.
    ],

    packages=find_packages(exclude=['doc', 'ez_setup', 'examples', 'tests']),
    package_data = {
    ## Fill me in.
    },

    install_requires = [
    'Nevow == 0.6',
    'Louie >= 1.0b2',
    ],
    zip_safe = False,

    )
