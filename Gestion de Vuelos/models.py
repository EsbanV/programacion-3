from sqlalchemy import Column, String, DateTime, Enum
import enum
from db import Base
from TDA_Double_Linked_List import _DoublyLinkedBase
from typing import List

#---- Modelos ORM -_--#
class EstadoVuelo(str, enum.Enum):
    programado = "programado"
    emergencia  = "emergencia"
    retrasado   = "retrasado"

class VueloORM(Base):
    __tablename__ = "vuelos"
    codigo = Column(String, primary_key=True, index=True)
    estado = Column(Enum(EstadoVuelo, native_enum=False), nullable=False)
    hora   = Column(DateTime, nullable=False)
    origen = Column(String, nullable=False)
    destino= Column(String, nullable=False)

#---- Basicamente añade validaciones y utiliza a _DoublyLinkedBase como una interfaz----#
class ListaVuelos(_DoublyLinkedBase):
    def insertar_al_frente(self, vuelo):   
        self.add_first(vuelo)

    def insertar_al_final(self, vuelo):    
        self.add_last(vuelo)
        
    def obtener_primero(self):
        if self.is_empty(): raise IndexError("Lista vacía")
        return self._header._next._element
    
    def obtener_ultimo(self):
        if self.is_empty(): raise IndexError("Lista vacía")
        return self._trailer._prev._element
    
    def longitud(self): 
        return len(self)
    
    def insertar_en_posicion(self, vuelo, posicion: int):

        n = len(self)

        if posicion < 0 or posicion > n: 
            raise IndexError("Posición fuera de rango")
        if posicion == 0:   
            return self.insertar_al_frente(vuelo)
        if posicion == n:   
            return self.insertar_al_final(vuelo)
        if posicion <= n//2:
            nodo = self._header._next
            for _ in range(posicion-1): nodo = nodo._next
        else:
            nodo = self._trailer._prev
            for _ in range(n-posicion): nodo = nodo._prev
        self._insert_between(vuelo, nodo, nodo._next)

    def extraer_de_posicion(self, posicion: int):

        n = len(self)

        if self.is_empty(): 
            raise IndexError("Lista vacía")
        if posicion < 0 or posicion >= n: 
            raise IndexError("Posición fuera de rango")
        if posicion == 0:   
            return self.delete_first()
        if posicion == n-1: 
            return self.delete_last()
        if posicion <= n//2:
            nodo = self._header._next
            for _ in range(posicion): nodo = nodo._next
        else:
            nodo = self._trailer._prev
            for _ in range(n-1-posicion): nodo = nodo._prev
        return self._delete_node(nodo)

    def a_lista(self) -> List:
        elems = []
        nodo = self._header._next
        while nodo is not self._trailer:
            elems.append(nodo._element)
            nodo = nodo._next
        return elems

lista = ListaVuelos()