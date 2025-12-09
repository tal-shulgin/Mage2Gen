import string
import os
import re
from xml.etree import ElementTree as ET
from xml.dom import minidom

class DefaultFormatter(string.Formatter):
    def __init__(self, default=''):
        self.default = default
    
    def get_field(self, field_name, args, kwargs):
        try:
            return super().get_field(field_name, args, kwargs)
        except (KeyError, AttributeError):
            return self.default

def upperfirst(word):
    if not word:
        return ''
    return word[0].upper() + word[1:]

def lowerfirst(word):
    if not word:
        return ''
    return word[0].lower() + word[1:]

def prettify_xml(elem):
    """
    Return a pretty-printed XML string for the Element.
    Preserves attribute order by using ElementTree indent (Py3.9+) or fallback.
    """
    try:
        # Python 3.9+ supports indentation natively in ElementTree
        if hasattr(ET, 'indent'):
            ET.indent(elem, space="    ")
            return ET.tostring(elem, encoding='utf-8').decode('utf-8')
        else:
            # Fallback for older python (e.g. 3.7/3.8)
            # We use a manual indentation logic on the tree to avoid minidom sorting
            _indent(elem)
            return ET.tostring(elem, encoding='utf-8').decode('utf-8')
    except Exception:
        # Ultimate fallback if something fails
        rough_string = ET.tostring(elem, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="    ")

def _indent(elem, level=0):
    """Manual indentation for ElementTree."""
    i = "\n" + level * "    "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "    "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            _indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

def merge_xml_files(existing_path, new_xml_string):
    """
    Merges new_xml_string into the file at existing_path.
    Returns the merged XML string.
    """
    try:
        # DO NOT register global namespace; let parser handle attributes as-is
        
        # Parse existing file
        tree = ET.parse(existing_path)
        root = tree.getroot()
        
        # Parse new content
        new_root = ET.fromstring(new_xml_string)
        
        if root.tag != new_root.tag:
            return new_xml_string

        # Merge new_root children into root
        _merge_elements(root, new_root)
        
        # Use our new prettify function instead of minidom
        return prettify_xml(root)
        
    except Exception as e:
        print(f"Warning: XML Merge failed ({e}). Overwriting.")
        return new_xml_string

def _get_element_id(elem):
    """Identify elements by specific attributes for merging."""
    target_attrs = ['id', 'name', 'frontName', 'url', 'class', 'instance', 'for']
    
    tag = elem.tag
    if '}' in tag:
        tag = tag.split('}', 1)[1]

    ident_attr = None
    ident_val = None
    
    for attr in target_attrs:
        if attr in elem.attrib:
            ident_attr = attr
            ident_val = elem.attrib[attr]
            break
    
    if ident_attr:
        return f"{tag}[@{ident_attr}='{ident_val}']"
    return tag

def _merge_elements(base_elem, new_elem):
    existing_map = {}
    for child in base_elem:
        ident = _get_element_id(child)
        existing_map[ident] = child
    
    for new_child in new_elem:
        ident = _get_element_id(new_child)
        
        if ident in existing_map:
            target = existing_map[ident]
            target.attrib.update(new_child.attrib)
            
            if new_child.text and new_child.text.strip():
                target.text = new_child.text

            _merge_elements(target, new_child)
        else:
            base_elem.append(new_child)

def to_pascal_case(snake_str):
    """Converts snake_case or sentence string to PascalCase."""
    components = snake_str.replace(' ', '_').split('_')
    return "".join(x.title() for x in components)