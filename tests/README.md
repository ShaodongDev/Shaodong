# Blog regression checks

Build with the deployed Hugo version (0.120.4 extended), then check the output:

```sh
hugo --minify --destination /tmp/shaodong-check
python3 tests/verify-build.py /tmp/shaodong-check
node --test cloudflare/domain-redirects/index.test.mjs
```

To compare a change against an earlier build, add
`--baseline /path/to/earlier-build` to the Python command. This also checks that
existing output URLs, original article titles, body text and non-image markup,
article fragments, original images/PDFs, feed titles, content, item IDs and
publication dates survive the change. Image markup may change for optimization.

Image variants are generated from page-bundle resources at build time. Original
files are retained. Browser pages use responsive WebP sources with a PNG/JPEG
fallback, while RSS uses absolute conventional image URLs without lazy loading.

The posts archive remains fully linked without JavaScript. JavaScript adds
filtering and browser-history behavior; ordinary tag links lead to scoped,
server-rendered taxonomy pages.
