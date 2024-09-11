import sys
from pathlib import Path

p = Path('.')
print(sys.path)
sys.path.append(f'{p}/api')