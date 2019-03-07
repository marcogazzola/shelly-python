import os
import re
import setuptools
import shellypython


def readme():
    # we have intersphinx link in our readme, so let's replace them
    # for the long_description to make pypi happy
    reg = re.compile(r':.+?:`(.+?)\s?(<.+?>)?`')
    with open('README.rst') as f:
        return re.sub(reg, r'\1', f.read())


REQUIREMENTS = [
    line.strip() for line in open(
        os.path.join(os.path.dirname(__file__), 'requirements.txt')
        ).readlines()
    ]

setuptools.setup(
    name="shellypython",
    version=shellypython.__version__,
    author="Marco Gazzola",
    description="Python interface for Shelly.cloud devices.",
    long_description=readme(),
    long_description_content_type="text/x-rst",
    url="https://github.com/marcogazzola/shelly-python",
    download_url='https://github.com/marcogazzola/shelly-python/tarball/%s' % (
        shellypython.__version__),
    keywords=['shelly', 'shelly-cloud', 'rele', 'api', 'mqtt'],
    packages=['shellypython'],
    package_dir={"shellypython": "shellypython"},
    install_requires=REQUIREMENTS,
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
