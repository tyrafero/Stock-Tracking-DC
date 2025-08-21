from django.conf import settings
from stock.models import Stock

print(f"DEBUG: {settings.DEBUG}")
print(f"DEFAULT_FILE_STORAGE: {getattr(settings, 'DEFAULT_FILE_STORAGE', 'Default Django FileSystemStorage')}")

# Test with your latest stock
latest_stock = Stock.objects.latest('id')
print(f"Latest stock: {latest_stock.item_name}")
print(f"Has image: {bool(latest_stock.image)}")
if latest_stock.image:
    print(f"Image name: {latest_stock.image.name}")
    print(f"Image URL: {latest_stock.image.url}")