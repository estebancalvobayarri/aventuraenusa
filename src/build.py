#!/usr/bin/env python3
"""
Generador de la web estática de Aventura en USA.

Uso:  python3 src/build.py

Lee cada página de src/pages/*.html (contenido + metadatos SEO en la cabecera)
y genera el HTML final en la raíz del repositorio con la MISMA estructura de
URLs que aventuraenusa.es (p. ej. /monitor-de-campamento/actividades/).

Imágenes: se referencian con su ruta original de WordPress
(/wp-content/uploads/AAAA/MM/archivo.ext). Si el archivo todavía no existe en
el repositorio se muestra un hueco señalizado con el nombre de la foto; en
cuanto se copia la imagen a esa ruta y se vuelve a ejecutar este script, el
hueco se sustituye por la foto real (manteniendo la misma URL que tenía en la
web antigua, así no se pierde el posicionamiento en Google Imágenes).
"""
import datetime
import html
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
PAGES = SRC / "pages"
SITE = "https://aventuraenusa.es"
import hashlib
# Versión de CSS/JS = huella de su contenido: cambia en cuanto se modifican,
# así los navegadores no se quedan con una copia antigua.
BUILD_VERSION = hashlib.md5(b"".join((Path(__file__).resolve().parent.parent / f).read_bytes()
                                     for f in ("assets/css/style.css", "assets/js/main.js"))).hexdigest()[:10]
# Prefijo de ruta. Vacío cuando la web se sirve en la raíz del dominio
# (aventuraenusa.es). Para la vista previa en
# https://<usuario>.github.io/aventuraenusa/ se usa BASE_PATH=/aventuraenusa
BASE = os.environ.get("BASE_PATH", "").rstrip("/")
ROOT_LINK_RE = re.compile(r'((?:href|src|action|data-src|data-map-src|data-bg-pending)=")/(?!/)')


def with_base(doc):
    """Antepone BASE a los enlaces internos que empiezan por "/"."""
    if not BASE:
        return doc
    doc = ROOT_LINK_RE.sub(lambda m: m.group(1) + BASE + "/", doc)
    doc = doc.replace("url('/", "url('" + BASE + "/")
    doc = doc.replace('content="0; url=/', 'content="0; url=' + BASE + "/")
    doc = doc.replace('location.replace("/', 'location.replace("' + BASE + "/")
    return doc

# ---------------------------------------------------------------------------
# Datos generales
# ---------------------------------------------------------------------------
BUSINESS = {
    "name": "Aventura en USA",
    "legal": "Move Abroad Experience S.L.",
    "phone_display": "(+34) 672 852 975",
    "phone": "+34672852975",
    "whatsapp": "https://api.whatsapp.com/send?phone=34672852975",
    "email": "info@aventuraenusa.es",
    "address": "Valencia, Comunidad Valenciana, España",
    "hours": "L-V: 8:00-18:00",
    "lat": "39.476587",
    "lng": "-0.351675",
}
LOGO = "/wp-content/uploads/2024/07/blanco.png"
FAVICON = "/wp-content/uploads/2020/05/favicon-top.png"
MAP_SRC = "https://maps.google.com/maps?q=Valencia%2C%20Espa%C3%B1a&t=&z=10&ie=UTF8&iwloc=&output=embed"
GOOGLE_VERIFICATION = "rTl-2J5RTp2SfOaf6XRH5ECmC2Bk3Gg9_0Ac0wV3j1U"

MENU = [
    ("inicio", "Inicio", "/", []),
    ("monitor", "Monitor de campamento", "/monitor-de-campamento/", [
        ("vive", "Vive la experiencia", "/monitor-de-campamento/"),
        ("actividades", "Actividades", "/monitor-de-campamento/actividades/"),
        ("dia", "El día a día", "/monitor-de-campamento/el-dia-a-dia/"),
        ("programa", "El programa", "/monitor-de-campamento/el-programa/"),
        ("costes", "Costes y Salario", "/monitor-de-campamento/costes-y-salarios/"),
        ("inscripcion", "Inscripción", "/monitor-de-campamento/inscripcion/"),
        ("importante", "Importante", "/monitor-de-campamento/importante/"),
    ]),
    ("reuniones", "Reuniones Explicativas", "/reuniones-explicativas/", []),
    ("historias", "Historias", "/historias-de-aventuras-en-usa/", []),
    ("contacto", "Contacto", "/contacto/", []),
]

