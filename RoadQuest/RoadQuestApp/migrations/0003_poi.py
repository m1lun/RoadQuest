# Generated by Django 5.0.6 on 2024-06-15 22:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('RoadQuestApp', '0002_routeitem_delete_todoitem'),
    ]

    operations = [
        migrations.CreateModel(
            name='POI',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('type', models.CharField(max_length=100)),
                ('address', models.CharField(blank=True, max_length=255, null=True)),
                ('city', models.CharField(blank=True, max_length=100, null=True)),
                ('state', models.CharField(blank=True, max_length=100, null=True)),
                ('postal_code', models.CharField(blank=True, max_length=20, null=True)),
                ('country', models.CharField(blank=True, max_length=100, null=True)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('phone_number', models.CharField(blank=True, max_length=50, null=True)),
                ('website', models.URLField(blank=True, null=True)),
                ('rating', models.FloatField(blank=True, null=True)),
                ('review_count', models.IntegerField(blank=True, null=True)),
                ('price_level', models.IntegerField(blank=True, null=True)),
                ('opening_hours', models.TextField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('amenities', models.TextField(blank=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
