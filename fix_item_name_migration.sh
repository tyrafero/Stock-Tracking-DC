#!/bin/bash
# Fix for item_name TextField migration issue on production

echo "=== Fixing item_name TextField Migration Issue ==="
echo ""
echo "This script will:"
echo "1. Rollback migration 0046 (fake)"
echo "2. Remove any indexes on item_name fields"
echo "3. Re-apply migration 0046 with the fix"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    exit 1
fi

# Step 1: Fake rollback migration 0046
echo "Step 1: Rolling back migration 0046 (fake)..."
python manage.py migrate stock 0045 --fake

# Step 2: Manually remove any indexes on item_name
echo "Step 2: Removing indexes on item_name fields..."
python manage.py dbshell <<EOF
-- Drop index on stock.item_name if exists
SET @index_exists = (
    SELECT COUNT(*)
    FROM information_schema.statistics
    WHERE table_schema = DATABASE()
    AND table_name = 'stock_stock'
    AND column_name = 'item_name'
);

SET @sql = IF(@index_exists > 0,
    CONCAT('ALTER TABLE stock_stock DROP INDEX ',
        (SELECT index_name FROM information_schema.statistics
         WHERE table_schema = DATABASE()
         AND table_name = 'stock_stock'
         AND column_name = 'item_name'
         AND index_name != 'PRIMARY' LIMIT 1)),
    'SELECT 1');

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Drop index on stockhistory.item_name if exists
SET @index_exists = (
    SELECT COUNT(*)
    FROM information_schema.statistics
    WHERE table_schema = DATABASE()
    AND table_name = 'stock_stockhistory'
    AND column_name = 'item_name'
);

SET @sql = IF(@index_exists > 0,
    CONCAT('ALTER TABLE stock_stockhistory DROP INDEX ',
        (SELECT index_name FROM information_schema.statistics
         WHERE table_schema = DATABASE()
         AND table_name = 'stock_stockhistory'
         AND column_name = 'item_name'
         AND index_name != 'PRIMARY' LIMIT 1)),
    'SELECT 1');

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;
EOF

# Step 3: Re-apply migration 0046
echo "Step 3: Re-applying migration 0046..."
python manage.py migrate stock 0046

# Step 4: Apply remaining migrations
echo "Step 4: Applying remaining migrations..."
python manage.py migrate

echo ""
echo "=== Migration fix complete! ==="
