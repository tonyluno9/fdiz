#!/usr/bin/env python3
"""Fase 21: genera todos los efectos y músicas estilo SNES y los guarda en .ogg (ffmpeg libvorbis).
Cada sonido se puede regenerar solo:  python3 fase21_audio.py --solo SFX_MUNDO_MONEDA,MUSICA_MENU
Sin argumentos genera todos. El registro en el proyecto lo hace fase21_proyecto.py."""
import sys, os, json, subprocess, tempfile, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from snes_synth import *

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'FDI-Z'))
H = hz
rng = np.random.default_rng(7)


def sfx(dur):
    return Buf(dur)


# ---------------------------------------------------------------- EFECTOS
def convertido():
    b = sfx(1.0)
    b.add(0, tone(H('A3'), H('A1'), .9, 'p', .125, .6, vib=(14, .07), r=.2))
    b.add(0, noise(500, 150, .9, .5, 2))
    b.add(.45, tone(H('E4'), H('E2'), .5, 'p', .25, .35, vib=(20, .05)))
    return b.x

def lanzar():
    b = sfx(.4)
    b.add(0, noise(1200, 7000, .12, .6, 1)); b.add(.1, noise(7000, 1500, .22, .5, 4))
    b.add(0, tone(700, 250, .2, 'p', .25, .25))
    return b.x

def mordida():
    b = sfx(.35)
    for t in (0, .11): b.add(t, noise(3500, 900, .08, .8, 3))
    b.add(0, tone(320, 90, .16, 'p', .25, .5)); b.add(.11, tone(260, 70, .18, 'p', .25, .5))
    return b.x

def apagon():
    b = sfx(1.5)
    b.add(0, tone(1000, 38, 1.2, 'p', .5, .5, r=.3)); b.add(0, noise(800, 100, .25, .5, 5))
    b.add(.1, tone(60, 60, 1.0, 't', vol=.5, vib=(30, .03)))
    b.add(1.25, noise(6000, 3000, .03, .8, 3))
    return b.x

def escape():
    b = sfx(1.8)
    for k in range(4): b.add(k * .13, tone(H('E5') if k % 2 == 0 else H('B4'), None, .13, 'p', .5, .45))
    b.seq(.55, [H(n) for n in ('C5', 'E5', 'G5', 'C6', 'E6')], .09, wave='p', duty=.25, vol=.5)
    b.add(1.0, tone(H('G6'), None, .6, 'p', .125, .45, vib=(7, .01), r=.3))
    b.add(.55, tone(H('C3'), None, .9, 't', vol=.5))
    return b.x

def final_inicio():
    b = sfx(2.2)
    b.add(0, tone(H('D2'), None, 1.0, 't', vol=.8)); b.add(.5, tone(H('D#2'), None, 1.5, 't', vol=.8))
    b.add(0, noise(250, 100, 2.0, .35, 1.5))
    for n in ('D4', 'F4', 'A4'): b.add(.6, tone(H(n), None, 1.2, 'p', .125, .3, vib=(5, .008), r=.5))
    b.add(1.4, tone(H('A5'), None, .8, 't', vol=.6, r=.6)); b.add(1.4, tone(H('D#6'), None, .8, 't', vol=.35, r=.6))
    return b.x

def infestacion_sube():
    b = sfx(1.6)
    b.add(0, tone(H('A2'), H('C3'), .6, 'p', .5, .5, vib=(6, .01)))
    b.add(.55, tone(H('C3'), H('F#3'), .9, 'p', .5, .5, vib=(8, .015), r=.4))
    b.add(0, noise(220, 120, 1.4, .45, 1.2)); b.add(.55, tone(H('F#5'), H('F#5'), .8, 'p', .125, .2, r=.5))
    return b.x