FOOTER_PAGES = [
    ("Inicio", "/"),
    ("Monitor de campamento", "/monitor-de-campamento/"),
    ("Actividades", "/monitor-de-campamento/actividades/"),
    ("El día a día", "/monitor-de-campamento/el-dia-a-dia/"),
    ("El programa", "/monitor-de-campamento/el-programa/"),
    ("Costes y Salario", "/monitor-de-campamento/costes-y-salarios/"),
    ("Inscripción", "/monitor-de-campamento/inscripcion/"),
    ("Importante", "/monitor-de-campamento/importante/"),
    ("Reuniones Explicativas", "/reuniones-explicativas/"),
    ("Historias de Aventuras en USA", "/historias-de-aventuras-en-usa/"),
    ("Contacto", "/contacto/"),
    ("Aviso legal", "/aviso-legal/"),
    ("Política de privacidad", "/politica-de-privacidad/"),
    ("Protección de datos", "/proteccion-de-datos/"),
    ("Uso de cookies", "/uso-de-cookies/"),
    ("Accesibilidad", "/accesibilidad/"),
]

# URLs antiguas de WordPress que conviene redirigir (GitHub Pages no admite
# redirecciones 301; se usa canonical + meta refresh, que Google trata como
# redirección permanente).
REDIRECTS = {
    "/inicio/": "/",
    "/entrada-1/": "/",
    "/entrada-2/": "/",
    "/entrada-3/": "/",
    "/category/sin-categoria/": "/",
}

