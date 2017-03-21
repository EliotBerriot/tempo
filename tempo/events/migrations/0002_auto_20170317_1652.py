# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-17 16:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='entry',
            name='duration',
            field=models.DurationField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='entry',
            name='importance',
            field=models.IntegerField(choices=[(1, 'anectodic'), (2, 'small'), (4, 'high'), (8, 'very high')], default=1),
        ),
        migrations.AlterField(
            model_name='entry',
            name='like',
            field=models.IntegerField(choices=[(-4, 'awful'), (-2, 'bad'), (-1, 'negative'), (0, 'neutral'), (1, 'positive'), (2, 'good'), (4, 'great')], default=0),
        ),
    ]