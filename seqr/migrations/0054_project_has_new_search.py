# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-04-05 16:04
from __future__ import unicode_literals

from django.db import migrations, models
from elasticsearch_dsl import Index

from seqr.utils.es_utils import get_es_client, get_latest_loaded_samples


def set_has_new_search(apps, schema_editor):
    client = get_es_client()
    indices = [index['index'] for index in client.cat.indices(format="json", h='index')
               if index['index'] not in ['.kibana', 'index_operations_log']]
    mappings = Index('_all', using=client).get_mapping(doc_type='variant')
    new_search_indices = {index_name for index_name in indices
                          if 'samples_num_alt_1' in mappings[index_name]['mappings']['variant']['properties']}

    latest_loaded_samples = get_latest_loaded_samples()
    project_ids_with_new_search = set()
    for sample in latest_loaded_samples:
        for index_name in sample.elasticsearch_index.split(','):
            if index_name in new_search_indices:
                project_ids_with_new_search.add(sample.individual.family.project_id)

    # We get the model from the versioned app registry;
    # if we directly import it, it'll be the wrong version
    # see https://docs.djangoproject.com/en/1.11/ref/migration-operations/#django.db.migrations.operations.RunPython
    Project = apps.get_model("seqr", "Project")
    db_alias = schema_editor.connection.alias
    Project.objects.using(db_alias).filter(id__in=project_ids_with_new_search).update(has_new_search=True)


class Migration(migrations.Migration):

    dependencies = [
        ('seqr', '0053_auto_20190405_1525'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='has_new_search',
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(set_has_new_search, reverse_code=lambda *args: True),

    ]
