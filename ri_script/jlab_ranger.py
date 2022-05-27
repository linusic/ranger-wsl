import sys
import re
import subprocess
from urllib.parse import quote
from pathlib import Path

root_dir = "/" # the script is init starting in root_dir   
jl_cmd = f'"jupyter lab --no-browser --allow-root {root_dir}"'
chrome = "/mnt/c/Program\ Files/Google/Chrome/Application/chrome.exe"
# edge = "/mnt/c/Program\ Files\ \(x86\)/Microsoft/Edge/Application/msedge.exe --start-fullscreen"
pm2 = "/usr/local/lib/nodejs/node-v16.13.1-linux-x64/bin/pm2"

store_url_file_name = ".jlab_init_url"
_store_url_path = Path.home().joinpath(store_url_file_name)

# list
res = subprocess.run(f'{pm2} list', shell=True, stdout=subprocess.PIPE) 

logs = res.stdout.decode('utf-8')   
if "jl" in logs:  
    _store_url_str = _store_url_path.read_bytes().decode("utf-8")  # http://localhost:8888/lab

    if len(sys.argv) > 1:
        file_path = sys.argv[1] # had with / prefix . eg: /mnt 
        url = _store_url_str + "/tree" + quote(file_path)

        print(url)
    else:
        url = f"{http_domain}:{port}/lab/tree/mnt/d"

    res = subprocess.run(f'{chrome} {url}', shell=True, stdout=subprocess.PIPE) 
else:
    res = subprocess.run(f'{pm2} start  {jl_cmd} --name jl && sleep 2 && {pm2} logs  --nostream --lines 10', shell=True, stdout=subprocess.PIPE)
    logs = res.stdout.decode('utf-8')   
    r = re.compile(r"http://.*")
    url = r.findall(logs)[0]

    _store_url_path.write_bytes(url.encode("utf-8"))