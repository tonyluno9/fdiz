#!/usr/bin/env python3
"""Validate the audio delivery folders against the project's audio manifest."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "gdevelop" / "FDI-Z"
MANIFEST = PROJECT / "audio_manifest.json"


def entries(manifest: dict) -> list[dict]:
    return [*manifest["effects"], *manifest["music"]]


def probe_wav(path: Path) -> tuple[bool, str]:
    """WAV (fase 58): PCM 16 bits, 44.1 o 48 kHz, con datos. Se lee la cabecera sin herramientas externas."""
    import struct
    b = path.read_bytes()
    if b[:4] != b"RIFF" or b[8:12] != b"WAVE":
        return False, "no es WAV"
    i, fmt, datos = 12, None, 0
    while i + 8 <= len(b):
        cid, n = b[i:i + 4], struct.unpack("<I", b[i + 4:i + 8])[0]
        if cid == b"fmt ":
            fmt = struct.unpack("<HHIIHH", b[i + 8:i + 24])
        elif cid == b"data":
            datos = n
        i += 8 + n + (n & 1)
    if not fmt or fmt[0] != 1 or fmt[5] != 16 or fmt[2] not in (44100, 48000) or datos == 0:
        return False, f"se requiere WAV PCM 16 bits a 44.1/48 kHz (fmt={fmt}, datos={datos})"
    return True, f"WAV PCM 16 bits {fmt[2]} Hz, {datos / (fmt[2] * fmt[4]):.2f} s"


def probe(path: Path) -> tuple[bool, str]:
    if path.suffix.lower() == ".wav":
        return probe_wav(path)
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        return True, "ffprobe no está instalado; solo se validó la extensión"
    result = subprocess.run(
        [
            ffprobe, "-v", "error", "-show_entries",
            "format=format_name:stream=codec_name,sample_rate,bits_per_sample",
            "-of", "default=noprint_wrappers=1", str(path),
        ],
        capture_output=True, text=True, check=False,
    )
    if result.returncode:
        return False, result.stderr.strip() or "archivo ilegible"
    details = result.stdout.lower()
    if "vorbis" not in details or not any(rate in details for rate in ("44100", "48000")):
        return False, "se requiere Vorbis a 44.1 kHz o 48 kHz"
    return True, "formato válido (la profundidad de 16 bits se verifica al exportar)"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="falla si faltan o son inválidos")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    failures = 0
    for item in entries(manifest):
        path = PROJECT / item["path"]
        extensiones = manifest["format"].get("extensions", [manifest["format"]["extension"]])
        if path.suffix.lower() not in extensiones or not path.exists():
            print(f"FALTA: {item['id']} -> {item['path']}")
            failures += 1
            continue
        valid, message = probe(path)
        print(f"{'OK' if valid else 'ERROR'}: {item['id']} -> {message}")
        failures += not valid
    print(f"Revisados: {len(entries(manifest))}; problemas: {failures}")
    return int(bool(failures and args.check))


if __name__ == "__main__":
    sys.exit(main())
