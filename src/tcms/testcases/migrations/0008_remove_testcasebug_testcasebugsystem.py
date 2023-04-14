# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-12-20 15:06
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        (
            "testcases",
            "0007_set_default_tester_and_reviewer_to_null_if_user_is_deleted",
        ),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="testcasebug",
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name="testcasebug",
            name="bug_system",
        ),
        migrations.RemoveField(
            model_name="testcasebug",
            name="case",
        ),
        migrations.RemoveField(
            model_name="testcasebug",
            name="case_run",
        ),
        migrations.DeleteModel(
            name="TestCaseBug",
        ),
        migrations.DeleteModel(
            name="TestCaseBugSystem",
        ),
    ]
