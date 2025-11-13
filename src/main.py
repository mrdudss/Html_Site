from textnode import *
from filenode import *
import shutil, os, subprocess, sys
def main():
    basepath = sys.argv[1]
    if os.path.exists("/root/repo/Html_Site/docs"):
        shutil.rmtree("/root/repo/Html_Site/docs")
    os.mkdir("/root/repo/Html_Site/docs" ,mode=0o777)
    for items in os.listdir("/root/repo/Html_Site/static"):
        paths = f"/root/repo/Html_Site/static/{items}"
        if os.path.isdir(paths):
            search_dir(paths, 6)
        elif os.path.isfile(paths):
            shutil.copy(f"/root/repo/Html_Site/static/{items}", "/root/repo/Html_Site/docs")
    generate_pages_recursive("content", "template.html", "docs", basepath,"/root/repo/Html_Site")
    subprocess.run(["python3", "-m", "http.server", "8888"], cwd="public", check=True)
main()

