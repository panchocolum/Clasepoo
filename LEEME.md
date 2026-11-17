# EcoTech Solutions — Python y SQLite3

Implementación de las **22 clases y enumeraciones** del UML unificado, según la opción 2 elegida. No contiene APIs ni conexiones a servicios externos. Los archivos del profesor no fueron modificados.

## 1. Ejecutar

Extraiga el ZIP completo en una carpeta. Abra esa carpeta en Visual Studio Code y use la terminal:

```powershell
python -m pip install -r requirements.txt
python main.py
```

Si su equipo usa el lanzador `py`, puede sustituir `python` por `py`. Requiere Python 3.10 o posterior. `sqlite3` viene con Python: no se instala por separado.

La primera ejecución solicita nombre, email, usuario y una clave de 10 a 128 caracteres. Crea un empleado responsable sin departamento, con sueldo inicial cero, y su cuenta administradora. No existe una clave predeterminada. Al escribir la contraseña en la terminal, los caracteres no se muestran: es normal. Ejecute el programa desde una terminal, no desde una salida de consola que no admita entradas.

Después, elija `1` para iniciar sesión. El menú permite gestionar empleados, gerentes, departamentos, proyectos, asignaciones, horas, usuarios e informes. El rol Administrador puede modificar y exportar; el rol Consulta solo puede consultar los módulos y cambiar su propia clave.

## 2. Base de datos

`ecotech.db` ya contiene las tablas y el catálogo de roles/permisos, **sin empleados, cuentas ni contraseñas de ejemplo**. El programa la usa desde la misma carpeta de `main.py`. Los cambios se conservan entre ejecuciones.

Tablas: departamento, empleado, gerente, proyecto, asignacion, registro_tiempo, usuario, rol, permiso, usuario_rol y rol_permiso.

`Persona` no necesita una tabla propia: sus atributos se guardan en empleado. Gerente usa el mismo identificador del empleado y una tabla con los datos adicionales. Sesion permanece en memoria. Los servicios, repositorios, validadores, informes y el menú son clases de Python, no tablas.

`esquema.sql` incluye las sentencias de creación para estudiar la estructura. La inicialización del programa agrega los roles y permisos; el SQL por sí solo no crea cuentas.

## 3. Orden para probar a mano

1. Crear la cuenta inicial e iniciar sesión.
2. Crear un departamento.
3. Registrar un empleado o gerente usando el ID de ese departamento.
4. Si creó un gerente, designarlo desde Departamentos.
5. Crear un proyecto y cambiarlo a EN_CURSO.
6. Asignar el empleado al proyecto. La fecha no puede preceder al inicio del proyecto ni a la contratación.
7. Registrar horas en una fecha de la asignación.
8. Consultar los registros, actualizar datos y exportar el listado de empleados.
9. Cerrar y volver a abrir el programa para comprobar la persistencia.

Los informes se guardan en la carpeta `informes`, con fecha y hora para evitar sobrescribir archivos. PDF usa ReportLab y Excel usa openpyxl. El resto de la aplicación funciona con la biblioteca estándar, aunque falten esas dos librerías.

## 4. Qué se conserva del profesor

- Clases en archivos separados; constructores `__init__`, atributos de instancia y métodos `mostrar_info()` en las entidades.
- `import sqlite3`, conexión, cursor y consultas SQL escritas explícitamente.
- `CREATE TABLE IF NOT EXISTS`, `INSERT`, `SELECT`, `UPDATE` y `DELETE`.
- Parámetros `?`, `lastrowid`, `fetchone()` y `fetchall()`.
- Claves foráneas, confirmación de cambios y reversión ante errores.
- Uso de `print`, `input`, `if`, `for`, `try`, `except` y `finally`.

**La aplicación completa no es una copia línea por línea del ejemplo:** su ejemplo tiene tres clases y un script secuencial; usted eligió implementar las 22 clases del UML. Por eso, el SQL se distribuyó en BaseDatos y repositorios, y el menú en AplicacionCLI. No se usaron frameworks, ORM, servicios web ni programación asíncrona.

Las adiciones necesarias para ese UML son `super()` para herencia; ABC y abstractmethod para clases abstractas; Enum para estados; datetime para fechas/sesiones; pathlib para rutas; hashlib, secrets y hmac para claves; y dos librerías para los informes. `with conexion` es el contexto de sqlite3: hace commit si termina bien y rollback si ocurre una excepción. `JOIN` permite recuperar relaciones y `SUM` comprobar el total diario de horas.

## 5. Demostración similar al profesor

```powershell
python demo_crud.py
```

Este archivo muestra el CRUD paso a paso sobre datos ficticios, sin menú ni autenticación. **Al terminar elimina únicamente los registros que él mismo creó**, igual que el ejemplo del profesor; no vacía tablas ni elimina registros anteriores. Se entrega como ejercicio de estudio, no como una segunda interfaz segura. La aplicación que debe usarse para gestionar información es `main.py`.

## 6. Archivos y correspondencia

