# -*- coding: utf-8 -*-

from django.db import models


class CtcBlob(models.Model):
    """Blob data model class."""

    bctc_no = models.AutoField(db_column='bctc_no', primary_key=True)
    txt = models.BinaryField()

    class Meta:
        """Infomration about the data model itself."""

        managed = False
        db_table = 'ctc_blob'
