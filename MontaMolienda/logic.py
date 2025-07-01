from datetime import timedelta

# Parámetros reales del cargador
VOLTAJE = 85.6  # V
CORRIENTE = 200  # A
POTENCIA_CARGADOR = VOLTAJE * CORRIENTE / 1000  # 17.12 kW
EFICIENCIA = 0.90  # 90% de eficiencia (más realista)

# Capacidades REALES de batería (Ah) - valores ajustados
CAPACIDADES = {
    "Hangcha35": 120,   # 120 Ah (valor realista para montacargas)
    "G2Series25": 100,  # 100 Ah
    "KBPower": 110      # 110 Ah
}

def calcular_tiempo_restante(tipo, porcentaje_actual):
    if tipo not in CAPACIDADES:
        return timedelta(0)
    
    # Calcular capacidad total en Wh
    capacidad_total = CAPACIDADES[tipo] * VOLTAJE  # Ah * V = Wh
    
    capacidad_actual = (porcentaje_actual / 100) * capacidad_total
    capacidad_objetivo = 0.8 * capacidad_total
    capacidad_restante = max(0, capacidad_objetivo - capacidad_actual)
    
    # Tiempo en horas = capacidad restante (Wh) / (potencia cargador (W) * eficiencia)
    horas = capacidad_restante / (POTENCIA_CARGADOR * 1000 * EFICIENCIA)
    return timedelta(hours=horas)

def calcular_incremento_porcentaje(tipo, segundos_transcurridos):
    """Calcula cuánto porcentaje debería aumentar la batería en el tiempo transcurrido"""
    if tipo not in CAPACIDADES:
        return 0
    
    # Capacidad total en Wh
    capacidad_total = CAPACIDADES[tipo] * VOLTAJE
    
    # Energía suministrada en Wh
    energia = (POTENCIA_CARGADOR * 1000 * EFICIENCIA) * (segundos_transcurridos / 3600)
    
    # Porcentaje de incremento
    incremento = (energia / capacidad_total) * 100
    
    # Máximo 80% de carga
    return min(incremento, 80)