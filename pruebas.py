"""Pruebas sobre una base temporal: nunca modifican ecotech.db."""
import contextlib
import io
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from base_datos import BaseDatos
from repositorio_gestion import RepositorioGestion
from repositorio_usuarios import RepositorioUsuarios
from empleado import Empleado
from gerente import Gerente
from departamento import Departamento
from proyecto import Proyecto
from asignacion import Asignacion
from registro_tiempo import RegistroTiempo
from usuario import Usuario
from rol import Rol
from servicio_contrasenas import ServicioContrasenas
from servicio_autenticacion import ServicioAutenticacion
from aplicacion_cli import AplicacionCLI
from informe_pdf import InformePDF
from informe_excel import InformeExcel


class PruebasEcoTech(unittest.TestCase):
    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory()
        self.ruta = Path(self.temporal.name) / "prueba.db"
        self.base = BaseDatos(self.ruta)
        self.base.inicializar()
        self.gestion = RepositorioGestion(self.base)
        self.usuarios = RepositorioUsuarios(self.base)
        self.claves = ServicioContrasenas()
        self.auth = ServicioAutenticacion(self.usuarios, self.claves)
        self.empleado = Empleado(None, "Persona de prueba", "", "", "test@example.com", "2026-01-01", 900000, 1, None)
        self.gestion.crear_empleado(self.empleado)
        self.proyecto = Proyecto(None, "Proyecto", "Descripcion", "2026-01-01", "EN_CURSO")
        self.gestion.crear_proyecto(self.proyecto)

    def tearDown(self):
        self.base.cerrar()
        self.temporal.cleanup()

    def asignar(self):
        a = Asignacion(None, self.empleado.id, self.proyecto.id, "2026-02-01", "Programador")
        self.gestion.crear_asignacion(a)
        return a

    def cuenta(self, rol="Administrador"):
        usuario = Usuario(None, self.empleado.id, "prueba", self.claves.generar_hash("Clave de prueba 123"), roles=[Rol(None, rol)])
        self.usuarios.crear(usuario)
        return usuario

    def test_crud_empleado_y_persistencia(self):
        self.empleado.actualizar_contacto("nuevo@example.com", "123")
        self.empleado.cambiar_salario(950000)
        self.gestion.actualizar_empleado(self.empleado)
        self.base.cerrar()
        recuperado = self.gestion.obtener_empleado(self.empleado.id)
        self.assertEqual(recuperado.email, "nuevo@example.com")
        self.assertEqual(recuperado.salario_base, 950000)
        self.gestion.eliminar_empleado(recuperado.id)
        self.assertIsNone(self.gestion.obtener_empleado(recuperado.id))

    def test_claves_foraneas_y_rollback(self):
        empleado = Empleado(None, "Invalido", "", "", "test@example.com", "2026-01-01", 0, 1, 99999)
        with self.assertRaises(sqlite3.IntegrityError):
            self.gestion.crear_empleado(empleado)
        self.assertEqual(len(self.gestion.listar_empleados()), 1)
        self.assertEqual(self.base.conectar().execute("PRAGMA foreign_key_check").fetchall(), [])

    def test_gerente_y_departamento(self):
        d = Departamento(None, "Desarrollo")
        self.gestion.guardar_departamento(d)
        g = Gerente(None, "Gerente", "", "", "gerente@example.com", "2026-01-01", 1000000, 1, d.id, "2026-01-02", 100000)
        self.gestion.crear_empleado(g)
        self.gestion.designar_gerente(d.id, g.id)
        self.assertIsInstance(self.gestion.obtener_empleado(g.id), Gerente)
        self.assertEqual(self.gestion.listar_departamentos()[0].gerente_id, g.id)
        with self.assertRaises(ValueError): self.gestion.eliminar_departamento(d.id)
        self.gestion.asignar_departamento(g.id, None)
        self.assertIsNone(self.gestion.listar_departamentos()[0].gerente_id)
        self.gestion.eliminar_departamento(d.id)

    def test_crud_proyecto(self):
        self.proyecto.cambiar_estado("FINALIZADO")
        self.gestion.actualizar_proyecto(self.proyecto)
        self.assertEqual(self.gestion.obtener_proyecto(self.proyecto.id).estado, "FINALIZADO")
        self.gestion.eliminar_proyecto(self.proyecto.id)
        self.assertIsNone(self.gestion.obtener_proyecto(self.proyecto.id))

    def test_asignacion_superpuesta(self):
        a = self.asignar()
        with self.assertRaises(ValueError): self.asignar()
        self.gestion.finalizar_asignacion(a.id, "2026-02-10")
        otra = Asignacion(None, self.empleado.id, self.proyecto.id, "2026-02-11", "Programador")
        self.gestion.crear_asignacion(otra)
        self.assertEqual(len(self.gestion.listar_asignaciones()), 2)
        self.gestion.eliminar_asignacion(otra.id)

    def test_horas_validacion_y_crud(self):
        a = self.asignar()
        registro = RegistroTiempo(None, a.id, "2026-02-02", 20, "Trabajo")
        self.gestion.registrar_tiempo(registro)
        with self.assertRaises(ValueError):
            self.gestion.registrar_tiempo(RegistroTiempo(None, a.id, "2026-02-02", 5, "Exceso"))
        with self.assertRaises(ValueError):
            self.gestion.registrar_tiempo(RegistroTiempo(None, a.id, "2026-01-01", 1, "Fuera de fecha"))
        registro.actualizar(8, "Actualizado")
        self.gestion.registrar_tiempo(registro)
        self.assertEqual(self.gestion.listar_horas(self.empleado.id, "2026-02-01", "2026-02-28")[0].horas, 8)
        with self.assertRaises(ValueError): self.gestion.finalizar_asignacion(a.id, "2026-02-01")
        with self.assertRaises(ValueError): self.gestion.eliminar_asignacion(a.id)
        self.gestion.eliminar_registro(registro.id)
        self.assertEqual(self.gestion.listar_horas(self.empleado.id, "2026-02-01", "2026-02-28"), [])

    def test_bajas_preservan_historial(self):
        a = self.asignar()
        self.gestion.registrar_tiempo(RegistroTiempo(None, a.id, "2026-02-02", 1, "Trabajo"))
        self.gestion.eliminar_empleado(self.empleado.id)
        self.gestion.eliminar_proyecto(self.proyecto.id)
        self.assertEqual(self.gestion.obtener_empleado(self.empleado.id).activo, 0)
        self.assertEqual(self.gestion.obtener_proyecto(self.proyecto.id).estado, "CANCELADO")
        self.assertEqual(len(self.gestion.listar_horas(self.empleado.id, "2026-02-01", "2026-02-28")), 1)

    def test_hash_y_permisos(self):
        usuario = self.cuenta("Consulta")
        self.assertNotIn("Clave de prueba 123", usuario.hash_codificado)
        sesion = self.auth.autenticar("prueba", "Clave de prueba 123")
        self.assertTrue(self.auth.autorizar(sesion, "sistema.leer"))
        self.assertFalse(self.auth.autorizar(sesion, "gestion.editar"))
        app = AplicacionCLI(self.gestion, self.usuarios, self.claves, self.auth)
        app.sesion = sesion
        with self.assertRaises(ValueError): app.exigir_permiso("usuario.crear")
        self.auth.cerrar_sesion(sesion)
        self.assertFalse(self.auth.autorizar(sesion, "sistema.leer"))

    def test_bloqueo_persistente(self):
        self.cuenta()
        for _ in range(5):
            with self.assertRaises(ValueError): self.auth.autenticar("prueba", "incorrecta")
        self.base.cerrar()
        with self.assertRaises(ValueError): self.auth.autenticar("prueba", "Clave de prueba 123")
        self.assertEqual(self.usuarios.buscar_por_nombre("prueba").intentos_fallidos, 5)

    def test_cambio_clave_y_baja_usuario(self):
        self.cuenta()
        sesion = self.auth.autenticar("prueba", "Clave de prueba 123")
        self.auth.cambiar_clave(sesion, "Clave de prueba 123", "Otra clave segura 456")
        with self.assertRaises(ValueError): self.auth.autenticar("prueba", "Clave de prueba 123")
        self.assertTrue(self.auth.autenticar("prueba", "Otra clave segura 456").esta_vigente())
        self.gestion.eliminar_empleado(self.empleado.id)
        self.assertFalse(self.auth.autorizar(sesion, "sistema.leer"))

    def test_parametros_sql(self):
        self.empleado.nombre = "O'Brien'); DROP TABLE empleado; --"
        self.gestion.actualizar_empleado(self.empleado)
        self.assertEqual(self.gestion.obtener_empleado(self.empleado.id).nombre, self.empleado.nombre)
        self.assertIsNone(self.usuarios.buscar_por_nombre("' OR 1=1 --"))

    def test_datos_no_validos(self):
        for horas in (0, -1, 25, float("nan"), float("inf")):
            with self.assertRaises(ValueError): RegistroTiempo(None, 1, "2026-01-01", horas, "Trabajo")
        with self.assertRaises(ValueError): Proyecto(None, "X", "", "2026-02-30", "PLANIFICADO")
        with self.assertRaises(ValueError): self.empleado.cambiar_salario(-1)

    def test_inicio_y_menu_sin_errores(self):
        app = AplicacionCLI(self.gestion, self.usuarios, self.claves, self.auth)
        respuestas = ["Responsable", "responsable@example.com", "admin", "1", "admin", "1", "2", "0"]
        with patch("builtins.input", side_effect=respuestas), patch("aplicacion_cli.getpass", return_value="Clave de prueba 123"), contextlib.redirect_stdout(io.StringIO()) as salida:
            app.iniciar()
        self.assertIn("Sesion iniciada", salida.getvalue())
        self.assertIn("Responsable", salida.getvalue())
        self.assertEqual(self.usuarios.contar(), 1)

    def test_exportaciones(self):
        from openpyxl import load_workbook
        from pypdf import PdfReader
        datos = [["ID", "Nombre", "Email", "Salario", "Activo"], [1, "=1+1", "demo@example.com", 900000, 1]]
        ruta_excel = Path(self.temporal.name) / "informe.xlsx"
        ruta_pdf = Path(self.temporal.name) / "informe.pdf"
        InformeExcel("Empleados").generar(datos, ruta_excel)
        InformePDF("Empleados").generar(datos, ruta_pdf)
        libro = load_workbook(ruta_excel)
        self.assertEqual(libro.active["B4"].data_type, "s")
        self.assertEqual(libro.active["D4"].value, 900000)
        libro.close()
        self.assertIn("demo@example.com", PdfReader(ruta_pdf).pages[0].extract_text())


if __name__ == "__main__":
    unittest.main(verbosity=2)
