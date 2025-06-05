from django.db import migrations

def cleanup_products(apps, schema_editor):
    Product = apps.get_model('core', 'Product')
    CustomUser = apps.get_model('core', 'CustomUser')
    try:
        default_user = CustomUser.objects.get(id=1)  # Adjust ID or email
        Product.objects.filter(user__isnull=True).update(user=default_user)
        # Or delete products: Product.objects.filter(user__isnull=True).delete()
    except CustomUser.DoesNotExist:
        Product.objects.filter(user__isnull=True).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0002_product_created_at_product_status_product_updated_at_and_more'),  # Replace with last migration
    ]

    operations = [
        migrations.RunPython(cleanup_products),
    ]