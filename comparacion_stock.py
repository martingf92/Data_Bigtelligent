#!/usr/bin/env python3
"""
Comparación de dos CSVs de stock (vista original vs nueva)

Uso:
    python comparacion_stock.py "v_Item Availability View.csv" "v_Item Availability View_V2.csv" \
        --outdir ./salida --prefix resultado --keys ItemNo LocationCode

Salidas (en --outdir):
    - <prefix>_coinciden_completamente.csv
    - <prefix>_difieren.csv
    - <prefix>_solo_en_v2.csv
    - <prefix>_solo_en_v1.csv
Además imprime un resumen por consola.
"""
import argparse
import os
import sys
from typing import List
import pandas as pd

def parse_args():
    p = argparse.ArgumentParser(description="Compara dos CSVs por claves compuestas y genera 4 CSVs de diferencias.")
    p.add_argument("csv_v1", help="Ruta al CSV original (v1).")
    p.add_argument("csv_v2", help="Ruta al CSV nuevo (v2).")
    p.add_argument("--keys", nargs="+", default=["ItemNo", "LocationCode"], help="Columnas clave (clave compuesta).")
    p.add_argument("--outdir", default=".", help="Directorio de salida (por defecto, el actual).")
    p.add_argument("--prefix", default="", help="Prefijo para los archivos de salida (opcional).")
    # p.add_argument("--float-tol", type=float, default=None, help="Tolerancia para comparar floats (opcional).")
    return p.parse_args()

def ensure_outdir(path: str):
    os.makedirs(path, exist_ok=True)

def validate_columns(df1: pd.DataFrame, df2: pd.DataFrame):
    if set(df1.columns) != set(df2.columns):
        missing_in_v2 = [c for c in df1.columns if c not in df2.columns]
        missing_in_v1 = [c for c in df2.columns if c not in df1.columns]
        raise ValueError(
            "Las columnas de ambos archivos no coinciden.\n"
            f"Faltan en V2: {missing_in_v2}\n"
            f"Faltan en V1: {missing_in_v1}"
        )

def main():
    args = parse_args()
    keys: List[str] = args.keys
    outdir = args.outdir
    prefix = (args.prefix + "_") if args.prefix else ""

    # Cargar CSVs
    try:
        df_v1 = pd.read_csv(args.csv_v1)
        df_v2 = pd.read_csv(args.csv_v2)
    except Exception as e:
        print(f"[ERROR] No se pudieron leer los CSVs: {e}", file=sys.stderr)
        sys.exit(1)

    # Validaciones básicas
    for k in keys:
        if k not in df_v1.columns or k not in df_v2.columns:
            print(f"[ERROR] La clave '{k}' no existe en ambos CSVs.", file=sys.stderr)
            sys.exit(1)

    validate_columns(df_v1, df_v2)

    # Asegurar tipos consistentes en claves (por seguridad)
    for k in keys:
        df_v1[k] = df_v1[k].astype(str)
        df_v2[k] = df_v2[k].astype(str)

    # Merge interno para claves que aparecen en ambos
    merged = df_v1.merge(df_v2, on=keys, how="inner", suffixes=("_v1", "_v2"))
    cols_to_compare = [c for c in df_v1.columns if c not in keys]

    # Comparación fila a fila (todas las columnas excepto claves deben coincidir)
    eq_matrix = merged[[c + "_v1" for c in cols_to_compare]].eq(merged[[c + "_v2" for c in cols_to_compare]].values)
    identicas_mask = eq_matrix.all(axis=1)

    # 1) Coinciden completamente (reconstruir con columnas originales)
    identicas = merged.loc[identicas_mask, keys + [c + "_v1" for c in cols_to_compare]].copy()
    identicas.columns = df_v1.columns

    # 2) Difieren (mismas claves, alguna columna distinta). Incluimos columna 'diff_cols' con las que difieren.
    diferentes = merged.loc[~identicas_mask, keys + [c + "_v1" for c in cols_to_compare] + [c + "_v2" for c in cols_to_compare]].copy()
    if not diferentes.empty:
        diff_cols_list = []
        # Preparar nombres paralelos
        left_cols = [c + "_v1" for c in cols_to_compare]
        right_cols = [c + "_v2" for c in cols_to_compare]
        diffs = merged.loc[~identicas_mask, left_cols].ne(merged.loc[~identicas_mask, right_cols].values)
        for i, row in diffs.iterrows():
            diff_cols_list.append(",".join([cols_to_compare[j] for j, val in enumerate(row.values) if val]))
        diferentes.insert(len(keys), "diff_cols", diff_cols_list)

    # 3) Solo en V2 (aparecen en V2 y no en V1)
    solo_v2 = df_v2.merge(df_v1[keys], on=keys, how="left", indicator=True)
    solo_v2 = solo_v2[solo_v2["_merge"] == "left_only"].drop(columns="_merge")

    # 4) Solo en V1 (aparecen en V1 y no en V2)
    solo_v1 = df_v1.merge(df_v2[keys], on=keys, how="left", indicator=True)
    solo_v1 = solo_v1[solo_v1["_merge"] == "left_only"].drop(columns="_merge")

    # Salidas
    ensure_outdir(outdir)
    path_identicas = os.path.join(outdir, f"{prefix}coinciden_completamente.csv")
    path_difieren = os.path.join(outdir, f"{prefix}difieren.csv")
    path_solo_v2  = os.path.join(outdir, f"{prefix}solo_en_v2.csv")
    path_solo_v1  = os.path.join(outdir, f"{prefix}solo_en_v1.csv")

    identicas.to_csv(path_identicas, index=False)
    diferentes.to_csv(path_difieren, index=False)
    solo_v2.to_csv(path_solo_v2, index=False)
    solo_v1.to_csv(path_solo_v1, index=False)

    # Resumen
    print("=== Resumen de comparación ===")
    print(f"Filas idénticas: {len(identicas)}")
    print(f"Filas con diferencias (mismas claves): {len(diferentes)}")
    print(f"Solo en V2: {len(solo_v2)}")
    print(f"Solo en V1: {len(solo_v1)}")
    print("\nArchivos generados:")
    print(f"- {path_identicas}")
    print(f"- {path_difieren}")
    print(f"- {path_solo_v2}")
    print(f"- {path_solo_v1}")

if __name__ == "__main__":
    main()
