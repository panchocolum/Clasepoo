from datetime import date
from empleado import Empleado


class Gerente(Empleado):
    def __init__(self, id, nombre, direccion, telefono, email,
                 fecha_contratacion, salario_base, activo, departamento_id,
                 fecha_nombramiento, bono_gestion):
        super().__init__(id, nombre, direccion, telefono, email,
                         fecha_contratacion, salario_base, activo, departamento_id)
        if date.fromisoformat(fecha_nombramiento) < date.fromisoformat(fecha_contratacion):
            raise ValueError("El nombramiento no puede ser anterior a la contratacion.")
        if not isinstance(bono_gestion, int) or isinstance(bono_gestion, bool) or bono_gestion < 0:
            raise ValueError("El bono debe ser un entero mayor o igual a cero.")
        self.fecha_nombramiento = date.fromisoformat(fecha_nombramiento).isoformat()
        self.bono_gestion = bono_gestion

    def obtener_resumen(self):
        return super().obtener_resumen() + f" | Gerente | Bono: {self.bono_gestion}"

    def mostrar_info(self):
        super().mostrar_info()
        print(f"Fecha de nombramiento: {self.fecha_nombramiento}")
        print(f"Bono de gestion: {self.bono_gestion}")
