from setuptools import setup

with open('README.rst') as file:
    long_description = file.read()

description = 'workflow support for reproducible deduplication and merging'

setup(name='mergic',
      packages=['mergic'],
      description=description,
      long_description=long_description,
      license='MIT',
      author='Aaron Schumacher',
      author_email='ajschumacher@gmail.com',
      url='https://github.com/ajschumacher/mergic',
      download_url='https://github.com/ajschumacher/mergic/tarball/0.0.6',
      version='0.0.6',
      entry_points={'console_scripts': ['mergic = mergic:script']},
      classifiers=["Programming Language :: Python",
                   "Programming Language :: Python :: 2.7",
                   "License :: OSI Approved :: MIT License",
                   "Development Status :: 2 - Pre-Alpha"])
