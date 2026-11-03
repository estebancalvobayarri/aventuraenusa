#!/usr/bin/env python3
"""
Prepara las imágenes de la web a partir de la carpeta fotos/.

Uso:  python3 src/fotos.py        (necesita Pillow: pip install pillow)

Lee src/fotos.json (ruta final -> foto de fotos/), redimensiona y comprime cada
foto para web y la guarda en su ruta final (la misma URL que en la web antigua).
"""
import json
import unicodedata
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
FOTOS = ROOT / "fotos"
nfc = lambda s: unicodedata.normalize("NFC", s)

# Tamaño máximo según el tipo de imagen (ancho, alto). Si se indican los dos se recorta a esa proporción.
GALLERY = (990, 800)      # tres fotos de "Viaja y disfruta" (proporción 495x400)
SLIDE = (1270, 1028)      # carruseles (proporción 845x684)
HERO_W = 2400             # fondos a pantalla completa
CONTENT_W = 1600          # fotos dentro del contenido


def kind(dest):
    name = dest.rsplit("/", 1)[-1]
    if "495x400" in name:
        return GALLERY
    if any(k in name for k in ("maestros-ninos", "actividades-arts", "artes-escenicas", "sport-coaching",
                               "outdoor-and-adventure", "ninos-sonrientes", "aventura-en-usa")):
        return SLIDE
    if any(k in name for k in ("buena", "nyc-", "principal", "EL-PROGRAMA", "escritorio", "chinatown",
                               "pexels-hilmi-isilak-11183447-scaled-1")):
        return (HERO_W, None)
    return (CONTENT_W, None)


def main():
    mapping = {k: v for k, v in json.loads((ROOT / "src/fotos.json").read_text(encoding="utf-8")).items()
               if not k.startswith("_")}
    files = {nfc(p.name): p for p in FOTOS.iterdir() if p.is_file()}
    slide_dests = [d for d in mapping if kind(d) == SLIDE]
    done, missing = 0, []
    for dest, src_name in mapping.items():
        src = files.get(nfc(src_name))
        if not src:
            missing.append(src_name)
            continue
        im = ImageOps.exif_transpose(Image.open(src))
        w, h = kind(dest)
        # el waterfront también aparece en el carrusel: se deja sin recortar (sirve para ambos)
        if h:
            if im.width < w:  # no ampliar fotos pequeñas: se recorta a la proporción con su tamaño real
                w, h = im.width, round(im.width * h / w)
            im = ImageOps.fit(im.convert("RGB"), (w, h), Image.LANCZOS)
        else:
            if im.width > w:
                im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
        out = ROOT / dest
        out.parent.mkdir(parents=True, exist_ok=True)
        ext = out.suffix.lower()
        if ext == ".webp":
            im.convert("RGB").save(out, "WEBP", quality=80, method=6)
        elif ext == ".png":
            im.save(out, "PNG", optimize=True)
        else:
            im.convert("RGB").save(out, "JPEG", quality=80, optimize=True, progressive=True)
        done += 1
        print(f"✔ {dest}  ({out.stat().st_size // 1024} KB)  ← {src_name}")
    print(f"\n{done} imágenes generadas")
    if missing:
        print("No encontradas en fotos/:", ", ".join(missing))


if __name__ == "__main__":
    main()