# ---------------------------------------------------------------------------
# Iconos SVG
# ---------------------------------------------------------------------------
ICONS = {
    "check": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 16.2 4.8 12l-1.4 1.4L9 19 21 7l-1.4-1.4z"/></svg>',
    "check-bold": '<svg viewBox="0 0 512 512" aria-hidden="true"><path d="M173.9 439.4 7.5 273c-10-10-10-26.2 0-36.2l36.2-36.2c10-10 26.2-10 36.2 0L192 312.7 432.1 72.6c10-10 26.2-10 36.2 0l36.2 36.2c10 10 10 26.2 0 36.2L210.1 439.4c-10 10-26.2 10-36.2 0z"/></svg>',
    "thumbs": '<svg viewBox="0 0 512 512" aria-hidden="true"><path d="M104 224H24c-13.3 0-24 10.7-24 24v240c0 13.3 10.7 24 24 24h80c13.3 0 24-10.7 24-24V248c0-13.3-10.7-24-24-24zM512 254.6c0-35.3-29.1-64-64.6-64H321c18.8-27.1 33-59.6 33-96.8C354 33 312.2 0 284.6 0c-29 0-22.1 52.2-48.6 78.6-44.2 44.1-92.8 115-124 138.4v257.3c24.3 0 66.7 26.2 129.6 37.7 4.4.8 72 0 98.6 0 29.8 0 54-20.3 54-50.2 0-5.1-.6-10-1.7-14.6 18.5-6.6 32.2-23.3 32.2-44.2 0-7.6-1.9-14.7-5-21 13-6.7 22.4-19.8 22.4-35.1 0-10.6-3.9-20.4-10.4-28 21.3-5.4 40.4-26.5 40.4-50.4z"/></svg>',
    "phone": '<svg viewBox="0 0 512 512" aria-hidden="true"><path d="M497.4 361.8 385.4 313.8a24 24 0 0 0-28 6.9l-49.6 60.6A370.7 370.7 0 0 1 130.6 204.1l60.6-49.6a23.9 23.9 0 0 0 6.9-28l-48-112A24.2 24.2 0 0 0 122.6.6l-104 24A24 24 0 0 0 0 48c0 256.5 207.9 464 464 464a24 24 0 0 0 23.4-18.6l24-104a24.3 24.3 0 0 0-14-27.6z"/></svg>',
    "star": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2.5l2.9 6.3 6.9.7-5.2 4.6 1.5 6.8L12 17.4 5.9 20.9l1.5-6.8L2.2 9.5l6.9-.7z"/></svg>',
    "doc": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 2h12a2 2 0 0 1 2 2v16a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2zm1 3v4h10V5zm0 6v2h10v-2zm0 4v2h7v-2z"/></svg>',
    "users": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8zm7.5 0a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7zM9 13c-3.3 0-7 1.7-7 4v3h14v-3c0-2.3-3.7-4-7-4zm7.5 0c-.6 0-1.3.1-1.9.2 1.4 1 2.4 2.3 2.4 3.8v3h5v-3c0-2.2-3.1-4-5.5-4z"/></svg>',
    "whatsapp": '<svg viewBox="0 0 448 512" aria-hidden="true"><path d="M380.9 97.1A223.9 223.9 0 0 0 224.1 32c-123.5 0-224 100.5-224 224 0 39.5 10.3 78 29.9 112L0 480l117.7-30.9a223.2 223.2 0 0 0 106.3 27c123.4 0 226-100.5 226-224 0-59.8-25.4-116-69.1-155zM224.1 438.7a185.9 185.9 0 0 1-94.8-25.9l-6.8-4.1-69.8 18.3 18.6-68.1-4.4-7a184.5 184.5 0 0 1-28.3-98.5c0-102.6 83.5-186.1 186.2-186.1a184.4 184.4 0 0 1 131.6 54.5 185.3 185.3 0 0 1 56.5 131.7c0 102.7-85.7 186.2-188.8 186.2zm101.6-139.4c-5.5-2.8-32.8-16.2-37.9-18-5.1-1.9-8.8-2.8-12.5 2.8s-14.3 18-17.6 21.8c-3.2 3.7-6.5 4.2-12 1.4-32.6-16.3-54-29.1-75.5-66-5.7-9.8 5.7-9.1 16.3-30.3 1.8-3.7.9-6.9-.5-9.7s-12.5-30.1-17.1-41.2c-4.5-10.8-9.1-9.3-12.5-9.5-3.2-.2-6.9-.2-10.6-.2s-9.7 1.4-14.8 6.9c-5.1 5.6-19.4 19-19.4 46.3s19.9 53.7 22.6 57.4c2.8 3.7 39.1 59.7 94.8 83.8 35.2 15.2 49 16.5 66.6 13.9 10.7-1.6 32.8-13.4 37.4-26.4s4.6-24.1 3.2-26.4c-1.3-2.5-5-3.9-10.5-6.6z"/></svg>',
    "search": '<svg viewBox="0 0 24 24" aria-hidden="true" fill="currentColor"><path d="M10 2a8 8 0 0 1 6.3 12.9l5.4 5.4-1.4 1.4-5.4-5.4A8 8 0 1 1 10 2zm0 2a6 6 0 1 0 0 12 6 6 0 0 0 0-12z"/></svg>',
    "menu": '<svg viewBox="0 0 24 24" aria-hidden="true" fill="currentColor"><path d="M3 6h18v2H3zm0 5h18v2H3zm0 5h18v2H3z"/></svg>',
    "up": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 7l-7 7 1.4 1.4L12 9.8l5.6 5.6L19 14z"/></svg>',
    "left": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15.4 5.4 14 4l-8 8 8 8 1.4-1.4L8.8 12z"/></svg>',
    "right": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8.6 18.6 10 20l8-8-8-8-1.4 1.4 6.6 6.6z"/></svg>',
    "lock": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M17 9h-1V7a4 4 0 0 0-8 0v2H7a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-9a2 2 0 0 0-2-2zm-7-2a2 2 0 0 1 4 0v2h-4z"/></svg>',
}


def icon(name):
    return ICONS[name]


