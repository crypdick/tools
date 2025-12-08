# GitHub Pages Setup Guide

This guide will help you set up GitHub Pages for this repository at `tools.ricardodecal.com`.

## Step 1: Push the Files to GitHub

First, commit and push the new files we've created:

```bash
git add index.html CNAME .nojekyll .github/workflows/pages.yml
git commit -m "Add GitHub Pages setup"
git push origin main
```

## Step 2: Enable GitHub Pages in Repository Settings

1. Go to your repository on GitHub: https://github.com/crypdick/tools
2. Click on **Settings** (top menu)
3. In the left sidebar, click on **Pages** (under "Code and automation")
4. Under **Source**, select:
   - **Source**: GitHub Actions

   ⚠️ **Important**: Do NOT use "Deploy from a branch" - use "GitHub Actions" instead, since we created a custom workflow.

5. The page will show a message about the custom domain after the first deployment

## Step 3: Configure DNS in Cloudflare

Now you need to add a DNS record in Cloudflare to point `tools.ricardodecal.com` to GitHub Pages:

1. Log into your Cloudflare dashboard
2. Select your domain `ricardodecal.com`
3. Go to **DNS** settings
4. Click **Add record**
5. Configure as follows:
   - **Type**: `CNAME`
   - **Name**: `tools` (this creates tools.ricardodecal.com)
   - **Target**: `crypdick.github.io` (your GitHub Pages URL)
   - **Proxy status**: **DNS only** (gray cloud, not orange)

     ⚠️ **Critical**: Turn OFF Cloudflare's proxy (use "DNS only") initially. You can enable it later after HTTPS is set up.

   - **TTL**: Auto

6. Click **Save**

## Step 4: Verify GitHub Pages Deployment

After pushing your code:

1. Go to the **Actions** tab in your GitHub repository
2. You should see a workflow run for "Deploy to GitHub Pages"
3. Wait for it to complete (usually takes 1-2 minutes)
4. Once complete, go back to **Settings → Pages**
5. You should see: "Your site is live at https://tools.ricardodecal.com"

## Step 5: Enable HTTPS (GitHub will do this automatically)

1. After the first deployment, GitHub will automatically provision an SSL certificate for your custom domain
2. This can take anywhere from a few minutes to 24 hours
3. Once ready, you'll see a checkmark next to "Enforce HTTPS" in Settings → Pages
4. Check the box to enforce HTTPS

## Step 6: Optional - Enable Cloudflare Proxy

After HTTPS is working (step 5 complete):

1. Go back to Cloudflare DNS settings
2. Find your `tools` CNAME record
3. Click to edit it
4. Change **Proxy status** to **Proxied** (orange cloud)
5. Save

This will enable Cloudflare's CDN and DDoS protection.

## Troubleshooting

### Custom domain not working
- DNS can take up to 24-48 hours to propagate, but usually takes 5-15 minutes
- Verify your CNAME record in Cloudflare points to `crypdick.github.io`
- Make sure the CNAME file in your repository contains `tools.ricardodecal.com`

### HTTPS not working
- GitHub needs time to provision the SSL certificate (can take up to 24 hours)
- Ensure Cloudflare proxy is OFF (DNS only) when first setting up
- Try removing and re-adding the custom domain in GitHub Settings → Pages

### 404 errors
- Make sure the workflow completed successfully
- Check that `index.html` is in the root of your repository
- Verify the GitHub Pages source is set to "GitHub Actions"

### Check DNS propagation
You can check if your DNS is propagated using:
```bash
dig tools.ricardodecal.com
nslookup tools.ricardodecal.com
```

You should see it pointing to GitHub's servers (ending in github.io).

## Updating the Site

Any time you push to the `main` branch, the GitHub Actions workflow will automatically rebuild and deploy your site. You can:

1. Edit `index.html` to update the landing page
2. Add more HTML pages (they'll be accessible at `tools.ricardodecal.com/filename.html`)
3. Organize pages in subdirectories

## Testing Locally

To test your `index.html` locally before pushing:

```bash
# Simple Python HTTP server
python3 -m http.server 8000

# Then visit http://localhost:8000
```

## References

- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [Configuring a custom domain](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site)
- [Cloudflare and GitHub Pages](https://blog.cloudflare.com/secure-and-fast-github-pages-with-cloudflare/)
