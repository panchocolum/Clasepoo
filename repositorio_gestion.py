from datetime import date
from empleado import Empleado
from gerente import Gerente
from departamento import Departamento
from proyecto import Proyecto
from asignacion import Asignacion
from registro_tiempo import RegistroTiempo


class RepositorioGestion:
    def __init__(self, base_datos):
        self.base_datos = base_datos

    # Todas las consultas usan parametros ?, como en el ejemplo del profesor.
    def crear_empleado(self, empleado):
        with self.base_datos.transaccion() as conexion:
            cursor = conexion.cursor()
            try:
                cursor.execute("""INSERT INTO empleado
                    (nombre, direccion, telefono, email, fecha_contratacion,
                     salario_base, activo, departamento_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (empleado.nombre, empleado.direccion, empleado.telefono, empleado.email,
                     empleado.fecha_contratacion, empleado.salario_base, empleado.activo, empleado.departamento_id))
                empleado.id = cursor.lastrowid
                if isinstance(empleado, Gerente):
                    cursor.execute("INSERT INTO gerente VALUES (?, ?, ?)",
                                   (empleado.id, empleado.fecha_nombramiento, empleado.bono_gestion))
            finally:
                cursor.close()
        return empleado.id

    def obtener_empleado(self, id):
        cursor = self.base_datos.conectar().cursor()
        cursor.execute("""SELECT e.id, e.nombre, e.direccion, e.telefono, e.email,
            e.fecha_contratacion, e.salario_base, e.activo, e.departamento_id,
            g.fecha_nombramiento, g.bono_gestion FROM empleado e
            LEFT JOIN gerente g ON e.id = g.empleado_id WHERE e.id = ?""", (id,))
        fila = cursor.fetchone()
        cursor.close()
        if fila is None:
            return None
        if fila[9] is not None:
            return Gerente(*fila)
        return Empleado(*fila[:9])

    def listar_empleados(self):
        cursor = self.base_datos.conectar().cursor()
        cursor.execute("SELECT id FROM empleado ORDER BY id")
        ids = cursor.fetchall()
        cursor.close()
        return [self.obtener_empleado(fila[0]) for fila in ids]

    def actualizar_empleado(self, empleado):
        anterior = self.obtener_empleado(empleado.id)
        if anterior is None:
            raise ValueError("El empleado no existe.")
        # La reasignacion de departamento se realiza en su metodo propio.
        if empleado.departamento_id != anterior.departamento_id or empleado.activo != anterior.activo:
            raise ValueError("Use la opcion de departamento o de baja para ese cambio.")
        with self.base_datos.transaccion() as conexion:
            conexion.execute("UPDATE empleado SET nombre = ?, direccion = ?, telefono = ?, email = ?, salario_base = ? WHERE id = ?",
                             (empleado.nombre, empleado.direccion, empleado.telefono, empleado.email, empleado.salario_base, empleado.id))
            if isinstance(empleado, Gerente):
                conexion.execute("UPDATE gerente SET bono_gestion = ? WHERE empleado_id = ?", (empleado.bono_gestion, empleado.id))

    def eliminar_empleado(self, id):
        if self.obtener_empleado(id) is None:
            raise ValueError("El empleado no existe.")
        with self.base_datos.transaccion() as conexion:
            asignado = conexion.execute("SELECT 1 FROM asignacion WHERE empleado_id = ?", (id,)).fetchone()
            cuenta = conexion.execute("SELECT 1 FROM usuario WHERE empleado_id = ?", (id,)).fetchone()
            conexion.execute("UPDATE departamento SET gerente_id = NULL WHERE gerente_id = ?", (id,))
            if asignado or cuenta:
                conexion.execute("UPDATE empleado SET activo = 0 WHERE id = ?", (id,))
                conexion.execute("UPDATE usuario SET activo = 0 WHERE empleado_id = ?", (id,))
                return "Baja logica: se conserva el historial y se desactiva la cuenta."
            conexion.execute("DELETE FROM gerente WHERE empleado_id = ?", (id,))
            conexion.execute("DELETE FROM empleado WHERE id = ?", (id,))
            return "Empleado eliminado: no tenia historial ni cuenta."

    def guardar_departamento(self, departamento):
        with self.base_datos.transaccion() as conexion:
            if departamento.id is None:
                cursor = conexion.execute("INSERT INTO departamento (nombre) VALUES (?)", (departamento.nombre,))
                departamento.id = cursor.lastrowid
            else:
                cursor = conexion.execute("UPDATE departamento SET nombre = ? WHERE id = ?", (departamento.nombre, departamento.id))
                if cursor.rowcount == 0:
                    raise ValueError("El departamento no existe.")
        return departamento.id

    def listar_departamentos(self):
        cursor = self.base_datos.conectar().execute("SELECT id, nombre, gerente_id FROM departamento ORDER BY id")
        datos = [Departamento(*fila) for fila in cursor.fetchall()]
        cursor.close()
        return datos

    def eliminar_departamento(self, id):
        with self.base_datos.transaccion() as conexion:
            if conexion.execute("SELECT 1 FROM empleado WHERE departamento_id = ?", (id,)).fetchone():
                raise ValueError("Primero reasigne los empleados del departamento.")
            cursor = conexion.execute("DELETE FROM departamento WHERE id = ?", (id,))
            if not cursor.rowcount:
                raise ValueError("El departamento no existe.")

    def asignar_departamento(self, empleado_id, departamento_id):
        if self.obtener_empleado(empleado_id) is None:
            raise ValueError("El empleado no existe.")
        with self.base_datos.transaccion() as conexion:
            conexion.execute("UPDATE departamento SET gerente_id = NULL WHERE gerente_id = ?", (empleado_id,))
            conexion.execute("UPDATE empleado SET departamento_id = ? WHERE id = ?", (departamento_id, empleado_id))

    def designar_gerente(self, departamento_id, gerente_id):
        gerente = self.obtener_empleado(gerente_id)
        if not isinstance(gerente, Gerente) or not gerente.activo or gerente.departamento_id != departamento_id:
            raise ValueError("Debe ser un gerente activo perteneciente a ese departamento.")
        with self.base_datos.transaccion() as conexion:
            conexion.execute("UPDATE departamento SET gerente_id = ? WHERE id = ?", (gerente_id, departamento_id))

    def crear_proyecto(self, proyecto):
        with self.base_datos.transaccion() as conexion:
            cursor = conexion.execute("INSERT INTO proyecto (nombre, descripcion, fecha_inicio, estado) VALUES (?, ?, ?, ?)",
                                      (proyecto.nombre, proyecto.descripcion, proyecto.fecha_inicio, proyecto.estado))
            proyecto.id = cursor.lastrowid
        return proyecto.id

    def obtener_proyecto(self, id):
        fila = self.base_datos.conectar().execute("SELECT id, nombre, descripcion, fecha_inicio, estado FROM proyecto WHERE id = ?", (id,)).fetchone()
        return None if fila is None else Proyecto(*fila)

    def listar_proyectos(self):
        filas = self.base_datos.conectar().execute("SELECT id, nombre, descripcion, fecha_inicio, estado FROM proyecto ORDER BY id").fetchall()
        return [Proyecto(*fila) for fila in filas]

    def actualizar_proyecto(self, proyecto):
        anterior = self.obtener_proyecto(proyecto.id)
        if anterior is None:
            raise ValueError("El proyecto no existe.")
        if anterior.fecha_inicio != proyecto.fecha_inicio:
            raise ValueError("La fecha inicial no se modifica desde esta opcion.")
        with self.base_datos.transaccion() as conexion:
            conexion.execute("UPDATE proyecto SET nombre = ?, descripcion = ?, estado = ? WHERE id = ?",
                             (proyecto.nombre, proyecto.descripcion, proyecto.estado, proyecto.id))

    def eliminar_proyecto(self, id):
        if self.obtener_proyecto(id) is None:
            raise ValueError("El proyecto no existe.")
        with self.base_datos.transaccion() as conexion:
            if conexion.execute("SELECT 1 FROM asignacion WHERE proyecto_id = ?", (id,)).fetchone():
                conexion.execute("UPDATE proyecto SET estado = 'CANCELADO' WHERE id = ?", (id,))
                return "Proyecto cancelado; se conserva el historial."
            conexion.execute("DELETE FROM proyecto WHERE id = ?", (id,))
            return "Proyecto eliminado sin historial."

    def crear_asignacion(self, asignacion, empleado_id=None, proyecto_id=None):
        empleado_id = asignacion.empleado_id if empleado_id is None else empleado_id
        proyecto_id = asignacion.proyecto_id if proyecto_id is None else proyecto_id
        empleado = self.obtener_empleado(empleado_id)
        proyecto = self.obtener_proyecto(proyecto_id)
        if empleado is None or not empleado.activo or proyecto is None or proyecto.estado in ("FINALIZADO", "CANCELADO"):
            raise ValueError("Se requiere empleado activo y proyecto disponible.")
        if asignacion.fecha_inicio < max(empleado.fecha_contratacion, proyecto.fecha_inicio):
            raise ValueError("La asignacion no puede comenzar antes que el empleo o el proyecto.")
        with self.base_datos.transaccion() as conexion:
            # No se permiten periodos superpuestos para la misma pareja.
            existe = conexion.execute("""SELECT id FROM asignacion WHERE empleado_id = ? AND proyecto_id = ?
                AND fecha_inicio <= ? AND (fecha_fin IS NULL OR fecha_fin >= ?)""",
                (empleado_id, proyecto_id, asignacion.fecha_fin or "9999-12-31", asignacion.fecha_inicio)).fetchone()
            if existe:
                raise ValueError("Ya existe una asignacion en ese periodo.")
            cursor = conexion.execute("""INSERT INTO asignacion
                (empleado_id, proyecto_id, fecha_inicio, rol_proyecto, fecha_fin) VALUES (?, ?, ?, ?, ?)""",
                (empleado_id, proyecto_id, asignacion.fecha_inicio, asignacion.rol_proyecto, asignacion.fecha_fin))
            asignacion.id = cursor.lastrowid
        return asignacion.id

    def listar_asignaciones(self):
        filas = self.base_datos.conectar().execute("SELECT id, empleado_id, proyecto_id, fecha_inicio, rol_proyecto, fecha_fin FROM asignacion ORDER BY id").fetchall()
        return [Asignacion(*fila) for fila in filas]

    def finalizar_asignacion(self, id, fecha):
        fecha = date.fromisoformat(fecha).isoformat()
        with self.base_datos.transaccion() as conexion:
            fila = conexion.execute("SELECT fecha_inicio, fecha_fin FROM asignacion WHERE id = ?", (id,)).fetchone()
            ultima = conexion.execute("SELECT MAX(fecha) FROM registro_tiempo WHERE asignacion_id = ?", (id,)).fetchone()[0]
            if fila is None or fecha < fila[0] or (ultima is not None and fecha < ultima):
                raise ValueError("La fecha final no puede preceder al inicio ni a las horas registradas.")
            if fila[1] is not None:
                raise ValueError("La asignacion ya esta finalizada.")
            conexion.execute("UPDATE asignacion SET fecha_fin = ? WHERE id = ?", (fecha, id))

    def eliminar_asignacion(self, id):
        with self.base_datos.transaccion() as conexion:
            if conexion.execute("SELECT 1 FROM registro_tiempo WHERE asignacion_id = ?", (id,)).fetchone():
                raise ValueError("La asignacion tiene horas; finalicela para conservar el historial.")
            cursor = conexion.execute("DELETE FROM asignacion WHERE id = ?", (id,))
            if not cursor.rowcount:
                raise ValueError("La asignacion no existe.")

    def registrar_tiempo(self, registro, asignacion_id=None):
        asignacion_id = registro.asignacion_id if asignacion_id is None else asignacion_id
        with self.base_datos.transaccion() as conexion:
            fila = conexion.execute("""SELECT a.empleado_id, a.fecha_inicio, a.fecha_fin, e.activo, p.estado
                FROM asignacion a JOIN empleado e ON e.id = a.empleado_id
                JOIN proyecto p ON p.id = a.proyecto_id WHERE a.id = ?""", (asignacion_id,)).fetchone()
            if fila is None or not fila[3] or fila[4] in ("FINALIZADO", "CANCELADO"):
                raise ValueError("La asignacion, el empleado o el proyecto no permiten registrar horas.")
            if registro.fecha < fila[1] or (fila[2] is not None and registro.fecha > fila[2]):
                raise ValueError("La fecha esta fuera del periodo de la asignacion.")
            total = conexion.execute("""SELECT COALESCE(SUM(r.horas),0) FROM registro_tiempo r
                JOIN asignacion a ON a.id = r.asignacion_id WHERE a.empleado_id = ? AND r.fecha = ? AND r.id != ?""",
                (fila[0], registro.fecha, registro.id or -1)).fetchone()[0]
            if total + registro.horas > 24:
                raise ValueError("El total diario del empleado supera 24 horas.")
            if registro.id is None:
                cursor = conexion.execute("INSERT INTO registro_tiempo (asignacion_id,fecha,horas,descripcion) VALUES (?,?,?,?)",
                                          (asignacion_id, registro.fecha, registro.horas, registro.descripcion))
                registro.id = cursor.lastrowid
            else:
                cursor = conexion.execute("UPDATE registro_tiempo SET horas = ?, descripcion = ? WHERE id = ? AND asignacion_id = ? AND fecha = ?",
                                          (registro.horas, registro.descripcion, registro.id, asignacion_id, registro.fecha))
                if not cursor.rowcount:
                    raise ValueError("El registro no existe o se intento cambiar su asignacion o fecha.")
        return registro.id

    def listar_horas(self, empleado_id, desde, hasta):
        desde = date.fromisoformat(desde).isoformat()
        hasta = date.fromisoformat(hasta).isoformat()
        if hasta < desde:
            raise ValueError("El rango de fechas no es valido.")
        filas = self.base_datos.conectar().execute("""SELECT r.id,r.asignacion_id,r.fecha,r.horas,r.descripcion
            FROM registro_tiempo r JOIN asignacion a ON a.id = r.asignacion_id
            WHERE a.empleado_id = ? AND r.fecha BETWEEN ? AND ? ORDER BY r.fecha,r.id""", (empleado_id, desde, hasta)).fetchall()
        return [RegistroTiempo(*fila) for fila in filas]

    def eliminar_registro(self, id):
        with self.base_datos.transaccion() as conexion:
            cursor = conexion.execute("DELETE FROM registro_tiempo WHERE id = ?", (id,))
            if not cursor.rowcount:
                raise ValueError("El registro no existe.")
