#!/usr/bin/env python3
"""Build the static mznews publication with Python's standard library."""
import json, re, posixpath
from pathlib import Path
from datetime import date, datetime, timezone, timedelta
from html import escape as esc
import xml.etree.ElementTree as ET
ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / 'site.json').read_text())
BASE = CONFIG['url'].rstrip('/')
CATEGORIES = ('News', 'Latest', 'Spotlight', 'Classics')

def paired(value):
    assert isinstance(value, dict) and set(value) == {'en', 'zh'}, 'Expected paired en/zh text'
    assert all(isinstance(x, str) and x.strip() for x in value.values()), 'Empty translation'

def validate(post):
    assert set(post) == {'slug','date','category','title','summary','body','links','papers'}, 'Unknown or missing post field'
    assert re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', post['slug'])
    date.fromisoformat(post['date'])
    assert post['category'] in CATEGORIES
    paired(post['title']); paired(post['summary'])
    assert set(post['body']) == {'en','zh'}
    for paragraphs in post['body'].values():
        assert isinstance(paragraphs,list) and paragraphs and all(isinstance(p,str) and p.strip() for p in paragraphs)
    for link in post['links']:
        assert set(link) == {'label','url'}
        assert link['url'].startswith(('https://','/')) and not link['url'].startswith('//')
    for paper in post['papers']:
        assert set(paper) == {'title','authors','journal','year','url','commentary'}, 'Unexpected paper field'
        assert all(isinstance(paper[k],str) and paper[k].strip() for k in ('title','journal','year','url'))
        assert paper['url'].startswith('https://')
        assert isinstance(paper['authors'],list) and paper['authors'] and all(isinstance(a,str) and a.strip() for a in paper['authors'])
        paired(paper['commentary'])
    if post['category'] == 'Latest': assert len(post['papers']) >= 2, 'Latest is a complete multi-paper daily digest'
    if post['category'] in ('Spotlight','Classics'): assert len(post['papers']) == 1
    raw = json.dumps(post,ensure_ascii=False).lower()
    for forbidden in ('notion','mailto:','★','☆','recipient','rating','score'):
        assert forbidden not in raw, f'Disallowed public content: {forbidden}'
    assert not re.search(r'[\w.+-]+@[\w.-]+\.[a-z]{2,}',raw), 'Email address in public content'

POSTS = [json.loads(p.read_text()) for p in sorted((ROOT/'content/posts').glob('*.json'))]
for post in POSTS: validate(post)
assert len({p['slug'] for p in POSTS}) == len(POSTS), 'Duplicate slug'
assert len({p['date'] for p in POSTS if p['category']=='Latest'}) == len([p for p in POSTS if p['category']=='Latest']), 'Only one Latest digest per day'
POSTS.sort(key=lambda p:(p['date'],p['slug']),reverse=True)

def postpath(p,lang='en'):
    return f"posts/{p['date']}-{p['slug']}/" + ('zh/' if lang=='zh' else '')
def href(target,current):
    if target.startswith('https://'): return target
    target = target.lstrip('/')
    result = posixpath.relpath(target or '.',current or '.')
    return result + ('/' if target.endswith('/') or not target else '')
def link(target,label,current,extra=''):
    return f'<a href="{esc(href(target,current))}" {extra}>{esc(label)}</a>'
def shell(title,body,current='',active='Home',lang='en',description='Mass spectrometry news and literature from UniMZ.',alternates=None):
    nav=''.join(link('' if x=='Home' else x.lower()+'/',x,current,'aria-current="page"' if x==active else '') for x in ('Home',)+CATEGORIES)
    alt=''
    if alternates:
        alt=''.join(f'<link rel="alternate" hreflang="{l}" href="{BASE}/{p}">' for l,p in alternates.items())
    return f'''<!doctype html>
<html lang="{'zh-CN' if lang=='zh' else 'en'}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{esc(title)} · mznews</title><meta name="description" content="{esc(description)}"><link rel="canonical" href="{BASE}/{current}">{alt}<link rel="stylesheet" href="{href('assets/style.css',current)}"><link rel="alternate" type="application/rss+xml" title="mznews" href="{href('feed.xml',current)}"></head><body><a class="skip" href="#main">Skip to content</a><header class="wrap"><div class="masthead"><a class="wordmark" href="{href('',current)}"><span class="brand">UniMZ</span>mznews</a><span class="mast-note">MASS SPECTROMETRY · NEWS & LITERATURE</span></div><nav class="nav" aria-label="Main navigation">{nav}</nav></header><main id="main" class="wrap">{body}</main><footer class="wrap"><span>© {date.today().year} UniMZ · mznews</span><div>{link('search/','Search',current)}{link('feed.xml','RSS',current)}{link('https://mzwiki.unimz.org','mzwiki',current)}</div></footer></body></html>'''
def write(path,text):
    p=ROOT/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