def objetivo_cumplido():
    b = sfx(.9)
    b.seq(0, [H(n) for n in ('C5', 'E5', 'G5')], .09, wave='p', duty=.25, vol=.5)
    b.add(.27, tone(H('C6'), None, .4, 'p', .25, .5, r=.2)); b.add(.27, tone(H('C5'), None, .4, 't', vol=.5, r=.2))
    return b.x

def objetivo_nuevo():
    b = sfx(.6)
    b.add(0, tone(H('G5'), None, .08, 'p', .125, .45)); b.add(.09, tone(H('C6'), None, .4, 'p', .125, .5, r=.3))
    return b.x

def paso_objetivo():
    b = sfx(.25)
    b.add(0, tone(H('E6'), None, .05, 'p', .5, .4)); b.add(.06, tone(H('A6'), None, .1, 'p', .5, .4, r=.06))
    return b.x

def rescate_logrado():
    b = sfx(1.6)
    b.seq(0, [H(n) for n in ('G4', 'C5', 'E5', 'G5')], .1, wave='p', duty=.25, vol=.5)
    b.add(.45, tone(H('E5'), None, .12, 'p', .25, .5)); b.add(.58, tone(H('G5'), None, .12, 'p', .25, .5))
    b.add(.72, tone(H('C6'), None, .7, 'p', .25, .55, vib=(6, .008), r=.3))
    b.add(.72, tone(H('C3'), None, .7, 't', vol=.6)); b.add(.72, tone(H('E5'), None, .7, 'p', .125, .25, r=.3))
    return b.x

def victoria_sfx():
    b = sfx(1.7)
    for k, n in enumerate(('C5', 'C5', 'C5', 'E5')): b.add(k * .13, tone(H(n), None, .12, 'p', .5, .5))
    b.add(.55, tone(H('G5'), None, .15, 'p', .5, .5)); b.add(.7, tone(H('E5'), None, .1, 'p', .5, .45))
    b.add(.82, tone(H('G5'), None, .8, 'p', .25, .55, vib=(6, .01), r=.4))
    b.add(.82, tone(H('C6'), None, .8, 'p', .125, .3, r=.4)); b.add(.55, tone(H('C3'), None, 1.0, 't', vol=.6))
    return b.x

def jefe_invocar():
    b = sfx(2.0)
    b.add(0, noise(3000, 300, 1.2, .8, 3)); b.add(0, tone(H('A1'), None, 1.8, 't', vol=.9, r=.8))
    for k, n in enumerate(('E3', 'C3', 'A2')): b.add(.15 + k * .25, tone(H(n), None, .3, 'p', .125, .5, vib=(8, .01)))
    b.add(.9, tone(H('A4'), H('A3'), .9, 'p', .25, .3, vib=(10, .03), r=.5))
    return b.x

def comer():
    b = sfx(.5)
    for k in range(3):
        b.add(k * .13, noise(2800, 900, .06, .8, 3)); b.add(k * .13, tone(500 - k * 60, 200, .05, 't', vol=.5))
    return b.x

def bidon():
    b = sfx(.6)
    b.add(0, noise(2500, 400, .08, .7, 4))
    for f, v in ((H('A3'), .5), (H('E4') * 1.02, .4), (H('C#5'), .25)): b.add(0, tone(f, f * .97, .5, 'p', .25, v, r=.45))
    return b.x

def interruptor():
    b = sfx(.2)
    b.add(0, noise(5000, 3000, .012, .9, 3)); b.add(0, tone(1800, 900, .025, 'p', .5, .5))
    b.add(.07, noise(4000, 2000, .012, .8, 3)); b.add(.07, tone(1200, 600, .025, 'p', .5, .4))
    return b.x

def locker():
    b = sfx(.7)
    b.add(0, tone(300, 520, .3, 'p', .125, .28, vib=(25, .05), r=.1))
    b.add(.32, noise(2500, 300, .15, .8, 4)); b.add(.32, tone(H('A2'), H('A1'), .25, 't', vol=.7))
    b.add(.34, tone(H('D#5') * 1.01, None, .3, 'p', .25, .2, r=.25))
    return b.x

