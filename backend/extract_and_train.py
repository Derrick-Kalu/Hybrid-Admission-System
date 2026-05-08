import json
import os

with open('notebooks/Model_Training.ipynb', 'r', encoding='utf-8') as f:
    notebook = json.load(f)

code = []
for cell in notebook['cells']:
    if cell['cell_type'] == 'code':
        code.append("".join(cell['source']))

script = "\n\n".join(code)

with open('train_model.py', 'w', encoding='utf-8') as f:
    f.write(script)

import sys
import subprocess
print("Extracted script. Now running training...")
subprocess.run([sys.executable, 'train_model.py'])
