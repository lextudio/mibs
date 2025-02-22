from mkdocs.plugins import BasePlugin
from mkdocs.config import config_options
import re

class OIDSearchPlugin(BasePlugin):
    config_scheme = (
        ('separator', config_options.Type(str, default='[\\s\\-\\.]+')),
    )

    def on_page_markdown(self, markdown, page, config, files):
        # Improved regex pattern to handle OIDs within HTML tags more effectively
        oid_pattern = re.compile(r'(\d+\.\d+(\.\d+)*)')
        processed_markdown = oid_pattern.sub(r' \1 ', markdown)
        return processed_markdown

    def on_config(self, config):
        # Update the search plugin configuration
        search_plugin = next((p for p in config['plugins'] if p.__class__.__name__ == 'SearchPlugin'), None)
        if search_plugin:
            search_plugin.config['separator'] = self.config['separator']
        return config
