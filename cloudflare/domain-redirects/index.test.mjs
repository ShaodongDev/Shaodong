import assert from "node:assert/strict";
import test from "node:test";
import redirects from "./index.mjs";

test("legacy and www URLs permanently redirect without losing their paths or queries", () => {
  for (const host of ["www.zhangshaodong.com", "shaodong.name", "www.shaodong.name"]) {
    for (const protocol of ["http:", "https:"]) {
      for (const path of [
        "/",
        "/2024/04/25/ir-in-social-science/",
        "/post/?tag=%E7%A7%91%E5%AD%A6&utm_source=old&tag=second",
        "/tags/%E4%B8%AD%E6%96%87/",
        "/feed.xml",
        "/2023/11/29/sharing_session/Sharing.pdf",
      ]) {
        for (const method of ["GET", "HEAD", "POST"]) {
          const response = redirects.fetch(new Request(`${protocol}//${host}${path}`, { method }));
          assert.equal(response.status, 308);
          assert.equal(response.headers.get("Location"), `https://zhangshaodong.com${path}`);
        }
      }
    }
  }
});

test("canonical and unrelated hosts cannot produce redirect loops or open redirects", () => {
  for (const host of ["zhangshaodong.com", "example.com", "zhangshaodong.com.example.com"]) {
    const response = redirects.fetch(new Request(`https://${host}/`));
    assert.equal(response.status, 404);
    assert.equal(response.headers.get("Location"), null);
  }
});

test("destination-looking query parameters cannot change the redirect's hostname", () => {
  const path = "/post/?next=https%3A%2F%2Fexample.com%2F&tag=python";
  const response = redirects.fetch(new Request(`https://www.zhangshaodong.com${path}`));
  assert.equal(response.headers.get("Location"), `https://zhangshaodong.com${path}`);
});