def maquina():
    b = sfx(.9)
    b.add(0, noise(1200, 200, .12, .8, 3)); b.add(0, tone(150, 60, .14, 't', vol=.9))
    b.add(.22, tone(H('B5'), None, .05, 'p', .5, .35)); b.add(.32, tone(H('E6'), None, .08, 'p', .5, .35))
    b.add(.5, noise(2000, 500, .1, .6, 4)); b.add(.5, tone(H('G2'), H('G1'), .15, 't', vol=.7))
    return b.x

def moneda():
    b = sfx(.5)
    b.add(0, tone(H('B5'), None, .06, 'p', .5, .5)); b.add(.06, tone(H('E6'), None, .3, 'p', .5, .5, r=.25))
    return b.x

def puerta_golpe():
    b = sfx(.35)
    b.add(0, tone(H('A2'), H('A1'), .25, 't', vol=1.0, r=.15)); b.add(0, noise(1800, 200, .12, .8, 4))
    return b.x

def puerta_abrir():
    b = sfx(.8)
    b.add(0, tone(170, 430, .5, 'p', .125, .3, vib=(32, .05), r=.12))
    b.add(.52, noise(4500, 2500, .015, .8, 3)); b.add(.52, tone(900, 500, .03, 'p', .5, .4))
    b.add(.56, tone(H('A2'), None, .1, 't', vol=.5))
    return b.x

# habilidades -------------------------------------------------------
def tony_hab():  # sartén chisporroteando + magia de comida
    b = sfx(1.0)
    x = noise(9000, 7000, .55, .6, .7)
    x *= (rng.uniform(0, 1, len(x)) > .45); b.add(0, x)
    b.seq(.5, [H(n) for n in ('D5', 'F#5', 'A5', 'D6')], .07, wave='p', duty=.25, vol=.45)
    return b.x

def tony_esp():  # banquete: subida de poder + explosión
    b = sfx(1.5)
    b.seq(0, [H(n) for n in ('C4', 'E4', 'G4', 'C5', 'E5', 'G5', 'C6')], .06, wave='p', duty=.25, vol=.5)
    b.add(.45, noise(4000, 400, .6, .9, 3)); b.add(.45, tone(H('C2'), None, .6, 't', vol=.9))
    for n in ('C5', 'E5', 'G5'): b.add(.5, tone(H(n), None, .8, 'p', .125, .25, r=.5))
    return b.x

def miranda_hab():  # mini canción de cuna (arrullo tipo Brahms, tema de dominio público)
    b = sfx(3.0); s = .24
    mel = [('E5', 1), ('E5', 1), ('G5', 2), ('E5', 1), ('E5', 1), ('G5', 2), ('E5', 1), ('G5', 1), ('C6', 1.5), ('B5', .5), ('A5', 1), ('A5', 1), ('G5', 2)]
    t = 0
    for n, d in mel:
        b.add(t, tone(H(n), None, d * s * .95, 'p', .5, .4, r=.05, vib=(5, .005)))
        t += d * s
    b.seq(0, [H('C3'), H('E3'), H('G3')] * 4, s, wave='t', vol=.45)
    return b.x

def miranda_esp():  # minigun
    b = sfx(1.5)
    for k in range(26):
        t = k * .045
        b.add(t, noise(5000, 1200, .035, .8, 3)); b.add(t, tone(220, 110, .04, 'p', .25, .5, r=.03))
    b.add(.0, tone(H('A1'), None, 1.2, 't', vol=.5))
    b.add(1.2, noise(3000, 300, .25, .5, 4))
    return b.x

