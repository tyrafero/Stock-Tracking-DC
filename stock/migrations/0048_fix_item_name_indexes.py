# Manual migration to fix item_name index issue
# This migration removes any indexes on item_name fields that prevent TextField conversion

from django.db import migrations, connection


def remove_item_name_indexes(apps, schema_editor):
    """Remove any indexes on item_name fields in stock and stockhistory tables"""
    with connection.cursor() as cursor:
        # Get list of indexes on stock_stock.item_name
        cursor.execute("""
            SELECT DISTINCT index_name
            FROM information_schema.statistics
            WHERE table_schema = DATABASE()
            AND table_name = 'stock_stock'
            AND column_name = 'item_name'
            AND index_name != 'PRIMARY'
        """)

        stock_indexes = cursor.fetchall()
        for row in stock_indexes:
            index_name = row[0]
            print(f"Dropping index {index_name} from stock_stock.item_name")
            cursor.execute(f"ALTER TABLE stock_stock DROP INDEX `{index_name}`")

        # Get list of indexes on stock_stockhistory.item_name
        cursor.execute("""
            SELECT DISTINCT index_name
            FROM information_schema.statistics
            WHERE table_schema = DATABASE()
            AND table_name = 'stock_stockhistory'
            AND column_name = 'item_name'
            AND index_name != 'PRIMARY'
        """)

        history_indexes = cursor.fetchall()
        for row in history_indexes:
            index_name = row[0]
            print(f"Dropping index {index_name} from stock_stockhistory.item_name")
            cursor.execute(f"ALTER TABLE stock_stockhistory DROP INDEX `{index_name}`")

        if not stock_indexes and not history_indexes:
            print("No indexes found on item_name fields")


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0047_alter_stock_condition_alter_stock_warehouse_name'),
    ]

    operations = [
        migrations.RunPython(remove_item_name_indexes, reverse_code=migrations.RunPython.noop),
    ]
