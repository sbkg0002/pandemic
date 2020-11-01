# Generated by Django 3.1.2 on 2020-11-01 15:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('game_tracker', '0006_auto_20201031_1910'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='city',
            name='number_of_agents',
        ),
        migrations.CreateModel(
            name='Agent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('city', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='agents', to='game_tracker.city')),
            ],
        ),
    ]