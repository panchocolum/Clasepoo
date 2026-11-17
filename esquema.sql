PRAGMA foreign_keys = ON;

CREATE TABLE asignacion (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        empleado_id INTEGER NOT NULL,
        proyecto_id INTEGER NOT NULL,
        fecha_inicio TEXT NOT NULL,
        fecha_fin TEXT,
        rol_proyecto TEXT NOT NULL CHECK (length(trim(rol_proyecto)) > 0),
        CHECK (fecha_fin IS NULL OR fecha_fin >= fecha_inicio),
        FOREIGN KEY (empleado_id) REFERENCES empleado(id),
        FOREIGN KEY (proyecto_id) REFERENCES proyecto(id)
        );

CREATE TABLE departamento (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL CHECK (length(trim(nombre)) > 0),
        gerente_id INTEGER UNIQUE,
        FOREIGN KEY (gerente_id) REFERENCES gerente(empleado_id)
        );

CREATE TABLE empleado (
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
        );

CREATE TABLE gerente (
        empleado_id INTEGER PRIMARY KEY,
        fecha_nombramiento TEXT NOT NULL,
        bono_gestion INTEGER NOT NULL CHECK (bono_gestion >= 0),
        FOREIGN KEY (empleado_id) REFERENCES empleado(id)
        );

CREATE TABLE permiso (codigo TEXT PRIMARY KEY, modulo TEXT NOT NULL, accion TEXT NOT NULL);

CREATE TABLE proyecto (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL CHECK (length(trim(nombre)) > 0),
        descripcion TEXT NOT NULL,
        fecha_inicio TEXT NOT NULL,
        estado TEXT NOT NULL CHECK (
            estado IN ('PLANIFICADO', 'EN_CURSO', 'FINALIZADO', 'CANCELADO')
        )
        );

CREATE TABLE registro_tiempo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        asignacion_id INTEGER NOT NULL,
        fecha TEXT NOT NULL,
        horas REAL NOT NULL CHECK (horas > 0 AND horas <= 24),
        descripcion TEXT NOT NULL CHECK (length(trim(descripcion)) > 0),
        FOREIGN KEY (asignacion_id) REFERENCES asignacion(id)
        );

CREATE TABLE rol (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT NOT NULL UNIQUE);

CREATE TABLE rol_permiso (
 rol_id INTEGER NOT NULL REFERENCES rol(id),
 permiso_codigo TEXT NOT NULL REFERENCES permiso(codigo), PRIMARY KEY (rol_id,permiso_codigo)
);

CREATE TABLE usuario (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 empleado_id INTEGER NOT NULL UNIQUE REFERENCES empleado(id),
 nombre_usuario TEXT NOT NULL UNIQUE,
 hash_codificado TEXT NOT NULL,
 activo INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0,1)),
 intentos_fallidos INTEGER NOT NULL DEFAULT 0,
 bloqueado_hasta TEXT
);

CREATE TABLE usuario_rol (
 usuario_id INTEGER NOT NULL REFERENCES usuario(id),
 rol_id INTEGER NOT NULL REFERENCES rol(id), PRIMARY KEY (usuario_id,rol_id)
);
