import sys
from pathlib import Path

for file_path in sys.argv[1:]:
#    path = f'{file_path[5]}:/{file_path[7:]}'
#    print(f'"{path}"')
    print(f'"{Path(file_path).name}"')
