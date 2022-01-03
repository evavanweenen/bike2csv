from setuptools import setuptools

setup(name='bike2csv',
    version='0.1',
    description='Convert FIT, PWX and TCX files from a bike computer to CSV',
    url='https://github.com/evavanweenen/bike2csv',
    author='Eva van Weenen',
    author_email='evanweenen@ethz.ch',
    license='MIT',
    packages=['bike2csv'],
    scripts=['bin/run'],
    zip_safe=False,
    install_requires=['fitparse'])