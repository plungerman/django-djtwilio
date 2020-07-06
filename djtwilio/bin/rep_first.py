# -*- coding: utf-8 -*-

import csv
import os
import sys

# env
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djtwilio.settings.shell")

from django.conf import settings


def main():
    """Replace 'rep_first' in message from value in that column of CSV."""

    message = 'yours, rep_first'
    rep = 'rep_first'
    indx = None
    export = 'test.csv'
    try:
        with open(export, 'rb') as phile:
            dialect = csv.Sniffer().sniff(phile.read(1024*1024))
            phile.seek(0)
            delimiter = dialect.delimiter
            reader = csv.reader(
                phile, delimiter=delimiter, quoting=csv.QUOTE_NONE,
            )
            for row in reader:
                if rep in row:
                    indx = row.index(rep)
                else:
                    if indx:
                        message = message.replace(rep, row[indx])
                print(message)
    except Exception as e:
        print("Exception: {}".format(str(e)))
        sys.exit(1)


if __name__ == "__main__":

    sys.exit(main())
