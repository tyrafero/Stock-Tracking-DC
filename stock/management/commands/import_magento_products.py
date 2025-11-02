import csv
import re
from decimal import Decimal, InvalidOperation
from django.core.management.base import BaseCommand
from django.db import transaction
from stock.models import Stock, Product, Category


class Command(BaseCommand):
    help = 'Import products from Magento CSV export'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the Magento CSV file')
        parser.add_argument('--dry-run', action='store_true', help='Preview import without saving')

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        dry_run = options['dry_run']

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No data will be saved'))

        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)

                created_products = 0
                updated_products = 0
                created_stock = 0
                updated_stock = 0
                skipped = 0

                with transaction.atomic():
                    for row in csv_reader:
                        try:
                            result = self.process_row(row, dry_run)
                            if result['action'] == 'created_product':
                                created_products += 1
                            elif result['action'] == 'updated_product':
                                updated_products += 1
                            elif result['action'] == 'created_stock':
                                created_stock += 1
                            elif result['action'] == 'updated_stock':
                                updated_stock += 1
                            elif result['action'] == 'skipped':
                                skipped += 1

                        except Exception as e:
                            self.stdout.write(
                                self.style.ERROR(f'Error processing row with SKU {row.get("sku", "Unknown")}: {str(e)}')
                            )
                            skipped += 1
                            continue

                    if dry_run:
                        # Rollback transaction in dry run mode
                        transaction.set_rollback(True)

                self.stdout.write(
                    self.style.SUCCESS(
                        f'Import completed!\n'
                        f'Products created: {created_products}\n'
                        f'Products updated: {updated_products}\n'
                        f'Stock items created: {created_stock}\n'
                        f'Stock items updated: {updated_stock}\n'
                        f'Skipped: {skipped}'
                    )
                )

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File not found: {csv_file}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error reading file: {str(e)}'))

    def process_row(self, row, dry_run=False):
        sku = row.get('sku', '').strip()
        name = row.get('name', '').strip()

        # Skip rows without SKU or name
        if not sku or not name:
            return {'action': 'skipped', 'reason': 'Missing SKU or name'}

        # Skip virtual products (warranties, etc.)
        if row.get('product_type') == 'virtual':
            return {'action': 'skipped', 'reason': 'Virtual product'}

        # Extract data from CSV
        description = self.clean_html(row.get('description', ''))
        price = self.parse_decimal(row.get('price', '0'))
        qty = self.parse_int(row.get('qty', '0'))
        categories = row.get('categories', '')
        image_path = row.get('base_image', '')

        # Build full image URL
        image_url = self.build_image_url(image_path)

        # Handle categories
        category = self.get_or_create_category(categories)

        # Create/Update Product
        product, product_created = Product.objects.get_or_create(
            name=name[:200],  # Truncate to Product model max_length
            defaults={
                'description': description[:500] if description else '',  # Limit length
                'default_price_inc': price,
                'is_active': row.get('product_online') == '1'
            }
        )

        if not product_created and not dry_run:
            # Update existing product
            product.name = name[:200]  # Ensure name is truncated on updates too
            product.description = description[:500] if description else ''
            product.default_price_inc = price
            product.is_active = row.get('product_online') == '1'
            product.save()

        # Create/Update Stock
        stock, stock_created = Stock.objects.get_or_create(
            sku=sku,
            defaults={
                'item_name': name[:50],  # Limit to field max length
                'quantity': qty,
                'category': category,
                'image_url': image_url if image_url else None,
                'created_by': 'magento_import'
            }
        )

        if not stock_created and not dry_run:
            # Update existing stock
            stock.item_name = name[:50]
            stock.quantity = qty
            stock.category = category
            stock.image_url = image_url if image_url else None
            stock.save()

        if dry_run:
            self.stdout.write(f'Would process: {sku} - {name} (Qty: {qty})')

        if product_created:
            return {'action': 'created_product'}
        elif stock_created:
            return {'action': 'created_stock'}
        else:
            return {'action': 'updated_stock'}

    def get_or_create_category(self, categories_string):
        """Extract and create category from Magento categories string"""
        if not categories_string:
            return None

        # Magento categories are usually in format like "Inventory/Projectors/Home theatre/Projectors"
        # Take the last part as the category name
        categories = categories_string.split(',')[0]  # Take first category if multiple
        if '/' in categories:
            category_name = categories.split('/')[-1].strip()
        else:
            category_name = categories.strip()

        if category_name and len(category_name) <= 50:  # Category model max_length
            category, created = Category.objects.get_or_create(
                group=category_name[:50]  # Category model uses 'group' field, not 'name'
            )
            return category
        return None

    def clean_html(self, text):
        """Remove HTML tags and clean text"""
        if not text:
            return ''

        # Remove HTML tags
        clean = re.sub('<.*?>', '', text)
        # Remove extra whitespace
        clean = ' '.join(clean.split())
        # Remove quotes and other problematic characters
        clean = clean.replace('""', '"').replace('&lt;', '<').replace('&gt;', '>')
        return clean

    def parse_decimal(self, value):
        """Safely parse decimal value"""
        try:
            return Decimal(str(value))
        except (InvalidOperation, ValueError):
            return Decimal('0.00')

    def parse_int(self, value):
        """Safely parse integer value"""
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return 0

    def build_image_url(self, image_path):
        """Build full image URL from Magento image path"""
        if not image_path or image_path.strip() == '':
            return None

        # Remove leading slash if present
        clean_path = image_path.lstrip('/')

        # Build full URL
        base_url = 'https://www.digitalcinema.com.au/media/catalog/product/cache/dd4850ad4231b6306bceadf38a0bbeed'
        return f"{base_url}{clean_path}"