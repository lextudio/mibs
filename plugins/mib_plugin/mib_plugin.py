import os
import json
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
        content += "## Objects\n\n"
        object_count = self.count_objects(mib_data)
        content += f"This MIB module contains {object_count} accessible objects.\n\n"
        
        # List all accessible objects
        for key, value in sorted(mib_data.items()):
            if isinstance(value, dict) and value.get('class') == 'objecttype' and value.get('maxaccess') != 'not-accessible':
                access = value.get('maxaccess', 'unknown')
                oid = value.get('oid', 'unknown')
                content += f"- {key} ({oid}) [Access: {access}]\n"
        
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
