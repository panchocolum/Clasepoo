from usuario import Usuario
from rol import Rol
from permiso import Permiso


class RepositorioUsuarios:
    def __init__(self, base_datos):
        self.base_datos = base_datos

    def contar(self):
        cursor = self.base_datos.conectar().cursor()
        cursor.execute("SELECT COUNT(*) FROM usuario")
        cantidad = cursor.fetchone()[0]
        cursor.close()
        return cantidad

    def buscar_por_nombre(self, nombre):
        cursor = self.base_datos.conectar().cursor()
        cursor.execute("""SELECT u.id, u.empleado_id, u.nombre_usuario, u.hash_codificado,
                       u.activo * e.activo, u.intentos_fallidos, u.bloqueado_hasta
                       FROM usuario u JOIN empleado e ON e.id = u.empleado_id
                       WHERE u.nombre_usuario = ?""", (nombre,))
        fila = cursor.fetchone()
        cursor.close()
        if fila is None:
            return None
        usuario = Usuario(*fila)
        usuario.roles = self.cargar_roles_permisos(usuario.id)
        return usuario

    def crear(self, usuario):
        if not usuario.roles:
            raise ValueError("La cuenta debe tener al menos un rol.")
        with self.base_datos.transaccion() as conexion:
            cursor = conexion.cursor()
            try:
                cursor.execute("SELECT activo FROM empleado WHERE id = ?", (usuario.empleado_id,))
                fila = cursor.fetchone()
                if fila is None or not fila[0]:
                    raise ValueError("El empleado debe existir y estar activo.")
                cursor.execute("""INSERT INTO usuario
                    (empleado_id, nombre_usuario, hash_codificado, activo) VALUES (?, ?, ?, ?)""",
                    (usuario.empleado_id, usuario.nombre_usuario, usuario.hash_codificado, usuario.activo))
                usuario.id = cursor.lastrowid
                for rol in usuario.roles:
                    cursor.execute("SELECT id FROM rol WHERE nombre = ?", (rol.nombre,))
                    fila = cursor.fetchone()
                    if fila is None:
                        raise ValueError("El rol no existe.")
                    cursor.execute("INSERT INTO usuario_rol VALUES (?, ?)", (usuario.id, fila[0]))
            finally:
                cursor.close()
        return usuario.id

    def guardar_estado_acceso(self, usuario):
        with self.base_datos.transaccion() as conexion:
            conexion.execute("UPDATE usuario SET intentos_fallidos = ?, bloqueado_hasta = ? WHERE id = ?",
                             (usuario.intentos_fallidos, usuario.bloqueado_hasta, usuario.id))

    def actualizar_hash(self, usuario_id, hash_codificado):
        with self.base_datos.transaccion() as conexion:
            conexion.execute("UPDATE usuario SET hash_codificado = ? WHERE id = ?", (hash_codificado, usuario_id))

    def cargar_roles_permisos(self, usuario_id):
        cursor = self.base_datos.conectar().cursor()
        cursor.execute("""SELECT r.id, r.nombre FROM rol r
                       JOIN usuario_rol ur ON r.id = ur.rol_id WHERE ur.usuario_id = ?""", (usuario_id,))
        roles = []
        for id, nombre in cursor.fetchall():
            rol = Rol(id, nombre)
            cursor.execute("""SELECT p.codigo, p.modulo, p.accion FROM permiso p
                           JOIN rol_permiso rp ON p.codigo = rp.permiso_codigo
                           WHERE rp.rol_id = ?""", (id,))
            for fila in cursor.fetchall():
                rol.agregar_permiso(Permiso(*fila))
            roles.append(rol)
        cursor.close()
        return roles
