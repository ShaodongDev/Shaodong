(() => {
  const filters = document.querySelector('[data-post-filters]');
  const list = document.querySelector('[data-post-list]');
  if (!filters || !list) return;

  const links = [...filters.querySelectorAll('a[data-tag]')];
  const entries = [...list.querySelectorAll('[data-post-tags]')].map(element => ({
    element,
    tags: JSON.parse(element.dataset.postTags),
  }));
  const empty = document.querySelector('[data-filter-empty]');
  const knownTags = new Set(links.map(link => link.dataset.tag));

  function render() {
    // URLSearchParams has already decoded the query parameter.
    let selected = (new URL(location.href).searchParams.get('tag') || 'all').toLowerCase();
    // Older article links encoded Chinese tag names twice. Keep those bookmarks working.
    if (!knownTags.has(selected) && /%[0-9a-f]{2}/i.test(selected)) {
      try {
        const decoded = decodeURIComponent(selected);
        if (knownTags.has(decoded)) selected = decoded;
      } catch { /* A malformed query should produce the normal empty state. */ }
    }
    let visible = 0;
    for (const { element, tags } of entries) {
      element.hidden = selected !== 'all' && !tags.includes(selected);
      if (!element.hidden) visible++;
    }
    for (const section of list.querySelectorAll('[data-post-year]')) {
      section.hidden = ![...section.querySelectorAll('[data-post-tags]')].some(element => !element.hidden);
    }
    for (const link of links) {
      const active = link.dataset.tag === selected;
      link.classList.toggle('highlight', active);
      if (active) link.setAttribute('aria-current', 'true');
      else link.removeAttribute('aria-current');
    }
    if (empty) empty.hidden = visible !== 0;
  }

  filters.addEventListener('click', event => {
    const link = event.target.closest('a[data-tag]');
    if (!link || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    const url = new URL(location.href);
    if (link.dataset.tag === 'all') url.searchParams.delete('tag');
    else url.searchParams.set('tag', link.dataset.tag);
    if (url.href !== location.href) history.pushState(null, '', url);
    render();
  });

  addEventListener('popstate', render);
  render();
})();
