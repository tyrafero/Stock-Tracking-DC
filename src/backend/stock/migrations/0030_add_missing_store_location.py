# Generated manually to fix missing location field
from django.db import migrations, models


def add_location_field_if_not_exists(apps, schema_editor):
    """Add location field only if it doesn't exist"""
    db_alias = schema_editor.connection.alias
    
    # Check if column exists
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'stock_store' 
            AND COLUMN_NAME = 'location'
        """)
        column_exists = cursor.fetchone()[0] > 0
    
    if not column_exists:
        # Add the field
        Store = apps.get_model('stock', 'Store')
        with schema_editor.connection.cursor() as cursor:
            cursor.execute("ALTER TABLE stock_store ADD COLUMN location VARCHAR(200) NOT NULL DEFAULT ''")


def reverse_add_location_field(apps, schema_editor):
    """Remove location field if it exists"""
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'stock_store' 
            AND COLUMN_NAME = 'location'
        """)
        column_exists = cursor.fetchone()[0] > 0
    
    if column_exists:
        cursor.execute("ALTER TABLE stock_store DROP COLUMN location")


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0029_auto_20250902_0652'),
    ]

    operations = [
        migrations.RunPython(
            add_location_field_if_not_exists,
            reverse_add_location_field
        ),
    ]