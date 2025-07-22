#!/usr/bin/env python3
"""
Obtener SOLO los productos que realmente aparecen en movimientos
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from config.database import DatabaseConfig

def get_productos_reales():
    db = DatabaseConfig()
    
    # Tu consulta EXACTA para productos que realmente tienen movimientos
    query = """
    SELECT DISTINCT
        p.CCODIGOPRODUCTO AS CodigoProducto,
        p.CNOMBREPRODUCTO AS NombreProducto
    FROM 
        admMovimientos m
    JOIN 
        admProductos p ON p.CIDPRODUCTO = m.CIDPRODUCTO
    WHERE
        p.CCODIGOPRODUCTO IN (
        ('MESCO25'),
        ('MESCO30'),
        ('MESPU07'),
        ('MREGR26'),
        ('MREGR30'),
        ('MREP613'),
        ('MREP614'),
        ('MREP620'),
        ('PAL0007'),
        ('PAL0008'),
        ('PAL0009'),
        ('PBSMZ04'),
        ('PBSMZ05'),
        ('PBSMZ06'),
        ('PBSMZ08'),
        ('PBSMZ09'),
        ('PBSMZ11'),
        ('PBSMZ14'),
        ('PCAGF02'),
        ('PCAGF03'),
        ('PCAGF04'),
        ('PCFAI03'),
        ('PCFAM03'),
        ('PCFAZ03'),
        ('PCFMO03'),
        ('PCFMO05'),
        ('PCFNA03'),
        ('PCFNE03'),
        ('PCFRS03'),
        ('PCFVA03'),
        ('PCFVE03'),
        ('PCFVI03'),
        ('PCFVL03'),
        ('PCGAI03'),
        ('PCGAM03'),
        ('PCGAZ03'),
        ('PCGMO03'),
        ('PCGNA03'),
        ('PCGNE03'),
        ('PCGRF03'),
        ('PCGRO03'),
        ('PCGRS03'),
        ('PCGVA03'),
        ('PCGVE03'),
        ('PCGVI03'),
        ('PCGVL01'),
        ('PCGVL03'),
        ('PESCO25'),
        ('PESEM17'),
        ('PESGR07'),
        ('PESGR10'),
        ('PESGR21'),
        ('PESGR22'),
        ('PESP607'),
        ('PESP610'),
        ('PG3EN01'),
        ('PG3EN08'),
        ('PM5EN04'),
        ('PREBS07'),
        ('PRECE01'),
        ('PRECE02'),
        ('PRECS01'),
        ('PREEF26'),
        ('PREEM17'),
        ('PREFS11'),
        ('PREFS12'),
        ('PREGG12'),
        ('PREGR07'),
        ('PREGR10'),
        ('PREGR23'),
        ('PREGR24'),
        ('PREGR25'),
        ('PRELG02'),
        ('PREMC11'),
        ('PREO407'),
        ('PREP107'),
        ('PREP108'),
        ('PREP112'),
        ('PREP113'),
        ('PREP607'),
        ('PBAR002'),
        ('PCMNE01'),
        ('PREP111'),
        ('PCFVV03'),
        ('MAREGR11'),
        ('RMREP614'),
        ('PESEM11'),
        ('MREP621'),
        ('MREP622'),
        ('RREGR10'),
        ('RPREP607'),
        ('CSER026'),
        ('PREGR27'),
        ('PREGR29'),
        ('PBSMZ22'),
        ('RMREP620'),
        ('CSER208'),
        ('PESEM12'),
        ('AREGR10'),
        ('AE1GR01'),
        ('AR1GR10'),
        ('ABEGR01'),
        ('PBAR003'),
        ('MAM5ESCNI'),
        ('PESGG12'),
        ('RPREBS07'),
        ('RPBSMZ08'),
        ('PRECCN2'),
        ('MGSMDLZ'),
        ('ZTAR003'),
        ('ZTAR004'),
        ('ZTAR005'),
        ('CSER209'),
        ('MGL01'),
        ('PREEF27'),
        ('FEUR10'),
        ('JS109'),
        ('EX45'),
        ('SEÑ1600'),
        ('PCGEAZ1'),
        ('MREGR23'),
        ('ZEMP006'),
        ('MAREGR15'),
        ('PESCO40'),
        ('PPIL001'),
        ('ZBES010'),
        ('ZBES005'),
        ('ZBESM907'),
        ('ZBRE010'),
        ('ZBRE005'),
        ('PPIL002'),
        ('PPIL003'),
        ('ZSAC004'),
        ('MAM5CESGR2'),
        ('RSERMAQ04'),
        ('RSERMAQ05'),
        ('RSERMAQ06'),
        ('PILCJA01'),
        ('PILCJA02'),
        ('FLSER001'),
        ('LBACE01'),
        ('ZEDU007'))
    ORDER BY p.CCODIGOPRODUCTO
    """
    
    df = db.execute_query(query)
    print(f"=== PRODUCTOS REALES CON MOVIMIENTOS ===")
    print(f"Total productos encontrados: {len(df)}")
    
    # Generar lista para código Python
    productos_lista = []
    for _, row in df.iterrows():
        codigo = row['CodigoProducto'].strip()
        productos_lista.append(f"'{codigo}'")
        print(f"  {codigo} - {row['NombreProducto'].strip()}")
    
    print(f"\n=== LISTA PARA CÓDIGO PYTHON ===")
    print("PRODUCTOS_VALIDOS = [")
    for i in range(0, len(productos_lista), 10):
        chunk = productos_lista[i:i+10]
        print("    " + ", ".join(chunk) + ",")
    print("]")

if __name__ == "__main__":
    get_productos_reales()