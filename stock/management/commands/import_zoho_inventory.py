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
from django.utils.text import slugify
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
        parser.add_argument(
            '--clear-stocks',
            action='store_true',
            help='Clear all existing stock records before import'
        )

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        dry_run = options['dry_run']
        skip_existing = options['skip_existing']
        clear_stocks = options['clear_stocks']

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be saved'))

        if clear_stocks and not dry_run:
            self.stdout.write(self.style.WARNING('Clearing all existing stock records...'))
            Stock.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Stock records cleared'))

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
                        import traceback
                        traceback.print_exc()
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
            import traceback
            traceback.print_exc()

    def _generate_sku(self, item_name):
        """
        Generate SKU from item name by slugifying it.
        Example: "Denon X4800H Receiver" -> "denon-x4800h-receiver"
        Max length: 90 characters (to leave room for suffixes like -bstock, -silverwater)
        """
        if not item_name:
            return None

        # Remove special characters and clean up the name
        clean_name = re.sub(r'[|/]', ' ', item_name)  # Replace | and / with spaces
        clean_name = re.sub(r'\s+', ' ', clean_name).strip()  # Normalize spaces

        # Slugify first
        sku = slugify(clean_name)

        # Truncate to max 90 chars (leaving room for suffixes)
        # Try to cut at word boundary (hyphen)
        max_length = 90
        if len(sku) > max_length:
            truncated = sku[:max_length]
            # Try to cut at last hyphen to keep words intact
            last_hyphen = truncated.rfind('-')
            if last_hyphen > 60:  # Only if we have at least 60 chars
                sku = truncated[:last_hyphen]
            else:
                sku = truncated

        return sku if sku else None

    def _parse_location_from_sku_field(self, sku_field):
        """
        Parse location/aisle information from the SKU field.
        The SKU field in CSV actually contains location info like:
        - "A 1-1"
        - "B 1-5"
        - "(OpenBox #84-Unit 3 upstairs)"
        - "A 1-1 / AJ-Comp Room demo"

        Returns: (aisle, note)
        """
        if not sku_field or sku_field.strip() == '':
            return None, None

        sku_field = sku_field.strip()

        # Try to extract aisle pattern (e.g., "A 1-1", "B 1-5")
        aisle_match = re.search(r'([A-Z]\s*\d+\s*-\s*\d+)', sku_field, re.IGNORECASE)

        aisle = None
        note = None

        if aisle_match:
            # Clean up the aisle (remove extra spaces)
            aisle = re.sub(r'\s+', '', aisle_match.group(1))

            # The rest might be a note
            remainder = sku_field.replace(aisle_match.group(1), '').strip()
            remainder = remainder.strip('/')
            if remainder:
                note = remainder
        else:
            # No aisle pattern found, treat entire field as note/location description
            note = sku_field

        return aisle, note

    def _process_row(self, row, row_num, stats, skip_existing):
        """Process a single CSV row and create/update Product and Stock records"""

        # Extract Zoho Item ID
        zoho_item_id = row.get('Item ID', '').strip()
        if not zoho_item_id:
            self.stdout.write(self.style.WARNING(f'Row {row_num}: No Item ID, skipping'))
            stats['products_skipped'] += 1
            return

        # Parse product name and determine condition
        item_name = row.get('Item Name', '').strip()
        if not item_name:
            self.stdout.write(self.style.WARNING(f'Row {row_num}: No Item Name, skipping'))
            stats['products_skipped'] += 1
            return

        warehouse_name = row.get('Warehouse Name', '').strip()

        condition, condition_suffix = self._extract_condition(item_name, warehouse_name)
        product_name = self._clean_product_name(item_name, condition_suffix)

        # Generate SKU from product name
        generated_sku = self._generate_sku(product_name)

        # Check if product already exists by Zoho Item ID
        existing_product = Product.objects.filter(zoho_item_id=zoho_item_id).first()

        # If no product found by Zoho ID, try by generated SKU
        if not existing_product and generated_sku:
            existing_product = Product.objects.filter(sku=generated_sku).first()

        if existing_product and skip_existing:
            self.stdout.write(f'Row {row_num}: Product {zoho_item_id} already exists, skipping')
            stats['products_skipped'] += 1
            return

        # Parse dates
        zoho_created = self._parse_datetime(row.get('Created Time', ''))
        zoho_modified = self._parse_datetime(row.get('Last Modified Time', ''))

        # Parse dimensions and weights
        package_weight = self._parse_decimal(row.get('Package Weight', ''))
        package_length = self._parse_decimal(row.get('Package Length', ''))
        package_width = self._parse_decimal(row.get('Package Width', ''))
        package_height = self._parse_decimal(row.get('Package Height', ''))

        # Get category from CF.Categories
        category_name = row.get('CF.Categories', '').strip()
        category = self._get_or_create_category(category_name) if category_name else None

        # Create or update Product
        product_data = {
            'name': product_name,
            'description': row.get('Sales Description', '').strip() or None,
            'default_price_inc': Decimal('0.00'),  # Prices excluded per requirements
            'is_active': row.get('Status', '').strip().lower() == 'active',
            'sku': generated_sku,  # Use generated SKU
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
            self.stdout.write(f'Row {row_num}: Updated product: {product_name} (SKU: {generated_sku})')
        else:
            # Create new product
            product = Product.objects.create(**product_data)
            stats['products_created'] += 1
            self.stdout.write(self.style.SUCCESS(f'Row {row_num}: Created product: {product_name} (SKU: {generated_sku})'))

        # Create Stock record
        stock_data = self._prepare_stock_data(row, product, condition, warehouse_name, category)
        if stock_data:
            # Extract location and quantity before creating stock
            stock_location = stock_data.pop('_stock_location', None)
            stock_quantity = stock_data.get('quantity', 0)

            stock = Stock.objects.create(**stock_data)
            stats['stock_created'] += 1

            location_info = f"{stock.aisle} at {warehouse_name}" if stock.aisle else warehouse_name or "default"
            self.stdout.write(f'  → Created stock: {stock.sku or "no-sku"} | Qty: {stock_quantity} | Location: {location_info}')

            # Create StockLocation record if location exists
            if stock_location and stock_quantity > 0:
                from stock.models import StockLocation
                stock_location_obj, created = StockLocation.objects.get_or_create(
                    stock=stock,
                    store=stock_location,
                    defaults={
                        'quantity': stock_quantity,
                        'aisle': stock_data.get('aisle')
                    }
                )
                if not created:
                    # Update existing location
                    stock_location_obj.quantity = stock_quantity
                    stock_location_obj.aisle = stock_data.get('aisle')
                    stock_location_obj.save()

                self.stdout.write(f'  → StockLocation: {stock_location.name} ({stock_location_obj.quantity} units)')

    def _process_row_dry_run(self, row, row_num, stats):
        """Process a row in dry-run mode (no database changes)"""

        zoho_item_id = row.get('Item ID', '').strip()
        if not zoho_item_id:
            self.stdout.write(self.style.WARNING(f'Row {row_num}: No Item ID, would skip'))
            stats['products_skipped'] += 1
            return

        item_name = row.get('Item Name', '').strip()
        warehouse_name = row.get('Warehouse Name', '').strip()
        sku_field = row.get('SKU', '').strip()

        condition, condition_suffix = self._extract_condition(item_name, warehouse_name)
        product_name = self._clean_product_name(item_name, condition_suffix)
        generated_sku = self._generate_sku(product_name)
        aisle, note = self._parse_location_from_sku_field(sku_field)

        existing = Product.objects.filter(zoho_item_id=zoho_item_id).exists()

        if existing:
            self.stdout.write(f'Row {row_num}: Would UPDATE product: {product_name} (SKU: {generated_sku})')
            stats['products_updated'] += 1
        else:
            self.stdout.write(f'Row {row_num}: Would CREATE product: {product_name} (SKU: {generated_sku})')
            stats['products_created'] += 1

        stats['stock_created'] += 1
        location_info = f"Aisle: {aisle}" if aisle else "No aisle"
        if note:
            location_info += f" | Note: {note}"
        self.stdout.write(f'  → Would create stock: {condition} at {warehouse_name or "default"} | {location_info}')

    def _extract_condition(self, item_name, warehouse_name):
        """
        Extract condition from item name and warehouse name.
        Returns: (condition_code, condition_suffix)
        """
        # Check warehouse name for condition markers
        warehouse_lower = warehouse_name.lower()

        if 'b-stock' in warehouse_lower or 'bstock' in warehouse_lower:
            return 'bstock', ''  # Don't add suffix, condition is in warehouse
        elif 'open box' in warehouse_lower or 'openbox' in warehouse_lower:
            return 'open_box', ''
        elif 'ex-demo' in warehouse_lower or 'demo' in warehouse_lower:
            return 'demo_unit', ''
        elif 'refurb' in warehouse_lower or 'refurbished' in warehouse_lower:
            return 'refurbished', ''

        # Check item name for condition markers
        item_lower = item_name.lower()
        if 'b-stock' in item_lower or 'bstock' in item_lower:
            return 'bstock', 'B-Stock'
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

        # Add condition suffix if provided
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

    def _prepare_stock_data(self, row, product, condition, warehouse_name, category):
        """Prepare stock data dictionary"""

        # Parse quantities
        opening_stock = self._parse_int(row.get('Opening Stock', '0'))
        stock_on_hand = self._parse_int(row.get('Stock On Hand', '0'))

        # Get or create warehouse/location
        location = None
        main_warehouse = None

        if warehouse_name:
            # Parse warehouse name to get the main location
            # Example: "Silverwater - [ B-Stock / Open Box / Ex- Demo / Refurb]" -> "Silverwater"
            main_warehouse = warehouse_name.split('-')[0].strip()
        else:
            # Default warehouse for items without warehouse name
            main_warehouse = 'Main Warehouse'

        # Try to find existing store/warehouse by name
        location = Store.objects.filter(name__icontains=main_warehouse).first()

        if not location:
            # Create a new warehouse if it doesn't exist
            location, created = Store.objects.get_or_create(
                name=main_warehouse,
                defaults={
                    'designation': 'warehouse',
                    'location': f'{main_warehouse}, NSW',
                    'is_active': True,
                }
            )
            if created:
                self.stdout.write(f'    Created new warehouse: {main_warehouse}')

        # Parse location/aisle from SKU field
        sku_field = row.get('SKU', '').strip()
        aisle, location_note = self._parse_location_from_sku_field(sku_field)

        # Generate unique stock SKU
        # Format: product-sku-condition (e.g., "denon-x4800h-receiver-new")
        stock_sku = None
        if product.sku:
            if condition and condition != 'new':
                stock_sku = f"{product.sku}-{condition}"
            else:
                stock_sku = product.sku

            # Ensure SKU doesn't exceed 100 chars
            if len(stock_sku) > 100:
                stock_sku = stock_sku[:100]

            # Make SKU unique by adding warehouse if duplicate
            if Stock.objects.filter(sku=stock_sku).exists():
                if location:
                    warehouse_slug = slugify(location.name)
                    # Calculate available space for warehouse suffix
                    max_base_length = 100 - len(warehouse_slug) - 1  # -1 for hyphen
                    if len(stock_sku) > max_base_length:
                        stock_sku = stock_sku[:max_base_length]
                    stock_sku = f"{stock_sku}-{warehouse_slug}"

        # Combine notes
        combined_note = location_note if location_note else None

        # Create stock data
        stock_data = {
            'product': product,
            'category': category,
            'item_name': product.name,
            'sku': stock_sku,
            'quantity': stock_on_hand,
            'opening_stock': opening_stock,
            'stock_on_hand': stock_on_hand,
            'condition': condition,
            'warehouse_name': warehouse_name or None,
            'location': location,
            'aisle': aisle,
            'note': combined_note,
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
        if created:
            self.stdout.write(f'    Created new category: {category_name}')
        return category
