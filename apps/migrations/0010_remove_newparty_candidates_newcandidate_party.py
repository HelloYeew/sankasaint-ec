# Generated by Django 4.1.1 on 2022-11-07 11:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0009_alter_voteresultparty_party'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='newparty',
            name='candidates',
        ),
        migrations.AddField(
            model_name='newcandidate',
            name='party',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='apps.newparty'),
        ),
    ]