# ---------------------------------------------------------------------------
# Imágenes: hueco o foto real
# ---------------------------------------------------------------------------
IMG_RE = re.compile(r"<img\b([^>]*?)\s*/?>", re.S)
ATTR_RE = re.compile(r'([\w:-]+)="([^"]*)"')
BG_RE = re.compile(r'data-bg="([^"]+)"')
missing_images = set()
present_images = set()


def img_exists(src):
    return src.startswith("/") and (ROOT / src.lstrip("/")).is_file()


def real_size(src):
    """Dimensiones reales de la foto (si Pillow está instalado)."""
    try:
        from PIL import Image
        with Image.open(ROOT / src.lstrip("/")) as im:
            return im.size
    except Exception:
        return None


def replace_img(m):
    attrs = dict(ATTR_RE.findall(m.group(1)))
    src = attrs.get("src", "")
    if not src.startswith("/wp-content/") or img_exists(src):
        tag = m.group(0)
        if src.startswith("/wp-content/"):
            present_images.add(src)
            dims = real_size(src)
            if dims:
                tag = re.sub(r'width="\d+"', f'width="{dims[0]}"', tag)
                tag = re.sub(r'height="\d+"', f'height="{dims[1]}"', tag)
        if "loading=" not in tag and "data-eager" not in tag:
            tag = tag.replace("<img", '<img loading="lazy" decoding="async"', 1)
        return tag.replace(" data-eager", "")
    missing_images.add(src)
    w, h = attrs.get("width"), attrs.get("height")
    style = f' style="aspect-ratio:{w}/{h}"' if w and h else ""
    cls = ("img-ph " + attrs.get("class", "")).strip()
    alt = attrs.get("alt", "")
    label = html.escape(src.rsplit("/", 1)[-1])
    aria = f' role="img" aria-label="{html.escape(alt)}"' if alt else ' aria-hidden="true"'
    return f'<div class="{cls}"{style}{aria} data-src="{html.escape(src)}"><span>Imagen pendiente:<br>{label}</span></div>'


def replace_bg(match_html):
    """Convierte data-bg="..." en background-image o en un fondo provisional."""

    def repl(m):
        src = m.group(1)
        if img_exists(src):
            present_images.add(src)
            return f'style="background-image:url(\'{src}\')"'
        missing_images.add(src)
        return f'data-bg-missing="{src}"'

    out = BG_RE.sub(repl, match_html)

    # añade clase y etiqueta a los contenedores sin fondo
    def tag_repl(m):
        tag = m.group(0)
        src = re.search(r'data-bg-missing="([^"]+)"', tag).group(1)
        light = "intro" in tag
        cls = "bg-ph-light" if light else "bg-ph"
        tag = re.sub(r'class="', f'class="{cls} ', tag, count=1)
        tag = tag.replace(f' data-bg-missing="{src}"', f' data-bg-pending="{src}"')
        return tag + f'<span class="bg-label">Fondo pendiente: {html.escape(src.rsplit("/", 1)[-1])}</span>'

    return re.sub(r'<(section|div)\b[^>]*data-bg-missing="[^"]+"[^>]*>', tag_repl, out)


# ---------------------------------------------------------------------------
# Plantilla
# ---------------------------------------------------------------------------
def nav_html(active):
    items = []
    for key, label, url, subs in MENU:
        cur = key == active or any(s[0] == active for s in subs)
        cls = []
        if cur:
            cls.append("current")
        if subs:
            cls.append("has-sub")
        c = f' class="{" ".join(cls)}"' if cls else ""
        aria = ' aria-current="page"' if key == active else ""
        sub = ""
        if subs:
            lis = "".join(
                f'<li{" class=\"current\"" if s[0] == active else ""}><a href="{s[2]}">{s[1]}</a></li>' for s in subs
            )
            sub = f'<ul class="sub-menu">{lis}</ul>'
        items.append(f'<li{c}><a href="{url}"{aria}>{label}</a>{sub}</li>')
    items.append('<li class="nav-cta"><a href="/monitor-de-campamento/inscripcion/">Inscríbete</a></li>')
    items.append(
        f'<li><a class="search-btn" href="/?s=" aria-label="Buscar en la web">{icon("search")}</a></li>'
    )
    return "".join(items)


