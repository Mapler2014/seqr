# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-07-23 18:08
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('seqr', '0043_auto_20180719_1212'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='locuslist',
            unique_together=set([('name', 'description', 'is_public', 'created_by')]),
        ),
    ]