class Departamento:
    def __init__(self, id, nombre, gerente_id=None):
        if not nombre.strip():
            raise ValueError("El nombre del departamento no puede estar vacio.")
        self.id = id
        self.nombre = nombre.strip()
        self.gerente_id = gerente_id

    def cambiar_nombre(self, nombre):
        if not nombre.strip():
            raise ValueError("El nombre del departamento no puede estar vacio.")
        self.nombre = nombre.strip()

    def mostrar_info(self):
        print(f"ID: {self.id}")
        print(f"Departamento: {self.nombre}")
        print(f"Gerente ID: {self.gerente_id}")
