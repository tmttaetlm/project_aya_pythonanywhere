# Generated by Django 3.2.3 on 2022-03-29 06:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Info',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=1000, null=True, verbose_name='Текст')),
                ('clue', models.CharField(max_length=50, null=True, verbose_name='Ключ')),
            ],
            options={
                'verbose_name': 'Допольнителное',
                'verbose_name_plural': 'Допольнителные',
            },
        ),
    ]