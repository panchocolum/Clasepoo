from datetime import date


class Asignacion:
    def __init__(self, id, empleado_id, proyecto_id, fecha_inicio,
                 rol_proyecto, fecha_fin=None):
        inicio = date.fromisoformat(fecha_inicio)
        if fecha_fin is not None and date.fromisoformat(fecha_fin) < inicio:
            raise ValueError("La fecha de fin no puede ser anterior al inicio.")
        if not rol_proyecto.strip():
            raise ValueError("El rol del proyecto no puede estar vacio.")
        self.id = id
        self.empleado_id = empleado_id
        self.proyecto_id = proyecto_id
        self.fecha_inicio = inicio.isoformat()
        self.fecha_fin = None if fecha_fin is None else date.fromisoformat(fecha_fin).isoformat()
        self.rol_proyecto = rol_proyecto.strip()

    def finalizar(self, fecha):
        fecha = date.fromisoformat(fecha).isoformat()
        if fecha < self.fecha_inicio:
            raise ValueError("La fecha final no puede ser anterior al inicio.")
        self.fecha_fin = fecha

    def esta_vigente(self, fecha):
        fecha = date.fromisoformat(fecha).isoformat()
        return fecha >= self.fecha_inicio and (self.fecha_fin is None or fecha <= self.fecha_fin)

    def mostrar_info(self):
        print(f"ID: {self.id}")
        print(f"Empleado ID: {self.empleado_id}")
        print(f"Proyecto ID: {self.proyecto_id}")
        print(f"Fecha de inicio: {self.fecha_inicio}")
        print(f"Fecha de fin: {self.fecha_fin}")
        print(f"Rol en el proyecto: {self.rol_proyecto}")
