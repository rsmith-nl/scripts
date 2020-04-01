#!/usr/bin/env python3
# file: unlock-excel.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2020 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2020-03-10T13:47:43+0100
# Last modified: 2020-04-01T20:59:12+0200
"""Remove passwords from modern excel 2007+ files (xlsx, xlsm)."""

import zipfile
import re
import sys
import logging
import shutil

__version__ = '0.2'


def main():
    files = setup()
    for path in files:
        try:
            backup_path = backup_file(path)
            remove_excel_password(backup_path, path)
        except (ValueError, shutil.SameFileError) as e:
            logging.info(e)


def setup():
    logging.basicConfig(level='INFO', format='%(levelname)s: %(message)s')
    if len(sys.argv) < 2:
        logging.info(f'unlock-excel.py v{__version__}; no files to unlock')
        print('Usage: unlock-excel.py <file> <file> ...')
        sys.exit(0)
    return sys.argv[1:]


def backup_file(path):
    first, last = path.rsplit('.', maxsplit=1)
    backup = first + '-orig' + '.' + last
    logging.info(f'moving "{path}" to "{backup}"')
    shutil.move(path, backup)
    return backup


def remove_excel_password(origpath, path):
    if not zipfile.is_zipfile(origpath):
        raise ValueError(f'"{origpath}" is not a valid zip-file.')
    with zipfile.ZipFile(origpath, mode="r") as inzf, zipfile.ZipFile(
        path, mode="w", compression=zipfile.ZIP_DEFLATED, compresslevel=1
    ) as outzf:
        infos = [name for name in inzf.infolist()]
        for info in infos:
            logging.debug(f'working on "{info.filename}"')
            data = inzf.read(info)
            if b'sheetProtect' in data:
                regex = r'<sheetProtect.*?/>'
                logging.info(f'worksheet "{info.filename}" is protected')
            elif b'workbookProtect' in data:
                regex = r'<workbookProtect.*?/>'
                logging.into('the workbook is protected')
            else:
                outzf.writestr(info, data)
                continue
            text = data.decode('utf-8')
            newtext = re.sub(regex, '', text)
            if len(newtext) != len(text):
                outzf.writestr(info, newtext)
                logging.info(f'removed password from "{info.filename}"')


if __name__ == '__main__':
    main()
