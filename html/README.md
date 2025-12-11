# HTML Tools

Single-file HTML+JavaScript web applications that run entirely in the browser, following [Simon Willison's HTML Tools patterns](https://simonwillison.net/2025/Dec/10/html-tools/).

## Running Tools

```shell
# Locally
open html/tool-name.html

# Hosted
open https://tools.ricardodecal.com/html/tool-name.html
```

## Creating Tools

### Core Principles

1.  **Single File**: HTML, CSS, and JavaScript in one file.
2.  **No Build Step**: No React, no webpack, no npm.
3.  **CDN Dependencies**: Load libraries from [cdnjs](https://cdnjs.com/) or [jsdelivr](https://www.jsdelivr.com/).
4.  **Mobile-Friendly**: Responsive design by default (16px inputs, readable text).
5.  **LLM-Friendly**: Easy to generate, read, and modify with AI.

### Required Structure

Start with this template to ensure consistency and mobile compatibility:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tool Name</title>
    <style>
    :root {
        --primary: #0066cc;
        --bg: #f4f4f9;
        --text: #333;
    }
    * { box-sizing: border-box; }
    body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        max-width: 800px;
        margin: 0 auto;
        padding: 20px;
        line-height: 1.6;
        color: var(--text);
        background: var(--bg);
    }
    input, textarea, button, select {
        font-size: 16px; /* Prevents zoom on iOS */
        font-family: inherit;
        padding: 8px;
        border: 1px solid #ccc;
        border-radius: 4px;
    }
    button {
        cursor: pointer;
        background: var(--primary);
        color: white;
        border: none;
    }
    button:hover { filter: brightness(0.9); }
    .error { color: #d32f2f; background: #ffebee; padding: 10px; border-radius: 4px; display: none; }
    footer {
        margin-top: 40px;
        padding-top: 20px;
        border-top: 1px solid #ddd;
        font-size: 0.9em;
        color: #666;
        text-align: center;
    }
    footer a { color: var(--primary); text-decoration: none; }
    footer a:hover { text-decoration: underline; }
    /* Add specific styles here */
    </style>
</head>
<body>
    <h1>Tool Name</h1>

    <div id="error" class="error"></div>
    
    <!-- Tool UI -->
    <main>
        <!-- Content goes here -->
    </main>

    <footer>
        <p>Made by Ricardo Decal. Updated YYYY-MM-DD</p>
        <p>
            <a href="https://tools.ricardodecal.com">Home</a> | 
            <a href="https://github.com/ricardodecal/tools/blob/main/html/tool-name.html">View source</a>
        </p>
    </footer>

    <script type="module">
    // Use modern ES modules
    // No first-level indentation inside script tag

    document.addEventListener('DOMContentLoaded', () => {
        const errorDiv = document.getElementById('error');
        
        function showError(msg) {
            errorDiv.textContent = msg;
            errorDiv.style.display = 'block';
        }

        // App logic
    });
    </script>
</body>
</html>
```

### Prototyping with LLMs

The most efficient way to build these tools is to prompt an LLM.

**Recommended Prompt:**
> "Build a single-file HTML tool that [does X]. No React. Use modern vanilla JavaScript. Style it cleanly with CSS variables. Include error handling."

---

## Standard Dependencies

Prefer these proven, CDN-hosted libraries when vanilla JS isn't enough:

- **Markdown**: `https://cdn.jsdelivr.net/npm/marked/marked.min.js`
- **PDFs**: `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/[version]/pdf.min.js`
- **OCR**: `https://cdn.jsdelivr.net/npm/tesseract.js@5/dist/tesseract.min.js`
- **Zip**: `https://cdn.jsdelivr.net/npm/jszip@3/dist/jszip.min.js`
- **Python**: `https://cdn.jsdelivr.net/pyodide/v0.25.0/full/pyodide.js`
- **SQLite**: `https://cdnjs.cloudflare.com/ajax/libs/sql.js/1.8.0/sql-wasm.js`

---

## Common Patterns

### Copy to Clipboard

Essential for text transformation tools.

```javascript
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        // Show "Copied!" feedback
    } catch (err) {
        console.error('Failed to copy:', err);
    }
}
```

### Paste Processing

Allow users to paste content directly into the page.

```javascript
document.addEventListener('paste', async (e) => {
    // Only handle if not pasting into an input
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
    
    e.preventDefault();
    const text = e.clipboardData.getData('text/plain');
    // const html = e.clipboardData.getData('text/html');
    
    // Process pasted data
});
```

### File I/O (Local)

Read files without uploading to a server.

```javascript
const input = document.createElement('input');
input.type = 'file';
input.accept = '.json,.csv'; // specific types
input.onchange = (e) => {
    const file = e.target.files[0];
    const reader = new FileReader();
    reader.onload = (e) => {
        const content = e.target.result;
        // Process content
    };
    reader.readAsText(file); // or readAsDataURL, readAsArrayBuffer
};
input.click();
```

### Download Generated File

Save results back to the user's machine.

```javascript
function downloadFile(content, filename, type = 'text/plain') {
    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
}
```

### Secrets & State

- **Secrets**: Store API keys in `localStorage` so they persist but stay on the client.
- **State**: Store shareable state in URL hash or query parameters.

```javascript
// Get the API key from localStorage or prompt the user to enter it
function getApiKey() {
  let apiKey = localStorage.getItem("ANTHROPIC_API_KEY");
  if (!apiKey) {
    apiKey = prompt("Please enter your Anthropic API key:");
    if (apiKey) {
      localStorage.setItem("ANTHROPIC_API_KEY", apiKey);
    }
  }
  return apiKey;
}
const apiKey = getApiKey();
if (!apiKey) {
  alert("API key not found. Please enter your Anthropic API key.");
  return;
}
```

---

## Anti-Patterns

❌ **React / JSX**: Requires a build step. Harder to copy-paste and edit.
❌ **npm / node_modules**: Makes the tool hard to run standalone.
❌ **Separate CSS/JS files**: Keeps it simpler to have one file to manage/share.
❌ **Server-side logic**: These tools should run entirely in the browser (use Pyodide or WebAssembly if needed).

---

## Workflow

1.  **Create**: `touch html/my-tool.html`
2.  **Generate**: Use LLM to scaffold the tool ("No React" prompt).
3.  **Refine**: Test locally, tweak CSS/JS.
4.  **Publish**: Commit and push. GitHub Pages serves it automatically.
