# Generated by Django 3.2.12 on 2022-04-05 14:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dojo', '0160_set_notnull_endpoint_statuses'),
    ]

    operations = [
        migrations.AddField(
            model_name='dojo_group',
            name='social_provider',
            field=models.CharField(blank=True, choices=[('AzureAD', 'AzureAD')], help_text='Group imported from a social provider.', max_length=10, null=True, verbose_name='Social Authentication Provider'),
        ),
    ]
