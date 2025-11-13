from textnode import *
import shutil
import os

def search_dir(paths, level):
    src_root = "/root/repo/Html_Site/static"
    dst_root = "/root/repo/Html_Site/public"

    rel = os.path.relpath(paths, src_root) 
    new_path = os.path.join(dst_root, rel)         
    os.makedirs(new_path, exist_ok=True)
    for items in os.listdir(paths):
        itempaths = f"{paths}/{items}"
        if os.path.isdir(itempaths):
            search_dir(itempaths, level+1)
        elif os.path.isfile(itempaths):
            shutil.copy(itempaths, new_path)

def generate_page(from_path, template_path, dest_path):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    with open(from_path) as f:
         markdown = f.read()
    with open(template_path) as f:
         template = f.read()
    htmlnode = markdown_to_html_node(markdown)
    html = htmlnode.to_html()
    title = extract_title(markdown)
    final = template.replace("{{ Title }}", title)
    final = final.replace("{{ Content }}", html)
    with open(dest_path, "w") as file:
        file.write(final)

def generate_pages_recursive(dir_path_content, template_path, dest_dir_path):
    src_root = "/root/repo/Html_Site/content"
    dst_root = "/root/repo/Html_Site/public"

    rel = os.path.relpath(dir_path_content, src_root) 
    new_path = os.path.join(dst_root, rel)         
    os.makedirs(new_path, exist_ok=True)
    for items in os.listdir(dir_path_content):
        itempath = os.path.join(dir_path_content, items) 
        if os.path.isdir(itempath):
            generate_pages_recursive(itempath, template_path, dest_dir_path)
        elif os.path.isfile(itempath):
            print(f"Generating page from {dir_path_content} to {dest_dir_path} using {template_path}")
            with open(itempath) as f:
                markdown = f.read()
            with open(template_path) as f:
                template = f.read()
            htmlnode = markdown_to_html_node(markdown)
            html = htmlnode.to_html()
            title = extract_title(markdown)
            final = template.replace("{{ Title }}", title)
            final = final.replace("{{ Content }}", html)
            with open(f"{new_path}/index.html", "w") as file:
                file.write(final)