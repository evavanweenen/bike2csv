import os
from bike2csv.fit import FIT
from bike2csv.xml import PWX, TCX

class Converter(object):
    """
    Convert file from any extension to csv
    Note that you can use this class for joblib parallel 
    """
    def __init__(self, _path_zip=None, _path_fit='./fit/', _path_csv='./csv/'):
        """
        _path_zip   - location of zip files (None if file are already unzipped)
        _path_fit   - location of fit/tcx/pwx files
        _path_csv   - location of csv files
        """
        self._path_zip = _path_zip
        self._path_fit = _path_fit
        self._path_csv = _path_csv

        if not os.path.exists(self._path_fit):
            os.makedirs(self._path_fit)
        if not os.path.exists(self._path_csv):
            os.makedirs(self._path_csv)

        self.FILE = {   '.fit'    : FIT,
                        '.FIT'    : FIT,
                        '.pwx'    : PWX,
                        '.tcx'    : TCX}

    def unzip(self, file):
        # split xxx.fit | .gz
        base, _ = os.path.splitext(file)

        if not os.path.exists(os.path.join(self._path_fit, base)):
            os.system(f"gzip -dk '{self._path_zip}/{file}'")
            os.system(f"mv '{self._path_zip}/{base}' '{self._path_fit}/{base}'")

    def convert(self, file):
        # split xxx | .fit
        file, _ = os.path.splitext(file)
        base, extension = os.path.splitext(file)

        if not os.path.exists(f'{self._path_csv}/record/{base}_record.csv'):
            print(base)
            if os.path.exists(os.path.join(self._path_fit, file)):
                if extension in self.FILE:
                    self.FILE[extension](file, self._path_fit, self._path_csv).parse()
                else:
                    raise NotImplementedError(f"{extension} not implemented.")
            else:
                raise ValueError(f"{extension} file could not be obtained.")