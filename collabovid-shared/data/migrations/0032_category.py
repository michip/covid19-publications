# Generated by Django 3.0.4 on 2020-06-03 17:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0031_delete_category'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField()),
            ],
        ),
    ]