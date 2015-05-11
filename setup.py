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
      download_url='https://github.com/ajschumacher/mergic/tarball/0.0.2',
      version='0.0.2',
      entry_points={'console_scripts': ['mergic = mergic:script']})
