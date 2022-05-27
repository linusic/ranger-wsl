import sys
from urllib.parse import quote

for file_path in sys.argv[1:]:
    url_str = f'file:///{file_path[5]}:/{quote(file_path[7:])}'
    print(f'"{url_str}"')
