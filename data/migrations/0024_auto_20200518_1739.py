# Generated by Django 3.0.4 on 2020-05-18 17:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0023_auto_20200507_1226'),
    ]

    operations = [
        migrations.CreateModel(
            name='Journal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='paper',
            name='pubmed_id',
            field=models.CharField(default=None, max_length=20, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='paper',
            name='journal',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='papers', to='data.Journal'),
        ),
    ]
