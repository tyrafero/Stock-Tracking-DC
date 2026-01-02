#!/bin/bash
# Production migration fix for item_name TextField issue

set -e  # Exit on error

echo "=== Production Migration Fix ==="
echo ""
echo "Step 1: Checking migration status..."
python manage.py showmigrations stock | grep -E "046|047|048"

echo ""
echo "Step 2: Rolling back migration 0046 (fake)..."
python manage.py migrate stock 0045 --fake

echo ""
echo "Step 3: Applying migration 0048 to remove indexes..."
python manage.py migrate stock 0048

echo ""
echo "Step 4: Re-applying migration 0046..."
python manage.py migrate stock 0046

echo ""
echo "Step 5: Applying all remaining migrations..."
python manage.py migrate

echo ""
echo "=== Migration fix complete! ==="
python manage.py showmigrations stock | tail -5
