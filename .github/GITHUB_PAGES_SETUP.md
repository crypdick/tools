# GitHub Pages Setup Guide

This guide will help you set up GitHub Pages for this repository at `tools.ricardodecal.com`.

## Files Created

1. **`index.html`** - Beautiful landing page with dark mode support
2. **`CNAME`** - Contains `tools.ricardodecal.com` for custom domain
3. **`.nojekyll`** - Prevents Jekyll processing
4. **`.github/workflows/pages.yml`** - Auto-deploy workflow
5. **`tests/test_placeholder.py`** - Placeholder test (can be removed when you add real tests)

## 🌐 Setting Up Custom Domain: tools.ricardodecal.com

Follow these steps to use your custom subdomain instead of `crypdick.github.io/tools/`:

### Step 1: Configure DNS in Cloudflare

Add a DNS record in Cloudflare to point `tools.ricardodecal.com` to GitHub Pages:

1. Log into your **Cloudflare dashboard**
2. Select domain: `ricardodecal.com`
3. Go to **DNS** settings
4. Click **Add record**
5. Configure:
   - **Type**: `CNAME`
   - **Name**: `tools` (this creates tools.ricardodecal.com)
   - **Target**: `crypdick.github.io` (your GitHub Pages URL)
   - **Proxy status**: **DNS only** ⚠️ (gray cloud, not orange)
   - **TTL**: Auto
6. Click **Save**

⚠️ **Critical**: Turn OFF Cloudflare's proxy (use "DNS only") initially. You can enable it later after HTTPS is set up.

### Step 2: Verify DNS Propagation

Wait 5-15 minutes, then check:

```shell
dig tools.ricardodecal.com
# Should show CNAME pointing to crypdick.github.io

# Or use nslookup
nslookup tools.ricardodecal.com
```

You should see it pointing to GitHub's servers.

### Step 3: Configure Custom Domain in GitHub

1. Go to: <https://github.com/crypdick/tools/settings/pages>
2. Under "Custom domain", enter: `tools.ricardodecal.com`
3. Click **Save**
4. GitHub will verify the DNS and update the CNAME file if needed

### Step 4: Enable HTTPS (GitHub will do this automatically)

GitHub will automatically provision an SSL certificate for your custom domain. This can take:

- Minimum: A few minutes
- Maximum: Up to 24 hours

Once ready:

1. You'll see a checkmark next to "Enforce HTTPS" in Settings → Pages
2. Check the box to enforce HTTPS

### Step 5: Optional - Enable Cloudflare Proxy

After HTTPS is working:

1. Go back to Cloudflare DNS settings
2. Find your `tools` CNAME record
3. Click to edit it
4. Change **Proxy status** to **Proxied** (orange cloud)
5. This enables Cloudflare's CDN and DDoS protection

---

## 🧪 Testing Locally

Before pushing changes, test your `index.html`:

```shell
python3 -m http.server 8000
# Visit http://localhost:8000
```

## 🔄 Automatic Deployments

Any push to the `main` branch automatically triggers:

1. Lint checks (pre-commit)
2. Tests (pytest)
3. GitHub Pages deployment

Monitor at: <https://github.com/crypdick/tools/actions>

## 📊 Workflow Status

Run `gh run list --limit 5` to see recent workflow runs:

```shell
cd /Users/rdecal/src/PERSONAL/tools
gh run list --limit 5
```

All should show ✅ success!

---

## 🐛 Troubleshooting

### Custom domain shows 404

- **Check DNS is propagated**: `dig tools.ricardodecal.com`
- **Verify CNAME file** contains: `tools.ricardodecal.com`
- **Configure custom domain in GitHub**: Settings → Pages → Custom domain
- Wait 5-15 minutes for DNS propagation (can take up to 24-48 hours)

### HTTPS certificate not provisioning

- Ensure Cloudflare proxy is OFF (DNS only)
- Wait up to 24 hours for certificate provisioning
- Try removing and re-adding custom domain in GitHub settings

### Workflow failures

- Check workflow logs: `gh run view <run-id> --log-failed`
- Ensure all pre-commit hooks pass locally: `pre-commit run --all-files`
- Verify pytest can find tests: `uv run --with pytest pytest tests/ -v`

### Verify deployment

- Check workflow completed: <https://github.com/crypdick/tools/actions>
- Verify `index.html` is in repository root
- Confirm GitHub Pages source is set to "GitHub Actions"

---

## 📝 Updating the Site

Any push to `main` automatically rebuilds and deploys. You can:

1. Edit `index.html` to update the landing page
2. Add more HTML pages (accessible at `tools.ricardodecal.com/filename.html`)
3. Organize pages in subdirectories

---

## 📚 Resources

- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [Custom Domain Configuration](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site)
- [Cloudflare + GitHub Pages](https://blog.cloudflare.com/secure-and-fast-github-pages-with-cloudflare/)
