"""
Django management command to create missing StockLocation records
Usage: python manage.py fix_stock_locations [--dry-run]
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from stock.models import Stock, StockLocation, Store


class Command(BaseCommand):
    help = 'Create StockLocation records for stock items that are missing them'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run without making changes to the database'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be saved'))

        # Get all stock items without StockLocation records
        stocks_without_locations = Stock.objects.filter(locations__isnull=True).distinct()

        total_stock = stocks_without_locations.count()
        self.stdout.write(f'Found {total_stock} stock items without StockLocation records')

        created_count = 0
        skipped_count = 0
        error_count = 0

        for stock in stocks_without_locations:
            try:
                # Determine which location to use
                location = None

                # Option 1: Use the stock's location ForeignKey
                if stock.location:
                    location = stock.location
                # Option 2: Try to find location by warehouse_name
                elif stock.warehouse_name:
                    location = Store.objects.filter(name__icontains=stock.warehouse_name.split('-')[0].strip()).first()

                # Option 3: Get or create a default location
                if not location:
                    if dry_run:
                        self.stdout.write(f'  Would skip {stock.item_name} - no location found')
                        skipped_count += 1
                        continue
                    else:
                        # Create default location
                        location, _ = Store.objects.get_or_create(
                            name='Silverwater Warehouse',
                            defaults={
                                'designation': 'warehouse',
                                'location': 'Silverwater, NSW',
                                'is_active': True,
                            }
                        )

                # Only create StockLocation if stock has quantity
                if stock.quantity and stock.quantity > 0:
                    if dry_run:
                        self.stdout.write(
                            f'  Would create StockLocation: {stock.item_name} at {location.name} ({stock.quantity} units)'
                        )
                        created_count += 1
                    else:
                        with transaction.atomic():
                            # Check if StockLocation already exists
                            existing = StockLocation.objects.filter(
                                stock=stock,
                                store=location
                            ).first()

                            if not existing:
                                StockLocation.objects.create(
                                    stock=stock,
                                    store=location,
                                    quantity=stock.quantity,
                                    aisle=stock.aisle
                                )
                                created_count += 1
                                self.stdout.write(
                                    self.style.SUCCESS(
                                        f'  Created StockLocation: {stock.item_name} at {location.name} ({stock.quantity} units)'
                                    )
                                )
                            else:
                                # Update existing
                                existing.quantity = stock.quantity
                                existing.aisle = stock.aisle
                                existing.save()
                                self.stdout.write(
                                    f'  Updated existing StockLocation: {stock.item_name} at {location.name}'
                                )
                else:
                    # Skip items with 0 or no quantity
                    skipped_count += 1
                    if dry_run:
                        self.stdout.write(f'  Would skip {stock.item_name} - quantity is 0')

            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f'  Error processing {stock.item_name}: {str(e)}')
                )

        # Print summary
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('FIX SUMMARY'))
        self.stdout.write('='*60)
        self.stdout.write(f'Total stock items without locations: {total_stock}')
        self.stdout.write(f'StockLocations created: {created_count}')
        self.stdout.write(f'Items skipped (0 quantity or no location): {skipped_count}')
        self.stdout.write(f'Errors: {error_count}')

        if dry_run:
            self.stdout.write(self.style.WARNING('\nDRY RUN - No changes were saved'))
        else:
            self.stdout.write(self.style.SUCCESS('\nFix completed successfully!'))
