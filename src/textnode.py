from enum import Enum
import re
#ENUMS-----------------------------------------------------
class BlockType(Enum):
    PARAGRAPH = "p"
    HEADING = "h"
    CODE = "code"
    QUOTE = "blockquote"
    ULIST = "ul"
    OLIST = "ol"
class TextType(Enum):
    TEXT = "text"
    BOLD = "bold"
    ITALIC = "italic"
    CODE = "code"
    LINK = "link"
    IMAGE = "image"

class TextNode:
    def __init__(self, text, text_type, url=None):
        self.text = text
        self.text_type = text_type
        self.url = url
    def __eq__(self, node):
        return (
            self.text == node.text 
            and self.text_type == node.text_type 
            and self.url == node.url
        )
    def __repr__(self):
        return f"TextNode({self.text}, {self.text_type}, {self.url})"
class HTMLNode:
    def __init__(self, tag=None, value=None, children=None, props=None):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def __repr__(self):
        return f"HTMLNode({self.tag}, {self.value}, children: {self.children}, {self.props})"
    
    def to_html(self):
        raise NotImplementedError("to_html method not implemented")

    def props_to_html(self):
        full_string = ""
        if self.props == None:
            return ""
        for item,value in self.props.items():
            string = f' {item}="{value}"'
            full_string = full_string+string
        return full_string
class LeafNode(HTMLNode):
    def __init__(self, tag, value, props=None):
        super().__init__(tag, value, None, props)

    def to_html(self):
        if self.value is None:
            raise ValueError("invalid HTML: no value")
        if self.tag is None:
            return f"{self.value}"
        return f"<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>"
    
    def __repr__(self):
        return f"LeafNode({self.tag}, {self.value}, {self.props})"
class ParentNode(HTMLNode):
    def __init__(self, tag, children, props=None):
        super().__init__(tag, None, children, props)

    def to_html(self):
        if self.tag is None:
            raise ValueError("invalid HTML: no tag")
        if self.children is None:
            raise ValueError("invalid HTML: no children")
        full_value=""
        for leaf in self.children:
            temp = leaf.to_html()
            full_value= full_value+temp
        return f"<{self.tag}{self.props_to_html()}>{full_value}</{self.tag}>"
    
    def __repr__(self):
        return f"ParentNode({self.tag}, children: {self.children}, {self.props})"
#functions# NODE----------------------------------------------
def text_to_textnodes(text):
    list_nodes = [TextNode(text, TextType.TEXT)]
    list_nodes = split_nodes_delimiter(list_nodes, "**", TextType.BOLD)
    list_nodes = split_nodes_delimiter(list_nodes, "_", TextType.ITALIC)
    list_nodes = split_nodes_delimiter(list_nodes, "`", TextType.CODE)
    list_nodes = split_nodes_image(list_nodes)
    list_nodes = split_nodes_link(list_nodes)
    return list_nodes

def text_node_to_html_node(text_node):
    match text_node.text_type:
        case TextType.TEXT:
            return LeafNode(None, text_node.text)
        case TextType.BOLD:
            return LeafNode("b", text_node.text)
        case TextType.ITALIC:
            return LeafNode("i", text_node.text)
        case TextType.CODE:
            return LeafNode("code", text_node.text)
        case TextType.LINK:
            return LeafNode("a", text_node.text, props={"href": {text_node.url}})
        case TextType.IMAGE:
            return LeafNode("img", "", props={"src": text_node.url, "alt": text_node.text})
        case _:
            return LeafNode(None, text_node.text)

def split_nodes_delimiter(old_nodes, delimiter, text_type):
    list_txt = []
    for nodes in old_nodes:
        if nodes.text_type != TextType.TEXT:
            list_txt.append(nodes)
            continue
        list_textnode = nodes.text.split(delimiter)
        if len(list_textnode) % 2 == 0:
            raise ValueError("invalid markdown, formatted section not closed")
        odd = True
        while len(list_textnode) != 0:
            if odd == True:
                temp = list_textnode.pop(0)
                if temp != "":
                    new_node = TextNode(temp, TextType.TEXT)
                    list_txt.append(new_node)
                odd = False
            elif odd == False:
                temp = list_textnode.pop(0)
                new_node = TextNode(temp, text_type)
                list_txt.append(new_node)
                odd = True
    return list_txt

def extract_markdown_images(text):
    return re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
def extract_markdown_links(text):
    return re.findall(r"(?<!\!)\[([^\[\]]*)\]\(([^\(\)]*)\)", text)

def split_nodes_image(old_nodes):
    list_txt = []
    for nodes in old_nodes:
        if nodes.text_type != TextType.TEXT:
            list_txt.append(nodes)
            continue
        matches = extract_markdown_images(nodes.text)
        if len(matches) == 0:
            list_txt.append(nodes)
            continue
        list_textnode = []
        for i in range(len(matches)):
            if i == 0:
                list_textnode = nodes.text.split(f"![{matches[i][0]}]({matches[i][1]})")
            elif i > 0:
                temp = [] + list_textnode
                list_textnode.pop()
                list_textnode += temp[1].split(f"![{matches[i][0]}]({matches[i][1]})")
        itemcount = 0
        while len(list_textnode) != 0:
                temp = list_textnode.pop(0)
                if temp != "":
                    new_node = TextNode(temp, nodes.text_type)
                    list_txt.append(new_node)
                if itemcount < len(matches):
                    new_node = TextNode(matches[itemcount][0], TextType.IMAGE, url=matches[itemcount][1])
                    list_txt.append(new_node)
                itemcount += 1
    return list_txt    
