# Generated by Django 3.2.16 on 2023-02-23 09:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cmt', '0012_cmtpublicdata_cmtpublicdef'),
    ]

    operations = [
        migrations.AddField(
            model_name='cmtcase',
            name='public_request',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cases', to='cmt.cmtpublicdata'),
        ),
    ]