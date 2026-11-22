"""Fase 64 · Datos de los diálogos en burbujas: banco de diálogos + voces de audios_fish. Se puede volver a correr.

Uso (desde la carpeta fdiz):
    python -I gdevelop/scripts/fase64_datos_dialogos.py
Lee:
  * "FDI-Z · Banco de diálogos (versión limpia).md" (raíz de fdiz): frases individuales (Partes 2 y 4) y conversaciones
    (Partes 1 y 3), con su situación.
  * audios_fish/<Personaje>/lista.txt + los .wav: archivo, situación y texto grabado.
Escribe:
  * gdevelop/scripts/dialogos_datos.js   datos que usa scripts/dialogo.js (no editar a mano: correr este script)
  * gdevelop/DIALOGOS.md                 qué voz corresponde a cada línea, qué dispara cada situación y qué falta

Voces: una línea tiene voz SOLO si en la lista.txt del mismo personaje hay un archivo cuyo texto grabado (sin las
etiquetas de tono "(sarcastic)", sin signos ni acentos) es igual al de la línea. Nunca se asigna un audio por parecido.
Situaciones: SITUACION (abajo) relaciona la situación del banco con un evento que dialogo.js sabe detectar. Las que no
tienen evento en el juego quedan con disparador None y se listan en DIALOGOS.md.
"""
import json, os, re, struct, sys, unicodedata

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, "..", ".."))
BANCO = os.path.join(RAIZ, "FDI-Z · Banco de diálogos (versión limpia).md")
VOCES = os.path.join(RAIZ, "audios_fish")
SALIDA_JS = os.path.join(AQUI, "dialogos_datos.js")
SALIDA_MD = os.path.join(RAIZ, "gdevelop", "DIALOGOS.md")

PJ = {"alan": "alan", "miranda": "miranda", "tony": "tony", "cesar": "cesar", "castillo": "castillo", "gabo": "gabo",
      "alessandro": "alessandro", "carlos": "carlos", "justino": "justino", "canepa": "canepa", "joel": "joel"}
CARPETA = {"alan": "Alan", "castillo": "Castillo", "cesar": "Cesar", "miranda": "Miranda", "tony": "Tony"}

