from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='BrandModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(max_length=100, unique=True)),
                ('logo_url', models.URLField(blank=True)),
            ],
            options={'db_table': 'brands'},
        ),
        migrations.CreateModel(
            name='ProductTypeModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('attribute_schema', models.JSONField(default=dict)),
            ],
            options={'db_table': 'product_types'},
        ),
        migrations.CreateModel(
            name='CategoryModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True)),
                ('icon', models.CharField(blank=True, max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('parent', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='children', to='catalog.categorymodel',
                )),
            ],
            options={'db_table': 'categories', 'ordering': ['name']},
        ),
        migrations.CreateModel(
            name='ProductModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(db_index=True, max_length=255)),
                ('price', models.DecimalField(decimal_places=0, max_digits=12)),
                ('stock', models.IntegerField(default=0)),
                ('description', models.TextField(blank=True)),
                ('cover_image', models.URLField(blank=True)),
                ('attributes', models.JSONField(default=dict)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('brand', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    to='catalog.brandmodel',
                )),
                ('category', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='products', to='catalog.categorymodel',
                )),
                ('product_type', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    to='catalog.producttypemodel',
                )),
            ],
            options={'db_table': 'products', 'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='VariantModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('sku', models.CharField(max_length=64, unique=True)),
                ('price', models.DecimalField(decimal_places=0, max_digits=12)),
                ('stock', models.IntegerField(default=0)),
                ('attributes', models.JSONField(default=dict)),
                ('product', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='variants', to='catalog.productmodel',
                )),
            ],
            options={'db_table': 'product_variants'},
        ),
    ]
