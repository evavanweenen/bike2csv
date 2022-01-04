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

        self.extension_map = {  '.fit'    : FIT,
                                '.FIT'    : FIT,
                                '.pwx'    : PWX,
                                '.tcx'    : TCX}

        if self.do_unzip():
            self.files = os.listdir(_path_zip)
        else:
            self.files = os.listdir(_path_fit)

    def do_unzip(self):
        return self._path_zip is not None

    def convert(self, file):
        #file = self.files[n]

        if self.do_unzip():
            # split xxx.fit | .gz
            file, zext = os.path.splitext(file)

            if not os.path.exists(os.path.join(self._path_fit, file)):
                os.system(f"gzip -dk '{self._path_zip}/{file}{zext}'")
                os.system(f"mv '{self._path_zip}/{file}' '{self._path_fit}/{file}'")

        # split xxx | .fit
        base, ext = os.path.splitext(file)

        # convert .fit file to csv
        if not os.path.exists(f'{self._path_csv}/record/{base}_record.csv'):
            print(base)
            if os.path.exists(os.path.join(self._path_fit, file)):
                if ext in self.extension_map:
                    self.extension_map[ext](file, self._path_fit, self._path_csv).parse()
                else:
                    raise NotImplementedError(f"{ext} not implemented.")
            else:
                raise ValueError(f"{ext} file could not be obtained.")