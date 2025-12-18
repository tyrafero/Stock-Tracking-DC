# Zoho Inventory Import Guide

This guide explains how to import products from Zoho Inventory into your Django stock tracking application.

## Recent Fixes (2025-11-05)

### Issues Fixed:

1. **Database Schema Error:** Fixed "Data too long for column 'item_name'" error
   - Migration `0045_fix_item_name_length.py` increases `item_name` field from `varchar(50)` to `varchar(200)`
   - Also fixes `StockHistory.item_name` field length

2. **Missing StockLocation Records:** Import now creates proper location tracking
   - Stock items now appear in "Locations" column with warehouse names and quantities
   - `total_across_locations` property now works correctly
   - Each imported stock item gets a StockLocation record automatically

3. **View Optimization:** Updated `view_stock` to prefetch related data
   - Locations, commitments, and product data now load efficiently
   - Reduces database queries significantly (N+1 query fix)

### How to Apply These Fixes:

If you've already run the import and encountered errors:

1. **Apply the database fix:**
   ```bash
   python manage.py migrate
   ```

2. **Fix existing stock items without locations:**
   ```bash
   python manage.py fix_stock_locations
   ```

   This creates StockLocation records for all existing stock items with quantity > 0.
   Run with `--dry-run` first to preview changes.

3. **Optional: Re-run the import** to update products:
   ```bash
   python manage.py import_zoho_inventory "/path/to/your/ZOHO_INVENTORY_LIST.csv"
   ```

The system will now:
- ✅ Handle long product names (up to 200 characters)
- ✅ Display locations with warehouse names and quantities
- ✅ Show total stock across all locations
- ✅ Display committed stock information

## Overview

The import process adds new fields to your database and creates a management command to import Zoho CSV exports. The system:

- Creates products with condition suffixes (e.g., "Product Name - Bstock")
- Links stock records to products via ForeignKey
- Handles duplicate Item IDs with different warehouse conditions
- Parses location/aisle information from SKU fields
- Preserves Zoho metadata for tracking

## What's Included

### 1. Database Migration (`0044_add_zoho_product_fields.py`)

Adds the following fields to the **Product** model (`stock_product` table):

**Essential Product Fields:**
- `sku` - Stock Keeping Unit (unique)
- `upc` - Universal Product Code
- `ean` - European Article Number
- `isbn` - International Standard Book Number
- `part_number` - Manufacturer part number
- `brand` - Product brand
- `manufacturer` - Product manufacturer
- `sales_description` - Sales description from Zoho
- `product_type` - Product type (goods/service)
- `unit` - Unit of measurement (box/pair/etc)

**Physical Dimensions:**
- `package_weight`, `package_length`, `package_width`, `package_height`
- `dimension_unit` - (cm/inch)
- `weight_unit` - (kg/lb)

**Zoho Integration:**
- `zoho_item_id` - Zoho Item ID (unique)
- `zoho_created_time` - Created time from Zoho
- `zoho_last_modified` - Last modified time from Zoho

Adds the following fields to the **Stock** model (`stock_stock` table):

- `product` - ForeignKey to Product (nullable for safe migration)
- `opening_stock` - Opening stock from Zoho
- `stock_on_hand` - Stock on hand from Zoho
- `warehouse_name` - Warehouse name from Zoho

**Updates Stock condition choices** to include:
- `new` (existing)
- `demo_unit` (existing)
- `bstock` (existing)
- `open_box` (NEW)
- `refurbished` (NEW)

### 2. Import Command (`import_zoho_inventory.py`)

Django management command located at:
```
stock/management/commands/import_zoho_inventory.py
```

## Installation Steps

### Step 1: Run the Migration

Apply the database changes:

```bash
python manage.py migrate stock 0044_add_zoho_product_fields
```

**Expected Output:**
```
Running migrations:
  Applying stock.0044_add_zoho_product_fields... OK
```

**Verification:**
Check that the migration was applied successfully:

```bash
python manage.py showmigrations stock
```

You should see a checkmark `[X]` next to `0044_add_zoho_product_fields`.

### Step 2: Prepare Your CSV File

1. Export your inventory from Zoho Inventory as CSV
2. Place the CSV file in an accessible location (e.g., `/home/user/Downloads/`)
3. Note the full path to the file

### Step 3: Run a Dry-Run First (RECOMMENDED)

Before importing, test with a dry-run to see what will happen:

```bash
python manage.py import_zoho_inventory "/path/to/your/ZOHO_INVENTORY_LIST.csv" --dry-run
```

