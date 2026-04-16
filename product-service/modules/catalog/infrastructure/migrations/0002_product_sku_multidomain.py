"""Migration: add sku field to ProductModel for multi-domain support."""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='productmodel',
            name='sku',
            field=models.CharField(blank=True, default='', max_length=64),
        ),
        migrations.AlterUniqueTogether(
            name='productmodel',
            unique_together=set(),
        ),
        # Add unique constraint after populating (handled in entrypoint)
    ]