def header_html(active):
    logo = f'<img src="{LOGO}" alt="Aventura en USA" width="480" height="480" data-eager fetchpriority="high">'
    return f"""<a class="skip-link" href="#main">Saltar al contenido</a>
<header class="site-header">
  <div class="topbar"><div class="container"><span>Powered by Move Abroad Experience S.L.</span></div></div>
  <div class="header-main">
    <div class="container">
      <a class="logo" href="/" aria-label="Aventura en USA - Inicio">{logo}</a>
      <nav class="main-nav" aria-label="Menú principal">
        <button class="menu-toggle" type="button" aria-label="Menú" aria-expanded="false">{icon("menu")}</button>
        <ul>{nav_html(active)}</ul>
      </nav>
    </div>
  </div>
</header>"""


def footer_html():
    pages = "".join(f'<li><a href="{u}">{t}</a></li>' for t, u in FOOTER_PAGES)
    b = BUSINESS
    year = datetime.date.today().year
    return f"""<footer class="site-footer">
  <div class="container footer-grid">
    <section class="f-pages" aria-label="Páginas">
      <h3>Páginas</h3>
      <ul>{pages}</ul>
    </section>
    <section class="f-contact" aria-label="Datos de contacto">
      <strong><a href="/">Aventura en USA</a></strong>
      <ul>
        <li>{b["address"]}</li>
        <li>Tel. <a href="tel:{b["phone"]}">{b["phone_display"]}</a></li>
        <li>Horario:<br>&nbsp; {b["hours"]}</li>
        <li><a href="mailto:{b["email"]}">{b["email"]}</a></li>
      </ul>
    </section>
    <section class="f-map" aria-label="Mapa">
      <div class="map-consent" data-map-src="{MAP_SRC}">
        <span>Para la correcta visualización, debe aceptar las cookies.</span>
        <button type="button" data-accept-cookies>Aceptar y mostrar el mapa</button>
      </div>
    </section>
  </div>
</footer>
<div class="socket"><div class="container"><span>© Copyright {year} - Aventura en USA · Move Abroad Experience S.L.</span><a class="f-credit" href="https://ecwebdesign.es/" target="_blank" rel="noopener"><img src="/assets/img/ecwebdesign.png" alt="Diseño y web: EC Web Design" width="94" height="12"></a></div></div>
<a class="to-top" href="#top" aria-label="Volver arriba">{icon("up")}</a>
<button class="cookie-lock" type="button" aria-label="Configuración de cookies">{icon("lock")}</button>
<div class="cookie-bar" role="dialog" aria-label="Aviso de cookies">
  <div class="cb-inner">
    <p>Utilizamos cookies técnicas necesarias para el funcionamiento de la web y, solo si las aceptas, cookies de terceros (Google Maps). Puedes aceptarlas o rechazarlas. Más información en nuestra <a href="/uso-de-cookies/">Política de cookies</a>.</p>
    <div class="cb-actions"><button type="button" class="cb-accept">Aceptar</button><button type="button" class="cb-reject">Rechazar</button></div>
  </div>
</div>
<div class="search-overlay" role="dialog" aria-label="Buscar">
  <button class="so-close" type="button" aria-label="Cerrar">×</button>
  <div class="so-inner">
    <label class="sr-only" for="search-input">Buscar</label>
    <input id="search-input" type="search" placeholder="Buscar…" autocomplete="off">
    <ul class="search-results"></ul>
  </div>
</div>"""


