/* Progressive reading aids. The complete report remains readable without JavaScript. */
(() => {
  'use strict';
  const main = document.querySelector('.main-content');
  main.querySelectorAll('.source-image img').forEach(img => {
    const unavailable = () => {
      img.hidden = true;
      img.closest('.source-image').querySelector('.image-fallback').hidden = false;
    };
    img.addEventListener('error', unavailable, { once: true });
    if (img.complete && !img.naturalWidth) unavailable();
  });
  const categories = ['AI 工具', 'AI 热门新闻', 'AI 变现', '黄金投资资讯', '国际政治', '财经新闻'];
  const ids = new Set([...document.querySelectorAll('[id]')].map(el => el.id));
  function ensureId(element, base) {
    if (element.id && document.getElementById(element.id) === element) return;
    let id = base, suffix = 2;
    while (ids.has(id)) id = `${base}-${suffix++}`;
    element.id = id; ids.add(id);
  }
  const groups = [...main.querySelectorAll(':scope > h2')].filter(h => categories.includes(h.textContent.trim()));
  if (!groups.length) return;
  const toc = document.createElement('details');
  toc.className = 'digest-toc';
  toc.open = !window.matchMedia('(max-width: 900px)').matches;
  const summary = document.createElement('summary');
  summary.textContent = '本期速览 · 栏目导航';
  toc.append(summary);
  const note = document.createElement('p');
  note.className = 'toc-note'; note.textContent = '按栏目浏览，点击标题直达正文'; toc.append(note);
  const nav = document.createElement('nav'); nav.setAttribute('aria-label', '本期栏目与新闻'); toc.append(nav);
  groups.forEach((heading, index) => {
    ensureId(heading, `category-${index + 1}`);
    const titles = [];
    let node = heading.nextElementSibling;
    while (node && node.tagName !== 'H2') {
      if (node.tagName === 'H3') titles.push(node);
      node = node.nextElementSibling;
    }
    const category = document.createElement('a');
    category.className = 'toc-group'; category.href = `#${heading.id}`;
    category.textContent = `${heading.textContent} · ${titles.length} 条`;
    const group = document.createElement('div'); group.className = 'toc-section';
    group.append(category); nav.append(group);
    const list = document.createElement('ol'); group.append(list);
    titles.forEach((title, n) => {
      ensureId(title, `news-${index + 1}-${n + 1}`);
      const li = document.createElement('li'); const link = document.createElement('a');
      link.href = `#${title.id}`; link.textContent = title.textContent.replace(/^\d+[.、]\s*/, '');
      li.append(link); list.append(li);
      const card = document.createElement('article'); card.className = 'news-item';
      card.setAttribute('aria-labelledby', title.id); title.before(card);
      let current = title;
      while (current && (current === title || !['H2', 'H3'].includes(current.tagName))) {
        const next = current.nextElementSibling; card.append(current); current = next;
      }
    });
  });
  main.querySelectorAll('p').forEach(p => {
    if (/^Codex 解读[：:]/.test(p.textContent.trim())) p.classList.add('analysis');
    else {
      const label = [...p.children].find(el => el.tagName === 'STRONG' && /Codex 解读[：:]$/.test(el.textContent.trim()));
      if (label) {
        const range = document.createRange();
        range.setStartBefore(label); range.setEnd(p, p.childNodes.length);
        const reading = document.createElement('span'); reading.className = 'codex-reading';
        reading.append(range.extractContents()); p.append(reading);
      }
    }
    if (/^(来源与时间|来源链接)[：:]/.test(p.textContent.trim())) p.classList.add('source-line');
  });
  groups[0].before(toc);
})();
