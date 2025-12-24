# Comprehensive fix for all index and field type issues
from django.db import migrations, connection


def fix_database_schema(apps, schema_editor):
    """Fix all schema issues in one go"""
    with connection.cursor() as cursor:

        # 1. Fix item_name field in stock_stock
        cursor.execute("SHOW COLUMNS FROM stock_stock WHERE Field = 'item_name'")
        result = cursor.fetchone()
        if result:
            current_type = result[1].lower()
            # If not TEXT, remove indexes and convert
            if 'text' not in current_type:
                # Drop any indexes on item_name
                cursor.execute("""
                    SELECT DISTINCT index_name FROM information_schema.statistics
                    WHERE table_schema = DATABASE() AND table_name = 'stock_stock'
                    AND column_name = 'item_name' AND index_name != 'PRIMARY'
                """)
                for row in cursor.fetchall():
                    try:
                        cursor.execute(f"ALTER TABLE stock_stock DROP INDEX `{row[0]}`")
                    except:
                        pass

                # Convert to LONGTEXT
                cursor.execute("ALTER TABLE stock_stock MODIFY item_name LONGTEXT NULL")

        # 2. Fix item_name field in stock_stockhistory
        cursor.execute("SHOW COLUMNS FROM stock_stockhistory WHERE Field = 'item_name'")
        result = cursor.fetchone()
        if result:
            current_type = result[1].lower()
            if 'text' not in current_type:
                cursor.execute("""
                    SELECT DISTINCT index_name FROM information_schema.statistics
                    WHERE table_schema = DATABASE() AND table_name = 'stock_stockhistory'
                    AND column_name = 'item_name' AND index_name != 'PRIMARY'
                """)
                for row in cursor.fetchall():
                    try:
                        cursor.execute(f"ALTER TABLE stock_stockhistory DROP INDEX `{row[0]}`")
                    except:
                        pass

                cursor.execute("ALTER TABLE stock_stockhistory MODIFY item_name LONGTEXT NULL")

        # 3. Fix condition field - ensure only one index exists
        cursor.execute("""
            SELECT index_name FROM information_schema.statistics
            WHERE table_schema = DATABASE() AND table_name = 'stock_stock'
            AND column_name = 'condition' AND index_name != 'PRIMARY'
        """)
        condition_indexes = [row[0] for row in cursor.fetchall()]

        # Keep only the first index, drop others
        if len(condition_indexes) > 1:
            for idx in condition_indexes[1:]:
                try:
                    cursor.execute(f"ALTER TABLE stock_stock DROP INDEX `{idx}`")
                except:
                    pass

        # 4. Fix warehouse_name field - ensure only one index exists
        cursor.execute("""
            SELECT index_name FROM information_schema.statistics
            WHERE table_schema = DATABASE() AND table_name = 'stock_stock'
            AND column_name = 'warehouse_name' AND index_name != 'PRIMARY'
        """)
        warehouse_indexes = [row[0] for row in cursor.fetchall()]

        if len(warehouse_indexes) > 1:
            for idx in warehouse_indexes[1:]:
                try:
                    cursor.execute(f"ALTER TABLE stock_stock DROP INDEX `{idx}`")
                except:
                    pass


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0047_alter_stock_condition_alter_stock_warehouse_name'),
    ]

    operations = [
        migrations.RunPython(fix_database_schema, reverse_code=migrations.RunPython.noop),
    ]
