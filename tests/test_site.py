import json, unittest, xml.etree.ElementTree as ET
import copy, runpy
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
BUILD=runpy.run_path(str(ROOT/'scripts/build.py'))
class SiteTests(unittest.TestCase):
    def test_latest_paper_counts_and_metadata(self):
        post=json.loads((ROOT/'content/posts/2026-10-07-mznews-is-live.json').read_text())
        post['category']='Latest'
        post['body']={'en':['No new qualifying papers were found in the sources checked today.'], 'zh':['今天检查的来源中未发现符合条件的新论文。']}
        paper={'title':'Original paper title', 'authors':['First Author','Second Author'], 'journal':'Journal', 'year':'2026', 'url':'https://example.org/paper', 'commentary':{'en':'Editorial discussion.', 'zh':'编辑评论。'}, 'first_online':'2026-10-07', 'publication_status':{'en':'Preprint','zh':'预印本'}, 'read_scope':{'en':'Abstract only','zh':'仅摘要'}, 'doi':'10.1234/example'}
        for count in (0,1,5):
            with self.subTest(count=count):
                post['papers']=[copy.deepcopy(paper) for _ in range(count)]
                BUILD['validate'](post)
        for lang,scope in [('en','Abstract only'),('zh','仅摘要')]:
            rendered=BUILD['paper_metadata'](paper,lang)
            self.assertIn('2026-10-07',rendered)
            self.assertIn(scope,rendered)
            self.assertIn('10.1234/example',rendered)
        post['papers']=[];post['body']['en']=[]
        with self.assertRaises(AssertionError): BUILD['validate'](post)
        for field,value in [('first_online','2026-02-30'),('read_scope',{'en':'Abstract only'}),('doi','invalid'),('unexpected','private')]:
            invalid=copy.deepcopy(paper);invalid[field]=value
            post['body']['en']=['Coverage statement.'];post['papers']=[invalid]
            with self.subTest(field=field),self.assertRaises((AssertionError,ValueError)): BUILD['validate'](post)

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
    def test_custom_domain(self):
        base='https://mznews.unimz.org'
        self.assertEqual(json.loads((ROOT/'site.json').read_text())['url'],base)
        self.assertEqual((ROOT/'CNAME').read_text().strip(),'mznews.unimz.org')
        for file in [*ROOT.rglob('*.html'),ROOT/'feed.xml',ROOT/'sitemap.xml',ROOT/'robots.txt']:
            text=file.read_text()
            self.assertNotIn('unimz.github.io',text)
            self.assertNotIn('/mznews/',text)
        locations=ET.parse(ROOT/'sitemap.xml').findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
        self.assertEqual(len(locations),6+2*len(list((ROOT/'content/posts').glob('*.json'))))
        for location in locations:
            self.assertTrue(location.text.startswith(base+'/'))
            target=ROOT/location.text.removeprefix(base+'/')/'index.html'
            self.assertTrue(target.exists(),str(target))
        for file in ROOT.rglob('index.html'):
            path=file.parent.relative_to(ROOT).as_posix()
            expected=base+'/' if path=='.' else base+'/'+path+'/'
            self.assertIn('<link rel="canonical" href="'+expected+'">',file.read_text())
    def test_public_content(self):
        for file in [*ROOT.rglob('*.html'),*ROOT.glob('content/posts/*.json'),ROOT/'feed.xml']:
            text=file.read_text().lower()
            for word in ('notion','rating','score','recipient','mailto:','★','☆'):
                self.assertNotIn(word,text,str(file))
if __name__=='__main__':unittest.main()
