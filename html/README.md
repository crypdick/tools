# HTML Tools

Single-file HTML+JavaScript web applications that run entirely in the browser, following [Simon Willison's HTML Tools patterns](https://simonwillison.net/2025/Dec/10/html-tools/).

## Running Tools

```shell
# Locally
open html/tool-name.html

# Hosted
open https://tools.ricardodecal.com/html/tool-name.html
```

## Examples

Browse the full collection at [tools.ricardodecal.com](https://tools.ricardodecal.com/html/).

See also: [Simon Willison's tools collection](https://tools.simonwillison.net/) for inspiration and reference implementations.

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

**Examples:**

- [**ocr**](https://tools.simonwillison.net/ocr) - Loads PDF.js and Tesseract.js from CDN to run OCR entirely in-browser without server uploads.
- [**pyodide-bar-chart**](https://tools.simonwillison.net/pyodide-bar-chart) - Loads Pyodide, Pandas, and matplotlib from CDN to render charts client-side.

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

**Examples:**

- [**hacker-news-thread-export**](https://tools.simonwillison.net/hacker-news-thread-export) - Fetches HN thread via API and provides one-tap clipboard copy of condensed thread for pasting into LLMs.
- [**paste-rich-text**](https://tools.simonwillison.net/paste-rich-text) - Extracts HTML from rich clipboard data on paste, particularly useful on mobile where inspecting HTML is difficult.

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

**Examples:**

- [**paste-rich-text**](https://tools.simonwillison.net/paste-rich-text) - Intercepts paste events to extract both plain text and HTML from clipboard data.
- [**bluesky-thread**](https://tools.simonwillison.net/bluesky-thread) - Accepts pasted Bluesky URLs and fetches thread data via API for nested display.

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

**Examples:**

- [**ocr**](https://tools.simonwillison.net/ocr) - Opens PDFs locally using FileReader, converts pages to images, and runs Tesseract OCR client-side.
- [**social-media-cropper**](https://tools.simonwillison.net/social-media-cropper) - Loads images via file input or paste, renders to canvas for interactive cropping to platform-specific dimensions.
- [**ffmpeg-crop**](https://tools.simonwillison.net/ffmpeg-crop) - Previews local video files in browser, allows dragging crop box, then generates ffmpeg command without uploading.

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

**Examples:**

- [**svg-render**](https://tools.simonwillison.net/svg-render) - Renders SVG to canvas, converts to blob, and triggers download as PNG/JPEG using createObjectURL.
- [**open-sauce-2025**](https://tools.simonwillison.net/open-sauce-2025) - Generates ICS calendar file from scraped schedule data and offers download via blob URL.

### Secrets & State

- **Secrets**: Store API keys in `localStorage` so they persist but stay on the client.
- **URL State**: Store shareable state in URL hash or query parameters.
- **Large State**: For state too large for the URL (e.g. document drafts), use `localStorage`.

**Example: API Key Management**
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

**Example: Auto-saving Large Content**
```javascript
// Auto-save content to localStorage
const STORAGE_KEY = 'my-tool-content';
const textarea = document.getElementById('content');

// Load saved content
textarea.value = localStorage.getItem(STORAGE_KEY) || '';

// Save on input with debounce
textarea.addEventListener('input', () => {
    localStorage.setItem(STORAGE_KEY, textarea.value);
    document.getElementById('status').textContent = 'Saved locally';
});
```

### CORS & APIs

You can call any API that supports CORS (Cross-Origin Resource Sharing) directly from the browser.

**CORS-Enabled APIs:**
- **LLMs**: Anthropic, OpenAI, Gemini (often require keys, see "Secrets" above).
- **GitHub API**: Fetch repos, issues, gists.
- **PyPI**: Get package info.

**Calling an LLM (Anthropic Example):**
```javascript
const response = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
        'x-api-key': apiKey, // From localStorage
        'anthropic-version': '2023-06-01',
        'content-type': 'application/json',
        'dangerously-allow-browser': 'true' // Required for client-side calls
    },
    body: JSON.stringify({
        model: "claude-3-opus-20240229",
        max_tokens: 1024,
        messages: [{ role: "user", content: "Hello, world" }]
    })
});
const data = await response.json();
```

**Examples:**

- [**haiku**](https://tools.simonwillison.net/haiku) - Streams webcam screenshots to Claude API with vision capabilities, stores API key in localStorage.
- [**openai-audio-output**](https://tools.simonwillison.net/openai-audio-output) - Calls OpenAI's GPT-4o audio API directly from browser to generate speech from text input.
- [**gemini-bbox**](https://tools.simonwillison.net/gemini-bbox) - Uses Gemini 2.5 API to return complex shaped image masks for object detection in uploaded images.
- [**pypi-changelog**](https://tools.simonwillison.net/pypi-changelog) - Fetches wheel URLs from PyPI API, downloads and diffs package versions entirely client-side.

### Running Python in Browser (Pyodide)

For tools that need Python libraries (Pandas, SQLite, etc.), use Pyodide to run Python entirely in the browser via WebAssembly.

```javascript
// 1. Add script: <script src="https://cdn.jsdelivr.net/pyodide/v0.25.0/full/pyodide.js"></script>
// 2. Initialize and run
async function runPython() {
    const pyodide = await loadPyodide();
    await pyodide.loadPackage("pandas");
    
    // Run Python code
    const result = await pyodide.runPythonAsync(`
        import pandas as pd
        df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        df.to_html()
    `);
    document.getElementById('output').innerHTML = result;
}
```

**Examples:**

- [**pyodide-bar-chart**](https://tools.simonwillison.net/pyodide-bar-chart) - Loads Pyodide, then uses micropip to install Pandas and matplotlib for client-side data visualization.
- [**numpy-pyodide-lab**](https://tools.simonwillison.net/numpy-pyodide-lab) - Interactive Numpy tutorial that runs Python code examples in-browser using Pyodide.
- [**apsw-query**](https://tools.simonwillison.net/apsw-query) - Runs APSW SQLite library via Pyodide to show EXPLAIN QUERY plans without server.

### WebAssembly

Beyond Python, many other tools can run in-browser via WASM:
- **FFmpeg**: Video/audio processing.
- **Squoosh**: Image compression.
- **DuckDB**: Analytical SQL queries.

**Examples:**

- [**ocr**](https://tools.simonwillison.net/ocr) - Uses Tesseract.js (WebAssembly port of Tesseract OCR engine) to recognize text in images client-side.
- [**sloccount**](https://tools.simonwillison.net/sloccount) - Ports David Wheeler's SLOCCount (Perl/C) to browser using WebAssembly for code line counting.
- [**micropython**](https://tools.simonwillison.net/micropython) - Runs MicroPython WebAssembly build for faster Python execution with smaller download than Pyodide.

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
