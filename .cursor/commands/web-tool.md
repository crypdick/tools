# Create Simon Willison-Style Web Tool

Build a single-file HTML+JavaScript web application following Simon Willison's patterns.

## Instructions

You are building a **single-page web application** that runs entirely in the browser. Follow these strict guidelines:

### Core Principles

1. **Single file** - Everything (HTML, CSS, JavaScript) in one file
2. **Zero dependencies** - No external JavaScript libraries unless absolutely necessary (prefer vanilla JS)
3. **No build step** - Works by opening the file directly in a browser
4. **Mobile-friendly** - Responsive and works on all devices
5. **Modern and beautiful** - Clean, professional UI with good UX

### Required Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>[Tool Name]</title>
    <style>
    * {
        box-sizing: border-box;
    }
    body {
        font-family: Helvetica, Arial, sans-serif;
        max-width: 800px;
        margin: 0 auto;
        padding: 20px;
        line-height: 1.6;
    }
    input, textarea, button, select {
        font-size: 16px; /* Prevents zoom on iOS */
        font-family: inherit;
    }
    button {
        cursor: pointer;
        padding: 10px 20px;
        background: #0066cc;
        color: white;
        border: none;
        border-radius: 4px;
    }
    button:hover {
        background: #0052a3;
    }
    /* Add more styles here with 2-space indents */
    </style>
</head>
<body>
    <h1>[Tool Name]</h1>

    <!-- Tool UI goes here -->

    <script type="module">
    // JavaScript with 2-space indents
    // No first-level indentation inside script tag

    document.addEventListener('DOMContentLoaded', () => {
      // Your code here
    });
    </script>
</body>
</html>
```

### CSS Guidelines

- Use **2-space indentation**
- Start with `* { box-sizing: border-box; }`
- Set `font-family: Helvetica, Arial, sans-serif;` on body
- All inputs/textareas **must be 16px** (prevents iOS zoom)
- Use modern, clean design with good spacing
- Make it responsive (works on mobile and desktop)

### JavaScript Guidelines

- Use **2-space indentation**
- Use `<script type="module">` for modern JS
- **No first-level indentation** inside the script tag
- Use vanilla JavaScript (no jQuery, React, etc.)
- Use `async/await` for async operations
- Add proper error handling
- Use `FormData`, `fetch`, modern APIs

### Common Patterns

**Copy to Clipboard:**

```javascript
async function copyToClipboard(text) {
  try {
    await navigator.clipboard.writeText(text);
    // Show success feedback
  } catch (err) {
    console.error('Failed to copy:', err);
  }
}
```

**Paste from Clipboard:**

```javascript
// Listen for paste events
document.addEventListener('paste', async (e) => {
  e.preventDefault();
  const text = e.clipboardData.getData('text/plain');
  const html = e.clipboardData.getData('text/html');
  // Process pasted data
});
```

**File Upload:**

```javascript
const input = document.createElement('input');
input.type = 'file';
input.accept = 'image/*'; // or specific types
input.onchange = (e) => {
  const file = e.target.files[0];
  const reader = new FileReader();
  reader.onload = (e) => {
    const data = e.target.result;
    // Process file data
  };
  reader.readAsDataURL(file); // or readAsText(), readAsArrayBuffer()
};
input.click();
```

**Download Generated File:**

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

### What NOT to Include

❌ No frameworks (React, Vue, Angular)
❌ No build tools (webpack, vite)
❌ No package managers (npm, yarn)
❌ No TypeScript (use vanilla JS)
❌ No external CSS frameworks (Bootstrap, Tailwind)
❌ Avoid external dependencies unless absolutely needed

### If You Must Use External Libraries

Only include proven, CDN-hosted libraries for specific needs:

```html
<!-- Example: For complex image manipulation -->
<script src="https://cdn.jsdelivr.net/npm/library@version/dist/library.min.js"></script>
```

Common acceptable libraries:

- Marked.js (for Markdown rendering)
- QR code generators
- Specialized parsers (YAML, TOML)
- SQLite WASM

## Output Requirements

Generate the complete HTML file ready to save and use:

- Descriptive title and heading
- Clear instructions or labels
- All necessary inputs/controls
- Result display area with copy/download buttons as appropriate
- Clean, professional styling
- Helpful error messages
- Works on mobile and desktop
- No console errors

The file should be immediately usable - just save and open in a browser!