# (personaje, situación normalizada) -> disparador de dialogo.js (None = no hay ese momento en el juego)
SITUACION = {
    ("alan", "espera en el salon"): "intro_espera", ("alan", "los zombies tumban la puerta del salon"): "intro_puerta",
    ("alan", "gorrear aparece una regla"): "hab_regla", ("alan", "gorrear aparece comida"): "hab_comida",
    ("alan", "reembolso aparecen escobas"): "esp", ("alan", "ojo de oferta se ve una zona oscura"): None,
    ("alan", "levanta una silla"): "silla", ("alan", "lanza una engrapadora"): "engrapadora", ("alan", "revisa un locker"): "locker",
    ("alan", "no alcanza para comida en la maquina"): None, ("alan", "compra un arma en la maquina"): None,
    ("alan", "recoge la tarjeta electronica"): "tarjeta", ("alan", "recupera las llaves de conserjeria"): "llaves",
    ("alan", "va a llamar desde site cic"): "llamada", ("alan", "recoge un bidon de gasolina"): "bidon",
    ("alan", "restaura la luz con el ultimo interruptor"): "luz", ("alan", "lleva la carnada a la neveria"): "carnada",
    ("alan", "rescata a justino"): "rescate_justino", ("alan", "cae con un companero cerca"): "cae_cerca",
    ("alan", "revive a un companero"): "revive", ("alan", "lo muerde un zombie"): "mordido",
    ("alan", "empieza a curar a un companero mordido"): "curar", ("alan", "empieza aguanten junto al camion"): "final",
    ("alan", "escapan en el camion"): "escape",
    ("miranda", "abre una puerta sin problema"): "puerta_abre", ("miranda", "termina una pelea"): "fin_pelea",
    ("miranda", "un companero se acelera"): "turbo", ("miranda", "antes del brote"): "intro_espera",
    ("miranda", "se atoran con una puerta"): "atorados", ("miranda", "duerme a los zombies con arrullo"): "hab",
    ("miranda", "activa minigun"): "esp", ("miranda", "recupera vida con su pasiva"): None,
    ("miranda", "le llegan zombies por un lado"): None, ("miranda", "empieza el apagon"): "apagon",
    ("miranda", "la reviven"): "revivido", ("miranda", "la muerden y tiene un companero cerca"): "mordido_cerca",
    ("miranda", "cae"): "cae", ("miranda", "empieza la oleada del camion"): "final", ("miranda", "escapa"): "escape",
    ("tony", "en el salon antes de la alerta"): "intro_espera", ("tony", "a media conversacion"): None,
    ("tony", "antes de que empiece el desmadre"): "intro_espera", ("tony", "llega la alerta al celular"): "intro_alerta",
    ("tony", "el equipo se toma un respiro"): "respiro", ("tony", "se calma el pasillo"): "calma",
    ("tony", "cocinar salen dos comidas"): "hab", ("tony", "cocinar se arma el festin en la neveria"): "festin",
    ("tony", "activa modo gym"): "esp", ("tony", "termina una persecucion"): None,
    ("tony", "encuentra la puerta electronica cerrada"): "puerta_electronica", ("tony", "completa un objetivo"): "objetivo_cumplido",
    ("tony", "el equipo revisa un locker"): "locker_equipo", ("tony", "revive a un companero"): "revive",
    ("tony", "lo muerden"): "mordido", ("tony", "cae"): "cae", ("tony", "escapa en el camion"): "escape",
    ("cesar", "el equipo duda"): "duda", ("cesar", "usa hackeo con una puerta cerca"): "hab_puerta",
    ("cesar", "aparece su ruta al objetivo"): "objetivo_nuevo", ("cesar", "usa control de la escuela"): "esp",
    ("cesar", "revive a un companero"): "revive", ("cesar", "lo reviven"): "revivido", ("cesar", "cae"): "cae",
    ("castillo", "antes de la alerta"): "intro_espera", ("castillo", "los zombies tumban la puerta"): "intro_puerta",
    ("castillo", "se atoran en una puerta restringida"): "atorados", ("castillo", "encuentra un arma en el piso"): "arma_piso",
    ("castillo", "usa tragar y se cura"): "hab", ("castillo", "usa app de salud y convierte zombies en aliados"): "esp",
    ("castillo", "se queda cubriendo la entrada"): None, ("castillo", "compra un arma"): None,
    ("castillo", "revisa la computadora del site"): "llamada", ("castillo", "el equipo duda durante la oleada"): "final_duda",
    ("castillo", "lo reviven"): "revivido", ("castillo", "cae"): "cae", ("castillo", "escapa"): "escape",
    ("gabo", "al entrar al salon"): "intro_espera", ("gabo", "se calma el pasillo dos cuadros"): "calma",
    ("gabo", "sale sin las cuartillas dos cuadros"): None, ("gabo", "activa supervelocidad"): "hab",
    ("gabo", "termina de correr"): None, ("gabo", "activa ecosistema"): "esp", ("gabo", "manda un arma por airdrop"): None,
    ("gabo", "se va la luz"): "apagon", ("gabo", "sale del salon"): None, ("gabo", "un companero se queda atras"): None,
    ("gabo", "lo muerden"): "mordido", ("gabo", "cae"): "cae", ("gabo", "sube al camion"): None, ("gabo", "escapa"): "escape",
    ("alessandro", "espera al profe"): "intro_espera", ("alessandro", "antes de la alerta"): "intro_espera",
    ("alessandro", "el equipo ve la hora"): None, ("alessandro", "los zombies tumban una puerta"): "puerta_rota",
    ("alessandro", "usa chiste y los zombies se rien"): "hab", ("alessandro", "activa reloj"): "esp",
    ("alessandro", "se calla el pasillo"): "calma", ("alessandro", "revisa un locker"): "locker",
    ("alessandro", "el equipo esta por comprar en la maquina"): None, ("alessandro", "encuentra a un companero caido"): "caido_visto",
    ("alessandro", "lo alcanzan los zombies"): None, ("alessandro", "lo muerden"): "mordido", ("alessandro", "cae"): "cae",
    ("alessandro", "la horda empieza a pegarle a una puerta"): "puerta_golpe", ("alessandro", "se prepara para la oleada final"): "final",
    ("alessandro", "escapa en el camion"): "escape",
    ("carlos", "se queda en silencio el pasillo"): "calma", ("carlos", "el equipo se acerca a una puerta"): None,
    ("carlos", "usa llave maestra"): "hab", ("carlos", "activa tanque"): "esp", ("carlos", "encuentra una tarjeta"): "tarjeta",
    ("carlos", "se va la luz"): "apagon", ("carlos", "corre contra el tiempo"): "final_tiempo",
    ("carlos", "lo agarra un zombie por detras"): None, ("carlos", "revive a un companero"): "revive", ("carlos", "cae"): "cae",
    ("carlos", "escapa"): "escape",
    ("justino", "al llegar a su rescate"): "rescate_inicio", ("justino", "durante el rescate"): None,
    ("justino", "le piden ayuda con el site"): None, ("justino", "se acerca una horda"): "horda",
    ("justino", "termina el rescate"): "rescate_justino",
    ("canepa", "el equipo llega al camion"): None, ("canepa", "empieza a revisar el motor"): "final_motor",
    ("canepa", "necesita una herramienta"): None, ("canepa", "pide que cubran la entrada"): "final_entrada",
    ("canepa", "se acerca otra oleada"): "final_oleada", ("canepa", "esta por terminar de reparar"): "final_casi",
    ("canepa", "intenta arrancar el camion"): None, ("canepa", "arranca el camion"): "escape",
    ("canepa", "el equipo sube al camion"): None, ("canepa", "el equipo escapa"): None,
}
# conversaciones: título normalizado -> (disparador, quién lo provoca o None, quién más debe estar cerca)
CONVERSACION = {
    "alan y miranda 1": (None, None, None),                          # "falla" un lanzamiento: no se puede saber
    "alan y miranda 2": ("hab", "miranda", "alan"),
    "alan y tony 1": ("horda", None, None),
    "alan y tony 2": ("esp", "tony", "alan"),
    "alan y cesar": ("hab_puerta", "cesar", "alan"),
    "alan y castillo": ("hab", "castillo", "alan"),
    "tony y miranda": (None, None, None),
    "tony y castillo": ("hab", "castillo", "tony"),
    "tony y cesar": ("hab_puerta", "cesar", "tony"),
    "miranda y castillo": ("atorados", "castillo", "miranda"),
    "alan y alessandro 1": ("hab", "alessandro", "alan"),
    "alan y alessandro 2": ("esp", "alessandro", "alan"),
    "alan y alessandro 3": ("esp", "alan", "alessandro"),
    "alan y gabo 1": ("hab", "gabo", "alan"),
    "alan y gabo 2": (None, None, None),                            # AirDrop: no hay ese momento
    "alan y gabo 3": ("rescate_justino", None, None),
    "alan y carlos": ("hab", "carlos", "alan"),
    "tony y alessandro 1": (None, None, None),
    "tony y alessandro 2": ("calma", None, None),
    "tony y alessandro 3": (None, None, None),
    "tony y alessandro 4": ("calma", None, None),
    "tony y gabo": ("esp", "tony", "gabo"),
    "tony y carlos": (None, None, None),
    "miranda y gabo": ("objetivo_cumplido", None, None),
    "miranda y alessandro": ("apagon", None, None),
    "miranda y carlos": ("apagon", None, None),
    "gabo y castillo": ("objetivo_llaves", None, None),
    "castillo y carlos": ("horda", None, None),
    "castillo y alessandro": ("esp", "alessandro", "castillo"),
    "cesar y carlos": (None, None, None),
    "cesar y alessandro": ("revive", "cesar", "alessandro"),          # César revive a Alessandro
    "justino y miranda 1": ("rescate_inicio", None, None),
    "justino y miranda 2": (None, None, None),
    "gabo y alessandro": (None, None, None),
    "gabo y carlos": ("esp", "carlos", "gabo"),
    "alessandro y carlos": ("final", None, None),
    "justino y gabo": ("rescate_inicio", None, None),
    "canepa y alessandro": ("final_entrada", None, None),
}


