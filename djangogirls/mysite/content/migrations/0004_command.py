# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0003_auto_20180914_1416'),
    ]

    operations = [
        migrations.CreateModel(
            name='command',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('address', models.GenericIPAddressField()),
                ('user', models.CharField(max_length=100)),
                ('passwd', models.CharField(max_length=100)),
                ('bridge', models.CharField(max_length=100)),
                ('interface', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
