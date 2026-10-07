import json, unittest, xml.etree.ElementTree as ET
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse, unquote
ROOT=Path(__file__).resolve().parents[1]
class Parser(HTMLParser):
    def __init__(self):super().__init__();self.links=[];self.lang=None;self.headings=0
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag=='html':self.lang=attrs.get('lang')
        if tag=='h1':self.headings+=1
        if tag in ('a','link','script'):self.links.append(attrs.get('href',attrs.get('src','')))
class SiteTests(unittest.TestCase):
    def test_pages_and_links(self):
        for file in ROOT.rglob('*.html'):
            parser=Parser();parser.feed(file.read_text());self.assertIn(parser.lang,['en','zh-CN']);self.assertEqual(parser.headings,1)
            for link in parser.links:
                if not link or link.startswith(('#','https://')):continue
                path=(file.parent/unquote(urlparse(link).path)).resolve()
                self.assertTrue(path.exists(),f'{file}: {link}')
    def test_launch_and_categories(self):
        posts=[json.loads(p.read_text()) for p in (ROOT/'content/posts').glob('*.json')]
        post=next(p for p in posts if p['slug']=='mznews-is-live');self.assertEqual(post['category'],'News');self.assertEqual(post['title']['en'],'mznews is live');self.assertEqual(post['date'],'2026-10-07')
        for cat in ('latest','spotlight','classics'):
            if not any(p['category'].lower()==cat for p in posts):
                self.assertIn('No posts yet.',(ROOT/cat/'index.html').read_text())
        for language in ('','zh/'):
            text=(ROOT/f'posts/2026-10-07-mznews-is-live/{language}index.html').read_text()
            self.assertIn('https://mzwiki.unimz.org',text);self.assertIn('hreflang="en"',text);self.assertIn('hreflang="zh"',text)
    def test_feed(self):
        items=ET.parse(ROOT/'feed.xml').findall('./channel/item');self.assertEqual(len(items),len(list((ROOT/'content/posts').glob('*.json'))));self.assertIn('mznews is live',[i.findtext('title') for i in items])
    def test_public_content(self):
        for file in [*ROOT.rglob('*.html'),*ROOT.glob('content/posts/*.json'),ROOT/'feed.xml']:
            text=file.read_text().lower()
            for word in ('notion','rating','score','recipient','mailto:','★','☆'):
                self.assertNotIn(word,text,str(file))
if __name__=='__main__':unittest.main()
