import sys
import os
import traceback

print(f"Python version: {sys.version}")
print(f"Executable: {sys.executable}")

try:
    import whisper
    print("Whisper imported successfully!")
except ImportError:
    print("Failed to import whisper (ImportError).")
    traceback.print_exc()
except Exception:
    print("Failed to import whisper (Exception).")
    traceback.print_exc()

try:
    import torch
    print(f"Torch imported successfully! Version: {torch.__version__}")
except ImportError:
    print("Failed to import torch.")
    traceback.print_exc()
