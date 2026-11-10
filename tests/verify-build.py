#!/usr/bin/env python3
"""Check generated SEO, images, feeds and existing URLs with Python's stdlib."""
import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import unquote, urljoin, urlsplit
import xml.etree.ElementTree as ET


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.meta, self.links, self.images, self.sources, self.scripts = [], [], [], [], []
        self.ids, self.posts, self.jsonld = set(), [], []
        self.lang, self.title, self.in_title, self.in_json = '', '', False, False
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get('id'):
            self.ids.add(a['id'])
        if tag == 'html':
            self.lang = a.get('lang', '')
        if tag == 'meta':
            self.meta.append(a)
        if tag in ('a', 'link'):
            self.links.append(a)
        if tag == 'a' and 'post-link' in a.get('class', '').split():
            self.posts.append(a)
        if tag == 'img':
            self.images.append(a)
        if tag == 'source':
            self.sources.append(a)
        if tag == 'title':
            self.in_title = True
        if tag == 'script':
            self.scripts.append(a)
            self.in_json = a.get('type') == 'application/ld+json'

    def handle_endtag(self, tag):
        if tag == 'title':
            self.in_title = False
        if tag == 'script':
            self.in_json = False

    def handle_data(self, text):
        if self.in_title:
            self.title += text
        if self.in_json:
            self.jsonld.append(text)

    def metadata(self, name):
        return next((m.get('content', '') for m in self.meta if (m.get('name') or m.get('property')) == name), '')


class Content(HTMLParser):
    """Record article markup while ignoring responsive image substitutions."""
    void = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}
    image_tags = {'picture', 'source', 'img'}

    def __init__(self, html, article=True):
        super().__init__(convert_charrefs=True)
        self.article, self.depth, self.events = article, 0, []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        if self.article and not self.depth:
            if tag == 'div' and 'article_content' in dict(attrs).get('class', '').split():
                self.depth = 1
            return
        if tag not in self.image_tags:
            self.events.append(('start', tag, tuple(sorted(attrs))))
        if self.article and tag not in self.void:
            self.depth += 1

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.void:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if self.article and not self.depth:
            return
        if self.article and tag not in self.void:
            self.depth -= 1
            if not self.depth:
                return
        if tag not in self.image_tags and tag not in self.void:
            self.events.append(('end', tag))

    def handle_data(self, text):
        if not self.article or self.depth:
            normalized = re.sub(r'\s+', ' ', text).strip()
            if normalized:
                self.events.append(('text', normalized))


