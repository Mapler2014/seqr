# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-03-21 16:56
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reference_data', '0011_primateai'),
    ]

    operations = [
        migrations.CreateModel(
            name='MGI',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('marker_id', models.CharField(max_length=15)),
                ('gene', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reference_data.GeneInfo')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='mgi',
            unique_together=set([('gene', 'marker_id')]),
        ),
    ]
