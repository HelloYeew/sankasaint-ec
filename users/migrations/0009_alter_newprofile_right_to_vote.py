# Generated by Django 4.1.2 on 2022-11-24 21:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_newprofile_blacklist_newprofile_right_to_vote_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newprofile',
            name='right_to_vote',
            field=models.BooleanField(default=True),
        ),
    ]