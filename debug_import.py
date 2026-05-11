import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'comic_web.settings')
django.setup()

try:
    from core import utils
    print("Import successful")
except Exception as e:
    print(f"Import failed: {e}")
    import traceback
    traceback.print_exc()
