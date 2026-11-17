import sqlite3
from pathlib import Path


class BaseDatos:
    def __init__(self, ruta=None):
        self.ruta = Path(ruta) if ruta is not None else Path(__file__).resolve().parent / "ecotech.db"
        self.conexion = None

    def conectar(self):
        if self.conexion is None:
            self.conexion = sqlite3.connect(self.ruta)
            self.conexion.execute("PRAGMA foreign_keys = ON")
        return self.conexion

    def transaccion(self):
        # El contexto de sqlite3 confirma al terminar y revierte si hay un error.
        return self.conectar()

    def cerrar(self):
        if self.conexion is not None:
            self.conexion.close()
            self.conexion = None

    def inicializar(self):
        conexion = self.conectar()
        cursor = conexion.cursor()
        try:
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
            cursor.execute("""
CREATE TABLE IF NOT EXISTS usuario (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 empleado_id INTEGER NOT NULL UNIQUE REFERENCES empleado(id),
 nombre_usuario TEXT NOT NULL UNIQUE,
 hash_codificado TEXT NOT NULL,
 activo INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0,1)),
 intentos_fallidos INTEGER NOT NULL DEFAULT 0,
 bloqueado_hasta TEXT
)
            """)
            cursor.execute("""
CREATE TABLE IF NOT EXISTS rol (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT NOT NULL UNIQUE)
            """)
            cursor.execute("""
CREATE TABLE IF NOT EXISTS permiso (codigo TEXT PRIMARY KEY, modulo TEXT NOT NULL, accion TEXT NOT NULL)
            """)
            cursor.execute("""
CREATE TABLE IF NOT EXISTS usuario_rol (
 usuario_id INTEGER NOT NULL REFERENCES usuario(id),
 rol_id INTEGER NOT NULL REFERENCES rol(id), PRIMARY KEY (usuario_id,rol_id)
)
            """)
            cursor.execute("""
CREATE TABLE IF NOT EXISTS rol_permiso (
 rol_id INTEGER NOT NULL REFERENCES rol(id),
 permiso_codigo TEXT NOT NULL REFERENCES permiso(codigo), PRIMARY KEY (rol_id,permiso_codigo)
)
            """)
            # Permisos iniciales. No se crean usuarios ni claves predeterminadas.
            for nombre in ("Administrador", "Consulta"):
                cursor.execute("INSERT OR IGNORE INTO rol (nombre) VALUES (?)", (nombre,))
            permisos = [("sistema.leer", "sistema", "leer"),
                        ("gestion.editar", "gestion", "editar"),
                        ("informe.exportar", "informe", "exportar"),
                        ("usuario.crear", "usuario", "crear")]
            for codigo, modulo, accion in permisos:
                cursor.execute("INSERT OR IGNORE INTO permiso VALUES (?, ?, ?)", (codigo, modulo, accion))
                cursor.execute("SELECT id FROM rol WHERE nombre = ?", ("Administrador",))
                rol_id = cursor.fetchone()[0]
                cursor.execute("INSERT OR IGNORE INTO rol_permiso VALUES (?, ?)", (rol_id, codigo))
            cursor.execute("SELECT id FROM rol WHERE nombre = ?", ("Consulta",))
            cursor.execute("INSERT OR IGNORE INTO rol_permiso VALUES (?, ?)", (cursor.fetchone()[0], "sistema.leer"))
            conexion.commit()
        except sqlite3.Error:
            conexion.rollback()
            raise
        finally:
            cursor.close()
