from datetime import date
from estado_proyecto import EstadoProyecto


class Proyecto:
    def __init__(self, id, nombre, descripcion, fecha_inicio, estado):
        if not nombre.strip():
            raise ValueError("El nombre del proyecto no puede estar vacio.")
        fecha_inicio = date.fromisoformat(fecha_inicio).isoformat()
        if estado not in ("PLANIFICADO", "EN_CURSO", "FINALIZADO", "CANCELADO"):
            raise ValueError("El estado del proyecto no es valido.")
        self.id = id
        self.nombre = nombre.strip()
        self.descripcion = descripcion.strip()
        self.fecha_inicio = fecha_inicio
        self.estado = EstadoProyecto(estado).value

    def cambiar_estado(self, estado):
        self.estado = EstadoProyecto(estado).value

    def mostrar_info(self):
        print(f"ID: {self.id}")
        print(f"Proyecto: {self.nombre}")
        print(f"Descripcion: {self.descripcion}")
        print(f"Fecha de inicio: {self.fecha_inicio}")
        print(f"Estado: {self.estado}")
