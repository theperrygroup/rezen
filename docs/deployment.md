# Documentation Deployment Guide

This guide covers all available options for deploying the ReZEN Python client documentation automatically.

## 📋 Table of Contents

- [GitHub Pages (Recommended)](#github-pages-recommended)
- [Netlify](#netlify)
- [Vercel](#vercel)
- [Read the Docs](#read-the-docs)
- [Manual Deployment](#manual-deployment)
- [Custom Domain Setup](#custom-domain-setup)
- [Troubleshooting](#troubleshooting)

---

## GitHub Pages (Recommended)

**✅ Automatic | ✅ Free | ✅ Custom Domain Support**

The recommended deployment method using GitHub Actions for automatic builds and GitHub Pages for hosting.

### Setup Steps

1. **Enable GitHub Pages**:
   - Go to your repository **Settings** → **Pages**
   - Set **Source** to "GitHub Actions"
   - The workflow is already configured in `.github/workflows/docs.yml`

2. **Verify Workflow**:
   ```yaml
   # The workflow automatically triggers on:
   # - Pushes to main/master branch
   # - Changes to docs/ folder
   # - Changes to mkdocs.yml
   # - Manual trigger via GitHub UI
   ```

3. **Access Documentation**:
   - Your docs will be available at: `https://username.github.io/repository-name/`
   - Check the Actions tab for deployment status

### Features

- ✅ **Automatic deployment** on every push to main
- ✅ **PR preview builds** (test-only, not deployed)
- ✅ **Build caching** for faster deployments
- ✅ **Strict mode** catches documentation errors
- ✅ **Custom domain** support with HTTPS

### Configuration

The GitHub Actions workflow (`.github/workflows/docs.yml`) includes:

- **Build job**: Builds documentation and uploads artifacts
- **Deploy job**: Deploys to GitHub Pages (main branch only)
- **Test job**: Tests documentation builds on PRs

---

## Netlify

**✅ Automatic | ✅ Free Tier | ✅ Preview Deployments**

Deploy to Netlify for enhanced features like form handling and edge functions.

### Setup Steps

1. **Get Netlify Credentials**:
   ```bash
   # Install Netlify CLI
   npm install -g netlify-cli
   
   # Login and get tokens
   netlify login
   netlify sites:create --name rezen-python-docs
   ```

2. **Set GitHub Secrets**:
   - Go to **Settings** → **Secrets and variables** → **Actions**
   - Add secrets:
     - `NETLIFY_AUTH_TOKEN`: Your Netlify personal access token
     - `NETLIFY_SITE_ID`: Your site ID from Netlify dashboard

3. **Enable Workflow**:
   ```bash
   # The workflow file is already created at:
   # .github/workflows/deploy-netlify.yml
   
   # To enable it, uncomment or create the file
   git add .github/workflows/deploy-netlify.yml
   git commit -m "Enable Netlify deployment"
   git push
   ```

### Features

- ✅ **Branch previews** for every PR
- ✅ **Form handling** (if you add contact forms)
- ✅ **Edge functions** for advanced features
- ✅ **Analytics** and performance monitoring
- ✅ **Custom headers** and redirects

---

## Vercel

**✅ Automatic | ✅ Free Tier | ✅ Global CDN**

Deploy to Vercel for excellent performance and developer experience.

### Setup Steps

1. **Connect Repository**:
   - Go to [Vercel Dashboard](https://vercel.com/dashboard)
   - Click **"New Project"**
   - Import your GitHub repository

2. **Configure Build Settings**:
   ```json
   // vercel.json is already configured with:
   {
     "buildCommand": "pip install -r docs/requirements.txt && mkdocs build",
     "installCommand": "pip install -r docs/requirements.txt",
     "framework": null
   }
   ```

3. **Deploy**:
   - Vercel automatically detects the `vercel.json` configuration
   - Pushes to main branch trigger automatic deployments
   - PRs get preview deployments

### Features

- ✅ **Zero-config deployment** with `vercel.json`
- ✅ **Preview URLs** for every commit
- ✅ **Global CDN** with edge caching
- ✅ **Analytics** and Web Vitals monitoring
- ✅ **Custom domains** with automatic HTTPS

---

## Read the Docs

**✅ Automatic | ✅ Free | ✅ Multiple Formats**

Use Read the Docs for comprehensive documentation hosting with PDF/ePub generation.

### Setup Steps

1. **Create RTD Account**:
   - Go to [Read the Docs](https://readthedocs.org/)
   - Sign up with your GitHub account

2. **Import Project**:
   - Click **"Import a Project"**
   - Select your repository
   - RTD automatically detects the `.readthedocs.yml` configuration

3. **Configure Build**:
   ```yaml
   # .readthedocs.yml is already configured with:
   # - Python 3.11
   # - MkDocs build system
   # - PDF/ePub generation
   # - Custom requirements
   ```

### Features

- ✅ **Multiple formats**: HTML, PDF, ePub
- ✅ **Version management** for different branches/tags
- ✅ **Search integration** with Elasticsearch
- ✅ **Analytics** and download tracking
- ✅ **Custom themes** and branding

---

## Manual Deployment

For custom hosting or one-time deployments.

### Build Locally

```bash
# Install dependencies
pip install -r docs/requirements.txt

# Build documentation
mkdocs build

# The built site is in ./site/ directory
# Upload contents to your web server
```

### Deploy to Any Static Host

```bash
# Examples for popular hosts:

# Amazon S3
aws s3 sync site/ s3://your-bucket-name/ --delete

# Google Cloud Storage
gsutil -m rsync -r -d site/ gs://your-bucket-name/

# Azure Blob Storage
az storage blob upload-batch -s site/ -d '$web' --account-name youraccount

# Firebase Hosting
firebase deploy --only hosting

# Surge.sh
npm install -g surge
cd site/
surge . your-domain.com
```

---

## Custom Domain Setup

Configure a custom domain for your documentation.

### GitHub Pages

1. **Add CNAME file**:
   ```bash
   echo "docs.yourdomain.com" > docs/CNAME
   git add docs/CNAME
   git commit -m "Add custom domain"
   git push
   ```

2. **Configure DNS**:
   ```
   # Add these DNS records:
   Type: CNAME
   Name: docs (or your subdomain)
   Value: username.github.io
   ```

3. **Enable HTTPS**:
   - Go to **Settings** → **Pages**
   - Check **"Enforce HTTPS"**

### Netlify

1. **Add Domain**:
   ```bash
   netlify domains:add docs.yourdomain.com
   ```

2. **Configure DNS**:
   ```
   # Add CNAME record:
   Type: CNAME
   Name: docs
   Value: your-site-name.netlify.app
   ```

### Vercel

1. **Add Domain**:
   - Go to project **Settings** → **Domains**
   - Add your custom domain

2. **Configure DNS**:
   ```
   # Add CNAME record:
   Type: CNAME
   Name: docs
   Value: cname.vercel-dns.com
   ```

---

## Troubleshooting

### Common Issues

#### Build Failures

```bash
# Check MkDocs configuration
mkdocs serve --strict

# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('mkdocs.yml'))"

# Check for missing dependencies
pip install -r docs/requirements.txt
```

#### Missing Files

```bash
# Ensure all navigation files exist
mkdocs build --strict

# Check for broken links
pip install mkdocs-linkcheck
mkdocs build --strict --config-file mkdocs.yml
```

#### GitHub Actions Failures

```yaml
# Common fixes in .github/workflows/docs.yml:

# 1. Check permissions (already configured)
permissions:
  contents: read
  pages: write
  id-token: write

# 2. Verify Python version
python-version: '3.11'

# 3. Check path filters
paths:
  - 'docs/**'
  - 'mkdocs.yml'
```

#### Deployment Issues

```bash
# GitHub Pages not showing changes
# - Check Actions tab for build status
# - Verify Pages settings in repository
# - Clear browser cache

# Netlify build failures
# - Check build logs in Netlify dashboard
# - Verify environment variables
# - Test build locally

# Vercel deployment issues
# - Check build logs in Vercel dashboard
# - Verify vercel.json configuration
# - Test with Vercel CLI locally
```

### Debug Commands

```bash
# Test local build
mkdocs build --clean --strict

# Serve locally with auto-reload
mkdocs serve --dev-addr=0.0.0.0:8000

# Check for plugin issues
mkdocs serve --verbose

# Validate all links
pip install mkdocs-linkcheck
mkdocs build --strict

# Performance profiling
mkdocs build --clean --strict --verbose --timing
```

---

## Monitoring & Analytics

### GitHub Pages

```html
<!-- Add to docs/extra.html -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

### Update mkdocs.yml

```yaml
extra:
  analytics:
    provider: google
    property: G-XXXXXXXXXX  # Replace with your GA4 ID
```

---

## Recommended Setup

For most projects, we recommend:

1. **Primary**: GitHub Pages with GitHub Actions (free, reliable)
2. **Preview**: Enable PR comments for build status
3. **Custom Domain**: Set up `docs.yourdomain.com`
4. **Analytics**: Add Google Analytics for usage insights
5. **Monitoring**: Set up alerts for build failures

**Next Steps**:
- ✅ Push to main branch to trigger first deployment
- ✅ Set up custom domain (optional)
- ✅ Configure analytics (optional)
- ✅ Monitor build status and fix any issues

Your documentation will be automatically deployed and updated whenever you make changes to the `docs/` folder or `mkdocs.yml` file! 