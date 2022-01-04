import argparse
from bike2csv.converter import Converter

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--_path_zip", type=str, help="Location of zip files", default=None)
    parser.add_argument("_path_fit", type=str, help="Location of unzipped fit/tcx/pwx files")
    parser.add_argument("_path_csv", type=str, help="Location of csv files")
    args = parser.parse_args()

    converter = Converter(**vars(args))

    for file in converter.files:
        converter.convert(file)

if __name__ == '__main__':
    main()