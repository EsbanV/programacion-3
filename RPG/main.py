from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from database import crear_base_datos, get_db
from models import Personaje, Mision, MisionPersonaje
from TDA_Cola import ArrayQueue

crear_base_datos()

app = FastAPI()

colas_misiones = {}

class PersonajeSchema(BaseModel):
    nombre: str

class MisionSchema(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    experiencia: int

@app.post("/personajes")
def crear_personaje(personaje: PersonajeSchema, db: Session = Depends(get_db)):
    nuevo = Personaje(nombre=personaje.nombre, experiencia=0)
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    colas_misiones[nuevo.id] = ArrayQueue()
    return nuevo

@app.get("/personajes")
def listar_personajes(db: Session = Depends(get_db)):
    return db.query(Personaje).all()

@app.post("/misiones")
def crear_mision(mision: MisionSchema, db: Session = Depends(get_db)):
    nueva = Mision(
        nombre=mision.nombre,
        descripcion=mision.descripcion,
        experiencia=mision.experiencia,
        estado="pendiente"
    )
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

@app.post("/personajes/{personaje_id}/misiones/{mision_id}")
def asignar_mision(personaje_id: int, mision_id: int, db: Session = Depends(get_db)):

    personaje = db.query(Personaje).filter(Personaje.id == personaje_id).first()
    if not personaje:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")
    mision = db.query(Mision).filter(Mision.id == mision_id).first()
    if not mision:
        raise HTTPException(status_code=404, detail="Misión no encontrada")
    
    asignacion = MisionPersonaje(personaje_id=personaje.id, mision_id=mision.id)
    db.add(asignacion)
    db.commit()
    
    if personaje_id not in colas_misiones:
        colas_misiones[personaje_id] = ArrayQueue()
    colas_misiones[personaje_id].enqueue(mision.id)
    
    return {"mensaje": f"Misión '{mision.nombre}' asignada a '{personaje.nombre}'"}

@app.post("/personajes/{personaje_id}/completar")
def completar_mision(personaje_id: int, db: Session = Depends(get_db)):
    personaje = db.query(Personaje).filter(Personaje.id == personaje_id).first()
    if not personaje:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")
    
    if personaje_id not in colas_misiones or colas_misiones[personaje_id].is_empty():
        raise HTTPException(status_code=404, detail="No hay misiones asignadas")
    
    mision_id = colas_misiones[personaje_id].dequeue()
    
    mision = db.query(Mision).filter(Mision.id == mision_id).first()
    if not mision:
        raise HTTPException(status_code=404, detail="Misión no encontrada en DB")
    
    mision.estado = "completada"
    personaje.experiencia += mision.experiencia
    db.commit()
    
    asignacion = db.query(MisionPersonaje).filter(
        MisionPersonaje.personaje_id == personaje_id,
        MisionPersonaje.mision_id == mision_id
    ).first()
    if asignacion:
        db.delete(asignacion)
        db.commit()
    
    return {"mensaje": f"Misión '{mision.nombre}' completada, experiencia actualizada a {personaje.experiencia}"}

@app.get("/personajes/{personaje_id}/misiones")
def listar_misiones(personaje_id: int, db: Session = Depends(get_db)):
    if personaje_id not in colas_misiones or colas_misiones[personaje_id].is_empty():
        return {"misiones": []}
    
    cola = colas_misiones[personaje_id]
    misiones_list = []
    n = len(cola)
    for i in range(n):
        index = (cola.front + i) % len(cola.data)
        m_id = cola.data[index]
        mision = db.query(Mision).filter(Mision.id == m_id).first()
        if mision:
            misiones_list.append({
                "id": mision.id,
                "nombre": mision.nombre,
                "descripcion": mision.descripcion,
                "experiencia": mision.experiencia,
                "estado": mision.estado
            })
    return {"misiones": misiones_list}
