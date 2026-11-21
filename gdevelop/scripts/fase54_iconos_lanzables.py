"""Fase 54 · Icono del lanzable en el panel según el objeto (balón / libro / engrapadora). Idempotente; va al final de la cadena (después de fase53).

Uso (desde la carpeta fdiz, con GDevelop CERRADO):  python3 gdevelop/scripts/fase54_iconos_lanzables.py
Antes el panel mostraba siempre el icono del balón. Ahora crea ico128_lanzable_{balon,libro,engrapadora}.png (los sprites del objeto recortados, escalados a ~100 px
y centrados en 128x128), añade las animaciones lanzable_<tipo> a HudInv y un evento por jugador que elige la animación con Sup.Lanz.
"""
import copy, datetime, json, os, shutil
from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
PRY = os.path.join(AQUI, "..", "FDI-Z", "FDI-Z.json")
HUD = os.path.join(AQUI, "..", "FDI-Z", "assets", "interfaz", "hud")
SPR = os.path.join(AQUI, "..", "..", "generado", "sprites", "objetos", "lanzables")
TIPOS = ("balon", "libro", "engrapadora")


def icono(tipo):
    if tipo == "balon":   # el icono original ya es el balón
        return Image.open(os.path.join(HUD, "ico128_lanzable.png")).convert("RGBA")
    im = Image.open(os.path.join(SPR, tipo + ".png")).convert("RGBA")
    im = im.crop(im.getbbox())
    k = 100 / max(im.size)   # el objeto ocupa unos 100 px de los 128, como el balón
    im = im.resize((round(im.width * k), round(im.height * k)), Image.NEAREST)
    out = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    out.paste(im, ((128 - im.width) // 2, (128 - im.height) // 2), im)
    return out


def main():
    d = json.load(open(PRY, encoding="utf-8"))
    resp = os.path.join(AQUI, "..", "respaldos"); os.makedirs(resp, exist_ok=True)
    bak = os.path.join(resp, "antes_de_fase54_%s.json" % datetime.date.today().strftime("%Y%m%d"))
    if not os.path.exists(bak): shutil.copy(PRY, bak)
    J = next(l for l in d["layouts"] if l["name"] == "Juego")
    base = next(r for r in d["resources"]["resources"] if r["name"] == "ui_hud/ico128_lanzable.png")
    hi = next(o for o in J["objects"] if o["name"] == "HudInv")
    anim0 = next(a for a in hi["animations"] if a["name"] == "lanzable")
    for t in TIPOS:
        f = "ico128_lanzable_%s.png" % t
        if t == "balon": shutil.copy(os.path.join(HUD, "ico128_lanzable.png"), os.path.join(HUD, f))
        else: icono(t).save(os.path.join(HUD, f))
        rn = "ui_hud/" + f
        if not any(r["name"] == rn for r in d["resources"]["resources"]):
            r = copy.deepcopy(base); r["name"] = rn; r["file"] = "assets/interfaz/hud/" + f; d["resources"]["resources"].append(r)
        if not any(a["name"] == "lanzable_" + t for a in hi["animations"]):
            a = copy.deepcopy(anim0); a["name"] = "lanzable_" + t; a["directions"][0]["sprites"][0]["image"] = rn; hi["animations"].append(a)
    g = next(e for e in J["events"] if e.get("name", "").startswith("Interfaz: HUD con paneles"))
    ev = g["events"]
    ev[:] = [e for e in ev if not any(a["type"]["value"] == "SetAnimationName" and a["parameters"][0] == "HudInv" and a["parameters"][1].startswith('"lanzable_"') for a in e.get("actions", []))]
    nuevos = []
    for e in ev:
        if any(a["type"]["value"] == "Montre" and a["parameters"][0] == "HudInv" for a in e.get("actions", [])) and any(c["type"]["value"] == "VarObjetTxt" and c["parameters"][:2] == ["Sup", "Lanz"] for c in e.get("conditions", [])):
            n = copy.deepcopy(e)
            n["actions"] = [{"type": {"inverted": False, "value": "SetAnimationName"}, "parameters": ["HudInv", '"lanzable_" + Sup.VariableString(Lanz)']}]
            nuevos.append(n)
    assert len(nuevos) == 4, len(nuevos)
    ev.extend(nuevos)
    json.dump(d, open(PRY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("OK fase54 (iconos de lanzables: %d eventos)" % len(nuevos))


main()
