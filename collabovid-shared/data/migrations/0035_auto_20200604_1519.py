# Generated by Django 3.0.4 on 2020-06-04 15:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('data', '0034_category_model_identifier'),
    ]

    operations = [
        migrations.CreateModel(
            name='CategoryMembership',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.FloatField(default=0.0)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='data.Category')),
                ('paper', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='data.Paper')),
            ],
        ),
        migrations.RemoveField(
            model_name='paper',
            name='categories',
        ),
        migrations.AddField(
            model_name='paper',
            name='categories',
            field=models.ManyToManyField(related_name='papers', through='data.CategoryMembership',
                                         to='data.Category')
        ),
    ]