def card(p,current,search=False):
    words=' '.join([p['title']['en'],p['title']['zh'],p['summary']['en'],p['summary']['zh']]+p['body']['en']+p['body']['zh']+[v for paper in p['papers'] for v in [paper['title'],' '.join(paper['authors']),paper['journal'],*paper['commentary'].values()]])
    data=f' data-search="{esc(words.lower())}"' if search else ''
    return f'''<article class="card"{data}><div class="meta"><span class="tag">{p['category']}</span><time datetime="{p['date']}">{p['date']}</time></div><h2>{link(postpath(p),p['title']['en'],current)}</h2><p>{esc(p['summary']['en'])}</p>{link(postpath(p),'Read article →',current,'class="read"')}</article>'''
INTRO={'Home':('A closer look at mass spectrometry.','News, recent literature, and perspectives on the research shaping mass spectrometry.'),'News':('News','Updates and announcements from UniMZ.'),'Latest':('Latest','Daily selections from the mass spectrometry literature, collected in one digest.'),'Spotlight':('Spotlight','A closer reading of one current paper.'),'Classics':('Classics','Revisiting the papers that shaped mass spectrometry.')}
for category,(title,description) in INTRO.items():
    current='' if category=='Home' else category.lower()+'/'
    selected=POSTS if category=='Home' else [p for p in POSTS if p['category']==category]
    stream=''.join(card(p,current) for p in selected) or '<p class="empty">No posts yet.</p>'
    body=f'''<section class="hero"><div class="eyebrow">{'The UniMZ journal' if category=='Home' else 'mznews / '+category}</div><h1>{title}</h1><p class="intro">{description}</p></section><div class="layout"><section aria-label="Posts"><h2 class="stream-label">{'All posts' if category=='Home' else category+' posts'}</h2>{stream}</section><aside class="aside"><h2>Part of UniMZ</h2><p>A place to follow mass spectrometry research and discover ideas worth reading.</p>{link('https://mzwiki.unimz.org','Explore mzwiki',current)}<div class="divider"><h2>Keep reading</h2>{link('search/','Search the archive →',current)}<br>{link('feed.xml','Subscribe via RSS →',current)}</div></aside></div>'''
    write(current+'index.html',shell(title,body,current,category,description=description))
for p in POSTS:
    for lang in ('en','zh'):
        current=postpath(p,lang)
        languages='<div class="language" aria-label="Article language"><span>Language</span>'+''.join(link(postpath(p,l),label,current,f'hreflang="{l}" lang="{l}"'+(' aria-current="page"' if l==lang else '')) for l,label in [('en','English'),('zh','中文')])+'</div>'
        prose=''.join(f'<p>{esc(x)}</p>' for x in p['body'][lang])
        papers=''.join(f'''<section class="paper"><h2>{esc(paper['title'])}</h2><p class="authors">{esc('; '.join(paper['authors']))}</p><p class="bibliography">{esc(paper['journal'])} · {esc(paper['year'])}</p><p>{esc(paper['commentary'][lang])}</p>{link(paper['url'],'Read paper',current)}</section>''' for paper in p['papers'])
        links='<div class="article-links">'+''.join(link(l['url'],l['label']+' →',current) for l in p['links'])+'</div>'
        body=f'''<article class="article">{link(p['category'].lower()+'/','← '+p['category'],current,'class="back"')}<h1>{esc(p['title'][lang])}</h1><div class="meta"><span class="tag">{p['category']}</span><time datetime="{p['date']}">{p['date']}</time> · Beijing</div>{languages}<div class="article-body">{prose}{papers}{links}</div></article>'''
        write(current+'index.html',shell(p['title'][lang],body,current,p['category'],lang,p['summary'][lang],{l:postpath(p,l) for l in ('en','zh')}))
body='<section class="hero"><div class="eyebrow">mznews / Archive</div><h1>Search</h1><p class="intro">Find articles in English or Chinese.</p></section><section class="search"><label for="query">Search posts</label><input id="query" type="search" placeholder="Title, topic, or author" autocomplete="off"><p class="search-status" id="search-status" role="status" aria-live="polite"></p><noscript><p>Browse all articles below. Your browser’s Find feature can also search this page.</p></noscript>'+''.join(card(p,'search/',True) for p in POSTS)+'</section><script src="../assets/search.js" defer></script>'
write('search/index.html',shell('Search',body,'search/',''))
write('404.html',shell('Page not found','<section class="hero"><h1>Page not found</h1><p>Please return to the <a href="'+BASE+'/">mznews homepage</a>.</p></section>'))
rss=ET.Element('rss',version='2.0');channel=ET.SubElement(rss,'channel')
for tag,value in [('title','mznews · UniMZ'),('link',BASE+'/'),('description','Mass spectrometry news and literature from UniMZ.'),('language','en')]:ET.SubElement(channel,tag).text=value
for p in POSTS:
    item=ET.SubElement(channel,'item');url=BASE+'/'+postpath(p)
    timestamp=datetime.fromisoformat(p['date']).replace(tzinfo=timezone(timedelta(hours=8)))
    for tag,value in [('title',p['title']['en']),('link',url),('guid',url),('description',p['summary']['en']+' / '+p['summary']['zh']),('category',p['category']),('pubDate',timestamp.strftime('%a, %d %b %Y %H:%M:%S %z'))]:ET.SubElement(item,tag).text=value
write('feed.xml',ET.tostring(rss,encoding='unicode',xml_declaration=True))
write('.nojekyll','')
print(f'Built {len(POSTS)} posts, each in English and Chinese.')
