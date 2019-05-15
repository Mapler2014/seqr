# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-03-20 21:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seqr', '0050_family_pubmed_ids'),
    ]

    operations = [
        migrations.AlterField(
            model_name='individual',
            name='case_review_status',
            field=models.CharField(choices=[(b'I', b'In Review'), (b'U', b'Uncertain'), (b'A', b'Accepted'), (b'R', b'Not Accepted'), (b'Q', b'More Info Needed'), (b'P', b'Pending Results and Records'), (b'N', b'NMI Review'), (b'W', b'Waitlist')], default=b'I', max_length=2),
        ),
    ]