# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0002_auto_20180914_1246'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ns1',
            name='address',
            field=models.GenericIPAddressField(),
        ),
        migrations.AlterField(
            model_name='ns2',
            name='address',
            field=models.GenericIPAddressField(),
        ),
    ]
