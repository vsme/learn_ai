import os
import re
from datetime import datetime

# Configuration
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(ROOT_DIR, 'index.html')
IGNORE_DIRS = {'.git', '.vscode', '__pycache__', 'templates', 'assets', 'css', 'js', 'images'}
IGNORE_FILES = {'index.html'}

def extract_metadata(file_path):
    """Extract title, description, order and icon from an HTML file."""
    title = "Untitled"
    description = "No description available."
    order = 9999
    icon = None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Extract Title
            title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
            if title_match:
                title = title_match.group(1).strip()
            
            # Extract Description (Meta tag)
            desc_match = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', content, re.IGNORECASE)
            if desc_match:
                description = desc_match.group(1).strip()
            
            # Extract Order
            order_match = re.search(r'<!--\s*order:\s*(\d+)\s*-->', content, re.IGNORECASE)
            if order_match:
                order = int(order_match.group(1))

            # Extract Icon
            icon_match = re.search(r'<!--\s*icon:\s*(.+?)\s*-->', content, re.IGNORECASE)
            if icon_match:
                icon = icon_match.group(1).strip()

    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        
    return {
        'title': title,
        'description': description,
        'order': order,
        'icon': icon,
        'path': file_path
    }

def scan_directory(root_path):
    """Scan the directory for HTML files grouped by folders."""
    categories = {}
    
    for entry in os.listdir(root_path):
        full_path = os.path.join(root_path, entry)
        
        if os.path.isdir(full_path) and entry not in IGNORE_DIRS:
            category_name = entry.upper() # Or format nicely
            modules = []
            
            for file in os.listdir(full_path):
                if file.endswith('.html') and file not in IGNORE_FILES:
                    file_path = os.path.join(full_path, file)
                    rel_path = os.path.relpath(file_path, root_path).replace('\\', '/')
                    
                    metadata = extract_metadata(file_path)
                    metadata['rel_path'] = rel_path
                    modules.append(metadata)
            
            if modules:
                categories[category_name] = modules
                
    return categories

def generate_html(categories):
    """Generate the index.html content."""
    
    # Template parts
    html_head = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Learning Hub</title>
    <style>
        :root {
            --primary-color: #2563eb;
            --secondary-color: #1e40af;
            --bg-color: #f8fafc;
            --card-bg: #ffffff;
            --text-main: #1e293b;
            --text-secondary: #64748b;
            --shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
            --shadow-hover: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
            --border-color: #e2e8f0;
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-main);
            line-height: 1.6;
        }

        header {
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
            padding: 4rem 2rem;
            text-align: center;
            margin-bottom: 3rem;
        }

        header h1 {
            font-size: 2.5rem;
            margin-bottom: 1rem;
            font-weight: 800;
        }

        header p {
            font-size: 1.2rem;
            opacity: 0.9;
            max-width: 600px;
            margin: 0 auto;
        }

        .github-badge {
            margin-top: 1rem;
            display: inline-block;
            transition: transform 0.2s ease;
        }

        .github-badge:hover {
            transform: scale(1.05);
        }

        main {
            max-width: 1200px;
            margin: 0 auto 4rem;
            padding: 0 2rem;
        }

        .category-section {
            margin-bottom: 4rem;
        }

        .category-title {
            font-size: 1.8rem;
            margin-bottom: 1.5rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid var(--border-color);
            color: var(--text-main);
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .category-badge {
            font-size: 0.9rem;
            background: #e0f2fe;
            color: #0284c7;
            padding: 0.2rem 0.6rem;
            border-radius: 999px;
            font-weight: 600;
        }

        .modules-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 2rem;
        }

        .card {
            background: var(--card-bg);
            border-radius: 1rem;
            padding: 2rem;
            box-shadow: var(--shadow);
            transition: all 0.3s ease;
            text-decoration: none;
            color: inherit;
            display: flex;
            flex-direction: column;
            border: 1px solid var(--border-color);
            height: 100%;
            position: relative;
            overflow: hidden;
        }

        .card:hover {
            transform: translateY(-5px);
            box-shadow: var(--shadow-hover);
            border-color: var(--primary-color);
        }
        
        .card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 4px;
            background: linear-gradient(to right, var(--primary-color), var(--secondary-color));
            opacity: 0;
            transition: opacity 0.3s ease;
        }
        
        .card:hover::before {
            opacity: 1;
        }

        .card-icon {
            font-size: 2rem;
            margin-bottom: 1rem;
            display: inline-block;
            padding: 0.5rem;
            background: #eff6ff;
            border-radius: 0.5rem;
            width: fit-content;
        }

        .card h3 {
            font-size: 1.25rem;
            margin-bottom: 0.75rem;
            color: var(--text-main);
            font-weight: 700;
        }

        .card p {
            color: var(--text-secondary);
            font-size: 0.95rem;
            flex-grow: 1;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }

        .card-footer {
            margin-top: 1.5rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.85rem;
            color: var(--primary-color);
            font-weight: 600;
        }

        footer {
            text-align: center;
            padding: 2rem;
            color: var(--text-secondary);
            font-size: 0.9rem;
            border-top: 1px solid var(--border-color);
            background: white;
        }

        @media (max-width: 640px) {
            header { padding: 3rem 1rem; }
            header h1 { font-size: 2rem; }
            main { padding: 0 1rem; }
        }
    </style>
