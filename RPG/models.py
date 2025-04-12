from sqlalchemy import Column, Integer, String, Text, Enum, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class Personaje(Base):
    __tablename__ = 'personajes'
    
    id = Column(Integer, primary_key=True)
    nombre = Column(String(30), nullable=False)
    experiencia = Column(Integer, default=0)

    misiones = relationship("MisionPersonaje", back_populates="personaje")

class Mision(Base):
    __tablename__ = 'misiones'
    
    id = Column(Integer, primary_key=True)
    nombre = Column(String(50), nullable=False)
    descripcion = Column(Text, nullable=True)
    experiencia = Column(Integer, default=0)
    estado = Column(Enum('pendiente', 'completada', name='estados'), nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.now)
    
    personajes = relationship("MisionPersonaje", back_populates="mision")

class MisionPersonaje(Base):
    __tablename__ = 'misiones_personaje'

    personaje_id = Column(Integer, ForeignKey('personajes.id'), primary_key=True)
    mision_id = Column(Integer, ForeignKey('misiones.id'), primary_key=True)
    
    personaje = relationship("Personaje", back_populates="misiones")
    mision = relationship("Mision", back_populates="personajes")
