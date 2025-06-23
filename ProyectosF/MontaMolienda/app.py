from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from db import get_db_connection
from logic import calcular_tiempo_restante, calcular_incremento_porcentaje
import time
import threading
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Variables de estado
estado_actual = {}
tiempo_ultima_actualizacion = {}

def actualizar_montacargas():
    global estado_actual
    while True:
        try:
            conn = get_db_connection()
            if conn:
                cur = conn.cursor()
                cur.execute("SELECT IDMontacarga, PorcentajeBateria, EnCarga, EnUso, Tipo FROM montacargas")
                montacargas = cur.fetchall()
                now = time.time()
                
                for m in montacargas:
                    id_m, porcentaje, en_carga, en_uso, tipo = m
                    
                    # Actualizar estado global
                    estado_actual[id_m] = {
                        "porcentaje": porcentaje,
                        "en_carga": bool(en_carga),
                        "en_uso": bool(en_uso),
                        "tipo": tipo
                    }
                    
                    # Actualizar porcentaje si está cargando
                    if en_carga and not en_uso and porcentaje < 80:
                        if id_m in tiempo_ultima_actualizacion:
                            segundos_transcurridos = now - tiempo_ultima_actualizacion[id_m]
                            incremento = calcular_incremento_porcentaje(tipo, segundos_transcurridos)
                            
                            if incremento > 0.5:  # Actualizar solo si hay cambio significativo
                                nuevo_porcentaje = min(80, porcentaje + incremento)
                                cur.execute("UPDATE montacargas SET PorcentajeBateria = ? WHERE IDMontacarga = ?", 
                                           (round(nuevo_porcentaje, 1), id_m))
                                logger.info(f"Montacarga {id_m} actualizado a {nuevo_porcentaje}%")
                        
                        # Actualizar tiempo de referencia
                        tiempo_ultima_actualizacion[id_m] = now
                    elif id_m in tiempo_ultima_actualizacion:
                        # Si ya no está cargando, eliminar del seguimiento
                        del tiempo_ultima_actualizacion[id_m]
                
                conn.commit()
                conn.close()
        except Exception as e:
            logger.error(f"Error en actualización: {e}")
        finally:
            time.sleep(5)  # Verificar cada 5 segundos

@app.on_event("startup")
def start_background_task():
    threading.Thread(target=actualizar_montacargas, daemon=True).start()

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("status.html", {"request": request})

@app.get("/api/montacargas")
async def obtener_estado():
    ahora = time.time()
    data = []
    
    for id_m, datos in estado_actual.items():
        en_uso = datos["en_uso"]
        en_carga = datos["en_carga"]
        porcentaje = datos["porcentaje"]
        tipo = datos["tipo"]
        
        if en_uso:
            item = {
                "id": id_m,
                "porcentaje": None,
                "en_uso": True,
                "en_carga": False,
                "tipo": tipo,
                "tiempo_restante": "Desconocido",
                "estimado_fin": 0,
                "notificar": False
            }
        elif en_carga:
            tiempo = calcular_tiempo_restante(tipo, porcentaje)
            tiempo_restante = str(tiempo).split(".")[0] if tiempo.total_seconds() > 0 else "Completo"
            estimado_fin = ahora + tiempo.total_seconds()
            
            item = {
                "id": id_m,
                "porcentaje": porcentaje,
                "en_uso": False,
                "en_carga": True,
                "tipo": tipo,
                "tiempo_restante": tiempo_restante,
                "estimado_fin": int(estimado_fin),
                "notificar": porcentaje >= 80
            }
        else:
            item = {
                "id": id_m,
                "porcentaje": porcentaje,
                "en_uso": False,
                "en_carga": False,
                "tipo": tipo,
                "tiempo_restante": "N/A",
                "estimado_fin": 0,
                "notificar": False
            }
        
        data.append(item)
    
    return JSONResponse(content=data)

@app.post("/api/toggle")
async def toggle_estado(id: int = Form(...), campo: str = Form(...), nuevo_porcentaje: int = Form(None)):
    try:
        conn = get_db_connection()
        if conn:
            cur = conn.cursor()
            
            # Verificar estado actual
            cur.execute("SELECT EnUso, EnCarga, Tipo FROM montacargas WHERE IDMontacarga = ?", (id,))
            row = cur.fetchone()
            if not row:
                return JSONResponse(status_code=404, content={"error": "Montacarga no encontrado"})
            
            uso, carga, tipo = row
            
            # Validar operación
            if campo == "EnUso" and not uso and carga:
                return JSONResponse(status_code=400, content={"error": "No se puede usar mientras está cargando"})
            if campo == "EnCarga" and not carga and uso:
                return JSONResponse(status_code=400, content={"error": "No se puede cargar mientras está en uso"})
            
            # Determinar nuevo estado (toggle)
            nuevo_estado = 1 if (uso if campo == "EnUso" else carga) == 0 else 0
            
            # Actualizar porcentaje si es necesario
            update_query = f"UPDATE montacargas SET {campo} = ?"
            params = [nuevo_estado]
            
            if campo == "EnUso" and nuevo_estado == 0 and nuevo_porcentaje is not None:
                if nuevo_porcentaje < 0 or nuevo_porcentaje > 100:
                    return JSONResponse(status_code=400, content={"error": "Porcentaje inválido"})
                update_query += ", PorcentajeBateria = ?"
                params.append(nuevo_porcentaje)
            
            update_query += " WHERE IDMontacarga = ?"
            params.append(id)
            
            cur.execute(update_query, tuple(params))
            conn.commit()
            
            # Actualizar estado global
            global estado_actual
            if id in estado_actual:
                estado_actual[id][campo.lower()] = bool(nuevo_estado)
                
                if campo == "EnUso" and nuevo_estado == 0 and nuevo_porcentaje is not None:
                    estado_actual[id]["porcentaje"] = nuevo_porcentaje
            
            # Calcular tiempo estimado si se activó la carga
            estimado_fin = 0
            if campo == "EnCarga" and nuevo_estado == 1:
                # Registrar inicio de carga
                tiempo_ultima_actualizacion[id] = time.time()
                
                # Calcular tiempo estimado
                porcentaje_actual = estado_actual[id]["porcentaje"]
                tiempo = calcular_tiempo_restante(tipo, porcentaje_actual)
                estimado_fin = time.time() + tiempo.total_seconds()
            
            return JSONResponse(content={
                "success": True,
                "estimado_fin": int(estimado_fin) if estimado_fin > 0 else 0
            })
    except Exception as e:
        logger.error(f"Error en toggle: {e}")
        return JSONResponse(status_code=500, content={"error": "Error interno del servidor"})
    finally:
        if conn:
            conn.close()