def jsonld(meta, url):
    b = BUSINESS
    org = {
        "@type": ["Organization", "LocalBusiness"],
        "@id": SITE + "/#organization",
        "name": b["name"],
        "legalName": b["legal"],
        "url": SITE + "/",
        "logo": SITE + LOGO,
        "image": SITE + LOGO,
        "telephone": b["phone"],
        "email": b["email"],
        "address": {"@type": "PostalAddress", "streetAddress": "Conde Salvatierra 21, Pta. 4", "postalCode": "46004",
                    "addressLocality": "Valencia", "addressRegion": "Comunidad Valenciana", "addressCountry": "ES"},
        "geo": {"@type": "GeoCoordinates", "latitude": float(b["lat"]), "longitude": float(b["lng"])},
        "openingHoursSpecification": [{"@type": "OpeningHoursSpecification",
                                       "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
                                       "opens": "08:00", "closes": "18:00"}],
        "areaServed": "ES",
    }
    website = {"@type": "WebSite", "@id": SITE + "/#website", "url": SITE + "/", "name": "Aventura en USA",
               "description": "En Aventura en USA te ayudamos a vivir, trabajar y aprender en Estados Unidos",
               "publisher": {"@id": SITE + "/#organization"}, "inLanguage": "es-ES",
               "potentialAction": {"@type": "SearchAction", "target": SITE + "/?s={search_term_string}",
                                   "query-input": "required name=search_term_string"}}
    webpage = {"@type": "WebPage", "@id": url + "#webpage", "url": url, "name": meta["title"],
               "isPartOf": {"@id": SITE + "/#website"}, "inLanguage": "es-ES"}
    if meta.get("description"):
        webpage["description"] = meta["description"]
    graph = [org, website, webpage]
    crumbs = meta.get("breadcrumb")
    if crumbs:
        graph.append({"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + u} for i, (n, u) in enumerate(crumbs)
        ]})
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False)


def page_html(meta, content):
    path = meta["path"]
    url = SITE + path
    robots = meta.get("robots", "index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1")
    if BASE:  # vista previa en github.io: que Google no la indexe
        robots = "noindex, nofollow"
    desc = meta.get("description", "")
    og_image = SITE + meta.get("og_image", "/wp-content/uploads/2024/07/vive-la-experiencia-buena.jpg")
    body_cls = "header-transparent" if meta.get("header") == "transparent" else "header-solid"
    title = html.escape(meta["title"])
    desc_tags = ""
    if desc:
        d = html.escape(desc)
        desc_tags = (f'<meta name="description" content="{d}">\n'
                     f'<meta property="og:description" content="{d}">\n'
                     f'<meta name="twitter:description" content="{d}">\n')
    canonical = f'<link rel="canonical" href="{url}">\n' if meta.get("canonical", True) else ""
    reading = f'<meta name="twitter:label1" content="Tiempo de lectura">\n<meta name="twitter:data1" content="{meta["reading"]}">\n' if meta.get("reading") else ""
    return f"""<!DOCTYPE html>
<html lang="es-ES">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
{desc_tags}<meta name="robots" content="{robots}">
{canonical}<meta name="google-site-verification" content="{GOOGLE_VERIFICATION}">
<meta name="geo.region" content="ES-VC">
<meta name="geo.placename" content="Valencia">
<meta name="geo.position" content="{BUSINESS['lat']};{BUSINESS['lng']}">
<meta name="ICBM" content="{BUSINESS['lat']}, {BUSINESS['lng']}">
<meta property="og:locale" content="es_ES">
<meta property="og:type" content="website">
<meta property="og:title" content="{title}">
<meta property="og:url" content="{url}">
<meta property="og:site_name" content="Aventura en USA">
<meta property="og:image" content="{og_image}">
<meta name="twitter:card" content="summary_large_image">
{reading}<meta name="theme-color" content="#154579">
<link rel="icon" href="{FAVICON}" type="image/png">
<link rel="apple-touch-icon" href="{FAVICON}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cabin:wght@400;500;600;700&display=swap">
<link rel="stylesheet" href="/assets/css/style.css?v={BUILD_VERSION}">
<script type="application/ld+json">{jsonld(meta, url)}</script>
</head>
<body class="{body_cls}" id="top" data-base="{BASE}">
{header_html(meta.get("nav", ""))}
<main id="main">
{content}
</main>
{footer_html()}
<script src="/assets/js/main.js?v={BUILD_VERSION}" defer></script>
</body>
</html>
"""


