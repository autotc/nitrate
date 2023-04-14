# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-06-16 14:49
from django.db import migrations


def forwards(apps, schema_editor):
    IssueTrackerProduct = apps.get_model("issuetracker", "IssueTrackerProduct")

    product_names = ["BitBucket", "Bugzilla", "GitHub", "JIRA", "GitLab", "Pagure"]

    for name in product_names:
        IssueTrackerProduct.objects.create(name=name)


class Migration(migrations.Migration):

    dependencies = [
        ("issuetracker", "0001_initial"),
    ]

    # Not remove created products here, remove table will remove the data
    # obviously.

    operations = [migrations.RunPython(forwards, reverse_code=migrations.RunPython.noop)]
