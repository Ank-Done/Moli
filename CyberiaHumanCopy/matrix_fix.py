# Simple test to create a working matrix query
def get_cobertura_matricial_simple(anio=None, agente=None):
    if not anio:
        anio = 2025
    
    # Simple working query that should actually return data
    query = f"""
    SELECT
        d.CRAZONSOCIAL AS RazonSocial,
        a.CNOMBREAGENTE AS Agente,
        ISNULL(SUM(CASE WHEN DATENAME(MONTH, m.CFECHA) = 'January' THEN 
            CASE
                WHEN p.CNOMBREPRODUCTO LIKE '%1 KG%' THEN m.CUNIDADES * 1
                WHEN p.CNOMBREPRODUCTO LIKE '%25 KG%' THEN m.CUNIDADES * 25
                WHEN p.CNOMBREPRODUCTO LIKE '%50 KG%' THEN m.CUNIDADES * 50
                ELSE m.CUNIDADES
            END 
        END), 0) AS Enero,
        ISNULL(SUM(CASE WHEN DATENAME(MONTH, m.CFECHA) = 'February' THEN 
            CASE
                WHEN p.CNOMBREPRODUCTO LIKE '%1 KG%' THEN m.CUNIDADES * 1
                WHEN p.CNOMBREPRODUCTO LIKE '%25 KG%' THEN m.CUNIDADES * 25
                WHEN p.CNOMBREPRODUCTO LIKE '%50 KG%' THEN m.CUNIDADES * 50
                ELSE m.CUNIDADES
            END 
        END), 0) AS Febrero,
        ISNULL(SUM(CASE WHEN DATENAME(MONTH, m.CFECHA) = 'March' THEN 
            CASE
                WHEN p.CNOMBREPRODUCTO LIKE '%1 KG%' THEN m.CUNIDADES * 1
                WHEN p.CNOMBREPRODUCTO LIKE '%25 KG%' THEN m.CUNIDADES * 25
                WHEN p.CNOMBREPRODUCTO LIKE '%50 KG%' THEN m.CUNIDADES * 50
                ELSE m.CUNIDADES
            END 
        END), 0) AS Marzo,
        0 AS Abril, 0 AS Mayo, 0 AS Junio, 0 AS Julio, 0 AS Agosto, 
        0 AS Septiembre, 0 AS Octubre, 0 AS Noviembre, 0 AS Diciembre,
        ISNULL(SUM(
            CASE
                WHEN p.CNOMBREPRODUCTO LIKE '%1 KG%' THEN m.CUNIDADES * 1
                WHEN p.CNOMBREPRODUCTO LIKE '%25 KG%' THEN m.CUNIDADES * 25
                WHEN p.CNOMBREPRODUCTO LIKE '%50 KG%' THEN m.CUNIDADES * 50
                ELSE m.CUNIDADES
            END
        ), 0) AS TotalAnual
    FROM 
        admMovimientos m
    JOIN admProductos p ON m.CIDPRODUCTO = p.CIDPRODUCTO
    JOIN admDocumentos d ON m.CIDDOCUMENTO = d.CIDDOCUMENTO
    JOIN admAgentes a ON d.CIDAGENTE = a.CIDAGENTE
    WHERE
        YEAR(m.CFECHA) = {anio}
        AND a.CNOMBREAGENTE IN (
            'MAYOREO / SPOT', 'MOLIENDAS', 'JAVIER ARROYO',
            'MOLIENDAS MAQ MDLZ', 'MDLZ P2', 'MOSTRADOR 1',
            'MOSTRADOR 2', 'MOSTRADOR 3'
        )
    GROUP BY d.CRAZONSOCIAL, a.CNOMBREAGENTE
    ORDER BY d.CRAZONSOCIAL
    """
    
    return query

print(get_cobertura_matricial_simple())