# Generated by Django 3.0.7 on 2020-07-05 11:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0044_auto_20200629_1557'),
    ]

    operations = [
        migrations.CreateModel(
            name='IgnoredPaper',
            fields=[
                ('doi', models.CharField(max_length=100, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='DeleteCandidate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.IntegerField(choices=[(0, 'Language')])),
                ('false_positive', models.BooleanField(default=False)),
                ('score', models.FloatField(default=1)),
                ('paper', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='data.Paper')),
            ],
        ),
        migrations.AddConstraint(
            model_name='deletecandidate',
            constraint=models.UniqueConstraint(fields=('paper', 'type'), name='Paper and Type'),
        ),
    ]