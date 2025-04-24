from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Literal
from datetime import datetime
from models import EstadoVuelo, VueloORM, lista
from sqlalchemy.orm import Session
from db import get_db

class VueloCreate(BaseModel):
    codigo: str
    estado: Literal["programado", "emergencia", "retrasado"]
    hora: datetime
    origen: str
    destino: str

class InsertPos(BaseModel):
    codigo: str
    estado: Literal["programado", "emergencia", "retrasado"]
    hora: datetime
    origen: str
    destino: str
    posicion: int

class Reorden(BaseModel):
    orden: List[str]

class VueloOut(BaseModel):
    codigo: str
    estado: EstadoVuelo
    hora: datetime
    origen: str
    destino: str

    class Config:
        orm_mode = True

app = FastAPI(title="API Gestión de Vuelos")

@app.post("/vuelos", response_model=VueloOut)
def crear_vuelo(v: VueloCreate, db: Session = Depends(get_db)):
    if db.query(VueloORM).filter(VueloORM.codigo == v.codigo).first():
        raise HTTPException(400, "El código ya existe")

    try:
        orm = VueloORM(codigo=v.codigo, estado=EstadoVuelo(v.estado), hora=v.hora, origen=v.origen, destino=v.destino)
        db.add(orm)
        db.commit()
        db.refresh(orm)

        if orm.estado == EstadoVuelo.emergencia:
            lista.insertar_al_frente(orm)
        else:
            lista.insertar_al_final(orm)

        return orm

    except Exception as e:
        db.rollback()
        raise HTTPException(500, f"Error al crear vuelo: {str(e)}")

@app.post("/vuelos/insertar", response_model=VueloOut)
def insertar_pos(payload: InsertPos, db: Session = Depends(get_db)):
    if db.query(VueloORM).filter(VueloORM.codigo == payload.codigo).first():
        raise HTTPException(400, "El código ya existe")

    try:
        orm = VueloORM(codigo=payload.codigo, estado=EstadoVuelo(payload.estado), hora=payload.hora, origen=payload.origen, destino=payload.destino)
        db.add(orm)
        db.commit()
        db.refresh(orm)

        lista.insertar_en_posicion(orm, payload.posicion)
        return orm

    except IndexError as e:
        db.rollback()
        raise HTTPException(400, f"Posición inválida: {str(e)}")

    except Exception as e:
        db.rollback()
        raise HTTPException(500, f"Error inesperado: {str(e)}")

@app.get("/vuelos/total")
def total_vuelos():
    return {"total": lista.longitud()}

@app.get("/vuelos/proximo", response_model=VueloOut)
def vuelo_proximo():
    try:
        return lista.obtener_primero()
    except IndexError:
        raise HTTPException(404, "La lista está vacía")

@app.get("/vuelos/ultimo", response_model=VueloOut)
def vuelo_ultimo():
    try:
        return lista.obtener_ultimo()
    except IndexError:
        raise HTTPException(404, "La lista está vacía")

@app.get("/vuelos/lista", response_model=List[VueloOut])
def listar_todos():
    return lista.a_lista()

@app.delete("/vuelos/extraer", response_model=VueloOut)
def extraer_vuelo(posicion: int, db: Session = Depends(get_db)):
    try:
        vuelo = lista.extraer_de_posicion(posicion)
        db.delete(vuelo)
        db.commit()
        return vuelo

    except IndexError as e:
        raise HTTPException(400, str(e))

    except Exception as e:
        db.rollback()
        raise HTTPException(500, f"Error al extraer vuelo: {str(e)}")