def split_nodes_link(old_nodes):
    list_txt = []
    for nodes in old_nodes:
        if nodes.text_type != TextType.TEXT:
            list_txt.append(nodes)
            continue
        matches = extract_markdown_links(nodes.text)
        if len(matches) == 0:
            list_txt.append(nodes)
            continue
        list_textnode = []
        for i in range(len(matches)):
            if i == 0:
                list_textnode = nodes.text.split(f"[{matches[i][0]}]({matches[i][1]})")
            elif i > 0:
                temp = [] + list_textnode
                list_textnode.pop()
                list_textnode += temp[1].split(f"[{matches[i][0]}]({matches[i][1]})")
        itemcount = 0
        while len(list_textnode) != 0:
                temp = list_textnode.pop(0)
                if temp != "":
                    new_node = TextNode(temp, nodes.text_type)
                    list_txt.append(new_node)
                if itemcount < len(matches):
                    new_node = TextNode(matches[itemcount][0], TextType.LINK, url=matches[itemcount][1])
                    list_txt.append(new_node)
                itemcount += 1
    return list_txt
#Blocks-----------------------------------------------------
def markdown_to_blocks(markdown):
    list_blocks = [b.strip() for b in re.split(r'\n{2,}', markdown) if b.strip()]
    return list_blocks

def block_to_block_type(block):
    HEADING = re.findall(r"^#{1,6}\s(.+)",block)
    CODE = re.findall(r"^```.*```$",block,re.S)
    QUOTE = re.findall(r"^(>.*$(\r?\n|\r)?)+",block,re.M)
    UNORDERED = re.findall(r"^(-\s.*$(\r?\n|\r)?)+",block,re.M)
    ORDERED = re.findall(r"^(\d+\.\s.*$(\r?\n|\r)?)+",block,re.M)
    if len(HEADING) != 0:
        return BlockType.HEADING
    elif len(CODE) != 0:
        return BlockType.CODE
    elif len(QUOTE) != 0:
        return BlockType.QUOTE
    elif len(UNORDERED) != 0:
        return BlockType.ULIST
    elif len(ORDERED) != 0:
        return BlockType.OLIST
    else:
        return BlockType.PARAGRAPH

def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    children = []
    for block in blocks:
        html_node = block_to_html_node(block)
        children.append(html_node)
    return ParentNode("div", children, None)
def block_to_html_node(block):
    block_type = block_to_block_type(block)
    if block_type == BlockType.PARAGRAPH:
        return paragraph_to_html_node(block)
    if block_type == BlockType.HEADING:
        return heading_to_html_node(block)
    if block_type == BlockType.CODE:
        return code_to_html_node(block)
    if block_type == BlockType.OLIST:
        return olist_to_html_node(block)
    if block_type == BlockType.ULIST:
        return ulist_to_html_node(block)
    if block_type == BlockType.QUOTE:
        return quote_to_html_node(block)
    raise ValueError("invalid block type")
def text_to_children(text):
    text_nodes = text_to_textnodes(text)
    children = []
    for text_node in text_nodes:
        html_node = text_node_to_html_node(text_node)
        children.append(html_node)
    return children
def paragraph_to_html_node(block):
    lines = block.split("\n")
    paragraph = " ".join(lines)
    children = text_to_children(paragraph)
    return ParentNode("p", children)
def heading_to_html_node(block):
    level = 0
    for char in block:
        if char == "#":
            level += 1
        else:
            break
    if level + 1 >= len(block):
        raise ValueError(f"invalid heading level: {level}")
    text = block[level + 1 :]
    children = text_to_children(text)
    return ParentNode(f"h{level}", children)
def code_to_html_node(block):
    if not block.startswith("```") or not block.endswith("```"):
        raise ValueError("invalid code block")
    text = block[4:-3]
    raw_text_node = TextNode(text, TextType.TEXT)
    child = text_node_to_html_node(raw_text_node)
    code = ParentNode("code", [child])
    return ParentNode("pre", [code])
def olist_to_html_node(block):
    items = block.split("\n")
    html_items = []
    for item in items:
        text = item[3:]
        children = text_to_children(text)
        html_items.append(ParentNode("li", children))
    return ParentNode("ol", html_items)
def ulist_to_html_node(block):
    items = block.split("\n")
    html_items = []
    for item in items:
        text = item[2:]
        children = text_to_children(text)
        html_items.append(ParentNode("li", children))
    return ParentNode("ul", html_items)
def quote_to_html_node(block):
    lines = block.split("\n")
    new_lines = []
    for line in lines:
        if not line.startswith(">"):
            raise ValueError("invalid quote block")
        new_lines.append(line.lstrip(">").strip())
    content = " ".join(new_lines)
    children = text_to_children(content)
    return ParentNode("blockquote", children)

def extract_title(markdown):
    blocklist = markdown_to_blocks(markdown)
    for block in blocklist:
        parent = block_to_html_node(block)
        if parent.tag == "h1":
            full_value=""
            for leaf in parent.children:
                temp = leaf.to_html()
                full_value= full_value+temp
                return full_value
        else:
            continue
    raise Exception("there is no h1 header")