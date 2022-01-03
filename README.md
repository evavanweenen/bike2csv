# bike2csv - Convert FIT, PWX and TCX files from a bike computer to CSV format

Parse any file obtained from a bike computer to a csv file.
This packages supports the following file extensions: `.fit`, `.FIT`, `.pwx` and `.tcx`.

## Installation
The package is available under pypi:
```
pip install bike2csv
```

## Usage
This code unzips `.gz` files, then converts this unzipped (`.fit`, `.FIT`, `.pwx` or `.tcx`) file to a `.csv` file. The code is designed such that all different file extensions are converted to similar csv files (e.g. the same column names). This makes it easier for analyzing and merging the files later.

If your exported files have a `.gz` format, you can run the sample script underneath to *unzip* your files and convert them to csv.
```python
import os
from bike2csv.converter import Converter

root = 'data/'
person = 'John Doe'

path = dict(_path_zip = os.path.join(root, 'export', person), # where your .fit.gz files are saved
            _path_fit = os.path.join(root, 'fit', person), # where your .fit files will be saved
            _path_csv = os.path.join(root, 'csv', person)) # where the .csv files will be saved

converter = Converter(**path)

for file in os.listdir(_path_zip):
    converter.unzip(file)
    converter.convert(file)
```

If your exported files are *not zipped* anymore, you can run the following sample script to convert your files to csv.
```python
import os
from bike2csv.converter import Converter

root = 'data/'
person = 'John Doe'

path = dict(_path_fit = os.path.join(root, 'fit', person), # where your .fit files are be saved
            _path_csv = os.path.join(root, 'csv', person)) # where the .csv files will be saved

converter = Converter(**path)

for file in os.listdir(_path_fit):
    converter.convert(file)
```
You can of course adjust the script as you please. 
A sample script can also be found under `bin/run.py`.

If you are running into problems, feel welcome to contact the author (evanweenen@ethz.ch).

## Attribution
To read `fit` files in python, this package makes use of the [fitparse](https://github.com/dtcooper/python-fitparse) package &copy; David Cooper, Carey Metcalfe, 2021.

## License
This code is &copy; E. van Weenen, 2022, and it is made available under the MIT license enclosed with the software.

Over and above the legal restrictions imposed by this license, if you use this software for an academic publication then you are obliged to provide proper attribution. 
```
E. van Weenen. bike2csv: Convert files from a bike computer to CSV, v0.1 (2022). github.com/evavanweenen/bike2csv.
```