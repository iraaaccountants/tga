# TGA Website

Corporate website for TGA Manangement Consultancy LLC, with a homepage, service directory landing page, four category pages and 14 individual subservice pages.

## Preview locally

Open `index.html` in a browser. The site uses plain HTML, CSS, and JavaScript, so no build step is required. Service cards link to their own HTML pages.

## Files

- `index.html` — homepage content and structure
- `services.html` — landing page listing all service categories and subservices
- `business-setup-pro.html`, `accounting-bookkeeping-audit.html`, `tax-advisory-transfer-pricing.html`, `aml-compliance.html` — individual service pages
- 14 individual subservice `.html` pages — detailed pages linked from the directory and category pages
- `styles.css` — layout, responsive styling, and blue theme
- `script.js` — mobile menu and sticky header behavior
- `assets/` — WebP versions of the logo, photography, client logos, and jurisdiction logos supplied in the company profile
- `robots.txt` and `sitemap.xml` — crawler guidance for all 20 canonical pages and the main homepage images
- `llms.txt` and `index.md` — concise AI-readable guide and Markdown version of the page content; `llm.txt` points to the standard `llms.txt` filename
- `business.json` and `openapi.json` — read-only public company profile and its OpenAPI 3.1 description

## Search and social metadata

Each page has its own title, description, canonical URL, social metadata and structured data for `https://www.tga-uae.com/`. The sitemap lists the homepage, service directory, four category pages and 14 subservice pages; section anchors are not separate pages. The OpenAPI file describes only the static `business.json` resource and does not imply a transactional API. Publish the site files at the preferred `www` address and redirect the non-`www` version to it before relying on those URLs. The GitHub repository alone does not serve the website at that domain.

Contact details and company claims should be reviewed before a public launch.
