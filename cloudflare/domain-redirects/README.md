# Blog domain redirects

This Worker permanently redirects the blog's alternate hostnames to
`https://zhangshaodong.com`, preserving paths and query strings. HTTP 308 also
preserves request methods. It has no route on the canonical hostname, so normal
blog traffic continues to use Cloudflare Pages directly.

The Worker is separate from the Hugo build. Cloudflare Pages `_redirects` files
do not support hostname matching; this uses Cloudflare's documented Worker
domain-redirect pattern instead.

## Test and deploy

From the repository root, with Wrangler authenticated to the blog's account:

```sh
node --test cloudflare/domain-redirects/index.test.mjs
npx wrangler deploy --config cloudflare/domain-redirects/wrangler.jsonc
```

The two `shaodong.name` routes require an active domain registration, delegation
to its Cloudflare nameservers, a proxied DNS record, and working HTTPS. A route
on Cloudflare cannot intercept a domain still delegated to an expiry-parking
service. Keep migration redirects for at least one year, preferably longer.

The 404 page is built separately by Hugo from `layouts/404.html`. Its presence
in the Pages deployment disables the default homepage fallback for missing
files. It must remain in subsequent deployments.

## Rollback

Remove this Worker's three route bindings to restore the previous hostname
behavior. This does not change the canonical site's Pages deployment. For a
Pages regression, roll back to the preceding production deployment in
Cloudflare Pages while investigating; keep the source changes synchronized
before the next Git-triggered deployment.

References:

- [Cloudflare domain redirects](https://developers.cloudflare.com/workers/examples/redirect/)
- [Cloudflare Pages 404 behavior](https://developers.cloudflare.com/pages/configuration/serving-pages/)
- [Google site-move guidance](https://developers.google.com/search/docs/crawling-indexing/site-move-with-url-changes)
