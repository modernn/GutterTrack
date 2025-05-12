# GutterTrack Deployment Guide

This guide explains how to deploy the GutterTrack Designer application to various hosting platforms.

## Building for Deployment

Before deploying, you need to build the application as a Progressive Web App (PWA):

```bash
# Install Flet if you haven't already
pip install flet==0.28.2

# Package the app as a PWA
flet pack main.py --pwa
```

This will create a `build` directory containing the compiled PWA files ready for deployment.

## Deployment Options

### 1. Netlify (Recommended)

Netlify provides an easy, free way to deploy static sites with a global CDN:

1. **Sign up** for a free Netlify account at [netlify.com](https://www.netlify.com/)
2. **Drag and drop** the `build` directory onto the Netlify dashboard, or
3. **Connect your GitHub repository** for continuous deployment:
   - Push your code to GitHub
   - In Netlify, choose "New site from Git"
   - Select your repository
   - Set build command to `flet pack main.py --pwa`
   - Set publish directory to `build`

### 2. GitHub Pages

Deploy using GitHub Pages:

1. **Push your code** to a GitHub repository
2. **Create a GitHub Actions workflow** file at `.github/workflows/deploy.yml`:

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [ main ]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
          
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install flet==0.28.2
          
      - name: Build PWA
        run: flet pack main.py --pwa
        
      - name: Deploy to GitHub Pages
        uses: JamesIves/github-pages-deploy-action@4.1.4
        with:
          branch: gh-pages
          folder: build
```

3. **Enable GitHub Pages** in your repository settings, using the `gh-pages` branch

### 3. Firebase Hosting

Deploy to Firebase for fast global hosting:

1. **Install Firebase CLI**:
   ```bash
   npm install -g firebase-tools
   ```

2. **Initialize Firebase** in your project directory:
   ```bash
   firebase login
   firebase init hosting
   ```
   - Select "Use an existing project" or create a new one
   - Set your public directory to `build`
   - Configure as a single-page app: Yes
   - Set up automatic builds and deploys: No

3. **Deploy to Firebase**:
   ```bash
   firebase deploy --only hosting
   ```

### 4. Any Static Host

The compiled PWA can be deployed to any service that can host static files:

- Amazon S3 + CloudFront
- Google Cloud Storage
- Microsoft Azure Storage
- Vercel
- Cloudflare Pages
- Digital Ocean App Platform

Simply upload the contents of the `build` directory to your chosen host.

## PWA Configuration

The PWA is configured through the `pwa.json` file that gets generated during the build process. You can customize this before building by creating a `pwa.json` file in your project directory:

```json
{
  "name": "GutterTrack Designer",
  "short_name": "GutterTrack",
  "start_url": ".",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#0175C2",
  "description": "Design RC tracks with gutter pieces",
  "orientation": "any",
  "icons": [
    {
      "src": "icons/icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "icons/icon-512.png",
      "sizes": "512x512",
      "type": "image/png"
    },
    {
      "src": "icons/icon-maskable-192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "maskable"
    },
    {
      "src": "icons/icon-maskable-512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "maskable"
    }
  ]
}
```

Make sure to create these icon files in an `icons` directory before building.

## Testing Your Deployment

After deploying, verify that:

1. The application loads correctly
2. The PWA can be installed (look for an "Add to Home Screen" or installation option)
3. The application works offline (try disconnecting from the internet after first load)
4. Track saving/loading functionality works properly

## Troubleshooting

### Common Issues

1. **"Page not found" errors on refresh**:
   - Configure your host to redirect all requests to `index.html` for client-side routing

2. **PWA not installable**:
   - Ensure your site is served over HTTPS
   - Verify that all required icons are present
   - Check the browser console for PWA-related errors

3. **Offline functionality not working**:
   - Make sure the service worker is registered correctly
   - Verify cache storage is working in your browser

### Debug Mode

For debugging deployment issues, you can build with debug mode enabled:

```bash
flet pack main.py --pwa --debug
```

This adds additional logging to the console that can help identify problems.

## Advanced: Custom Domain Setup

For a professional deployment, set up a custom domain:

1. **Purchase a domain** from a domain registrar (Namecheap, GoDaddy, Google Domains, etc.)
2. **Configure DNS** to point to your hosting provider
3. **Set up HTTPS** using your host's SSL certificate options or Let's Encrypt
4. **Update your PWA configuration** with the correct start_url and icons paths

## Keeping Up-to-Date

When you make updates to your application:

1. **Test locally** to ensure everything works
2. **Build a new PWA package**
3. **Re-deploy** using the same process as above
4. **Verify** that the service worker updates correctly

For users who have installed the PWA, a new version notification should appear when you update.