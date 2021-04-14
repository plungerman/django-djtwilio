#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import unicodedata

import django


django.setup()

# env
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djtwilio.settings.shell")

from django.db import connections

from djtwilio.core.data import CtcBlob


def main():
    """Testing SQL incantation to insert text into blob field."""
    body = 'the quick brown fox jumpéd over the lazy dog, sir!'
    # To load Binary (BLOB) data into an Informix table use the BYTE datatype.
    body = unicodedata.normalize('NFKD', body).encode('ascii', 'ignore')
    print(body)

    bob = CtcBlob.objects.using('informix').create(txt=body)
    print(bob.bctc_no)

    sql = """
        INSERT INTO ctc_rec (
            id, tick, add_date, due_date, cmpl_date,
            resrc, bctc_no, stat
        )
        VALUES (
            {0},"ADM",TODAY,TODAY,TODAY,"{1}",{2},"{3}"
        )
    """.format(
        '8675309',
        'TEXTOUT',
        bob.bctc_no,
        'E',
    )
    print(sql)
    with connections['informix'].cursor() as cursor:
        cursor.execute(sql)


if __name__ == "__main__":

    sys.exit(main())
