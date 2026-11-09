// This Worker is routed only to the blog's alternate hostnames.
const alternateHosts = new Set([
  "www.zhangshaodong.com",
  "shaodong.name",
  "www.shaodong.name",
]);

export default {
  fetch(request) {
    const destination = new URL(request.url);

    if (!alternateHosts.has(destination.hostname)) {
      return new Response("Not found", { status: 404 });
    }

    // Mutate the parsed URL so paths and query strings survive unchanged.
    destination.protocol = "https:";
    destination.hostname = "zhangshaodong.com";
    destination.port = "";

    return new Response(null, {
      status: 308,
      headers: {
        Location: destination.href,
        "Cache-Control": "public, max-age=3600",
      },
    });
  },
};