def cesar_hab():  # hackeo / escaneo digital
    b = sfx(1.0)
    fr = [H(n) for n in ('C6', 'E6', 'D6', 'G6', 'E6', 'A6', 'F6', 'B6', 'G6', 'C7')]
    b.seq(0, fr, .045, wave='p', duty=.125, vol=.4)
    b.add(.5, tone(H('C7'), H('C5'), .3, 'p', .25, .2))
    b.add(.55, tone(H('G6'), None, .08, 'p', .5, .45)); b.add(.65, tone(H('C7'), None, .25, 'p', .5, .45, r=.2))
    return b.x

def cesar_esp():  # alarma / sobrecarga del sistema
    b = sfx(1.5)
    for k in range(8): b.add(k * .11, tone(H('A5') if k % 2 == 0 else H('E5'), None, .11, 'p', .5, .45))
    b.add(.5, noise(300, 9000, .6, .7, 0.5))
    b.add(.9, noise(5000, 300, .5, .9, 3)); b.add(.9, tone(H('A2'), H('A1'), .5, 't', vol=.9))
    return b.x

def alan_hab():  # caja registradora "ka-ching"
    b = sfx(.9)
    b.add(0, noise(4000, 2000, .02, .9, 3)); b.add(0, tone(300, 100, .06, 't', vol=.7))
    b.add(.1, tone(H('B6'), None, .5, 'p', .5, .35, r=.45)); b.add(.1, tone(H('E7'), None, .5, 'p', .125, .25, r=.45))
    for k in range(3): b.add(.4 + k * .07, tone(H('E6'), None, .05, 'p', .5, .35))
    return b.x

def alan_esp():  # explosión de monedas
    b = sfx(1.4)
    for k in range(14):
        n = ('B5', 'E6', 'G6', 'B6')[k % 4]
        b.add(k * .05, tone(H(n), None, .06, 'p', .5, .4)); b.add(k * .05 + .03, tone(H(n) * 1.5, None, .05, 'p', .25, .2))
    b.add(.7, noise(5000, 600, .5, .8, 3)); b.add(.7, tone(H('E2'), H('E1'), .4, 't', vol=.9))
    b.add(.75, tone(H('E7'), None, .5, 'p', .125, .3, r=.4))
    return b.x

def castillo_hab():  # glub glub gulp
    b = sfx(.8)
    for t, f in ((0, 330), (.16, 280), (.34, 230)): b.add(t, tone(f, f * .45, .13, 'p', .5, .5, vib=(20, .08), r=.05))
    b.add(.5, noise(900, 300, .08, .4, 3)); b.add(.52, tone(H('C3'), H('C2'), .1, 't', vol=.6))
    return b.x

def castillo_esp():  # poción curativa
    b = sfx(1.4)
    pent = [H(n) for n in ('C5', 'D5', 'E5', 'G5', 'A5', 'C6', 'D6', 'E6', 'G6')]
    b.seq(0, pent, .07, wave='p', duty=.25, vol=.4, vib=(9, .01))
    b.add(.63, tone(H('C7'), None, .7, 'p', .125, .3, vib=(8, .01), r=.5))
    b.add(.63, tone(H('E5'), None, .7, 't', vol=.5, r=.5)); b.add(.63, tone(H('G5'), None, .7, 't', vol=.4, r=.5))
    return b.x

def alessandro_hab():  # "ba-dum-tss"
    b = sfx(1.3)
    for t, f in ((0, 220), (.18, 150)):
        b.add(t, tone(f * 1.6, f * .55, .14, 't', vol=.9, r=.1)); b.add(t, noise(1800, 500, .05, .5, 4))
    b.add(.42, noise(11000, 7000, .75, .7, 5)); b.add(.42, tone(H('C#4'), None, .1, 't', vol=.4))
    b.add(.42, noise(3000, 2500, .08, .6, 4))
    return b.x

def alessandro_esp():  # tic-tac y freno de tiempo
    b = sfx(1.8)
    for k in range(6):
        hi = k % 2 == 0; b.add(k * .17, noise(7000, 4000, .018, .9, 3)); b.add(k * .17, tone(2000 if hi else 1400, 1000, .03, 'p', .5, .35))
    b.add(1.05, tone(H('A5'), H('A2'), .65, 'p', .25, .45, vib=(10, .04), r=.3))
    b.add(1.05, tone(H('E5'), H('E2'), .65, 'p', .125, .25, r=.3))
    return b.x

