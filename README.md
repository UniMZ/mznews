# mznews

Mass spectrometry news and literature from UniMZ. A compact bilingual static publication for GitHub Pages.

## Build

Run `python scripts/build.py` with Python 3.10 or newer, then `python -m unittest discover -s tests`. No packages are required. Preview with `python -m http.server 8000`. Generated HTML, CSS, JavaScript and RSS are committed, so GitHub Pages can serve the repository root directly. The check workflow verifies that generated pages match their source.

The existing GitHub Pages settings determine deployment. This project does not change those settings. Set `url` in `site.json` to the confirmed public site URL before building; it controls canonical and RSS links. Relative navigation supports both a custom domain and the GitHub project path. Preserve any existing CNAME file.

## Add or edit an article

Create one UTF-8 JSON file in `content/posts/`, using the launch post as a complete example. Every post has exactly these fields:

- `slug`: stable lowercase URL slug; do not rename after publication.
- `date`: `YYYY-MM-DD`, using the Beijing publication date.
- `category`: `News`, `Latest`, `Spotlight`, or `Classics`.
- `title` and `summary`: objects with `en` and `zh` text.
- `body`: `en` and `zh` arrays of plain-text paragraphs.
- `links`: a list of `{ "label": "...", "url": "https://..." }`; local site paths may start with `/`.
- `papers`: an ordered array, empty for an announcement. Each paper has `title` (original title), `authors` (complete ordered array of names), `journal`, `year` (string), `url` (original HTTPS paper link), and `commentary` (`en` and `zh` editorial text).

Each Latest entry is one complete daily digest with multiple papers, in the selected reading order. Create at most one digest for a date. Spotlight and Classics each introduce one paper. Preserve original paper titles and author names in both languages; translate only editorial prose. Interface and navigation stay English. Use bibliographic information, original commentary and paper links. Do not reproduce papers or add evaluation metrics or private material.

The build validates the explicit schema and safely escapes all text. Unknown fields fail validation. English and Chinese article pages have stable URLs under `posts/YYYY-MM-DD-slug/` and `posts/YYYY-MM-DD-slug/zh/`. Home combines all categories in reverse date order. Empty sections remain empty until actual articles are added. RSS contains one entry per post. Search works in either language; without JavaScript all articles remain available.

After editing, rebuild, run the checks, and commit the source together with generated files. A pull request runs the same checks before merge. Deleting or changing a published slug requires separately removing its old generated directory and considering existing external links.
