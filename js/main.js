/* Zahnarztpraxis Dr. Schülein — interactions. No dependencies. */
(function () {
  'use strict';

  var root = document.documentElement;
  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- preloader: one full landing of the mark, then out on load ---------- */
  if (document.querySelector('.preloader')) {
    var MIN_MS = 1400;
    var lift = function () {
      setTimeout(function () { root.classList.add('is-loaded'); },
        Math.max(0, MIN_MS - performance.now()));
    };
    if (reduceMotion) root.classList.add('is-loaded');
    else if (document.readyState === 'complete') lift();
    else window.addEventListener('load', lift);
  }

  /* ---------- frozen viewport unit: refresh on width change only ---------- */
  var vhPx = window.__vhPx || window.innerHeight;
  var vw0 = window.innerWidth;
  window.addEventListener('resize', function () {
    if (window.innerWidth !== vw0) {
      vw0 = window.innerWidth;
      vhPx = window.innerHeight;
      root.style.setProperty('--vh', (vhPx * 0.01) + 'px');
    }
  });

  /* ---------- navigation strip (phone sheet) ---------- */
  var strip = document.querySelector('.strip');
  var toggle = document.querySelector('.strip__toggle');
  function setNav(open) {
    strip.setAttribute('data-open', open ? 'true' : 'false');
    toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    toggle.querySelector('.visually-hidden').textContent = open ? 'Menü schließen' : 'Menü öffnen';
    root.classList.toggle('nav-open', open);
  }
  if (strip && toggle) {
    toggle.addEventListener('click', function () { setNav(strip.getAttribute('data-open') !== 'true'); });
    strip.querySelector('.strip__menu').addEventListener('click', function (e) {
      if (e.target.closest('a')) setNav(false);
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && strip.getAttribute('data-open') === 'true') { setNav(false); toggle.focus(); }
    });
    window.matchMedia('(min-width: 62.0625rem)').addEventListener('change', function (m) {
      if (m.matches) setNav(false);
    });
  }

  /* ---------- reveal: whole groups, never per item ---------- */
  var reveals = document.querySelectorAll('.reveal');
  function finish(el) {
    el.classList.add('is-in');
    var done = function () { el.classList.add('is-done'); };
    el.addEventListener('transitionend', done, { once: true });
    setTimeout(done, 1000);
  }
  if (reduceMotion || !('IntersectionObserver' in window)) {
    reveals.forEach(function (el) { el.classList.add('is-in', 'is-done'); });
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) { finish(entry.target); io.unobserve(entry.target); }
      });
    }, { rootMargin: '0px 0px -10% 0px', threshold: 0.12 });
    reveals.forEach(function (el) { io.observe(el); });
    /* a jump (anchor, End key, restored scroll) can skip an element entirely */
    var sweeping = false;
    var sweep = function () {
      sweeping = false;
      reveals.forEach(function (el) {
        if (!el.classList.contains('is-in') && el.getBoundingClientRect().top < vhPx) { finish(el); io.unobserve(el); }
      });
    };
    window.addEventListener('scroll', function () {
      if (!sweeping) { sweeping = true; requestAnimationFrame(sweep); }
    }, { passive: true });
    window.addEventListener('load', sweep);
  }

  /* ---------- Leistungen index ----------
     Wide: exactly one entry is open, shown in the right-hand cell; hover or
     click picks it. Phones: each entry is a disclosure and may be closed. */
  var index = document.querySelector('[data-index]');
  if (index) {
    var entries = index.querySelectorAll('.entry');
    var narrow = window.matchMedia('(max-width: 48rem)');
    var hoverable = window.matchMedia('(hover: hover) and (pointer: fine)');
    var lastX = -1, lastY = -1;
    var activate = function (entry, open) {
      entries.forEach(function (e) {
        var on = e === entry && open;
        e.classList.toggle('is-active', on);
        e.querySelector('.entry__name').setAttribute('aria-expanded', on ? 'true' : 'false');
      });
    };
    entries.forEach(function (entry) {
      var btn = entry.querySelector('.entry__name');
      btn.addEventListener('click', function () {
        var isOpen = entry.classList.contains('is-active');
        activate(entry, narrow.matches ? !isOpen : true);
      });
      /* only real pointer motion switches: scrolling under a resting mouse
         fires enter/move events at unchanged coordinates — ignore those */
      btn.addEventListener('pointermove', function (e) {
        if (e.pointerType !== 'mouse' || !hoverable.matches || narrow.matches) return;
        if (e.clientX === lastX && e.clientY === lastY) return;
        lastX = e.clientX; lastY = e.clientY;
        if (!entry.classList.contains('is-active')) activate(entry, true);
      });
    });
    /* back to wide with nothing open: open the first again */
    narrow.addEventListener('change', function (m) {
      if (!m.matches && !index.querySelector('.entry.is-active')) activate(entries[0], true);
    });
  }

  /* ---------- FAQ accordion ---------- */
  document.querySelectorAll('.acc__btn').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var item = btn.closest('.acc');
      var open = !item.classList.contains('is-open');
      item.classList.toggle('is-open', open);
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  });

  /* ---------- office hours: live status in Berlin time ----------
     Computed in the browser, no request. Public holidays are not known here,
     so the plate says "laut Sprechzeiten". */
  var HOURS = { 1: [[8, 13], [14.5, 19]], 2: [[8, 12]], 3: [[8, 12], [13, 16]], 4: [[8, 12], [14.5, 19]], 5: [[8, 12]] };
  var DAYS = ['Sonntag', 'Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag'];
  var fmt = function (h) { var m = Math.round((h % 1) * 60); return Math.floor(h) + ':' + (m < 10 ? '0' : '') + m; };

  function berlinNow() {
    try {
      var parts = new Intl.DateTimeFormat('en-GB', {
        timeZone: 'Europe/Berlin', weekday: 'short', hour: 'numeric', minute: 'numeric', hour12: false
      }).formatToParts(new Date());
      var get = function (t) { return parts.filter(function (p) { return p.type === t; })[0].value; };
      var day = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].indexOf(get('weekday'));
      return { day: day, h: (parseInt(get('hour'), 10) % 24) + parseInt(get('minute'), 10) / 60 };
    } catch (e) {
      var d = new Date();
      return { day: d.getDay(), h: d.getHours() + d.getMinutes() / 60 };
    }
  }

  function statusText(now) {
    var today = HOURS[now.day] || [];
    for (var i = 0; i < today.length; i++) {
      if (now.h >= today[i][0] && now.h < today[i][1]) {
        return { open: true, text: 'Jetzt geöffnet · bis ' + fmt(today[i][1]) + ' Uhr' };
      }
    }
    for (var k = 0; k < 8; k++) {
      var d = (now.day + k) % 7, slots = HOURS[d] || [];
      for (var j = 0; j < slots.length; j++) {
        if (k > 0 || slots[j][0] > now.h) {
          var when = k === 0 ? 'heute' : k === 1 ? 'morgen' : DAYS[d];
          return { open: false, text: 'Geschlossen · wieder ' + when + ' ab ' + fmt(slots[j][0]) + ' Uhr' };
        }
      }
    }
    return { open: false, text: 'Geschlossen' };
  }

  function paintHours() {
    var now = berlinNow();
    var st = document.querySelector('[data-status]');
    if (st) {
      var s = statusText(now);
      st.classList.toggle('is-open', s.open);
      st.classList.toggle('is-closed', !s.open);
      st.querySelector('[data-status-text]').textContent = s.text;
    }
    document.querySelectorAll('[data-hours] [data-day], [data-week] [data-day]').forEach(function (el) {
      el.classList.toggle('is-today', +el.getAttribute('data-day') === now.day);
    });
    var week = document.querySelector('[data-week]');
    if (week) {
      var inDay = HOURS[now.day] && now.h >= 8 && now.h <= 19;
      week.classList.toggle('has-now', !!inDay);
      if (inDay) week.style.setProperty('--now', now.h.toFixed(3));
    }
  }
  paintHours();
  setInterval(paintHours, 60000);

  /* ---------- appointment form — validation; delivery still to be connected ---------- */
  var form = document.getElementById('contact-form');
  if (form) {
    var status = form.querySelector('.form__status');
    var messages = {
      'f-name': 'Bitte geben Sie Ihren Namen an.',
      'f-tel': 'Bitte geben Sie eine Telefonnummer an, damit wir Sie zurückrufen können.',
      'f-mail': 'Bitte prüfen Sie die E-Mail-Adresse.',
      'f-consent': 'Bitte bestätigen Sie die Datenschutzhinweise.'
    };
    var check = function (input) {
      var field = input.closest('.field');
      var err = document.getElementById(input.id + '-err');
      var ok = input.checkValidity();
      if (input.type === 'email' && ok && input.value) ok = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(input.value);
      if (input.type === 'tel' && ok && input.value) ok = input.value.replace(/\D/g, '').length >= 6;
      field.classList.toggle('is-invalid', !ok);
      input.setAttribute('aria-invalid', ok ? 'false' : 'true');
      if (err) {
        err.textContent = ok ? '' : messages[input.id];
        input.setAttribute('aria-describedby', err.id);
      }
      return ok;
    };
    var checked = form.querySelectorAll('[required], [type="email"]');
    checked.forEach(function (input) {
      input.addEventListener('blur', function () { if (input.value || input.type === 'checkbox') check(input); });
      input.addEventListener('input', function () { if (input.closest('.field').classList.contains('is-invalid')) check(input); });
    });
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var firstBad = null;
      checked.forEach(function (input) { if (!check(input) && !firstBad) firstBad = input; });
      if (firstBad) { firstBad.focus(); return; }
      /* TODO before launch: connect a DSGVO-compliant form service (e.g. Web3Forms, EU hosting). */
      status.textContent = 'Das Formular ist noch nicht freigeschaltet. Bitte rufen Sie uns an: 0395 544 29 61.';
    });
  }

  /* ---------- footer year ---------- */
  document.querySelectorAll('[data-year]').forEach(function (el) { el.textContent = new Date().getFullYear(); });
})();
