import sqlite3
from pathlib import Path

from departamento import Departamento
from empleado import Empleado
from gerente import Gerente
from proyecto import Proyecto
from asignacion import Asignacion
from registro_tiempo import RegistroTiempo


# Igual que el ejemplo del profesor: ejecucion secuencial, sin menu.
# La ruta mantiene ecotech.db junto a main.py aunque se ejecute desde otra carpeta.
ruta_db = Path(__file__).resolve().parent / "ecotech.db"
conexion = None
cursor = None

try:
    # ======================================================
    # 1. CONEXION Y CONFIGURACION DE LA BASE DE DATOS
    # ======================================================
    conexion = sqlite3.connect(ruta_db)
    cursor = conexion.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    print("CONEXION CON BASE DE DATOS ECOTECH")
    print("Conexion realizada correctamente.")

    # ======================================================
    # 2. CREACION DE TABLAS
    # ======================================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS departamento (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL CHECK (length(trim(nombre)) > 0),
        gerente_id INTEGER UNIQUE,
        FOREIGN KEY (gerente_id) REFERENCES gerente(empleado_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS empleado (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL CHECK (length(trim(nombre)) > 0),
        direccion TEXT NOT NULL,
        telefono TEXT NOT NULL,
        email TEXT NOT NULL,
        fecha_contratacion TEXT NOT NULL,
        salario_base INTEGER NOT NULL CHECK (salario_base >= 0),
        activo INTEGER NOT NULL CHECK (activo IN (0, 1)),
        departamento_id INTEGER,
        FOREIGN KEY (departamento_id) REFERENCES departamento(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gerente (
        empleado_id INTEGER PRIMARY KEY,
        fecha_nombramiento TEXT NOT NULL,
        bono_gestion INTEGER NOT NULL CHECK (bono_gestion >= 0),
        FOREIGN KEY (empleado_id) REFERENCES empleado(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS proyecto (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL CHECK (length(trim(nombre)) > 0),
        descripcion TEXT NOT NULL,
        fecha_inicio TEXT NOT NULL,
        estado TEXT NOT NULL CHECK (
            estado IN ('PLANIFICADO', 'EN_CURSO', 'FINALIZADO', 'CANCELADO')
        )
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS asignacion (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        empleado_id INTEGER NOT NULL,
        proyecto_id INTEGER NOT NULL,
        fecha_inicio TEXT NOT NULL,
        fecha_fin TEXT,
        rol_proyecto TEXT NOT NULL CHECK (length(trim(rol_proyecto)) > 0),
        CHECK (fecha_fin IS NULL OR fecha_fin >= fecha_inicio),
        FOREIGN KEY (empleado_id) REFERENCES empleado(id),
        FOREIGN KEY (proyecto_id) REFERENCES proyecto(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS registro_tiempo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        asignacion_id INTEGER NOT NULL,
        fecha TEXT NOT NULL,
        horas REAL NOT NULL CHECK (horas > 0 AND horas <= 24),
        descripcion TEXT NOT NULL CHECK (length(trim(descripcion)) > 0),
        FOREIGN KEY (asignacion_id) REFERENCES asignacion(id)
        )
    """)

    conexion.commit()
    print("Tablas creadas correctamente.")

    # ======================================================
    # 3. CRUD DEPARTAMENTO
    # ======================================================
    print("\n========== CRUD DEPARTAMENTO ==========")
    departamento1 = Departamento(None, "Desarrollo")
    departamento2 = Departamento(None, "Operaciones")

    cursor.execute(
        "INSERT INTO departamento (nombre) VALUES (?)",
        (departamento1.nombre,)
    )
    departamento1.id = cursor.lastrowid
    cursor.execute(
        "INSERT INTO departamento (nombre) VALUES (?)",
        (departamento2.nombre,)
    )
    departamento2.id = cursor.lastrowid
    conexion.commit()

    cursor.execute("SELECT id, nombre, gerente_id FROM departamento")
    print("LISTADO DE DEPARTAMENTOS")
    for fila in cursor.fetchall():
        print(f"ID: {fila[0]} | Nombre: {fila[1]} | Gerente ID: {fila[2]}")

    cursor.execute(
        "UPDATE departamento SET nombre = ? WHERE id = ?",
        ("Desarrollo de Software", departamento1.id)
    )
    conexion.commit()
    cursor.execute("SELECT id, nombre FROM departamento WHERE id = ?", (departamento1.id,))
    print("Departamento actualizado:", cursor.fetchone())

    # ======================================================
    # 4. CRUD EMPLEADO Y GERENTE
    # ======================================================
    print("\n========== CRUD EMPLEADO ==========")
    empleado1 = Empleado(None, "Ana Demo", "Calle de ejemplo 100", "900000001",
                         "ana@example.com", "2026-01-05", 900000, 1, departamento1.id)
    gerente1 = Gerente(None, "Luis Demo", "Calle de ejemplo 200", "900000002",
                       "luis@example.com", "2026-01-05", 1400000, 1, departamento2.id,
                       "2026-02-01", 150000)

    # Gerente hereda los datos de Empleado; esos datos se guardan una sola vez.
    cursor.execute(
        """INSERT INTO empleado
        (nombre, direccion, telefono, email, fecha_contratacion,
         salario_base, activo, departamento_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (empleado1.nombre, empleado1.direccion, empleado1.telefono, empleado1.email,
         empleado1.fecha_contratacion, empleado1.salario_base,
         empleado1.activo, empleado1.departamento_id)
    )
    empleado1.id = cursor.lastrowid
    cursor.execute(
        """INSERT INTO empleado
        (nombre, direccion, telefono, email, fecha_contratacion,
         salario_base, activo, departamento_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (gerente1.nombre, gerente1.direccion, gerente1.telefono, gerente1.email,
         gerente1.fecha_contratacion, gerente1.salario_base,
         gerente1.activo, gerente1.departamento_id)
    )
    gerente1.id = cursor.lastrowid
    cursor.execute(
        "INSERT INTO gerente (empleado_id, fecha_nombramiento, bono_gestion) VALUES (?, ?, ?)",
        (gerente1.id, gerente1.fecha_nombramiento, gerente1.bono_gestion)
    )

    # El gerente debe pertenecer al departamento que dirige.
    cursor.execute("SELECT departamento_id FROM empleado WHERE id = ?", (gerente1.id,))
    fila = cursor.fetchone()
    if fila is None or fila[0] != departamento2.id:
        raise ValueError("El gerente no pertenece al departamento indicado.")
    cursor.execute(
        "UPDATE departamento SET gerente_id = ? WHERE id = ?",
        (gerente1.id, departamento2.id)
    )
    conexion.commit()

    # Se usan los metodos de las clases, como en el material del profesor.
    empleado1.mostrar_info()
    gerente1.mostrar_info()
    cursor.execute("SELECT id, nombre, email, salario_base, departamento_id FROM empleado")
    print("\nLISTADO DE EMPLEADOS")
    for fila in cursor.fetchall():
        print(f"ID: {fila[0]} | Nombre: {fila[1]} | Email: {fila[2]} | Salario: {fila[3]} | Departamento: {fila[4]}")

    cursor.execute(
        "UPDATE empleado SET email = ? WHERE id = ?",
        ("ana.actualizada@example.com", empleado1.id)
    )
    cursor.execute(
        "UPDATE gerente SET bono_gestion = ? WHERE empleado_id = ?",
        (180000, gerente1.id)
    )
    conexion.commit()
    cursor.execute("SELECT id, nombre, email FROM empleado WHERE id = ?", (empleado1.id,))
    print("Empleado actualizado:", cursor.fetchone())
    cursor.execute("SELECT empleado_id, fecha_nombramiento, bono_gestion FROM gerente")
    print("GERENTES DESPUES DEL UPDATE")
    for fila in cursor.fetchall():
        print(f"Empleado ID: {fila[0]} | Nombramiento: {fila[1]} | Bono: {fila[2]}")

    # ======================================================
    # 5. CRUD PROYECTO
    # ======================================================
    print("\n========== CRUD PROYECTO ==========")
    proyecto1 = Proyecto(None, "Sistema de reciclaje", "Registro de materiales",
                         "2026-11-01", "PLANIFICADO")
    proyecto2 = Proyecto(None, "Control de energia", "Registro de consumo",
                         "2026-11-01", "PLANIFICADO")
    cursor.execute(
        "INSERT INTO proyecto (nombre, descripcion, fecha_inicio, estado) VALUES (?, ?, ?, ?)",
        (proyecto1.nombre, proyecto1.descripcion, proyecto1.fecha_inicio, proyecto1.estado)
    )
    proyecto1.id = cursor.lastrowid
    cursor.execute(
        "INSERT INTO proyecto (nombre, descripcion, fecha_inicio, estado) VALUES (?, ?, ?, ?)",
        (proyecto2.nombre, proyecto2.descripcion, proyecto2.fecha_inicio, proyecto2.estado)
    )
    proyecto2.id = cursor.lastrowid
    conexion.commit()
    cursor.execute("SELECT id, nombre, fecha_inicio, estado FROM proyecto")
    print("LISTADO DE PROYECTOS")
    for fila in cursor.fetchall():
        print(f"ID: {fila[0]} | Proyecto: {fila[1]} | Inicio: {fila[2]} | Estado: {fila[3]}")

    cursor.execute("UPDATE proyecto SET estado = ? WHERE id = ?", ("EN_CURSO", proyecto1.id))
    conexion.commit()
    cursor.execute("SELECT id, nombre, estado FROM proyecto WHERE id = ?", (proyecto1.id,))
    print("Proyecto actualizado:", cursor.fetchone())

    # ======================================================
    # 6. CRUD ASIGNACION
    # ======================================================
    print("\n========== CRUD ASIGNACION ==========")
    asignacion1 = Asignacion(None, empleado1.id, proyecto1.id, "2026-11-10", "Programador")
    asignacion2 = Asignacion(None, gerente1.id, proyecto2.id, "2026-11-10", "Coordinador")
    # Se comprueba que no exista otra asignacion sin finalizar para esta pareja.
    cursor.execute(
        "SELECT id FROM asignacion WHERE empleado_id = ? AND proyecto_id = ? AND fecha_fin IS NULL",
        (asignacion1.empleado_id, asignacion1.proyecto_id)
    )
    if cursor.fetchone() is not None:
        raise ValueError("El empleado ya tiene una asignacion vigente en ese proyecto.")
    cursor.execute(
        """INSERT INTO asignacion
        (empleado_id, proyecto_id, fecha_inicio, fecha_fin, rol_proyecto)
        VALUES (?, ?, ?, ?, ?)""",
        (asignacion1.empleado_id, asignacion1.proyecto_id, asignacion1.fecha_inicio,
         asignacion1.fecha_fin, asignacion1.rol_proyecto)
    )
    asignacion1.id = cursor.lastrowid
    # Se comprueba que no exista otra asignacion sin finalizar para esta pareja.
    cursor.execute(
        "SELECT id FROM asignacion WHERE empleado_id = ? AND proyecto_id = ? AND fecha_fin IS NULL",
        (asignacion2.empleado_id, asignacion2.proyecto_id)
    )
    if cursor.fetchone() is not None:
        raise ValueError("El empleado ya tiene una asignacion vigente en ese proyecto.")
    cursor.execute(
        """INSERT INTO asignacion
        (empleado_id, proyecto_id, fecha_inicio, fecha_fin, rol_proyecto)
        VALUES (?, ?, ?, ?, ?)""",
        (asignacion2.empleado_id, asignacion2.proyecto_id, asignacion2.fecha_inicio,
         asignacion2.fecha_fin, asignacion2.rol_proyecto)
    )
    asignacion2.id = cursor.lastrowid
    conexion.commit()
    cursor.execute("SELECT id, empleado_id, proyecto_id, fecha_inicio, rol_proyecto FROM asignacion")
    print("LISTADO DE ASIGNACIONES")
    for fila in cursor.fetchall():
        print(f"ID: {fila[0]} | Empleado: {fila[1]} | Proyecto: {fila[2]} | Inicio: {fila[3]} | Rol: {fila[4]}")

    cursor.execute("UPDATE asignacion SET rol_proyecto = ? WHERE id = ?", ("Desarrollador Python", asignacion1.id))
    conexion.commit()
    cursor.execute("SELECT id, rol_proyecto FROM asignacion WHERE id = ?", (asignacion1.id,))
    print("Asignacion actualizada:", cursor.fetchone())

    # ======================================================
    # 7. CRUD REGISTRO DE TIEMPO
    # ======================================================
    print("\n========== CRUD REGISTRO DE TIEMPO ==========")
    registro1 = RegistroTiempo(None, asignacion1.id, "2026-11-17", 6, "Programacion de clases")
    registro2 = RegistroTiempo(None, asignacion2.id, "2026-11-17", 4, "Coordinacion del proyecto")

    # El for evita repetir las mismas validaciones para ambos registros.
    for registro in (registro1, registro2):
        cursor.execute(
            "SELECT empleado_id, fecha_inicio, fecha_fin FROM asignacion WHERE id = ?",
            (registro.asignacion_id,)
        )
        fila = cursor.fetchone()
        if fila is None:
            raise ValueError("La asignacion indicada no existe.")
        if registro.fecha < fila[1] or (fila[2] is not None and registro.fecha > fila[2]):
            raise ValueError("La fecha del registro esta fuera de la asignacion.")

        # Suma de horas de ese empleado, incluso si tiene varios proyectos.
        cursor.execute(
            """SELECT COALESCE(SUM(registro_tiempo.horas), 0)
            FROM registro_tiempo
            JOIN asignacion ON registro_tiempo.asignacion_id = asignacion.id
            WHERE asignacion.empleado_id = ? AND registro_tiempo.fecha = ?""",
            (fila[0], registro.fecha)
        )
        total_horas = cursor.fetchone()[0]
        if total_horas + registro.horas > 24:
            raise ValueError("El empleado supera 24 horas registradas en el dia.")
        cursor.execute(
            "INSERT INTO registro_tiempo (asignacion_id, fecha, horas, descripcion) VALUES (?, ?, ?, ?)",
            (registro.asignacion_id, registro.fecha, registro.horas, registro.descripcion)
        )
        registro.id = cursor.lastrowid
    conexion.commit()

    cursor.execute("SELECT id, asignacion_id, fecha, horas, descripcion FROM registro_tiempo")
    print("LISTADO DE REGISTROS")
    for fila in cursor.fetchall():
        print(f"ID: {fila[0]} | Asignacion: {fila[1]} | Fecha: {fila[2]} | Horas: {fila[3]} | Descripcion: {fila[4]}")

    cursor.execute(
        "UPDATE registro_tiempo SET descripcion = ? WHERE id = ?",
        ("Programacion y revision de clases", registro1.id)
    )
    conexion.commit()
    cursor.execute("SELECT id, descripcion FROM registro_tiempo WHERE id = ?", (registro1.id,))
    print("Registro actualizado:", cursor.fetchone())

    # ======================================================
    # 8. DELETE DE LOS DATOS DE ESTA DEMOSTRACION
    # ======================================================
    # Igual que el ejemplo docente: primero se eliminan las filas dependientes.
    # Se usan SOLO los ID obtenidos en esta ejecucion; no se vacian tablas.
    print("\n========== DELETE ==========")
    cursor.execute("DELETE FROM registro_tiempo WHERE id = ?", (registro1.id,))
    cursor.execute("DELETE FROM registro_tiempo WHERE id = ?", (registro2.id,))
    cursor.execute("DELETE FROM asignacion WHERE id = ?", (asignacion1.id,))
    cursor.execute("DELETE FROM asignacion WHERE id = ?", (asignacion2.id,))
    cursor.execute("DELETE FROM proyecto WHERE id = ?", (proyecto1.id,))
    cursor.execute("DELETE FROM proyecto WHERE id = ?", (proyecto2.id,))

    # Se retira la referencia al gerente antes de eliminar su ficha.
    cursor.execute("UPDATE departamento SET gerente_id = NULL WHERE id = ?", (departamento2.id,))
    cursor.execute("DELETE FROM gerente WHERE empleado_id = ?", (gerente1.id,))
    cursor.execute("DELETE FROM empleado WHERE id = ?", (empleado1.id,))
    cursor.execute("DELETE FROM empleado WHERE id = ?", (gerente1.id,))
    cursor.execute("DELETE FROM departamento WHERE id = ?", (departamento1.id,))
    cursor.execute("DELETE FROM departamento WHERE id = ?", (departamento2.id,))
    conexion.commit()
    print("Datos de demostracion eliminados correctamente.")
    print("Las tablas y los datos anteriores se conservan.")
    print("\nPROCESO TERMINADO")

except ValueError as error:
    if conexion is not None:
        conexion.rollback()
    print("Error de validacion:", error)

except sqlite3.IntegrityError:
    if conexion is not None:
        conexion.rollback()
    print("No se pudo guardar: revise las relaciones y los valores permitidos.")

except sqlite3.Error:
    if conexion is not None:
        conexion.rollback()
    print("No se pudo completar la operacion con la base de datos.")

finally:
    if cursor is not None:
        cursor.close()
    if conexion is not None:
        conexion.close()
        print("Conexion cerrada correctamente.")
