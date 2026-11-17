from datetime import datetime, timedelta, timezone
from sesion import Sesion


class ServicioAutenticacion:
    def __init__(self, repositorio, servicio_contrasenas):
        self.repositorio = repositorio
        self.contrasenas = servicio_contrasenas
        self.max_intentos = 5
        self.minutos_bloqueo = 5
        self.duracion_sesion_min = 30

    def autenticar(self, nombre, clave):
        usuario = self.repositorio.buscar_por_nombre(nombre.strip())
        mensaje = "No se pudo iniciar sesion. Revise las credenciales o intente mas tarde."
        if usuario is None or not usuario.activo:
            raise ValueError(mensaje)
        ahora = datetime.now(timezone.utc)
        if usuario.bloqueado_hasta:
            if ahora < datetime.fromisoformat(usuario.bloqueado_hasta):
                raise ValueError(mensaje)
            usuario.registrar_acceso()
        if not self.contrasenas.verificar(clave, usuario.hash_codificado):
            usuario.registrar_fallo()
            if usuario.intentos_fallidos >= self.max_intentos:
                usuario.bloqueado_hasta = (ahora + timedelta(minutes=self.minutos_bloqueo)).isoformat()
            self.repositorio.guardar_estado_acceso(usuario)
            raise ValueError(mensaje)
        usuario.registrar_acceso()
        self.repositorio.guardar_estado_acceso(usuario)
        return Sesion(usuario, self.duracion_sesion_min)

    def autorizar(self, sesion, codigo_permiso):
        if sesion is None or not sesion.esta_vigente():
            return False
        usuario = self.repositorio.buscar_por_nombre(sesion.usuario.nombre_usuario)
        return usuario is not None and usuario.id == sesion.usuario.id and bool(usuario.activo) and usuario.tiene_permiso(codigo_permiso)

    def cerrar_sesion(self, sesion):
        sesion.cerrar()

    def cambiar_clave(self, sesion, actual, nueva):
        if not self.autorizar(sesion, "sistema.leer"):
            raise ValueError("Se requiere una sesion autorizada.")
        usuario = self.repositorio.buscar_por_nombre(sesion.usuario.nombre_usuario)
        if not self.contrasenas.verificar(actual, usuario.hash_codificado):
            raise ValueError("La clave actual no es correcta.")
        self.repositorio.actualizar_hash(usuario.id, self.contrasenas.generar_hash(nueva))
