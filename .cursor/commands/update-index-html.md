Please update `index.html` to reflect the current list of tools in the repository.

1. **Scan for Tools**:
    * List all executable scripts in `python/` (look for `*.py`) and `bash/` (look for `*.sh` or executable files).
    * Ignore `__init__.py`, `conftest.py`, files in `__pycache__`, or library files.

2. **Analyze New Tools**:
    * For each tool not yet in `index.html`:
        * Read the file header/docstring to get a **short description** and a **usage command** (e.g., `uv run ...`).

3. **Update `index.html`**:
    * Add a list item `<li>` for the tool in the corresponding section (Python or Bash).
    * Use the following format:

        ```html
        <li>
            <strong><a href="relative/path/to/tool">tool_name</a></strong>
            <br>
            Short description of what the tool does.
            <br>
            <code>uv run path/to/tool [args]</code>
        </li>
        ```

    * If the section currently has a "Coming soon..." placeholder, replace it with a `<ul class="tools-list">`.

4. **Cleanup**:
    * Ensure proper indentation and formatting in the HTML file.
