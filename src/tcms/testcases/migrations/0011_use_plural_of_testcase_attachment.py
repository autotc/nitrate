# Generated by Django 3.0.7 on 2020-10-03 09:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("testcases", "0010_remove_max_length_from_authfield"),
    ]

    operations = [
        migrations.RenameField(
            model_name="testcase",
            old_name="attachment",
            new_name="attachments",
        ),
    ]