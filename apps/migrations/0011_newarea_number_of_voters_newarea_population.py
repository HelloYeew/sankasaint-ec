# Generated by Django 4.1.3 on 2022-11-21 11:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0010_remove_newparty_candidates_newcandidate_party'),
    ]

    operations = [
        migrations.AddField(
            model_name='newarea',
            name='number_of_voters',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='newarea',
            name='population',
            field=models.IntegerField(default=0),
        ),
    ]