</head>
<body>

    <header>
        <h1>AI Learning Hub</h1>
        <p>探索人工智能的世界，从基础算法到前沿技术。</p>
        <a href="https://github.com/vsme/ai-viz" target="_blank" rel="noopener noreferrer" class="github-badge">
            <img src="//img.shields.io/github/stars/vsme/ai-viz" alt="GitHub Repo stars" />
        </a>
    </header>

    <main>
"""

    html_footer = """
    </main>

    <footer>
        <p>&copy; 2025 AI Learning Hub. Generated automatically.</p>
    </footer>

</body>
</html>
"""
    
    content_html = ""
    
    # Sort categories
    sorted_categories = sorted(categories.keys())
    
    for category in sorted_categories:
        modules = categories[category]
        
        # Sort modules by order (ascending) then title
        modules.sort(key=lambda x: (x['order'], x['title']))
        
        content_html += f"""
        <section class="category-section">
            <h2 class="category-title">
                {category}
                <span class="category-badge">{len(modules)} Modules</span>
            </h2>
            <div class="modules-grid">
        """
        
        for module in modules:
            title = module['title']
            desc = module['description']
            link = module['rel_path']
            extracted_icon = module['icon']
            
            # Icon logic: Extracted > Keyword > Default
            if extracted_icon:
                icon = extracted_icon
            else:
                # Basic icon logic based on keywords
                icon = "📄"
                if "RAG" in title.upper(): icon = "🧠"
                elif "SEARCH" in title.upper() or "检索" in title: icon = "🔍"
                elif "SPLITTER" in title.upper(): icon = "✂️"
                elif "HEAP" in title.upper(): icon = "🌲"
                elif "K-MEANS" in title.upper(): icon = "📊"
            
            content_html += f"""
                <a href="{link}" class="card">
                    <div class="card-icon">{icon}</div>
                    <h3>{title}</h3>
                    <p>{desc if desc != "No description available." else "点击查看详情"}</p>
                    <div class="card-footer">
                        <span>View Module &rarr;</span>
                    </div>
                </a>
            """
            
        content_html += """
            </div>
        </section>
        """

    if not categories:
        content_html += """
        <div style="text-align: center; padding: 4rem; color: var(--text-secondary);">
            <h2>No modules found</h2>
            <p>Add folders with HTML files to get started.</p>
        </div>
        """

    return html_head + content_html + html_footer

def main():
    print("Scanning directory...")
    categories = scan_directory(ROOT_DIR)
    print(f"Found {len(categories)} categories.")
    
    print("Generating index.html...")
    html_content = generate_html(categories)
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(html_content)
        
    print(f"Successfully generated {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
