# An easy way to check which HTML templates are not used in the codebase.

import os
import re

TEMPLATE_DIR = 'templates'
# 1. List all templates
all_templates = set()
for root, dirs, files in os.walk(TEMPLATE_DIR):
    for f in files:
        if f.endswith('.html'):
            relpath = os.path.relpath(os.path.join(root, f), TEMPLATE_DIR)
            all_templates.add(relpath.replace('\\', '/'))

# 2. Search usage in .py and .html
used_templates = set()
pat = re.compile(r"(['\"])([\w./-]+\.html)\1")
for folder in ('.', 'routes'):
    for root, dirs, files in os.walk(folder):
        for f in files:
            if f.endswith('.py') or f.endswith('.html'):
                with open(os.path.join(root, f), encoding='utf-8') as fh:
                    content = fh.read()
                    for m in pat.finditer(content):
                        used_templates.add(m.group(2))

# 3. Print unused templates
unused = all_templates - used_templates
print("Unused templates:")
for t in sorted(unused):
    print(t)