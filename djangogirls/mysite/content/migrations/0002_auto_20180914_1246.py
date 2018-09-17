# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ovs1',
            name='number',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='ovs2',
            name='number',
            field=models.CharField(max_length=100),
        ),
    ]