def redirect_html(old, new):
    url = SITE + new
    return f"""<!DOCTYPE html>
<html lang="es-ES">
<head>
<meta charset="UTF-8">
<title>Aventura en USA</title>
<meta name="robots" content="noindex, follow">
<link rel="canonical" href="{url}">
<meta http-equiv="refresh" content="0; url={new}">
<script>location.replace("{new}" + location.hash);</script>
</head>
<body><p>Esta página se ha trasladado a <a href="{new}">{url}</a>.</p></body>
</html>
"""


# ---------------------------------------------------------------------------
# Construcción
# ---------------------------------------------------------------------------
META_RE = re.compile(r"\A\s*<!--\s*meta\s*(\{.*?\})\s*-->", re.S)


def strip_tags(s):
    s = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", s, flags=re.S)
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


def out_path(path):
    if path == "/404.html":
        return ROOT / "404.html"
    return ROOT / path.strip("/") / "index.html" if path != "/" else ROOT / "index.html"


def main():
    sitemap = []
    search = []
    pages = sorted(PAGES.glob("*.html"))
    for f in pages:
        raw = f.read_text(encoding="utf-8")
        m = META_RE.match(raw)
        if not m:
            raise SystemExit(f"Falta la cabecera <!--meta {{...}} --> en {f}")
        meta = json.loads(m.group(1))
        content = raw[m.end():].strip()
        content = re.sub(r"\{\{icon:([\w-]+)\}\}", lambda mm: icon(mm.group(1)), content)
        content = replace_bg(content)
        target = out_path(meta["path"])
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(with_base(IMG_RE.sub(replace_img, page_html(meta, content))), encoding="utf-8")
        if meta.get("sitemap", True) and "noindex" not in meta.get("robots", ""):
            sitemap.append((meta["path"], meta.get("lastmod"), meta.get("priority", "0.8")))
        if meta["path"] != "/404.html":
            search.append({"title": meta["title"].replace(" - Aventura en USA", ""), "url": meta["path"],
                           "description": meta.get("description", ""), "text": strip_tags(content)[:4000]})
        print("✔", meta["path"])

    for old, new in REDIRECTS.items():
        t = out_path(old)
        t.parent.mkdir(parents=True, exist_ok=True)
        t.write_text(with_base(redirect_html(old, new)), encoding="utf-8")
        print("↪", old, "→", new)

    # sitemap.xml (+ los nombres de sitemap que usaba Yoast en la web antigua)
    today = datetime.date.today().isoformat()
    urls = "".join(
        f"  <url>\n    <loc>{SITE}{p}</loc>\n    <lastmod>{lm or today}</lastmod>\n    <priority>{pr}</priority>\n  </url>\n"
        for p, lm, pr in sorted(sitemap, key=lambda x: (x[0] != "/", x[0]))
    )
    xml = f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n'
    (ROOT / "sitemap.xml").write_text(xml, encoding="utf-8")
    (ROOT / "page-sitemap.xml").write_text(xml, encoding="utf-8")
    index_xml = (f'<?xml version="1.0" encoding="UTF-8"?>\n<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                 f'  <sitemap>\n    <loc>{SITE}/page-sitemap.xml</loc>\n    <lastmod>{today}</lastmod>\n  </sitemap>\n</sitemapindex>\n')
    (ROOT / "sitemap_index.xml").write_text(index_xml, encoding="utf-8")
    (ROOT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap_index.xml\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")
    (ROOT / "search-index.json").write_text(json.dumps(search, ensure_ascii=False), encoding="utf-8")

    # listado de imágenes pendientes
    lines = ["# Imágenes pendientes", "",
             "Copia cada imagen en la ruta indicada (respetando carpetas y nombre) y ejecuta `python3 src/build.py`.",
             "Así las fotos conservan exactamente la misma URL que tenían en la web antigua.", ""]
    for s in sorted(missing_images):
        lines.append(f"- [ ] `{s.lstrip('/')}`")
    if present_images:
        lines += ["", "## Ya incluidas", ""] + [f"- [x] `{s.lstrip('/')}`" for s in sorted(present_images)]
    (ROOT / "IMAGENES.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\n{len(pages)} páginas · {len(missing_images)} imágenes pendientes · {len(present_images)} imágenes presentes")


if __name__ == "__main__":
    main()
