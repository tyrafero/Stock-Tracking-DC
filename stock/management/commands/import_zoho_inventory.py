"""
Django management command to import Zoho Inventory products
Usage: python manage.py import_zoho_inventory <path_to_csv> [--dry-run]
"""

import csv
import re
from datetime import datetime
from decimal import Decimal, InvalidOperation
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from stock.models import Product, Stock, Category, Store


class Command(BaseCommand):
    help = 'Import products and stock from Zoho Inventory CSV export'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the Zoho CSV file')
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run without making changes to the database'
        )
        parser.add_argument(
            '--skip-existing',
            action='store_true',
            help='Skip products that already exist (based on Zoho Item ID)'
        )

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        dry_run = options['dry_run']
        skip_existing = options['skip_existing']

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be saved'))

        self.stdout.write(f'Reading CSV file: {csv_file}')

        stats = {
            'total_rows': 0,
            'products_created': 0,
            'products_updated': 0,
            'products_skipped': 0,
            'stock_created': 0,
            'errors': 0,
        }

        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)

                for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
                    stats['total_rows'] += 1

                    try:
                        if dry_run:
                            self._process_row_dry_run(row, row_num, stats)
                        else:
                            with transaction.atomic():
                                self._process_row(row, row_num, stats, skip_existing)
                    except Exception as e:
                        stats['errors'] += 1
                        self.stdout.write(
                            self.style.ERROR(f'Row {row_num}: Error - {str(e)}')
                        )
                        continue

            # Print summary
            self.stdout.write('\n' + '='*60)
            self.stdout.write(self.style.SUCCESS('IMPORT SUMMARY'))
            self.stdout.write('='*60)
            self.stdout.write(f'Total rows processed: {stats["total_rows"]}')
            self.stdout.write(f'Products created: {stats["products_created"]}')
            self.stdout.write(f'Products updated: {stats["products_updated"]}')
            self.stdout.write(f'Products skipped: {stats["products_skipped"]}')
            self.stdout.write(f'Stock records created: {stats["stock_created"]}')
            self.stdout.write(self.style.ERROR(f'Errors: {stats["errors"]}'))

            if dry_run:
                self.stdout.write(self.style.WARNING('\nDRY RUN - No changes were saved'))
            else:
                self.stdout.write(self.style.SUCCESS('\nImport completed successfully!'))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File not found: {csv_file}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Fatal error: {str(e)}'))

    def _process_row(self, row, row_num, stats, skip_existing):
        """Process a single CSV row and create/update Product and Stock records"""

        # Extract Zoho Item ID
        zoho_item_id = row.get('Item ID', '').strip()
        if not zoho_item_id:
            self.stdout.write(self.style.WARNING(f'Row {row_num}: No Item ID, skipping'))
            stats['products_skipped'] += 1
            return

        # Check if product already exists
        existing_product = Product.objects.filter(zoho_item_id=zoho_item_id).first()

        if existing_product and skip_existing:
            self.stdout.write(f'Row {row_num}: Product {zoho_item_id} already exists, skipping')
            stats['products_skipped'] += 1
            return

        # Parse product name and determine condition
        item_name = row.get('Item Name', '').strip()
        warehouse_name = row.get('Warehouse Name', '').strip()

        condition, condition_suffix = self._extract_condition(item_name, warehouse_name)
        product_name = self._clean_product_name(item_name, condition_suffix)

        # Parse dates
        zoho_created = self._parse_datetime(row.get('Created Time', ''))
        zoho_modified = self._parse_datetime(row.get('Last Modified Time', ''))

        # Parse dimensions and weights
        package_weight = self._parse_decimal(row.get('Package Weight', ''))
        package_length = self._parse_decimal(row.get('Package Length', ''))
        package_width = self._parse_decimal(row.get('Package Width', ''))
        package_height = self._parse_decimal(row.get('Package Height', ''))

        # Create or update Product
        product_data = {
            'name': product_name,
            'description': row.get('Sales Description', '').strip() or None,
            'default_price_inc': Decimal('0.00'),  # Prices excluded per requirements
            'is_active': row.get('Status', '').strip().lower() == 'active',
            'sku': row.get('SKU', '').strip() or None,
            'upc': row.get('UPC', '').strip() or None,
            'ean': row.get('EAN', '').strip() or None,
            'isbn': row.get('ISBN', '').strip() or None,
            'part_number': row.get('Part Number', '').strip() or None,
            'brand': row.get('Brand', '').strip() or None,
            'manufacturer': row.get('Manufacturer', '').strip() or None,
            'sales_description': row.get('Sales Description', '').strip() or None,
            'product_type': row.get('Product Type', '').strip() or None,
            'unit': row.get('Unit', '').strip() or None,
            'package_weight': package_weight,
            'package_length': package_length,
            'package_width': package_width,
            'package_height': package_height,
            'dimension_unit': row.get('Dimension Unit', '').strip() or None,
            'weight_unit': row.get('Weight Unit', '').strip() or None,
            'zoho_item_id': zoho_item_id,
            'zoho_created_time': zoho_created,
            'zoho_last_modified': zoho_modified,
        }

        if existing_product:
            # Update existing product
            for key, value in product_data.items():
                setattr(existing_product, key, value)
            existing_product.save()
            product = existing_product
            stats['products_updated'] += 1
            self.stdout.write(f'Row {row_num}: Updated product: {product_name}')
        else:
            # Create new product
            product = Product.objects.create(**product_data)
            stats['products_created'] += 1
            self.stdout.write(self.style.SUCCESS(f'Row {row_num}: Created product: {product_name}'))

        # Create Stock record
        stock_data = self._prepare_stock_data(row, product, condition, warehouse_name)
        if stock_data:
            # Extract location and quantity before creating stock
            stock_location = stock_data.pop('_stock_location', None)
            stock_quantity = stock_data.get('quantity', 0)

            stock = Stock.objects.create(**stock_data)
            stats['stock_created'] += 1
            self.stdout.write(f'  → Created stock record: {stock.sku or "no-sku"} at {warehouse_name or "default"}')

            # Create StockLocation record if location exists
            if stock_location and stock_quantity > 0:
                from stock.models import StockLocation
                stock_location_obj = StockLocation.objects.create(
                    stock=stock,
                    store=stock_location,
                    quantity=stock_quantity,
                    aisle=stock_data.get('aisle')
                )
                self.stdout.write(f'  → Created StockLocation: {stock_location.name} with {stock_quantity} units')

    def _process_row_dry_run(self, row, row_num, stats):
        """Process a row in dry-run mode (no database changes)"""

        zoho_item_id = row.get('Item ID', '').strip()
        if not zoho_item_id:
            self.stdout.write(self.style.WARNING(f'Row {row_num}: No Item ID, would skip'))
            stats['products_skipped'] += 1
            return

        item_name = row.get('Item Name', '').strip()
        warehouse_name = row.get('Warehouse Name', '').strip()

        condition, condition_suffix = self._extract_condition(item_name, warehouse_name)
        product_name = self._clean_product_name(item_name, condition_suffix)

        existing = Product.objects.filter(zoho_item_id=zoho_item_id).exists()

        if existing:
            self.stdout.write(f'Row {row_num}: Would UPDATE product: {product_name}')
            stats['products_updated'] += 1
        else:
            self.stdout.write(f'Row {row_num}: Would CREATE product: {product_name}')
            stats['products_created'] += 1

        stats['stock_created'] += 1
        self.stdout.write(f'  → Would create stock: {condition} at {warehouse_name or "default"}')

    def _extract_condition(self, item_name, warehouse_name):
        """
        Extract condition from item name and warehouse name.
        Returns: (condition_code, condition_suffix)
        """
        # Check warehouse name for condition markers
        warehouse_lower = warehouse_name.lower()

        if 'b-stock' in warehouse_lower or 'bstock' in warehouse_lower:
            return 'bstock', 'Bstock'
        elif 'open box' in warehouse_lower or 'openbox' in warehouse_lower:
            return 'open_box', 'Open Box'
        elif 'ex-demo' in warehouse_lower or 'demo' in warehouse_lower:
            return 'demo_unit', 'Demo'
        elif 'refurb' in warehouse_lower or 'refurbished' in warehouse_lower:
            return 'refurbished', 'Refurbished'

        # Check item name for condition markers
        item_lower = item_name.lower()
        if 'b-stock' in item_lower or 'bstock' in item_lower:
            return 'bstock', 'Bstock'
        elif 'demo' in item_lower:
            return 'demo_unit', 'Demo'
        elif 'open box' in item_lower:
            return 'open_box', 'Open Box'
        elif 'refurb' in item_lower:
            return 'refurbished', 'Refurbished'

        return 'new', ''

    def _clean_product_name(self, item_name, condition_suffix):
        """
        Clean product name and add condition suffix if applicable.
        """
        # Remove existing condition markers from name
        name = item_name
        patterns = [
            r'\s*-?\s*b-?stock\s*',
            r'\s*-?\s*demo\s*',
            r'\s*-?\s*open\s*box\s*',
            r'\s*-?\s*refurb(?:ished)?\s*',
        ]
        for pattern in patterns:
            name = re.sub(pattern, ' ', name, flags=re.IGNORECASE)

        # Clean up extra spaces and hyphens
        name = re.sub(r'\s+', ' ', name).strip()
        name = re.sub(r'\s*-\s*$', '', name)  # Remove trailing dash

        # Add condition suffix if not 'new'
        if condition_suffix:
            return f"{name} - {condition_suffix}"
        return name

    def _parse_datetime(self, date_str):
        """Parse datetime string from Zoho"""
        if not date_str or date_str.strip() == '':
            return None

        try:
            # Zoho format: "2022-06-24 11:38:16"
            dt = datetime.strptime(date_str.strip(), '%Y-%m-%d %H:%M:%S')
            return timezone.make_aware(dt)
        except ValueError:
            return None

    def _parse_decimal(self, value_str):
        """Parse decimal value, removing currency symbols and commas"""
        if not value_str or value_str.strip() == '':
            return None

        try:
            # Remove currency symbols, commas, and whitespace
            cleaned = re.sub(r'[AUD$,\s]', '', value_str)
            if cleaned == '' or cleaned == '0':
                return None
            return Decimal(cleaned)
        except (InvalidOperation, ValueError):
            return None

    def _parse_int(self, value_str):
        """Parse integer value"""
        if not value_str or value_str.strip() == '':
            return 0

        try:
            cleaned = re.sub(r'[,\s]', '', str(value_str))
            return int(float(cleaned))
        except (ValueError, TypeError):
            return 0

    def _extract_aisle_from_sku(self, sku_str):
        """
        Extract aisle location from SKU field.
        Examples: "A4-1" -> "A4-1", "B 1-5" -> "B1-5"
        """
        if not sku_str:
            return None

        # Match patterns like "A4-1", "B 1-5", etc.
        match = re.search(r'([A-Z]\s*\d+\s*-\s*\d+)', sku_str, re.IGNORECASE)
        if match:
            # Clean up spaces
            aisle = re.sub(r'\s+', '', match.group(1))
            return aisle

        return None

    def _prepare_stock_data(self, row, product, condition, warehouse_name):
        """Prepare stock data dictionary"""

        # Parse quantities
        opening_stock = self._parse_int(row.get('Opening Stock', '0'))
        stock_on_hand = self._parse_int(row.get('Stock On Hand', '0'))

        # Get or create default warehouse/location
        location = None
        if warehouse_name:
            # Try to find existing store/warehouse by name
            location = Store.objects.filter(name__icontains=warehouse_name.split('-')[0].strip()).first()

            if not location:
                # Create a default location if warehouse name is provided
                location, created = Store.objects.get_or_create(
                    name='Silverwater',
                    defaults={
                        'designation': 'warehouse',
                        'location': 'Silverwater, NSW',
                        'is_active': True,
                    }
                )

        # Extract aisle from SKU field
        sku_field = row.get('SKU', '').strip()
        aisle = self._extract_aisle_from_sku(sku_field)

        # Generate unique SKU for this stock item
        # Use Zoho SKU if available, otherwise generate from product
        stock_sku = None
        if sku_field and sku_field not in ['', ' ']:
            # Clean SKU field - remove spaces
            stock_sku = re.sub(r'\s+', '', sku_field)
        else:
            # Generate SKU from product info
            if product.sku:
                stock_sku = f"{product.sku}-{condition}"

        # Create stock data
        stock_data = {
            'product': product,
            'item_name': product.name,
            'sku': stock_sku,
            'quantity': stock_on_hand,
            'opening_stock': opening_stock,
            'stock_on_hand': stock_on_hand,
            'condition': condition,
            'warehouse_name': warehouse_name or None,
            'location': location,
            'aisle': aisle,
            're_order': 0,  # Will be set separately if needed
            'last_updated': timezone.now(),
            'timestamp': timezone.now(),
            'date': timezone.now(),
            'export_to_csv': False,
            '_stock_location': location,  # Store location for StockLocation creation
        }

        return stock_data

    def _get_or_create_category(self, category_name):
        """Get or create category"""
        if not category_name or category_name.strip() == '':
            return None

        category, created = Category.objects.get_or_create(
            group=category_name.strip()
        )
        return category
