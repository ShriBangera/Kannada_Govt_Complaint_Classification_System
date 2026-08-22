import subprocess
import sys

packages = ['mysql-connector-python']

for package in packages:
    print(f"Installing {package}...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

print("✓ All dependencies installed successfully!")