def norm(s):
    s = unicodedata.normalize("NFD", s)
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn").lower()
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", s)).strip()


def limpiar(s):
    s = s.replace("\\!", "!").replace("\\?", "?").replace("\\", "")
    return re.sub(r"\s+", " ", s.replace("**", "")).strip()


def wav_dur(ruta):
    b = open(ruta, "rb").read()
    if b[:4] != b"RIFF" or b[8:12] != b"WAVE":
        raise SystemExit("No es WAV: " + ruta)
    i, fmt, n = 12, None, 0
    while i + 8 <= len(b):
        cid, sz = b[i:i + 4], struct.unpack("<I", b[i + 4:i + 8])[0]
        if cid == b"fmt ":
            fmt = struct.unpack("<HHIIHH", b[i + 8:i + 24])
        elif cid == b"data":
            n = sz
        i += 8 + sz + (sz & 1)
    return round(n / (fmt[2] * fmt[4]), 2)


def leer_banco():
    texto = open(BANCO, encoding="utf-8").read().splitlines()
    parte, quien, conv, sit = 0, None, None, ""
    lineas, convs = [], []
    for raw in texto:
        l = limpiar(raw)
        m = re.match(r"^# Parte (\d)", l)
        if m:
            parte = int(m.group(1)); continue
        if parte in (2, 4):
            m = re.match(r"^## (.+)$", l)
            if m and not l.startswith("### "):
                quien = PJ.get(norm(m.group(1)).split(" ")[0]); continue
            m = re.match(r"^### (.+)$", l)
            if m:
                quien = PJ.get(norm(m.group(1)).split(" ")[0]); continue
            m = re.match(r"^\* (.+) · ([A-ZÁÉÍÓÚÑ]+: .+)$", l)          # la situación puede tener « · » («Gorrear · Aparece…»)
            if m and quien:
                situacion = m.group(1)
                cuadros = [re.sub(r"^[A-ZÁÉÍÓÚÑ]+: ", "", c.strip()) for c in m.group(2).split(" / ")]
                lineas.append({"pj": quien, "situacion": situacion, "cuadros": cuadros})
        if parte in (1, 3):
            m = re.match(r"^### (.+)$", l)
            if m:
                conv = {"titulo": m.group(1), "situacion": "", "lineas": []}; convs.append(conv); continue
            if conv and re.match(r"^\*[^*].*\*$", raw.strip()):
                conv["situacion"] = limpiar(raw.strip().strip("*")); continue
            m = re.match(r"^\* ([A-ZÁÉÍÓÚÑ]+): (.+)$", l)
            if m and conv:
                conv["lineas"].append({"pj": PJ[norm(m.group(1))], "txt": m.group(2)})
    return lineas, convs