def gabo_hab():  # impulso de velocidad
    b = sfx(.7)
    for t in (0, .22): b.add(t, tone(180, 1800, .2, 'p', .25, .4, r=.05)); b.add(t, noise(1500, 9000, .2, .6, .8))
    return b.x

def gabo_esp():  # estampido sónico con eco de estela
    b = sfx(1.4)
    b.add(0, tone(H('F#2'), H('F#1'), .35, 't', vol=1)); b.add(0, noise(6000, 300, .4, .9, 3))
    for k, v in enumerate((.6, .4, .27, .17)): b.add(.3 + k * .16, tone(1500, 600, .1, 'p', .25, v * .6))
    return b.x

def carlos_hab():  # llaves y cerradura
    b = sfx(.9)
    for k, n in enumerate(('B6', 'G6', 'D7', 'A6', 'E7')): b.add(k * .045, tone(H(n), None, .06, 't', vol=.45))
    b.add(.3, noise(4500, 2500, .015, .9, 3)); b.add(.3, tone(1100, 500, .03, 'p', .5, .4))
    b.add(.42, noise(3000, 400, .08, .8, 4)); b.add(.42, tone(H('E2'), H('E1'), .18, 't', vol=.9))
    return b.x

def carlos_esp():  # armadura de tanque
    b = sfx(1.4)
    b.add(0, tone(90, 55, .35, 'p', .25, .6)); b.add(0, noise(2500, 300, .2, .8, 4))
    for f, v in ((H('A4'), .35), (H('E5') * 1.01, .3), (H('C#6') * .99, .2)): b.add(.02, tone(f, f * .985, .8, 'p', .25, v, r=.7))
    b.add(.5, tone(150, 320, .6, 't', vol=.7, r=.2))
    b.add(.55, tone(H('E4'), H('E5'), .5, 'p', .125, .3, r=.3))
    return b.x

