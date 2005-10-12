from os.path import join as opj
from distutils import core, sysconfig
from nufox import __version__

def ld(path):
    #lib directory path maker
    return opj(sysconfig.get_python_lib(), path)

data_files = [[ld('nufox/athena'), ['nufox/athena/MochiKit.js',
                                    'nufox/athena/athena.js']],
              [ld('nufox/javascript'), ['nufox/javascript/preLiveglue.js',
                                        'nufox/javascript/postLiveglue.js' ]]]
core.setup(name="Nufox",
           version=__version__,
           description="Remote XUL server framework",
           author="Timothy Stebbing",
           author_email="tjs@stebbing.id.au",
           url='http://trac.nunatak.com.au/projects/nufox/',
           packages=['nufox', 'nufox.athena'],
           data_files=data_files,
           classifiers=["Development Status :: 4 - Beta",
                        "Environment :: Web Environment :: Mozilla",
                        "Intended Audience :: Developers",
                        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
                        "Operating System :: OS Independent",
                        "Programming Language :: Python",
                        "Topic :: Software Development :: User Interfaces"])
