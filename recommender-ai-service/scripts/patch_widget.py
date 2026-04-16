"""Patch home.html AI widget JS with improved version."""
import sys
from pathlib import Path

HOME = Path(__file__).parent.parent.parent / "api_gateway/templates/home.html"

NEW_WIDGET = r"""// ═══ AI RECOMMENDATION WIDGET ═══
const AI_BASE = 'http://localhost:8011';

function renderAIBook(book) {
  const price  = Number(book.price || 0).toLocaleString('vi-VN');
  const bid    = book.product_id || book.id;
  const cat    = (book.category || '').toUpperCase().slice(0, 12);
  const reason = book.reason
    ? '<div style="font-size:.68rem;color:var(--p);margin-top:.25rem;line-height:1.3">💡 ' + book.reason + '</div>'
    : '';
  const stars  = book.avg_rating >= 4
    ? '<span style="color:#F59E0B;font-size:.72rem">★' + Number(book.avg_rating).toFixed(1) + '</span>'
    : '';
  const coverHtml = book.cover_image
    ? '<img src="' + book.cover_image + '" alt="' + (book.title||'') + '" style="width:100%;height:100%;object-fit:cover" loading="lazy" onerror="this.style.display=\'none\';this.nextElementSibling.style.display=\'flex\'">'
    : '';
  const fallbackStyle = book.cover_image ? 'display:none' : '';
  return '<div class="book-card" onclick="openDetail(' + bid + ')" style="cursor:pointer" title="' + (book.title||'') + '">'
    + '<div class="book-cover">'
    + coverHtml
    + '<div class="book-cover-fallback" style="' + fallbackStyle + '">📚</div>'
    + (cat ? '<div class="cover-cat">' + cat + '</div>' : '')
    + '</div>'
    + '<div class="book-body">'
    + '<div class="book-title">' + (book.title||'') + '</div>'
    + '<div class="book-author">' + (book.author||'') + '</div>'
    + stars + reason
    + '<div class="book-footer">'
    + '<span class="book-price">' + price + '₫</span>'
    + '<button class="btn-cart" onclick="event.stopPropagation();addToCart(' + bid + ')" title="Thêm vào giỏ">🛒</button>'
    + '</div></div></div>';
}

function enrichWithCovers(items) {
  if (!window._allBooksCache) return items;
  const bmap = {};
  (window._allBooksCache || []).forEach(function(b) { bmap[b.id] = b; });
  return items.map(function(item) {
    const bid = item.product_id || item.id;
    const cached = bmap[bid];
    if (cached && cached.cover_image && !item.cover_image) {
      return Object.assign({}, item, {cover_image: cached.cover_image});
    }
    return item;
  });
}

async function loadAIRecommendations() {
  const cid      = window._customerId || null;
  const suggestEl = document.getElementById('ai-suggest-you');
  const titleEl   = document.getElementById('ai-widget-title');
  const collabSec = document.getElementById('ai-collab-section');
  const collabEl  = document.getElementById('ai-similar-users');

  if (suggestEl) suggestEl.innerHTML = '<div class="loading"><div class="spin"></div></div>';

  try {
    const endpoint = cid
      ? AI_BASE + '/api/v1/recommend/' + cid + '?limit=8'
      : AI_BASE + '/api/v1/recommend/popular?limit=8';

    const res = await Promise.race([
      fetch(endpoint),
      new Promise(function(_, rej) { setTimeout(function() { rej('timeout'); }, 4000); })
    ]);

    if (!res.ok) throw new Error('api_error');
    const data  = await res.json();
    let items   = data.recommendations || data.items || [];
    items = enrichWithCovers(items);

    if (titleEl) {
      titleEl.textContent = cid
        ? (items.length ? '💡 Gợi ý cho bạn — dựa trên hành vi của bạn' : '🔥 Sách phổ biến')
        : '🔥 Sách phổ biến';
    }
    if (suggestEl) {
      suggestEl.innerHTML = items.length
        ? items.slice(0, 8).map(renderAIBook).join('')
        : '<div class="empty-state"><div class="empty-icon">📚</div>Chưa có gợi ý — hãy xem thêm sách!</div>';
    }

    if (cid && collabSec && collabEl) {
      try {
        const cr = await Promise.race([
          fetch(AI_BASE + '/api/v1/recommend/collaborative/' + cid + '?limit=6'),
          new Promise(function(_, rej) { setTimeout(function() { rej('timeout'); }, 3000); })
        ]);
        if (cr.ok) {
          const cd = await cr.json();
          const citems = enrichWithCovers(cd.items || []);
          if (citems.length) {
            collabSec.style.display = '';
            collabEl.innerHTML = citems.slice(0, 6).map(renderAIBook).join('');
          }
        }
      } catch (_) {}
    }
  } catch (_) {
    const fallback = (window._allBooksCache || []).slice(0, 8).map(function(b) {
      return {product_id: b.id, title: b.title, author: b.author,
              category: b.category, price: b.price,
              cover_image: b.cover_image || b.cover || '',
              reason: 'phổ biến trong cộng đồng', avg_rating: 0};
    });
    if (titleEl) titleEl.textContent = '🔥 Sách phổ biến';
    if (suggestEl) {
      suggestEl.innerHTML = fallback.length
        ? fallback.map(renderAIBook).join('')
        : '<div class="empty-state"><div class="empty-icon">📚</div>Không thể tải gợi ý</div>';
    }
  }
}

async function trackAndRefresh(customerId, bookId, interactionType) {
  if (!customerId || !bookId) return;
  try {
    await fetch(AI_BASE + '/api/v1/track', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({customer_id: customerId, product_id: bookId, interaction_type: interactionType}),
    });
    loadAIRecommendations();
  } catch (_) {}
}

document.addEventListener('DOMContentLoaded', function() {
  const stored = localStorage.getItem('mb_customer');
  if (stored) { try { window._customerId = JSON.parse(stored).id; } catch (_) {} }
  const waitForBooks = setInterval(function() {
    if (window._allBooksCache && window._allBooksCache.length > 0) {
      clearInterval(waitForBooks);
      loadAIRecommendations();
    }
  }, 300);
  setTimeout(function() { clearInterval(waitForBooks); loadAIRecommendations(); }, 2000);
});
"""

with open(HOME, encoding='utf-8') as f:
    content = f.read()

start_marker = '// ═══ AI RECOMMENDATION WIDGET ═══'
end_marker = 'loadAIRecommendations();\n});\n'

start = content.find(start_marker)
end = content.find(end_marker, start) + len(end_marker)

if start == -1:
    print("ERROR: marker not found")
    sys.exit(1)

new_content = content[:start] + NEW_WIDGET + content[end:]
with open(HOME, 'w', encoding='utf-8') as f:
    f.write(new_content)
print(f"Patched home.html: replaced {end-start} chars with {len(NEW_WIDGET)} chars")