SFX = {
 'SFX_COMBATE_CONVERTIDO': ('efectos/combate/convertido.ogg', convertido, 70),
 'SFX_COMBATE_LANZAR': ('efectos/combate/lanzar.ogg', lanzar, 60),
 'SFX_COMBATE_MORDIDA': ('efectos/combate/mordida.ogg', mordida, 65),
 'SFX_EVENTO_APAGON': ('efectos/eventos/apagon.ogg', apagon, 70),
 'SFX_EVENTO_ESCAPE': ('efectos/eventos/escape.ogg', escape, 75),
 'SFX_EVENTO_FINAL_INICIO': ('efectos/eventos/final_inicio.ogg', final_inicio, 75),
 'SFX_EVENTO_INFESTACION_SUBE': ('efectos/eventos/infestacion_sube.ogg', infestacion_sube, 70),
 'SFX_EVENTO_OBJETIVO_CUMPLIDO': ('efectos/eventos/objetivo_cumplido.ogg', objetivo_cumplido, 65),
 'SFX_EVENTO_OBJETIVO_NUEVO': ('efectos/eventos/objetivo_nuevo.ogg', objetivo_nuevo, 65),
 'SFX_EVENTO_PASO_OBJETIVO': ('efectos/eventos/paso_objetivo.ogg', paso_objetivo, 55),
 'SFX_EVENTO_RESCATE_LOGRADO': ('efectos/eventos/rescate_logrado.ogg', rescate_logrado, 70),
 'SFX_EVENTO_VICTORIA': ('efectos/eventos/victoria.ogg', victoria_sfx, 65),
 'SFX_INTERFAZ_JEFE_INVOCAR': ('efectos/interfaz/jefe_invocar.ogg', jefe_invocar, 75),
 'SFX_MOVIMIENTO_COMER': ('efectos/movimiento/comer.ogg', comer, 55),
 'SFX_MUNDO_BIDON': ('efectos/mundo/bidon.ogg', bidon, 60),
 'SFX_MUNDO_INTERRUPTOR': ('efectos/mundo/interruptor.ogg', interruptor, 55),
 'SFX_MUNDO_LOCKER': ('efectos/mundo/locker.ogg', locker, 60),
 'SFX_MUNDO_MAQUINA': ('efectos/mundo/maquina.ogg', maquina, 60),
 'SFX_MUNDO_MONEDA': ('efectos/mundo/moneda.ogg', moneda, 55),
 'SFX_MUNDO_PUERTA_GOLPE': ('efectos/mundo/puerta_golpe.ogg', puerta_golpe, 60),
 'SFX_MUNDO_PUERTA_ABRIR': ('efectos/mundo/puerta_abrir.ogg', puerta_abrir, 60),
 'SFX_HABILIDAD_TONY': ('efectos/habilidades/tony_habilidad.ogg', tony_hab, 70),
 'SFX_HABILIDAD_TONY_ESPECIAL': ('efectos/habilidades/tony_especial.ogg', tony_esp, 75),
 'SFX_HABILIDAD_MIRANDA': ('efectos/habilidades/miranda_habilidad.ogg', miranda_hab, 65),
 'SFX_HABILIDAD_MIRANDA_ESPECIAL': ('efectos/habilidades/miranda_especial.ogg', miranda_esp, 70),
 'SFX_HABILIDAD_CESAR': ('efectos/habilidades/cesar_habilidad.ogg', cesar_hab, 65),
 'SFX_HABILIDAD_CESAR_ESPECIAL': ('efectos/habilidades/cesar_especial.ogg', cesar_esp, 70),
 'SFX_HABILIDAD_ALAN': ('efectos/habilidades/alan_habilidad.ogg', alan_hab, 65),
 'SFX_HABILIDAD_ALAN_ESPECIAL': ('efectos/habilidades/alan_especial.ogg', alan_esp, 70),
 'SFX_HABILIDAD_CASTILLO': ('efectos/habilidades/castillo_habilidad.ogg', castillo_hab, 65),
 'SFX_HABILIDAD_CASTILLO_ESPECIAL': ('efectos/habilidades/castillo_especial.ogg', castillo_esp, 70),
 'SFX_HABILIDAD_ALESSANDRO': ('efectos/habilidades/alessandro_habilidad.ogg', alessandro_hab, 70),
 'SFX_HABILIDAD_ALESSANDRO_ESPECIAL': ('efectos/habilidades/alessandro_especial.ogg', alessandro_esp, 70),
 'SFX_HABILIDAD_GABO': ('efectos/habilidades/gabo_habilidad.ogg', gabo_hab, 65),
 'SFX_HABILIDAD_GABO_ESPECIAL': ('efectos/habilidades/gabo_especial.ogg', gabo_esp, 70),
 'SFX_HABILIDAD_CARLOS': ('efectos/habilidades/carlos_habilidad.ogg', carlos_hab, 65),
 'SFX_HABILIDAD_CARLOS_ESPECIAL': ('efectos/habilidades/carlos_especial.ogg', carlos_esp, 70),
}

# ---------------------------------------------------------------- MÚSICA
def D16(k, s, h): return dict(k=k, s=s, h=h)
def ch(*xs): return [(r, t.split()) for r, t in xs]

