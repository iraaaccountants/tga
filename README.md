# TGA Website

Corporate website for TGA Manangement Consultancy LLC, with a homepage, separate About Us, Why TGA and Our Team pages, Contact Us page, FAQ page, brand page, Media Kit, Privacy Policy, Terms and Conditions, service directory, seven main categories, sixteen detailed service area pages, three additional assistance pages, and 22 individual subservice pages.

## Preview locally

Run a local static server from this directory (for example, `python -m http.server 8000`) and open `http://localhost:8000/`. The site uses plain HTML, CSS, and JavaScript, so no build step is required. Local hosting keeps root-relative home links working as they do on the live site.

## Files

- `index.html` — homepage content and structure
- `about.html`, `why-tga.html`, `our-team.html`, `kintu-gandhi.html` and `contact.html` — company, approach, team, Managing Partner profile and contact pages
- `faq.html` — questions about TGA service areas and preparing an enquiry
- `brand.html`, `media-kit.html`, `privacy.html`, `terms.html` — brand resources, downloads and website notices
- `services.html` — landing page listing all service categories and subservices
- `business-setup.html`, `pro-services.html`, `accounting-bookkeeping-audit.html`, `tax-advisory-transfer-pricing.html`, `aml-compliance.html` — individual service pages
- 22 individual subservice `.html` pages — detailed pages linked from the directory and category pages
- `visa-immigration.html`, `labour-mohre.html`, `document-clearing.html`, `police-clearance.html`, and `poa-registration-assistance.html` — visa, document, clearance and POA assistance
- `styles.css` — layout, responsive styling, and blue theme
- `script.js` — mobile menu and sticky header behavior
- `assets/` — WebP logo and photography, client and jurisdiction logos, a labelled team collage, plus square PNG favicon and touch icons; `assets/media-kit/TGA-Media-Kit.zip` contains web-ready downloads
- `robots.txt` and `sitemap.xml` — crawler guidance for all 54 canonical pages and key page images
- `scripts/check_seo.py` — checks metadata, structured data syntax, local links, favicon references and sitemap coverage before publishing
- `llms.txt` and `index.md` — concise AI-readable guide and Markdown version of the page content; `llm.txt` points to the standard `llms.txt` filename
- `business.json` and `openapi.json` — read-only public company profile and its OpenAPI 3.1 description

## Search and social metadata

Each page has its own title, description, canonical URL, social metadata and structured data for `https://www.tga-uae.com/`. The sitemap lists 36 pages, including brand, Media Kit and website notices; section anchors are not separate pages. The favicon uses PNG and ICO formats for search-engine and browser compatibility. Run `python scripts/check_seo.py` before publishing. The OpenAPI file describes only the static `business.json` resource and does not imply a transactional API. The site is also hosted separately on an nginx server; pushing to GitHub does not update that server automatically. Production nginx redirects `/index.html` to `/` and sends `noindex` headers on the Markdown, JSON and `llms.txt` companion resources so HTML pages remain the search results.

Contact details and company claims should be reviewed before a public launch.
