import os
import setuptools
import shellypython
with open("README.md", "r") as fh:
    long_description = fh.read()

REQUIREMENTS = [
    line.strip() for line in open(
        os.path.join(os.path.dirname(__file__), 'requirements.txt')
        ).readlines()
    ]

setuptools.setup(
    name="shelly-python",
    version=shellypython.__version__,
    author="Marco Gazzola",
    description="Python interface for Shelly.cloud devices.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/marcogazzola/shelly-python",
    download_url='https://github.com/marcogazzola/shelly-python/tarball/%s' % (
        shellypython.__version__),
    keywords=['shelly cloud', 'rele', 'api', 'mqtt', 'home assistant'],
    packages=['shelly-python'],
    package_dir={"shelly-python": "shellypython"},
    install_requires=REQUIREMENTS,
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