def m_menu():
    c = ch(('A2', 'A3 C4 E4'), ('F2', 'F3 A3 C4'), ('C3', 'C4 E4 G4'), ('G2', 'G3 B3 D4'),
           ('A2', 'A3 C4 E4'), ('F2', 'F3 A3 C4'), ('E2', 'E3 G#3 B3'), ('A2', 'A3 C4 E4'))
    lead = ("E5:1.5 C5:.5 A4:1 C5:1 C5:1.5 A4:.5 F4:1 A4:1 G4:1 C5:1 E5:2 D5:1.5 B4:.5 G4:2 "
            "E5:1.5 C5:.5 A4:1 E5:1 F5:1.5 C5:.5 A4:2 E5:1 G#4:1 B4:1 E5:1 A4:4")
    return music(96, c, lead, 'p', .25, .45, 'q', arp=[0, 1, 2, 1], arp_step=.5,
                 drums=D16('x...............', '................', '..x...x...x...x.'))

def m_p1():
    c = ch(('D2', 'D3 F3 A3'), ('D2', 'D3 F3 A3'), ('Bb2', 'Bb3 D4 F4'), ('A2', 'A3 C#4 E4'),
           ('D2', 'D3 F3 A3'), ('G2', 'G3 Bb3 D4'), ('A2', 'A3 C#4 E4'), ('D2', 'D3 F3 A3'))
    lead = ("A4:2 R:1 D5:1 F5:1.5 E5:.5 D5:2 D5:2 C5:1 Bb4:1 C#5:3 R:1 "
            "A4:2 R:1 D5:1 G5:1.5 F5:.5 D5:2 E5:1 C#5:1 A4:2 D5:4")
    return music(108, c, lead, 'p', .125, .4, 'q', arp=[0, 2, 1, 2], arp_step=.5, arp_vol=.18,
                 drums=D16('x.......x.......', '................', 'x...x...x...x...'))

def m_p2():
    c = ch(('E2', 'E3 G3 B3'), ('C2', 'C3 E3 G3'), ('D2', 'D3 F#3 A3'), ('E2', 'E3 G3 B3'),
           ('E2', 'E3 G3 B3'), ('C2', 'C3 E3 G3'), ('B1', 'B2 D#3 F#3'), ('E2', 'E3 G3 B3'))
    lead = ("B4:1 E5:1 G5:1 F#5:1 E5:2 G5:1 E5:1 F#5:1 A5:1 F#5:1 D5:1 E5:3 R:1 "
            "B4:1 E5:1 G5:1 B5:1 A5:1 G5:1 E5:1 C5:1 D#5:1 F#5:1 B5:2 E5:4")
    return music(132, c, lead, 'p', .25, .45, 'e', arp=[0, 1, 2, 1], arp_step=.25, arp_vol=.16,
                 drums=D16('x.......x..x....', '....x.......x...', 'x.x.x.x.x.x.x.x.'))

def m_p3():
    c = ch(('C#2', 'C#3 E3 G#3'), ('A1', 'A2 C#3 E3'), ('B1', 'B2 D#3 F#3'), ('G#1', 'G#2 C3 D#3'),
           ('C#2', 'C#3 E3 G#3'), ('A1', 'A2 C#3 E3'), ('F#2', 'F#3 A3 C#4'), ('G#1', 'G#2 C3 D#3'))
    lead = ("G#5:.5 C#6:.5 B5:.5 G#5:.5 E5:1 G#5:1 A5:.5 C#6:.5 B5:.5 A5:.5 E5:2 B5:.5 D#6:.5 F#6:.5 D#6:.5 B5:2 "
            "G#5:1 C6:1 D#6:2 G#5:.5 C#6:.5 B5:.5 G#5:.5 E5:1 G#5:1 A5:.5 C#6:.5 E6:.5 C#6:.5 A5:2 "
            "F#5:.5 A5:.5 C#6:.5 A5:.5 F#6:2 G#5:.5 C6:.5 D#6:.5 C6:.5 G#6:2")
    return music(156, c, lead, 'p', .5, .4, 'e', arp=[0, 2, 1, 2], arp_step=.25, arp_vol=.15,
                 drums=D16('x..xx..xx..xx...', '....x.......x.x.', 'xxxxxxxxxxxxxxxx'))

