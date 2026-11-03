/* 截圖燈箱（手寫，不是產生的）：點 .pg-zoom／.pg-case-img／.pg-zoom-hint 在同頁放大。
   沒有 JS 時，這些連結照原本的行為另開大圖。用原生 <dialog>：Esc 關閉、背景不能操作、焦點留在燈箱裡。 */
(function () {
  if (!window.HTMLDialogElement) return;
  var links = Array.prototype.slice.call(document.querySelectorAll('a.pg-zoom, a.pg-case-img'));
  if (!links.length) return;

  // 同一張圖只算一次（首頁連結和「看大圖」按鈕指向同一張）
  var items = [], seen = {};
  links.forEach(function (a) {
    var href = a.getAttribute('href');
    if (seen[href] !== undefined) return;
    var img = a.querySelector('img');
    var fig = a.closest('figure');
    var cap = fig && fig.querySelector('figcaption');
    seen[href] = items.length;
    items.push({ src: href, alt: img ? img.alt : '', cap: cap ? cap.textContent : (img ? img.alt : '') });
  });

  var ARROW = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 5l-7 7 7 7"/></svg>';
  var dlg = document.createElement('dialog');
  dlg.className = 'pg-lb';
  dlg.setAttribute('aria-label', '放大的截圖');
  dlg.innerHTML =
    '<button type="button" class="pg-lb-btn pg-lb-close" aria-label="關閉"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg></button>' +
    '<figure class="pg-lb-fig"><img class="pg-lb-img" alt=""><figcaption class="pg-lb-cap"><span class="pg-lb-n"></span><span class="pg-lb-t"></span></figcaption></figure>' +
    (items.length > 1
      ? '<button type="button" class="pg-lb-btn pg-lb-prev" aria-label="上一張">' + ARROW + '</button>' +
        '<button type="button" class="pg-lb-btn pg-lb-next" aria-label="下一張">' + ARROW + '</button>'
      : '');
  document.body.appendChild(dlg);

  var img = dlg.querySelector('.pg-lb-img');
  var num = dlg.querySelector('.pg-lb-n');
  var txt = dlg.querySelector('.pg-lb-t');
  var cur = 0, opener = null;

  function show(i) {
    cur = (i + items.length) % items.length;
    var it = items[cur];
    img.src = it.src;
    img.alt = it.alt;
    num.textContent = items.length > 1 ? (cur + 1) + ' / ' + items.length : '';
    txt.textContent = it.cap;
  }
  function open(i, from) {
    opener = from;
    show(i);
    document.documentElement.classList.add('pg-lb-on');
    dlg.showModal();
    dlg.querySelector('.pg-lb-close').focus();
  }
  dlg.addEventListener('close', function () {
    document.documentElement.classList.remove('pg-lb-on');
    if (opener && opener.focus) opener.focus({ preventScroll: true });
  });

  document.addEventListener('click', function (ev) {
    if (ev.button !== 0 || ev.metaKey || ev.ctrlKey || ev.shiftKey || ev.altKey) return;  // 中鍵／Ctrl 照常另開
    var a = ev.target.closest && ev.target.closest('a.pg-zoom, a.pg-case-img, a.pg-zoom-hint');
    if (!a) return;
    var i = seen[a.getAttribute('href')];
    if (i === undefined) return;
    ev.preventDefault();
    // 「看大圖」按鈕不進 Tab 順序，關閉後把焦點還給同一張圖的連結
    open(i, a.classList.contains('pg-zoom-hint') ? links.filter(function (l) { return l.getAttribute('href') === a.getAttribute('href'); })[0] : a);
  });

  dlg.addEventListener('click', function (ev) {
    var b = ev.target.closest('button');
    if (b) {
      if (b.classList.contains('pg-lb-close')) dlg.close();
      else if (b.classList.contains('pg-lb-prev')) show(cur - 1);
      else if (b.classList.contains('pg-lb-next')) show(cur + 1);
      return;
    }
    if (!ev.target.closest('.pg-lb-img')) dlg.close();  // 點遮罩或圖說旁的空白處關閉
  });
  dlg.addEventListener('keydown', function (ev) {
    if (items.length < 2) return;
    if (ev.key === 'ArrowLeft') { ev.preventDefault(); show(cur - 1); }
    else if (ev.key === 'ArrowRight') { ev.preventDefault(); show(cur + 1); }
  });

  // 手機左右滑動切換
  var sx = null, sy = 0;
  dlg.addEventListener('touchstart', function (ev) {
    if (ev.touches.length !== 1) { sx = null; return; }
    sx = ev.touches[0].clientX; sy = ev.touches[0].clientY;
  }, { passive: true });
  dlg.addEventListener('touchend', function (ev) {
    if (sx === null || items.length < 2) return;
    var dx = ev.changedTouches[0].clientX - sx, dy = ev.changedTouches[0].clientY - sy;
    sx = null;
    if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy) * 1.5) {
      show(dx < 0 ? cur + 1 : cur - 1);
      dlg.dataset.swiped = '1';  // 讓接著觸發的 click 不要當成點遮罩
      setTimeout(function () { delete dlg.dataset.swiped; }, 400);
    }
  });
  dlg.addEventListener('click', function (ev) {
    if (dlg.dataset.swiped) { ev.stopImmediatePropagation(); }
  }, true);
})();
