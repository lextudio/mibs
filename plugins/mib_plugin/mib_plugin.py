import os
import json
import shutil
from mkdocs.plugins import BasePlugin
from mkdocs.structure.pages import Page
from mkdocs.structure.files import Files, File

class MibPlugin(BasePlugin):
    def __init__(self):
        self.mib_count = 0
        self.total_objects = 0
        
    def count_objects(self, mib_data):
        """Count SNMP objects in a MIB module"""
        count = 0
        for key, value in mib_data.items():
            if isinstance(value, dict):
                if value.get('class') == 'objecttype' and value.get('maxaccess') != 'not-accessible':
                    count += 1
        return count
        
    def on_config(self, config):
        # Count MIBs and objects during initialization
        mib_files = [f for f in os.listdir('json') if f.endswith('.json')]
        self.mib_count = len(mib_files)
        self.total_objects = 0
        
        for mib_file in mib_files:
            with open(os.path.join('json', mib_file), 'r') as f:
                mib_data = json.load(f)
                self.total_objects += self.count_objects(mib_data)
        return config

    def on_files(self, files, config):
        original_files = files.src_paths
        new_files = Files([])
        
        # Add existing files first
        for file_path in original_files:
            file = files.get_file_from_path(file_path)
            if file:
                new_files.append(file)
                
        # Generate MIB pages
        mib_files = [f for f in os.listdir('json') if f.endswith('.json')]
        
        for mib_file in mib_files:
            with open(os.path.join('json', mib_file), 'r') as f:
                mib_data = json.load(f)
                module_name = os.path.splitext(mib_file)[0]
                page_content = self.generate_mib_page(mib_data, module_name)
                
                # Create the file object
                dest_path = f"{module_name}.md"
                file_obj = File(
                    path=dest_path,
                    src_dir=config['docs_dir'],
                    dest_dir=config['site_dir'],
                    use_directory_urls=config['use_directory_urls']
                )
                
                # Write content
                os.makedirs(config['docs_dir'], exist_ok=True)
                temp_path = os.path.join(config['docs_dir'], dest_path)
                with open(temp_path, 'w') as f:
                    f.write(page_content)
                
                if dest_path not in original_files:
                    new_files.append(file_obj)
        
        return new_files

    def generate_mib_page(self, mib_data, module_name):
        content = f"# {module_name}\n\n"
        
        # Add dependencies section
        imports = mib_data.get('imports', {})
        if imports:
            content += "## Dependencies\n\n"
            content += "This MIB module imports definitions from the following MIB modules:\n\n"
            content += "<table>\n"
            content += "<tr><th>Imported Module</th><th>Symbols</th></tr>\n"
            for imported_module, symbols in imports.items():
                if imported_module != 'class':
                    if imported_module in ["RFC-1212", "RFC-1215", "RFC1065-SMI", "RFC1155-SMI", "RFC1158-MIB", "RFC1213-MIB", "SNMPv2-CONF", "SNMPv2-SMI", "SNMPv2-TC", "SNMPv2-TM"]:
                        content += f"<tr><td>{imported_module}</td><td>{', '.join(symbols)}</td></tr>\n"
                    else:
                        content += f"<tr><td><a href=\"../{imported_module}/\">{imported_module}</a></td><td>{', '.join(symbols)}</td></tr>\n"
            content += "</table>\n\n"
        content += "## Objects\n\n"
        object_count = self.count_objects(mib_data)
        content += f"This MIB module contains {object_count} accessible objects.\n\n"
        
        # Generate table for accessible objects
        content += "<table>\n"
        content += "<tr><th>Object Name</th><th>OID</th><th>Access</th><th>Status</th><th>Syntax</th><th>Node Type</th></tr>\n"
        for key, value in sorted(mib_data.items()):
            if isinstance(value, dict) and value.get('class') == 'objecttype' and value.get('maxaccess') != 'not-accessible':
                access = value.get('maxaccess', 'unknown')
                oid = value.get('oid', 'unknown')
                status = value.get('status', 'unknown')
                syntax = value.get('syntax', {}).get('type', 'unknown')
                nodetype = value.get('nodetype', 'unknown')
                content += f"<tr><td>{key}</td><td>{oid}</td><td>{access}</td><td>{status}</td><td>{syntax}</td><td>{nodetype}</td></tr>\n"
        content += "</table>\n"
        
        # Add download link for original MIB document
        content += f"\n[Download original MIB document](../asn1/{module_name})\n"
        
        return content

    def on_page_markdown(self, markdown, page, config, files):
        if page.file.src_path == "mibs.md":
            # Generate list of MIB files
            mib_files = sorted([
                os.path.splitext(f)[0] 
                for f in os.listdir('json') 
                if f.endswith('.json')
            ])
            
            # Create markdown list with count
            mib_list = "# MIB Documents\n\n"
            mib_list += f"This repository contains **{self.mib_count} MIB modules** with a total of **{self.total_objects} accessible SNMP objects**. "
            mib_list += "Each MIB module provides standardized definitions for managing network devices and services via SNMP.\n\n"
            mib_list += "## Available MIB Modules\n\n"
            
            for mib in mib_files:
                mib_list += f"- [{mib}]({mib}.md)\n"
            
            return mib_list
        
        elif page.file.src_path == "index.md":
            # Add statistics to the introduction
            lines = markdown.split('\n')
            insert_pos = 3  # After the first paragraph
            stats_text = f"\nCurrently, this repository contains **{self.mib_count} MIB modules** with a total of **{self.total_objects} accessible SNMP objects**.\n"
            lines.insert(insert_pos, stats_text)
            return '\n'.join(lines)

        return markdown

    def on_post_build(self, config):
        src_dir = os.path.join(config['docs_dir'], 'asn1')
        dest_dir = os.path.join(config['site_dir'], 'asn1')
        
        if os.path.exists(src_dir):
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
            for item in os.listdir(src_dir):
                s = os.path.join(src_dir, item)
                d = os.path.join(dest_dir, item)
                if os.path.isdir(s):
                    shutil.copytree(s, d, dirs_exist_ok=True)
                else:
                    shutil.copy2(s, d)
