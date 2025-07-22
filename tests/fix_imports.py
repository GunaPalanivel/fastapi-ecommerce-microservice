import os
import re

files_to_fix = [
    "services/order_service.py",
    "services/product_service.py", 
    "routers/orders.py",
    "routers/products.py",
    "schemas/order.py",
    "schemas/product.py",
    "utils/pagination.py"
]

for file_path in files_to_fix:
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Add Optional to typing imports if missing
        if 'from typing import' in content and 'Optional' not in content:
            content = re.sub(
                r'from typing import ([^Optional\n]*)\n',
                r'from typing import \1, Optional\n',
                content
            )
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        print(f"Fixed imports in {file_path}")
    else:
        print(f"File not found: {file_path}")
