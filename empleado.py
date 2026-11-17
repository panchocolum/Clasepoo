from datetime import date
from persona import Persona


class Empleado(Persona):
    def __init__(self, id, nombre, direccion, telefono, email,
                 fecha_contratacion, salario_base, activo, departamento_id):
        super().__init__(id, nombre, direccion, telefono, email)
        fecha_contratacion = date.fromisoformat(fecha_contratacion).isoformat()
        # En este ejercicio, los sueldos se expresan en pesos enteros.
        if not isinstance(salario_base, int) or isinstance(salario_base, bool) or salario_base < 0:
            raise ValueError("El salario debe ser un entero mayor o igual a cero.")
        if activo not in (0, 1):
            raise ValueError("Activo debe ser 0 o 1.")
        self.fecha_contratacion = fecha_contratacion
        self.salario_base = salario_base
        self.activo = activo
        self.departamento_id = departamento_id

    def cambiar_salario(self, monto):
        if not isinstance(monto, int) or isinstance(monto, bool) or monto < 0:
            raise ValueError("El salario debe ser un entero no negativo.")
        self.salario_base = monto

    def dar_de_baja(self):
        self.activo = 0

    def obtener_resumen(self):
        return f"{self.id}: {self.nombre} | Salario: {self.salario_base}"

    def mostrar_info(self):
        super().mostrar_info()
        print(f"Fecha de contratacion: {self.fecha_contratacion}")
        print(f"Salario base: {self.salario_base}")
        print(f"Activo: {self.activo}")
        print(f"Departamento ID: {self.departamento_id}")
