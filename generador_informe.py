from abc import ABC, abstractmethod
from datetime import datetime


class GeneradorInforme(ABC):
    def __init__(self, titulo):
        self.titulo = titulo
        self.fecha_generacion = datetime.now()

    @abstractmethod
    def generar(self, datos, ruta):
        pass
