# Generated by Django 4.1.1 on 2022-09-30 06:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0002_alter_candidate_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='candidate',
            name='area',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='apps.area'),
        ),
    ]