def disk_path(root, url):
    path = root / unquote(urlsplit(url).path).lstrip('/')
    return path / 'index.html' if path.is_dir() else path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('build', type=Path)
    parser.add_argument('--baseline', type=Path)
    args = parser.parse_args()
    root = args.build.resolve()
    sitemap = ET.parse(root / 'sitemap.xml')
    urls = [e.text for e in sitemap.iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
    articles = [u for u in urls if re.search(r'/20\d\d/\d\d/\d\d/[^/]+/$', u)]
    assert articles, 'No article URLs in sitemap'
    descriptions, article_pages = [], {}

    for url in urls:
        assert disk_path(root, url).is_file(), f'Missing sitemap page: {url}'
        page = Page(disk_path(root, url).read_text())
        assert 'noindex' not in page.metadata('robots'), f'Noindex URL in sitemap: {url}'

    for url in articles:
        path = disk_path(root, url)
        page = Page(path.read_text())
        article_pages[url] = page
        assert page.lang in ('en', 'zh-CN'), (url, page.lang)
        assert page.metadata('robots') == 'index,follow', url
        assert [a['href'] for a in page.links if a.get('rel') == 'canonical'] == [url], url
        description = page.metadata('description').strip()
        assert len(description) > 20, f'Blank or unhelpful description: {url}'
        descriptions.append(description)
        schemas = [json.loads(s) for s in page.jsonld]
        schema = next(s for s in schemas if s.get('@type') == 'BlogPosting')
        assert schema['author']['name'] == page.metadata('author'), url
        assert schema['author']['url'].endswith('/about/'), url
        assert schema['description'].strip() == description, url
        assert all(disk_path(root, image).is_file() for image in schema['image']), f'Broken social/schema image: {url}'
        assert any('utteranc.es/client.js' in s.get('src', '') for s in page.scripts), url
        for image in page.images:
            assert image.get('alt', '').strip(), f'Missing alt: {url} {image}'
            assert int(image.get('width', 0)) > 0 and int(image.get('height', 0)) > 0, image
            assert disk_path(root, urljoin(url, image['src'])).is_file(), image
        for source in page.sources:
            for candidate in source['srcset'].split(', '):
                assert disk_path(root, urljoin(url, candidate.split()[0])).is_file(), candidate
        for link in page.links:
            href = link.get('href', '')
            if href.startswith('/') and not href.startswith('//'):
                target = disk_path(root, href)
                assert target.is_file(), f'Broken local link: {url} -> {href}'
                fragment = urlsplit(href).fragment
                if fragment and target.suffix == '.html':
                    assert unquote(fragment) in Page(target.read_text()).ids, (href, fragment)
        if args.baseline:
            old = Page(disk_path(args.baseline, url).read_text())
            assert old.title == page.title, f'Article title changed: {url}'
            assert old.metadata('author') == page.metadata('author'), f'Article author changed: {url}'
            assert Content(disk_path(args.baseline, url).read_text()).events == Content(path.read_text()).events, f'Article text or markup changed: {url}'
            assert old.ids <= page.ids, f'An existing article fragment was removed: {url}'
            assert old.metadata('article:published_time') == page.metadata('article:published_time')

    assert len(descriptions) == len(set(descriptions)), 'Duplicate article descriptions'
    archive = Page((root / 'post/index.html').read_text())
    assert len(archive.posts) == len(articles), 'Archive repeats or omits articles'
    assert all(a.get('data-preview') for a in archive.posts), 'Hover previews missing'
    for url in urls:
        if '/tags/' in url and not url.endswith('/tags/'):
            term = unquote(urlsplit(url).path.rstrip('/').split('/')[-1])
            scoped = Page(disk_path(root, url).read_text())
            for link in scoped.posts:
                article = article_pages[urljoin(url, link['href'])]
                tags = [urlsplit(a['href']).query.lower() for a in article.links if a.get('href', '').startswith('/post/?tag=')]
                assert any(unquote(q).removeprefix('tag=') == term for q in tags), (term, link)

    feed = ET.parse(root / 'feed.xml')
    items = {item.findtext('guid'): item for item in feed.findall('.//item')}
    for guid, item in items.items():
        markup = item.findtext('description', '')
        page = Page(markup)
        for image in page.images:
            assert image['src'].startswith('https://'), (guid, image)
            assert image.get('loading') != 'lazy', (guid, image)
            assert disk_path(root, image['src']).is_file(), image
        assert '<picture' not in markup, 'RSS should have a conventional image fallback'
    if args.baseline:
        previous = ET.parse(args.baseline / 'feed.xml')
        old_items = {item.findtext('guid'): item for item in previous.findall('.//item')}
        assert set(old_items) == set(items), 'RSS item identities changed'
        for guid, old in old_items.items():
            new = items[guid]
            assert old.findtext('pubDate') == new.findtext('pubDate'), guid
            assert old.findtext('title') == new.findtext('title'), guid
            before, after = old.findtext('description', ''), new.findtext('description', '')
            assert Content(before, article=False).events == Content(after, article=False).events, f'RSS content changed: {guid}'
            for tag in ('table', 'pre', 'embed'):
                assert len(re.findall(fr'<{tag}\b', after)) >= len(re.findall(fr'<{tag}\b', before)), (guid, tag)
        before_files = [p for p in args.baseline.rglob('*') if p.is_file()]
        assert all((root / p.relative_to(args.baseline)).is_file() for p in before_files), 'An existing output URL disappeared'
        for p in before_files:
            if p.suffix.lower() in ('.png', '.jpg', '.jpeg', '.pdf'):
                assert p.read_bytes() == (root / p.relative_to(args.baseline)).read_bytes(), f'Original asset altered: {p}'

    assert 'noindex' in Page((root / '404.html').read_text()).metadata('robots')
    assert 'noindex' in Page((root / 'categories/index.html').read_text()).metadata('robots')
    assert not any(u.endswith('/categories/') for u in urls)
    print(f'PASS: {len(articles)} articles; metadata, canonicals, authors, scoped tags, image resources, comments, RSS, existing URLs and original assets.')


if __name__ == '__main__':
    main()
