# Generated by Django 4.2.16 on 2024-09-11 01:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Playlist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('playlist_id', models.CharField(max_length=255, unique=True)),
                ('title', models.CharField(max_length=255)),
                ('season_number', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Episode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('video_id', models.CharField(max_length=255, unique=True)),
                ('thumbnail', models.URLField()),
                ('duration', models.IntegerField()),
                ('playlist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='episodes', to='videos.playlist')),
            ],
        ),
    ]
