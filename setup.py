from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='bike2csv',
    version='0.1',
    author='Eva van Weenen',
    author_email='evanweenen@ethz.ch',
    description='Convert FIT, PWX and TCX files from a bike computer to CSV',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/evavanweenen/bike2csv',
    license='MIT',
    packages=['bike2csv'],
    scripts=['bin/run.py'],
    zip_safe=False,
    install_requires=['fitparse']
    )