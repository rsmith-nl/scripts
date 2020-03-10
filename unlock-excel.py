#!/usr/bin/env python3
# file: unlock-excel.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2020 R.F. Smith <rsmith@xs4all.nl>
# Created: 2020-03-10T09:35:46+0100
# Last modified: 2020-03-10T13:47:43+0100
"""Remove passwords from modern excel files (xlsx, xlsm)."""

import zipfile
import re
import sys
import logging
import shutil


def main(argv):
    logging.basicConfig(level='INFO', format='%(levelname)s: %(message)s')
    #logging.basicConfig(level='DEBUG', format='%(levelname)s: %(message)s')
    if not argv:
        logging.info('no files to unlock')
    for path in argv:
        try:
            backup_path = backup_file(path)
            remove_excel_password(backup_path, path)
        except (ValueError, shutil.SameFileError) as e:
            logging.info(e)


def backup_file(path):
    logging.debug(f'making a copy of "{path}"')
    first, last = path.rsplit('.', maxsplit=1)
    backup = first + '-orig' + '.' + last
    shutil.move(path, backup)
    return backup


def remove_excel_password(origpath, path):
    if not zipfile.is_zipfile(origpath):
        raise ValueError(f'"{origpath}" is not a valid zip-file.')
    with zipfile.ZipFile(origpath, mode="r") as inzf, zipfile.ZipFile(path, mode="w", compression=zipfile.ZIP_DEFLATED) as outzf:
        sheets = [name for name in inzf.namelist()]
        for sheet in sheets:
            logging.debug(f'working on "{sheet}"')
            data = inzf.read(sheet)
            if 'xl/worksheets/sheet' not in sheet or b'sheetProtect' not in data:
                outzf.writestr(sheet, data)
                continue
            text = data.decode('utf-8')
            newtext = re.sub(r'<sheetProtect.*?/>', '', text)
            if len(newtext) != len(text):
                outzf.writestr(sheet, newtext)
                logging.debug(f'removed password from "{sheet}"')


if __name__ == '__main__':
    main(sys.argv[1:])