**What to Look For:**
- Check that product names have correct condition suffixes
- Verify row counts and error messages
- Review which products would be created vs. updated

**Example Output:**
```
DRY RUN MODE - No changes will be saved
Reading CSV file: /home/user/Downloads/ZOHO_INVENTORY_LIST.csv
Row 2: Would CREATE product: Audiolab M-One Stereo Integrated Amplifier
  → Would create stock: new at Silverwater
Row 3: Would CREATE product: Audiolab M-DAC+ Digital-to-Analogue Converter
  → Would create stock: new at Silverwater
Row 16: Would CREATE product: Epson EH-TW8400 4K PRO-UHD Home Cinema Projector
  → Would create stock: new at Silverwater
Row 17: Would CREATE product: Epson EH-TW8400 4K PRO-UHD Home Cinema Projector - Bstock
  → Would create stock: bstock at Silverwater - [ B-Stock / Open Box / Ex- Demo / Refurb]

============================================================
IMPORT SUMMARY
============================================================
Total rows processed: 4287
Would CREATE products: 3215
Would UPDATE products: 0
Would CREATE stock: 4287
Errors: 0

DRY RUN - No changes were saved
```

### Step 4: Run the Actual Import

Once you're satisfied with the dry-run results:

```bash
python manage.py import_zoho_inventory "/path/to/your/ZOHO_INVENTORY_LIST.csv"
```

**Example Output:**
```
Reading CSV file: /home/user/Downloads/ZOHO_INVENTORY_LIST.csv
Row 2: Created product: Audiolab M-One Stereo Integrated Amplifier
  → Created stock record: no-sku at Silverwater
Row 3: Created product: Audiolab M-DAC+ Digital-to-Analogue Converter
  → Created stock record: A1-1 at Silverwater
...

============================================================
IMPORT SUMMARY
============================================================
Total rows processed: 4287
Products created: 3215
Products updated: 0
Products skipped: 0
Stock records created: 4287
Errors: 0

Import completed successfully!
```

## Command Options

### Basic Usage
```bash
python manage.py import_zoho_inventory <csv_file_path>
```

### Available Options

**`--dry-run`**
- Simulates the import without saving to database
- Shows what would be created/updated
- **Always run this first!**

```bash
python manage.py import_zoho_inventory "file.csv" --dry-run
```

**`--skip-existing`**
- Skips products that already exist (based on Zoho Item ID)
- Useful for incremental imports

```bash
python manage.py import_zoho_inventory "file.csv" --skip-existing
```

**Combine options:**
```bash
python manage.py import_zoho_inventory "file.csv" --dry-run --skip-existing
```

## Product Name Examples

The import script automatically adds condition suffixes to product names based on warehouse information:

### Example Transformations:

| Original Item Name | Warehouse Name | Final Product Name | Condition |
|-------------------|----------------|-------------------|-----------|
| Audiolab M-One Stereo Integrated Amplifier | Silverwater | Audiolab M-One Stereo Integrated Amplifier | `new` |
| Epson EH-TW8400 4K PRO-UHD Home Cinema Projector | Silverwater | Epson EH-TW8400 4K PRO-UHD Home Cinema Projector | `new` |
| Epson EH-TW8400 4K PRO-UHD Home Cinema Projector | Silverwater - [ B-Stock / Open Box / Ex- Demo / Refurb] | Epson EH-TW8400 4K PRO-UHD Home Cinema Projector - Bstock | `bstock` |
| Marantz HD-AMP1 Mini Integrated Amplifier | Silverwater - [ B-Stock / Open Box / Ex- Demo / Refurb] | Marantz HD-AMP1 Mini Integrated Amplifier - Bstock | `bstock` |
| Pioneer SX-N30AE Hi-Res Stereo Receiver | Silverwater | Pioneer SX-N30AE Hi-Res Stereo Receiver | `new` |
| Pioneer SX-N30AE Hi-Res Stereo Receiver | Silverwater - [ B-Stock / Open Box / Ex- Demo / Refurb] | Pioneer SX-N30AE Hi-Res Stereo Receiver - Bstock | `bstock` |

### Condition Mapping:

| Warehouse Name Contains | Product Name Suffix | Stock Condition Field |
|------------------------|--------------------|--------------------|
| "B-Stock" or "bstock" | " - Bstock" | `bstock` |
| "Open Box" or "openbox" | " - Open Box" | `open_box` |
| "Ex-Demo" or "Demo" | " - Demo" | `demo_unit` |
| "Refurb" or "Refurbished" | " - Refurbished" | `refurbished` |
| None (new items) | (no suffix) | `new` |

