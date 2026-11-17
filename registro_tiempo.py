from datetime import date


class RegistroTiempo:
    def __init__(self, id, asignacion_id, fecha, horas, descripcion):
        fecha = date.fromisoformat(fecha).isoformat()
        if not 0 < horas <= 24:
            raise ValueError("Las horas deben ser mayores que cero y no superar 24.")
        if not descripcion.strip():
            raise ValueError("La descripcion no puede estar vacia.")
        self.id = id
        self.asignacion_id = asignacion_id
        self.fecha = fecha
        self.horas = horas
        self.descripcion = descripcion.strip()

    def actualizar(self, horas, descripcion):
        if not 0 < horas <= 24 or not descripcion.strip():
            raise ValueError("Horas o descripcion no validas.")
        self.horas = horas
        self.descripcion = descripcion.strip()

    def mostrar_info(self):
        print(f"ID: {self.id}")
        print(f"Asignacion ID: {self.asignacion_id}")
        print(f"Fecha: {self.fecha}")
        print(f"Horas: {self.horas}")
        print(f"Descripcion: {self.descripcion}")
