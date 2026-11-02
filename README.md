# Aventura en USA — web estática

Réplica de [aventuraenusa.es](https://aventuraenusa.es) (distribución, colores, tipografías y textos) preparada para publicarse con **GitHub Pages** y sustituir a la web de WordPress sin perder posicionamiento.

## Estructura

| Carpeta / archivo | Qué contiene |
|---|---|
| `src/pages/*.html` | Contenido de cada página + sus metadatos SEO (título, descripción, ruta…) en la cabecera `<!--meta {...} -->` |
| `src/build.py` | Genera el HTML final (cabecera, menú, pie, SEO, sitemap…) |
| `assets/css/style.css` · `assets/js/main.js` | Estilos e interacciones |
| `wp-content/uploads/…` | Aquí van las imágenes, **con la misma ruta que tenían en WordPress** |
| `index.html`, `monitor-de-campamento/…`, etc. | HTML generado (no editar a mano) |
| `IMAGENES.md` | Lista de imágenes que faltan y dónde copiarlas |

## Editar y regenerar

```bash
python3 src/build.py
```

Edita los archivos de `src/pages/` y vuelve a ejecutar el comando. Las páginas generadas se actualizan solas.

## Imágenes

Mientras falte una foto se muestra un hueco rayado con su nombre. Copia la imagen en la ruta que indica `IMAGENES.md` (por ejemplo `wp-content/uploads/2024/07/blanco.png`), ejecuta `python3 src/build.py` y el hueco se convierte en la foto real.

## SEO conservado

- **Mismas URLs** que la web actual (con barra final), mismos títulos y descripciones.
- `canonical`, `robots` (las páginas legales siguen en `noindex`), etiquetas geo y la verificación de Google Search Console.
- Datos estructurados (Organization / LocalBusiness, WebSite, WebPage y migas de pan) y etiquetas Open Graph.
- `sitemap.xml`, `sitemap_index.xml` y `page-sitemap.xml` (los nombres que ya conoce Google) y `robots.txt`.
- Imágenes servidas en sus rutas originales `/wp-content/uploads/…` (se mantiene Google Imágenes).
- Redirecciones de URLs antiguas sin contenido (`/inicio/`, `/entrada-1/`…) y página `404.html` propia.

## Vista previa y puesta en marcha

La web se publica sola con GitHub Actions (`.github/workflows/pages.yml`) en cada cambio de `main`.

1. **Activar GitHub Pages** (una sola vez): *Settings → Pages → Build and deployment → Source: **GitHub Actions***.
   Vista previa: `https://estebancalvobayarri.github.io/aventuraenusa/` (marcada como `noindex` para que Google no la confunda con la web real).
2. **Día del cambio de dominio**:
   - Añade al repositorio un archivo `CNAME` con el texto `aventuraenusa.es` (la web pasa a generarse para la raíz del dominio).
   - *Settings → Pages → Custom domain*: `aventuraenusa.es`.
   - DNS en tu proveedor: registros `A` de `aventuraenusa.es` → `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`; registro `CNAME` de `www` → `estebancalvobayarri.github.io`.
   - Marca **Enforce HTTPS** cuando GitHub lo permita.
3. **Google Search Console** (la verificación ya está incluida): envía `https://aventuraenusa.es/sitemap.xml` e inspecciona las páginas principales.
4. **Formulario de contacto**: usa [FormSubmit](https://formsubmit.co); el primer envío manda un correo de activación a `info@aventuraenusa.es` que hay que confirmar una vez.
