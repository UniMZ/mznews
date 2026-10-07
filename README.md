# mznews

Mass spectrometry news and literature from UniMZ. A compact bilingual static publication for GitHub Pages.

## Build

Run `python scripts/build.py` with Python 3.10 or newer, then `python -m unittest discover -s tests`. No packages are required. Preview with `python -m http.server 8000`. Generated HTML, CSS, JavaScript and RSS are committed, so GitHub Pages can serve the repository root directly. The check workflow verifies that generated pages match their source.

The existing GitHub Pages settings determine deployment. This project does not change those settings. The confirmed public URL is `https://mznews.unimz.org`, recorded in `site.json`; it controls canonical, RSS and sitemap links. `CNAME` preserves this custom domain. Relative navigation supports both a custom domain and the GitHub project path. Preserve any existing CNAME file.

## Add or edit an article

Create one UTF-8 JSON file in `content/posts/`, using the launch post as a complete example. Every post has exactly these fields:

- `slug`: stable lowercase URL slug; do not rename after publication.
- `date`: `YYYY-MM-DD`, using the Beijing publication date.
- `category`: `News`, `Latest`, `Spotlight`, or `Classics`.
- `title` and `summary`: objects with `en` and `zh` text.
- `body`: `en` and `zh` arrays of plain-text paragraphs.
- `links`: a list of `{ "label": "...", "url": "https://..." }`; local site paths may start with `/`.
- `papers`: an ordered array, empty for an announcement. Each paper has `title` (original title), `authors` (complete ordered array of names), `journal`, `year` (string), `url` (original HTTPS paper link), and `commentary` (`en` and `zh` editorial text).

Optional paper fields are `first_online` (verified `YYYY-MM-DD` date), `publication_status` (`en` and `zh` text, for example identifying a preprint or journal article), `read_scope` (`en` and `zh` text identifying the evidence actually read, such as abstract only), and `doi` (a DOI identifier beginning with `10.`, without a resolver URL). Provide these when verified; omit unknown metadata rather than guessing. A publication year does not establish its first-online date. Metadata appears beside the bibliographic information in each language; field labels stay English.

Each Latest entry is one complete daily digest with zero, one or many papers, in the selected reading order. There is no fixed count, cap or filler requirement. A zero-paper digest must honestly explain the coverage and that no new qualifying papers were found in both language bodies; never invent a paper to fill an entry. Create at most one digest for a date. Spotlight and Classics each introduce one paper. Preserve original paper titles and author names in both languages; translate only editorial prose. Interface and navigation stay English. Use bibliographic information, original commentary and paper links. Do not reproduce papers or add evaluation metrics or private material.

The build validates the explicit schema and safely escapes all text. Unknown fields fail validation. English and Chinese article pages have stable URLs under `posts/YYYY-MM-DD-slug/` and `posts/YYYY-MM-DD-slug/zh/`. Home combines all categories in reverse date order. Empty sections remain empty until actual articles are added. RSS contains one entry per post. Search works in either language; without JavaScript all articles remain available.

After editing, rebuild, run the checks, and commit the source together with generated files. A pull request runs the same checks before merge. Deleting or changing a published slug requires separately removing its old generated directory and considering existing external links.
