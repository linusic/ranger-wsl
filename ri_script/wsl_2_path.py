import sys

for file_path in sys.argv[1:]:
    path = f'{file_path[5]}:/{file_path[7:]}'
    print(f'"{path}"')
