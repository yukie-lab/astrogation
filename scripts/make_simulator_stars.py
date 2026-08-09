#!/usr/bin/env python
"""simulator/stars.js を生成する(Phase 4 改訂 (1))。

出典: Yale Bright Star Catalogue, 5th Revised Ed.
      (Hoffleit & Warren 1991), VizieR V/50 `catalog.gz`。
抽出: RA/Dec (J2000)・Vmag・B−V、V ≤ 6.5 のみ。
実行時のシミュレータは生成物 stars.js を static 読込するだけで、
ネットワークにも本スクリプトにも依存しない。

使い方:
    python scripts/make_simulator_stars.py <catalog.gz へのパス>
    (省略時は VizieR からダウンロードを試みる)

V/50 のバイト配置(1 始まり):
    76-77 RAh, 78-79 RAm, 80-83 RAs, 84 DE 符号, 85-86 DEd,
    87-88 DEm, 89-90 DEs, 103-107 Vmag, 110-114 B-V
RA/Dec 欠損(新星等の非恒星エントリ)と Vmag 欠損は捨てる。
B−V 欠損は 0.30(白色寄りの中庸値、表示専用)で補う。
"""
import gzip
import io
import sys
import urllib.request
from pathlib import Path

URL = "https://cdsarc.cds.unistra.fr/ftp/V/50/catalog.gz"
VMAG_LIMIT = 6.5
BV_DEFAULT = 0.30

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "simulator" / "stars.js"


def load_bytes(argv):
    if len(argv) > 1:
        return Path(argv[1]).read_bytes()
    print(f"downloading {URL} ...")
    with urllib.request.urlopen(URL, timeout=60) as r:
        return r.read()


def parse(raw):
    stars = []
    skipped_pos, skipped_mag = 0, 0
    for line in io.TextIOWrapper(gzip.open(io.BytesIO(raw)), encoding="ascii",
                                 errors="replace"):
        line = line.rstrip("\n")
        if len(line) < 107:
            line = line.ljust(115)
        try:
            rah = int(line[75:77]); ram = int(line[77:79])
            ras = float(line[79:83])
            sgn = -1.0 if line[83] == "-" else 1.0
            ded = int(line[84:86]); dem = int(line[86:88]); des = int(line[88:90])
        except ValueError:
            skipped_pos += 1
            continue
        try:
            vmag = float(line[102:107])
        except ValueError:
            skipped_mag += 1
            continue
        if vmag > VMAG_LIMIT:
            continue
        try:
            bv = float(line[109:114])
        except ValueError:
            bv = BV_DEFAULT
        ra_deg = 15.0 * (rah + ram / 60.0 + ras / 3600.0)
        dec_deg = sgn * (ded + dem / 60.0 + des / 3600.0)
        stars.append((round(ra_deg, 4), round(dec_deg, 4),
                      round(vmag, 2), round(bv, 2)))
    return stars, skipped_pos, skipped_mag


def main(argv):
    stars, skipped_pos, skipped_mag = parse(load_bytes(argv))
    rows = ",\n".join(
        "[" + ",".join(repr(v) for v in s) + "]" for s in stars)
    OUT.write_text(f"""/*
 * stars.js — 生成物。手動編集禁止(scripts/make_simulator_stars.py が生成)。
 * 出典: Yale Bright Star Catalogue, 5th Revised Ed.
 *       (Hoffleit & Warren 1991), VizieR V/50。V <= {VMAG_LIMIT}、N = {len(stars)}。
 * 列: [RA_deg (J2000), Dec_deg, Vmag, B-V](B-V 欠損は {BV_DEFAULT} で補完)
 * 全星を無限遠(視差ゼロ)として扱う — README の境界宣言参照。
 */
"use strict";
const STARS = [
{rows}
];
if (typeof module !== "undefined" && module.exports) module.exports = STARS;
if (typeof window !== "undefined") window.STARS = STARS;
""", encoding="utf-8")
    print(f"wrote {OUT}  N={len(stars)}  "
          f"(位置欠損 {skipped_pos}, Vmag 欠損 {skipped_mag})")


if __name__ == "__main__":
    main(sys.argv)