## Aisle/Location Handling

The import script extracts aisle information from the SKU field:

**Examples:**
- SKU: `"A4-1"` → Aisle: `"A4-1"`
- SKU: `"B 1-5"` → Aisle: `"B1-5"` (spaces removed)
- SKU: `"(OpenBox #84-Unit 3 upstairs)"` → Aisle: (extracted pattern if found)

## Duplicate Handling

Zoho exports may contain the same Item ID multiple times with different warehouse names. The import creates:

1. **One Product** per unique base name + condition combination
2. **Multiple Stock records** for the same product at different warehouses

**Example:**
- Row 16: Item ID `21182000000072561`, Warehouse: "Silverwater"
  - Creates: Product "Epson EH-TW8400" (new) + Stock record
- Row 17: Item ID `21182000000072561`, Warehouse: "Silverwater - B-Stock"
  - Creates: Product "Epson EH-TW8400 - Bstock" + Stock record

## Post-Import Checklist

After running the import, verify:

### 1. Check Product Counts
```bash
python manage.py shell
```

```python
from stock.models import Product, Stock

# Check total products
print(f"Total products: {Product.objects.count()}")

# Check products with Zoho IDs
print(f"Products from Zoho: {Product.objects.filter(zoho_item_id__isnull=False).count()}")

# Check stock records linked to products
print(f"Stock with products: {Stock.objects.filter(product__isnull=False).count()}")

# View sample products with conditions
from django.db.models import Q
bstock_products = Product.objects.filter(Q(name__icontains='- Bstock') | Q(name__icontains='- Demo'))
print(f"Products with condition suffixes: {bstock_products.count()}")
for p in bstock_products[:5]:
    print(f"  - {p.name}")
```

### 2. Check Stock Conditions
```python
from stock.models import Stock
from django.db.models import Count

# Count by condition
conditions = Stock.objects.values('condition').annotate(count=Count('id'))
for c in conditions:
    print(f"{c['condition']}: {c['count']}")
```

### 3. Verify Warehouse Assignments
```python
from stock.models import Stock

# Check warehouse names
warehouses = Stock.objects.values('warehouse_name').distinct()
for w in warehouses:
    count = Stock.objects.filter(warehouse_name=w['warehouse_name']).count()
    print(f"{w['warehouse_name'] or '(none)'}: {count} items")
```

### 4. Check for SKU Assignments
```python
from stock.models import Stock, Product

# Products with SKUs
print(f"Products with SKU: {Product.objects.filter(sku__isnull=False).count()}")

# Stock with SKUs
print(f"Stock with SKU: {Stock.objects.filter(sku__isnull=False).count()}")

# Stock with aisle locations
print(f"Stock with aisle: {Stock.objects.filter(aisle__isnull=False).count()}")
```

## Import Results & Errors

### Typical Import Summary

After running the import, you'll see a summary like:

```
============================================================
IMPORT SUMMARY
============================================================
Total rows processed: 4289
Products created: 1465
Products updated: 2789
Products skipped: 0
Stock records created: 1285
Errors: 3004
```

### Understanding Errors

**Duplicate SKU Errors** (most common):
```
Row 4222: Created product: Carson Selina 230-Inch Screen
Row 4222: Error - (1062, "Duplicate entry 'F4-5' for key 'sku'")
```

This occurs when:
- Multiple products in Zoho have the same SKU value
- The product is created successfully, but the stock record fails due to duplicate SKU constraint
- **Impact:** Product is imported, but stock tracking may be incomplete

**Workaround:**
- Products are still created successfully
- Stock items with duplicate SKUs won't be created
- You can manually update SKUs in the database or Zoho before re-importing

### Missing Locations ("at default")

During import, you may see:
```
Row 4228: Updated product: Mobile Fidelity SourcePoint 8
  → Created stock record: no-sku at default
```

This means:
- No warehouse name was found in the CSV, or
- The warehouse name field was empty in Zoho

**Solution:** Run the `fix_stock_locations` command after import:
```bash
python manage.py fix_stock_locations
```

## Common Issues & Solutions

### Issue 1: Migration Already Applied

**Error:** `Migration stock.0044_add_zoho_product_fields is already applied`

**Solution:** The migration has already been run. You can proceed directly to importing.

### Issue 2: File Not Found

**Error:** `File not found: /path/to/file.csv`

