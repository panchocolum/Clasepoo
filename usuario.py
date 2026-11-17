class Usuario:
    def __init__(self, id, empleado_id, nombre_usuario, hash_codificado,
                 activo=1, intentos_fallidos=0, bloqueado_hasta=None, roles=None):
        if not nombre_usuario.strip():
            raise ValueError("El usuario no puede estar vacio.")
        self.id = id
        self.empleado_id = empleado_id
        self.nombre_usuario = nombre_usuario.strip()
        self.hash_codificado = hash_codificado
        self.activo = activo
        self.intentos_fallidos = intentos_fallidos
        self.bloqueado_hasta = bloqueado_hasta
        self.roles = [] if roles is None else roles

    def tiene_permiso(self, codigo):
        for rol in self.roles:
            for permiso in rol.permisos:
                if permiso.codigo == codigo:
                    return True
        return False

    def registrar_fallo(self):
        self.intentos_fallidos += 1

    def registrar_acceso(self):
        self.intentos_fallidos = 0
        self.bloqueado_hasta = None

    def mostrar_info(self):
        # Nunca se muestra el hash ni la clave.
        print(f"ID: {self.id} | Usuario: {self.nombre_usuario} | Activo: {self.activo}")
