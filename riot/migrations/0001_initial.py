# Generated by Django 2.0.1 on 2018-01-14 03:36

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Champion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('champion_id', models.IntegerField(unique=True)),
                ('name', models.CharField(max_length=12, unique=True)),
                ('palette', models.CharField(max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='Match',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('result', models.BooleanField()),
                ('game_id', models.IntegerField(unique=True)),
                ('champ_id', models.IntegerField(unique=True)),
                ('summoner_id', models.IntegerField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Summoner',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('summoner_id', models.IntegerField(unique=True)),
                ('name', models.CharField(max_length=32, unique=True)),
            ],
        ),
    ]