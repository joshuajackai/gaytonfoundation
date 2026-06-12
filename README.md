# Boots on the Ground · An Evening of Legacy

Event website for the Chandler Walker Gayton Foundation memorial fundraiser honoring Chandler Walker Gayton (1990 to 2024).

**Event:** Saturday, December 5, 2026 · 5 PM to 12 AM
**Venue:** Dsquared, 4105 Airport Way S., Seattle, WA 98108

## Staging

Staging site is published via Cloudflare:
https://gaytonfoundation.joshua-888.workers.dev/

## Structure

A single self-contained static page. All styles and scripts are inline in `index.html`. External dependencies load from CDNs (Google Fonts, Unsplash imagery).

## Local preview

Open `index.html` in a browser, or run any static server:

```
npx serve .
```

## Deploying to Cloudflare

Connect this repository in the Cloudflare dashboard (Workers & Pages → Create → connect to Git) and select the `main` branch. No build command is needed. Output directory is the repo root.

Maintained by Josh Jackai for the Chandler Walker Gayton Foundation.
