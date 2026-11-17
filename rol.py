class Rol:
    def __init__(self, id, nombre, permisos=None):
        self.id = id
        self.nombre = nombre
        self.permisos = [] if permisos is None else permisos

    def agregar_permiso(self, permiso):
        if not any(p.codigo == permiso.codigo for p in self.permisos):
            self.permisos.append(permiso)

    def quitar_permiso(self, permiso):
        self.permisos = [p for p in self.permisos if p.codigo != permiso.codigo]

    def mostrar_info(self):
        print(f"Rol: {self.nombre}")