def leer_voces():
    voces = {}
    for pj, carpeta in CARPETA.items():
        lista = os.path.join(VOCES, carpeta, "lista.txt")
        if not os.path.exists(lista):
            continue
        for fila in open(lista, encoding="utf-8").read().splitlines()[1:]:
            if not fila.strip():
                continue
            archivo, situacion, dialogo = fila.split("\t")
            ruta = os.path.join(VOCES, carpeta, archivo)
            if not os.path.exists(ruta):
                continue
            hablado = re.sub(r"\([^)]*\)", " ", dialogo)
            voces.setdefault(pj, []).append({"archivo": archivo, "carpeta": carpeta, "situacion": situacion,
                                             "texto": norm(hablado), "dur": wav_dur(ruta)})
    return voces


def main():
    if not os.path.exists(BANCO):
        raise SystemExit("Falta el banco de diálogos: " + BANCO)
    lineas, convs = leer_banco()
    voces = leer_voces()
    usadas = set()

    def voz_de(pj, txt):
        t = norm(txt)
        for v in voces.get(pj, []):
            if v["texto"] == t:
                usadas.add((pj, v["archivo"]))
                return v
        return None

    datos_l, datos_c, sin_regla = [], [], []
    for l in lineas:
        clave = (l["pj"], norm(l["situacion"]))
        if clave not in SITUACION:
            sin_regla.append(clave)
        disp = SITUACION.get(clave)
        cuadros = []
        for c in l["cuadros"]:
            v = voz_de(l["pj"], c)
            cuadros.append({"txt": c, "voz": ("voces/%s/%s" % (l["pj"], v["archivo"])) if v else None, "dur": v["dur"] if v else None})
        datos_l.append({"pj": l["pj"], "situacion": l["situacion"], "disp": disp, "cuadros": cuadros})
    for c in convs:
        clave = norm(c["titulo"])
        if clave not in CONVERSACION:
            sin_regla.append(("conv", clave))
        disp, actor, cerca = CONVERSACION.get(clave, (None, None, None))
        ls = []
        for x in c["lineas"]:
            v = voz_de(x["pj"], x["txt"])
            ls.append({"pj": x["pj"], "txt": x["txt"], "voz": ("voces/%s/%s" % (x["pj"], v["archivo"])) if v else None, "dur": v["dur"] if v else None})
        datos_c.append({"titulo": c["titulo"], "situacion": c["situacion"], "disp": disp, "actor": actor, "cerca": cerca, "lineas": ls})
    if sin_regla:
        raise SystemExit("Situaciones del banco sin regla en SITUACION/CONVERSACION: %s" % sin_regla)

    recursos = sorted({(pj, v["carpeta"], v["archivo"]) for pj, lst in voces.items() for v in lst if (pj, v["archivo"]) in usadas})
    sobran = sorted((pj, v["archivo"]) for pj, lst in voces.items() for v in lst if (pj, v["archivo"]) not in usadas)
    js = ("/* FDI-Z · Fase 64 · Datos de los diálogos en burbujas. GENERADO por scripts/fase64_datos_dialogos.py desde el banco\n"
          " * de diálogos y audios_fish: no editar a mano. */\n"
          "gdjs.fdizDialogosDatos = " + json.dumps({"lineas": datos_l, "conversaciones": datos_c,
                                                   "voces": ["voces/%s/%s" % (pj, a) for pj, _, a in recursos]},
                                                  ensure_ascii=False, indent=1) + ";\n")
    open(SALIDA_JS, "w", encoding="utf-8", newline="\n").write(js)
    json.dump({"recursos": [{"nombre": "voces/%s/%s" % (pj, a), "archivo": "../../audios_fish/%s/%s" % (cp, a)} for pj, cp, a in recursos]},
              open(os.path.join(AQUI, "dialogos_voces.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    # ---------------- documento
    NOM = {"alan": "Alan", "miranda": "Miranda", "tony": "Tony", "cesar": "César", "castillo": "Castillo", "gabo": "Gabo",
           "alessandro": "Alessandro", "carlos": "Carlos", "justino": "Justino", "canepa": "Canepa"}
    md = ["# Diálogos en burbujas y voces (fase 64)", "",
          "Generado por `gdevelop/scripts/fase64_datos_dialogos.py` desde `FDI-Z · Banco de diálogos (versión limpia).md` y `audios_fish/*/lista.txt`. "
          "Una línea tiene voz solo si el texto grabado (sin las etiquetas de tono) es igual al de la línea. "
          "«Disparador» es el momento del juego que la activa (ver `scripts/dialogo.js`); «—» = ese momento no existe en el juego y la línea no se usa.", "",
          "## Frases individuales", "", "| Personaje | Situación | Disparador | Línea | Voz |", "|---|---|---|---|---|"]
    for l in datos_l:
        for k, c in enumerate(l["cuadros"]):
            voz = "`audios_fish/%s/%s`" % (CARPETA[l["pj"]], c["voz"].split("/")[-1]) if c["voz"] else ("sin voz (profe)" if l["pj"] in ("justino", "canepa") else "**falta**")
            md.append("| %s | %s%s | %s | %s | %s |" % (NOM[l["pj"]], l["situacion"], " (%d/%d)" % (k + 1, len(l["cuadros"])) if len(l["cuadros"]) > 1 else "",
                                                   l["disp"] or "—", c["txt"], voz))
    md += ["", "## Conversaciones", "", "| Conversación | Situación | Disparador | Línea | Voz |", "|---|---|---|---|---|"]
    for c in datos_c:
        for x in c["lineas"]:
            voz = "`audios_fish/%s/%s`" % (CARPETA[x["pj"]], x["voz"].split("/")[-1]) if x["voz"] else ("sin voz (profe)" if x["pj"] in ("justino", "canepa") else "**falta**")
            md.append("| %s | %s | %s | %s: %s | %s |" % (c["titulo"], c["situacion"], c["disp"] or "—", NOM[x["pj"]], x["txt"], voz))
    usadas_n = len(recursos)
    faltan = [(l["pj"], c["txt"]) for l in datos_l if l["disp"] for c in l["cuadros"] if not c["voz"] and l["pj"] not in ("justino", "canepa")] + \
             [(x["pj"], x["txt"]) for c in datos_c if c["disp"] for x in c["lineas"] if not x["voz"] and x["pj"] not in ("justino", "canepa")]
    md += ["", "## Resumen", "",
           "- Voces encontradas en `audios_fish`: %d; relacionadas con su línea: %d." % (sum(len(v) for v in voces.values()), usadas_n),
           "- Archivos sin línea en el banco: %s." % (", ".join("`%s`" % a for _, a in sobran) or "ninguno"),
           "- Líneas que el juego usa y no tienen voz (se ven solo en texto): %d. Personajes sin carpeta de voces: Gabo, Alessandro, Carlos (y los profes, que no tienen voz)." % len(faltan), ""]
    open(SALIDA_MD, "w", encoding="utf-8", newline="\n").write("\n".join(md))
    print("Diálogos: %d frases, %d conversaciones, %d voces relacionadas de %d, %d líneas usadas sin voz, archivos sin línea: %s"
          % (len(datos_l), len(datos_c), usadas_n, sum(len(v) for v in voces.values()), len(faltan), sobran))


if __name__ == "__main__":
    main()
