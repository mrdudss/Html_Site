from textnode import *
from filenode import *
import shutil, os, subprocess
def main():
    if os.path.exists("/root/repo/Html_Site/public"):
        shutil.rmtree("/root/repo/Html_Site/public")
    os.mkdir("/root/repo/Html_Site/public" ,mode=0o777)
    for items in os.listdir("/root/repo/Html_Site/static"):
        paths = f"/root/repo/Html_Site/static/{items}"
        if os.path.isdir(paths):
            search_dir(paths, 6)
        elif os.path.isfile(paths):
            shutil.copy(f"/root/repo/Html_Site/static/{items}", "/root/repo/Html_Site/public")
    generate_pages_recursive("content", "template.html", "public/index.html")
    subprocess.run(["python3", "-m", "http.server", "8888"], cwd="public", check=True)
main()

