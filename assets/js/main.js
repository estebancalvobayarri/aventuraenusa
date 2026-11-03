/* Aventura en USA — interacciones de la web */
(function () {
  'use strict';
  var body = document.body;
  var BASE = body.getAttribute('data-base') || '';

  /* ---------- Cabecera que se encoge al hacer scroll + botón "volver arriba" ---------- */
  var toTop = document.querySelector('.to-top');
  function onScroll() {
    var y = window.scrollY || window.pageYOffset;
    body.classList.toggle('is-scrolled', y > 40);
    if (toTop) toTop.classList.toggle('show', y > 400);
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* ---------- Animación de entrada al hacer scroll ---------- */
  var revealEls = document.querySelectorAll('.icon-circles, .timeline .tl-item');
  if (revealEls.length && 'IntersectionObserver' in window) {
    document.documentElement.classList.add('js-reveal');
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add('in-view'); io.unobserve(en.target); }
      });
    }, { threshold: 0.35, rootMargin: '0px 0px -8% 0px' });
    revealEls.forEach(function (el) { io.observe(el); });
  }

  /* ---------- Menú móvil ---------- */
  var nav = document.querySelector('.main-nav');
  var toggle = document.querySelector('.menu-toggle');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  /* ---------- Sliders (testimonios y galerías) ---------- */
  document.querySelectorAll('[data-slider]').forEach(function (slider) {
    var slides = slider.querySelectorAll('.slide');
    // Las fotos ocultas del carrusel se descargan ya, para que no aparezca un hueco al pasar de foto
    slider.querySelectorAll('img[loading="lazy"]').forEach(function (img) { img.loading = 'eager'; });
    if (slides.length < 2) { if (slides[0]) slides[0].classList.add('active'); return; }
    var dotsWrap = slider.querySelector('.dots');
    var current = 0, timer = null;
    var delay = parseInt(slider.getAttribute('data-autoplay') || '0', 10);
    var dots = [];
    if (dotsWrap) {
      slides.forEach(function (_, i) {
        var b = document.createElement('button');
        b.type = 'button';
        b.setAttribute('aria-label', 'Ir a la diapositiva ' + (i + 1));
        b.addEventListener('click', function () { go(i); restart(); });
        dotsWrap.appendChild(b);
        dots.push(b);
      });
    }
    function go(i) {
      slides[current].classList.remove('active');
      if (dots[current]) dots[current].classList.remove('active');
      current = (i + slides.length) % slides.length;
      slides[current].classList.add('active');
      if (dots[current]) dots[current].classList.add('active');
    }
    function restart() {
      if (!delay) return;
      clearInterval(timer);
      timer = setInterval(function () { go(current + 1); }, delay);
    }
    var prev = slider.querySelector('.prev'), next = slider.querySelector('.next');
    if (prev) prev.addEventListener('click', function () { go(current - 1); restart(); });
    if (next) next.addEventListener('click', function () { go(current + 1); restart(); });
    slider.addEventListener('mouseenter', function () { clearInterval(timer); });
    slider.addEventListener('mouseleave', restart);
    go(0);
    restart();
  });

  /* ---------- Cookies: solo técnicas por defecto; mapas tras aceptar ---------- */
  var KEY = 'aeu_cookie_consent';
  function getConsent() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }
  function setConsent(v) { try { localStorage.setItem(KEY, v); } catch (e) {} }
  var bar = document.querySelector('.cookie-bar');

  function loadMaps() {
    document.querySelectorAll('[data-map-src]').forEach(function (box) {
      var f = document.createElement('iframe');
      f.src = box.getAttribute('data-map-src');
      f.className = 'map-frame';
      f.style.height = box.offsetHeight ? box.offsetHeight + 'px' : '150px';
      f.loading = 'lazy';
      f.title = 'Mapa de Valencia';
      f.referrerPolicy = 'no-referrer-when-downgrade';
      box.replaceWith(f);
    });
  }
  function applyConsent() {
    if (getConsent() === 'all') loadMaps();
  }
  if (bar) {
    if (!getConsent()) bar.classList.add('show');
    bar.querySelector('.cb-accept').addEventListener('click', function () { setConsent('all'); bar.classList.remove('show'); applyConsent(); });
    bar.querySelector('.cb-reject').addEventListener('click', function () { setConsent('essential'); bar.classList.remove('show'); });
  }
  document.querySelectorAll('.cookie-lock').forEach(function (b) {
    b.addEventListener('click', function () { if (bar) bar.classList.add('show'); });
  });
  document.querySelectorAll('[data-accept-cookies]').forEach(function (b) {
    b.addEventListener('click', function () { setConsent('all'); if (bar) bar.classList.remove('show'); applyConsent(); });
  });
  applyConsent();

  /* ---------- Buscador ---------- */
  var overlay = document.querySelector('.search-overlay');
  var index = null;
  function norm(s) { return (s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, ''); }
  function openSearch() {
    if (!overlay) return;
    overlay.classList.add('show');
    var input = overlay.querySelector('input');
    input.focus();
    if (!index) {
      fetch(BASE + '/search-index.json').then(function (r) { return r.json(); }).then(function (d) { index = d; runSearch(); }).catch(function () { index = []; });
    }
  }
  function runSearch() {
    var input = overlay.querySelector('input');
    var list = overlay.querySelector('.search-results');
    var q = norm(input.value.trim());
    list.innerHTML = '';
    if (!q || !index) return;
    var words = q.split(/\s+/);
    var hits = index.filter(function (p) {
      var hay = norm(p.title + ' ' + p.description + ' ' + p.text);
      return words.every(function (w) { return hay.indexOf(w) !== -1; });
    });
    if (!hits.length) { list.innerHTML = '<li><p>No se han encontrado resultados.</p></li>'; return; }
    hits.forEach(function (p) {
      var li = document.createElement('li');
      var a = document.createElement('a'); a.href = BASE + p.url; a.textContent = p.title;
      var d = document.createElement('p'); d.textContent = p.description;
      li.appendChild(a); li.appendChild(d); list.appendChild(li);
    });
  }
  document.querySelectorAll('.search-btn').forEach(function (b) { b.addEventListener('click', function (e) { e.preventDefault(); openSearch(); }); });
  if (overlay) {
    overlay.querySelector('.so-close').addEventListener('click', function () { overlay.classList.remove('show'); });
    overlay.querySelector('input').addEventListener('input', runSearch);
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') overlay.classList.remove('show'); });
    var params = new URLSearchParams(location.search);
    if (params.get('s')) { overlay.querySelector('input').value = params.get('s'); openSearch(); }
  }

  /* ---------- Formulario de contacto ---------- */
  var form = document.querySelector('#contact-form');
  if (form) {
    var msg = form.querySelector('.form-msg');
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      msg.className = 'form-msg';
      var answer = form.elements['verificacion'].value.trim();
      if (answer !== '5') {
        msg.textContent = 'La respuesta a la pregunta de seguridad no es correcta.';
        msg.classList.add('err');
        return;
      }
      if (!form.checkValidity()) { form.reportValidity(); return; }
      var btn = document.querySelector('[type="submit"][form="contact-form"]') || form.querySelector('[type="submit"]');
      btn.disabled = true; btn.textContent = 'Enviando…';
      var data = new FormData(form);
      data.delete('verificacion');
      fetch(form.getAttribute('data-endpoint'), { method: 'POST', body: data, headers: { 'Accept': 'application/json' } })
        .then(function (r) { if (!r.ok) throw new Error(); return r.json(); })
        .then(function () {
          form.reset();
          msg.textContent = 'Gracias, hemos recibido tu mensaje. Te responderemos lo antes posible.';
          msg.classList.add('ok');
        })
        .catch(function () {
          msg.innerHTML = 'No se ha podido enviar el mensaje. Escríbenos a <a href="mailto:info@aventuraenusa.es">info@aventuraenusa.es</a> o por WhatsApp al (+34) 672 852 975.';
          msg.classList.add('err');
        })
        .finally(function () { btn.disabled = false; btn.textContent = 'Enviar'; });
    });
  }
})();