| Archivo | Clase y responsabilidad |
|---|---|
| persona.py | Persona, base abstracta de los datos personales |
| empleado.py | Empleado, datos laborales |
| gerente.py | Gerente, especialización de Empleado |
| departamento.py | Departamento |
| proyecto.py | Proyecto |
| estado_proyecto.py | EstadoProyecto, enumeración |
| asignacion.py | Asignacion entre empleado y proyecto |
| registro_tiempo.py | RegistroTiempo de una asignación |
| usuario.py | Usuario y sus roles |
| rol.py | Rol y su colección de permisos |
| permiso.py | Permiso |
| sesion.py | Sesion local en memoria |
| servicio_contrasenas.py | ServicioContrasenas |
| servicio_autenticacion.py | ServicioAutenticacion |
| validador_entrada.py | ValidadorEntrada |
| base_datos.py | BaseDatos y creación de tablas |
| repositorio_gestion.py | RepositorioGestion, operaciones SQL del negocio |
| repositorio_usuarios.py | RepositorioUsuarios, cuentas/roles/permisos |
| generador_informe.py | GeneradorInforme abstracto |
| informe_pdf.py | InformePDF |
| informe_excel.py | InformeExcel |
| aplicacion_cli.py | AplicacionCLI, menú y validación de permisos |
| main.py | Construye los objetos y conecta las clases |

## 7. Ajustes concretos respecto del UML anterior

La carpeta `UML` incluye una lámina unificada en blanco y negro, en draw.io, XML, SVG, PNG y HTML. Sus clases, atributos y firmas de métodos se obtuvieron de los archivos Python para reflejar los nombres efectivamente implementados; se omiten los constructores y las anotaciones de tipos en esa vista. El constructor completo se encuentra en cada archivo.

- Los nombres de métodos usan snake_case en Python: `obtenerResumen` pasa a `obtener_resumen`, por ejemplo. Se agregaron `mostrar_info` y los métodos auxiliares de consulta/eliminación necesarios para el menú.
- Se conservan atributos públicos como en el ejemplo docente. Por tanto, los signos privados/protegidos del UML anterior se actualizaron en la vista de implementación: las validaciones se realizan en constructores, métodos y repositorios. No se afirma que Python impida a otro script asignar directamente un atributo. Si el docente exige encapsulamiento con propiedades o atributos privados, ese punto deberá ajustarse.
- Para simplificar la persistencia y evitar cálculos monetarios con coma flotante, salario y bono usan enteros en pesos sin centavos. No se implementan conversiones. Las horas admiten fracciones mediante float/REAL. Este ajuste de tipos debe figurar en el UML de implementación.
- Las asociaciones se representan con identificadores, como `alumno_id` y `curso_id` en Matricula del profesor. En Usuario y Rol se usan listas de objetos para permisos.
- EstadoProyecto valida el valor; Proyecto conserva su representación textual para SQLite.
- Las tablas y la aplicación no imponen todas las reglas de negocio por sí solas: algunas reglas de fecha, permisos y horas se verifican en Python. No se debe editar la DB directamente esperando las mismas validaciones del menú.

## 8. Reglas del programa

- No se permiten asignaciones superpuestas para la misma pareja empleado/proyecto.
- Las horas deben estar dentro de la asignación, ser mayores que cero y no superar 24 en total diario por empleado.
- Un gerente dirige un departamento al que pertenece. Al cambiarlo de departamento se retira la designación anterior.
- Un empleado con asignaciones o cuenta recibe una baja lógica; su cuenta se desactiva. Sin referencias se permite DELETE. El menú impide dar de baja la propia cuenta activa.
- Un proyecto con asignaciones se cancela, conservando su historial. Sin asignaciones se permite DELETE.
- Una asignación con horas no se elimina: se finaliza. Las horas sí tienen eliminación explícita para corregir registros.
- Cinco intentos de clave incorrecta bloquean el usuario durante cinco minutos. La sesión dura treinta minutos. La baja de un empleado también impide utilizar su cuenta.
- El inicio de sesión protege el menú, no cifra el archivo SQLite. Quien tenga acceso local de escritura al archivo o al código puede alterarlos. No se presenta como sistema listo para producción.

## 9. Pruebas

```powershell
python -m pip install -r requirements-pruebas.txt
python pruebas.py
```

Las pruebas usan una base temporal y no modifican ecotech.db. Comprueban CRUD, persistencia, claves foráneas, rollback, relaciones, fechas/horas, bajas, permisos, claves, bloqueo, inicio del menú y lectura de las exportaciones.

## 10. Uso de IA y revisión del estudiante

Este código fue generado con apoyo de IA a partir del UML, la guía y los cuatro archivos del profesor. No se atribuyen cambios ni pruebas al estudiante. Antes de entregar, revise y ejecute cada módulo, compare el estilo con lo explicado por el profesor y registre sus propios ajustes. Para la defensa, comience por `demo_crud.py`, después BaseDatos y RepositorioGestion, y finalmente el recorrido `main → AplicacionCLI → servicio/repositorio → sqlite3`.