def m_final():
    c = ch(('A2', 'A3 C4 E4'), ('F2', 'F3 A3 C4'), ('C3', 'C4 E4 G4'), ('G2', 'G3 B3 D4'),
           ('A2', 'A3 C4 E4'), ('F2', 'F3 A3 C4'), ('G2', 'G3 B3 D4'), ('E2', 'E3 G#3 B3'))
    lead = ("A4:1 C5:1 E5:1 A5:1 A5:1.5 G5:.5 F5:1 C5:1 E5:1 G5:1 C6:2 D6:1 B5:1 G5:1 D5:1 "
            "A4:1 C5:1 E5:1 A5:1 C6:1.5 A5:.5 F5:2 G5:1 B5:1 D6:1 B5:1 E5:1 G#5:1 B5:1 E6:1")
    return music(168, c, lead, 'p', .5, .45, 'e', arp=[0, 1, 2, 1], arp_step=.25, arp_vol=.15, vib=(6, .008),
                 drums=D16('x...x...x...x.x.', '....x.......x...', 'x.x.x.x.x.x.x.xx'))

def m_derrota():
    c = ch(('A2', 'A3 C4 E4'), ('F2', 'F3 A3 C4'), ('D2', 'D3 F3 A3'), ('E2', 'E3 G#3 B3'))
    lead = "C5:2 B4:1 A4:1 A4:2 G4:1 F4:1 F4:2 E4:1 D4:1 E4:4"
    return music(88, c, lead, 'p', .5, .4, 'q', arp=[0, 1, 2], arp_step=1, arp_vol=.12, loop=False, tail=2.0)

def m_victoria():
    c = ch(('C3', 'C4 E4 G4'), ('F2', 'F3 A3 C4'), ('G2', 'G3 B3 D4'), ('C3', 'C4 E4 G4'))
    lead = "G4:.5 C5:.5 E5:.5 G5:.5 C6:2 A5:1 F5:1 A5:2 G5:1 D5:1 B4:1 D5:1 C5:1 E5:1 G5:1 C6:1"
    return music(132, c, lead, 'p', .25, .5, 'q', arp=[0, 1, 2, 1], arp_step=.25, arp_vol=.15, loop=False, tail=2.0,
                 drums=D16('x...x...x...x...', '....x.......x...', 'x.x.x.x.x.x.x.x.'))

MUS = {
 'MUSICA_MENU': ('musica/menu.ogg', m_menu, 45, True),
 'MUSICA_PARTIDA_1': ('musica/partida_1.ogg', m_p1, 45, True),
 'MUSICA_PARTIDA_2': ('musica/partida_2.ogg', m_p2, 45, True),
 'MUSICA_PARTIDA_3': ('musica/partida_3.ogg', m_p3, 45, True),
 'MUSICA_FINAL_AGUANTEN': ('musica/final_aguanten.ogg', m_final, 50, True),
 'MUSICA_VICTORIA': ('musica/victoria.ogg', m_victoria, 50, False),
 'MUSICA_DERROTA': ('musica/derrota.ogg', m_derrota, 50, False),
}


def render(ident):
    if ident in SFX:
        path, fn, _ = SFX[ident]; x = master(fn(), peak=.9, eco=True, fade=.01)
    else:
        path, fn, _, _ = MUS[ident]; x = fn()
    out = os.path.join(ROOT, path); os.makedirs(os.path.dirname(out), exist_ok=True)
    tmp = tempfile.mktemp(suffix='.wav'); write_wav(tmp, x)
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', tmp, '-ar', '44100', '-ac', '1', '-c:a', 'libvorbis', '-q:a', '5', out], check=True)
    os.remove(tmp)
    return path, len(x) / SR


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--solo'); a = ap.parse_args()
    ids = a.solo.split(',') if a.solo else list(SFX) + list(MUS)
    info = {}
    for i in ids:
        p, d = render(i); info[i] = round(d, 2); print(f'{i:38s} {d:5.2f}s  {p}')
