from setuptools import setup
from mergic import __version__


description = 'workflow support for reproducible deduplication and merging'

with open('README.rst') as file:
    long_description = file.read()

url = 'https://github.com/ajschumacher/mergic'

setup(name='mergic',
      packages=['mergic'],
      description=description,
      long_description=long_description,
      license='MIT',
      author='Aaron Schumacher',
      author_email='ajschumacher@gmail.com',
      url=url,
      download_url=url + '/tarball/' + __version__,
      version=__version__,
      entry_points={'console_scripts': ['mergic = mergic:script']},
      classifiers=["Programming Language :: Python",
                   "Programming Language :: Python :: 2.7",
                   "License :: OSI Approved :: MIT License",
                   "Development Status :: 2 - Pre-Alpha"])