**Solution:**
- Check the file path is correct
- Use absolute paths (e.g., `/home/user/Downloads/file.csv`)
- Enclose paths with spaces in quotes: `"/path with spaces/file.csv"`

### Issue 3: Duplicate Key Errors

**Error:** `UNIQUE constraint failed: stock_product.sku`

**Cause:** Multiple rows have the same SKU value

**Solution:**
- The import will skip rows that cause errors and continue
- Check the error output to see which rows failed
- You may need to manually review and clean duplicate SKUs in Zoho

### Issue 4: Missing Warehouse/Location

**Behavior:** Stock records created without location assignments

**Solution:** The import creates a default "Silverwater" warehouse if it doesn't exist. You can:
1. Create warehouse/store records before importing
2. Manually assign locations after import
3. Update the import script to match your warehouse names

### Issue 5: Product Names Look Wrong

**Problem:** Condition suffixes not appearing correctly

**Solution:**
1. Check the `Warehouse Name` column in your CSV
2. Verify the warehouse name contains condition markers (e.g., "B-Stock")
3. Run with `--dry-run` to preview names before importing

## Re-running the Import

If you need to re-import:

### Option 1: Update Existing Products
```bash
python manage.py import_zoho_inventory "file.csv"
```
This will **update** existing products based on Zoho Item ID.

### Option 2: Skip Existing Products
```bash
python manage.py import_zoho_inventory "file.csv" --skip-existing
```
This will only import **new** products.

### Option 3: Clean Slate
If you need to start fresh:

```bash
python manage.py shell
```

```python
from stock.models import Product, Stock

# WARNING: This deletes all imported products and their stock
# Only do this if you're sure!
Product.objects.filter(zoho_item_id__isnull=False).delete()

# Or delete all products (BE CAREFUL!)
# Product.objects.all().delete()
```

Then re-run the import.

## Performance Notes

- **Large imports (4000+ rows):** May take 5-10 minutes
- **Progress output:** The script prints progress for each row
- **Database transactions:** Each row is wrapped in a transaction for safety
- **Memory usage:** CSV is read line-by-line (minimal memory footprint)

## Data Mapping Reference

### Excluded Zoho Fields

The following Zoho fields are **NOT** imported (as per requirements):

- Selling Price, Purchase Price
- Opening Stock Value
- Inventory Valuation Method
- Is Returnable Item, Sellable, Purchasable, Track Inventory, Is Combo Product
- Sales Account, Purchase Account, Inventory Account
- Preferred Vendor
- Reorder Level (already exists in Stock model)

### Field Mapping

| Zoho CSV Column | Django Model | Field Name |
|----------------|--------------|------------|
| Item ID | Product | `zoho_item_id` |
| Item Name | Product | `name` (with condition suffix) |
| SKU | Product | `sku` |
| UPC | Product | `upc` |
| EAN | Product | `ean` |
| ISBN | Product | `isbn` |
| Part Number | Product | `part_number` |
| Brand | Product | `brand` |
| Manufacturer | Product | `manufacturer` |
| Sales Description | Product | `sales_description` |
| Product Type | Product | `product_type` |
| Unit | Product | `unit` |
| Package Weight | Product | `package_weight` |
| Package Length | Product | `package_length` |
| Package Width | Product | `package_width` |
| Package Height | Product | `package_height` |
| Dimension Unit | Product | `dimension_unit` |
| Weight Unit | Product | `weight_unit` |
| Created Time | Product | `zoho_created_time` |
| Last Modified Time | Product | `zoho_last_modified` |
| Opening Stock | Stock | `opening_stock` |
| Stock On Hand | Stock | `stock_on_hand` |
| Warehouse Name | Stock | `warehouse_name` |
| SKU (parsed) | Stock | `aisle` |

## Support

If you encounter issues:

1. Run with `--dry-run` first to diagnose
2. Check the error output for specific row numbers
3. Review the CSV file for data quality issues
4. Verify database migration was applied successfully

## Next Steps

After successful import:

1. **Review Products:** Check the Django admin or product list view
2. **Link Stock to Products:** Existing stock can be manually linked via the admin
3. **Set Reorder Levels:** Update reorder levels for products as needed
4. **Configure Locations:** Ensure warehouse/store locations are properly set up
5. **Test Workflows:** Verify product and stock management features work correctly

---

**Import Command Location:**
`stock/management/commands/import_zoho_inventory.py`

**Migration File:**
`stock/migrations/0044_add_zoho_product_fields.py`

**Last Updated:** 2025-11-05
