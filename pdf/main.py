import subprocess
import re


def preprocess_markdown(input_file, cleaned_file):
    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Remove GitLab-specific TOC marker
    content = content.replace("[[_TOC_]]", "")
    
    # Fix Python code block rendering
    # Look for Python code blocks and ensure they're properly formatted
    pattern = r"```python\s*\n(.*?)\n```"
    
    def fix_code_block(match):
        code = match.group(1)
        # Remove any leading brackets that might be causing rendering issues
        code = re.sub(r'^\[\]\s*', '', code)
        return f"```python\n{code}\n```"
    
    content = re.sub(pattern, fix_code_block, content, flags=re.DOTALL)

    # You can add more preprocessing here if needed

    with open(cleaned_file, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Preprocessed and saved to {cleaned_file}")


def run_pandoc(cleaned_file, defaults_file="defaults.yaml"):
    cmd = [
        "pandoc",
        "--defaults", defaults_file,
        cleaned_file,
        "--pdf-engine=xelatex",  # Using xelatex for better Unicode support
        "--pdf-engine-opt=-shell-escape",
        "--highlight-style=tango",  # Better code highlighting
    ]
    try:
        subprocess.run(cmd, check=True)
        print(f"✅ PDF generated using {defaults_file}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error generating PDF: {e}")
        # Print more detailed error information
        print(f"Command: {' '.join(cmd)}")


if __name__ == "__main__":
    original_md = "input.md"
    cleaned_md = "cleaned_input.md"

    preprocess_markdown(original_md, cleaned_md)
    run_pandoc(cleaned_md)