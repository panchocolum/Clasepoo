import sqlite3
from datetime import date, datetime
from getpass import getpass
from pathlib import Path
from empleado import Empleado
from gerente import Gerente
from departamento import Departamento
from proyecto import Proyecto
from asignacion import Asignacion
from registro_tiempo import RegistroTiempo
from usuario import Usuario
from rol import Rol
from informe_pdf import InformePDF
from informe_excel import InformeExcel


class AplicacionCLI:
    def __init__(self, gestion, usuarios, contrasenas, autenticacion):
        self.gestion = gestion
        self.usuarios = usuarios
        self.contrasenas = contrasenas
        self.autenticacion = autenticacion
        self.sesion = None

    def iniciar(self):
        print("========== ECOTECH SOLUTIONS ==========")
        while True:
            try:
                if self.usuarios.contar() == 0:
                    self.configurar_cuenta_inicial()
                if self.sesion is not None and not self.autenticacion.autorizar(self.sesion, "sistema.leer"):
                    self.autenticacion.cerrar_sesion(self.sesion)
                    self.sesion = None
                if self.sesion is None or not self.sesion.esta_vigente():
                    if input("1. Iniciar sesion | 0. Salir: ") != "1":
                        break
                    self.iniciar_sesion()
                if not self.mostrar_menu():
                    break
            except ValueError as error:
                print("Revise los datos:", error)
            except sqlite3.IntegrityError:
                print("No se guardo: hay datos duplicados o relaciones no validas.")
            except sqlite3.Error:
                print("No se pudo completar la operacion con la base de datos.")
            except ImportError:
                print("Falta una libreria de informes. Ejecute: python -m pip install -r requirements.txt")
            except OSError:
                print("No se pudo escribir el informe. Compruebe que el archivo no este abierto.")
        if self.sesion is not None:
            self.autenticacion.cerrar_sesion(self.sesion)

    def configurar_cuenta_inicial(self):
        print("Primera ejecucion: cree su propia cuenta administradora.")
        nombre = input("Nombre del responsable: ")
        email = input("Email: ")
        usuario = input("Nombre de usuario: ")
        clave = getpass("Clave (10 a 128 caracteres): ")
        if clave != getpass("Repita la clave: "):
            raise ValueError("Las claves no coinciden.")
        resumen = self.contrasenas.generar_hash(clave)
        empleado = Empleado(None, nombre, "", "", email, date.today().isoformat(), 0, 1, None)
        cuenta = Usuario(None, None, usuario, resumen, roles=[Rol(None, "Administrador")])
        self.gestion.crear_empleado(empleado)
        cuenta.empleado_id = empleado.id
        try:
            self.usuarios.crear(cuenta)
        except (sqlite3.Error, ValueError):
            self.gestion.eliminar_empleado(empleado.id)
            raise
        print("Cuenta creada. No se almacenan claves en texto plano.")

    def iniciar_sesion(self):
        self.sesion = self.autenticacion.autenticar(input("Usuario: "), getpass("Clave: "))
        print("Sesion iniciada.")

    def exigir_permiso(self, codigo):
        if not self.autenticacion.autorizar(self.sesion, codigo):
            raise ValueError("Su sesion no tiene permiso para esta operacion.")

    def mostrar_menu(self):
        self.exigir_permiso("sistema.leer")
        print("\n1. Empleados y gerentes\n2. Departamentos\n3. Proyectos\n4. Asignaciones")
        print("5. Horas\n6. Informes\n7. Crear usuario\n8. Cambiar clave\n9. Cerrar sesion\n0. Salir")
        opcion = input("Opcion: ")
        if opcion == "1": self.gestionar_empleados()
        elif opcion == "2": self.gestionar_departamentos()
        elif opcion == "3": self.gestionar_proyectos()
        elif opcion == "4": self.gestionar_asignaciones()
        elif opcion == "5": self.gestionar_horas()
        elif opcion == "6": self.exportar_informe()
        elif opcion == "7": self.crear_usuario()
        elif opcion == "8":
            actual = getpass("Clave actual: ")
            nueva = getpass("Clave nueva: ")
            if nueva != getpass("Repita la clave nueva: "):
                raise ValueError("Las claves no coinciden.")
            self.autenticacion.cambiar_clave(self.sesion, actual, nueva)
            print("Clave actualizada.")
        elif opcion == "9":
            self.autenticacion.cerrar_sesion(self.sesion)
            self.sesion = None
        elif opcion == "0": return False
        else: print("Opcion no valida.")
        return True

    def gestionar_empleados(self):
        self.exigir_permiso("sistema.leer")
        opcion = input("1. Registrar | 2. Listar | 3. Actualizar | 4. Eliminar/dar baja | 0. Volver: ")
        if opcion == "2":
            for empleado in self.gestion.listar_empleados(): empleado.mostrar_info()
            return
        if opcion == "0": return
        self.exigir_permiso("gestion.editar")
        if opcion == "1":
            nombre = input("Nombre: ")
            direccion = input("Direccion: ")
            telefono = input("Telefono: ")
            email = input("Email: ")
            fecha = input("Contratacion (AAAA-MM-DD): ")
            salario = int(input("Salario en pesos enteros: "))
            dep = input("ID departamento (vacio: sin departamento): ")
            dep = None if not dep.strip() else int(dep)
            tipo = input("Es gerente? (s/n): ").lower()
            if tipo == "s":
                empleado = Gerente(None, nombre, direccion, telefono, email, fecha, salario, 1, dep,
                                   input("Nombramiento (AAAA-MM-DD): "), int(input("Bono en pesos enteros: ")))
            elif tipo == "n":
                empleado = Empleado(None, nombre, direccion, telefono, email, fecha, salario, 1, dep)
            else: raise ValueError("Responda s o n.")
            print("ID creado:", self.gestion.crear_empleado(empleado))
        elif opcion == "3":
            empleado = self.gestion.obtener_empleado(int(input("ID empleado: ")))
            if empleado is None: raise ValueError("El empleado no existe.")
            empleado.actualizar_contacto(input("Nuevo email: "), input("Nuevo telefono: "))
            empleado.cambiar_salario(int(input("Nuevo salario: ")))
            if isinstance(empleado, Gerente):
                bono = int(input("Nuevo bono: "))
                if bono < 0: raise ValueError("El bono no puede ser negativo.")
                empleado.bono_gestion = bono
            self.gestion.actualizar_empleado(empleado)
            print("Empleado actualizado.")
        elif opcion == "4":
            id = int(input("ID empleado: "))
            if id == self.sesion.usuario.empleado_id:
                raise ValueError("No puede dar de baja su propia cuenta desde esta sesion.")
            print(self.gestion.eliminar_empleado(id))
        else: print("Opcion no valida.")

    def gestionar_departamentos(self):
        self.exigir_permiso("sistema.leer")
        opcion = input("1. Crear | 2. Listar | 3. Renombrar | 4. Eliminar | 5. Asignar empleado | 6. Designar gerente | 0. Volver: ")
        if opcion == "2":
            for departamento in self.gestion.listar_departamentos(): departamento.mostrar_info()
            return
        if opcion == "0": return
        self.exigir_permiso("gestion.editar")
        if opcion == "1":
            print("ID creado:", self.gestion.guardar_departamento(Departamento(None, input("Nombre: "))))
        elif opcion == "3":
            id = int(input("ID departamento: "))
            self.gestion.guardar_departamento(Departamento(id, input("Nuevo nombre: ")))
            print("Departamento actualizado.")
        elif opcion == "4":
            self.gestion.eliminar_departamento(int(input("ID departamento: ")))
            print("Departamento eliminado.")
        elif opcion == "5":
            empleado_id = int(input("ID empleado: "))
            dep = input("ID departamento (vacio: retirar asignacion): ")
            self.gestion.asignar_departamento(empleado_id, None if not dep.strip() else int(dep))
            print("Departamento del empleado actualizado.")
        elif opcion == "6":
            departamento_id = int(input("ID departamento: "))
            self.gestion.designar_gerente(departamento_id, int(input("ID empleado gerente: ")))
            print("Gerente designado.")
        else: print("Opcion no valida.")

    def gestionar_proyectos(self):
        self.exigir_permiso("sistema.leer")
        opcion = input("1. Crear | 2. Listar | 3. Actualizar | 4. Eliminar/cancelar | 0. Volver: ")
        if opcion == "2":
            for proyecto in self.gestion.listar_proyectos(): proyecto.mostrar_info()
            return
        if opcion == "0": return
        self.exigir_permiso("gestion.editar")
        if opcion == "1":
            proyecto = Proyecto(None, input("Nombre: "), input("Descripcion: "), input("Inicio (AAAA-MM-DD): "), "PLANIFICADO")
            print("ID creado:", self.gestion.crear_proyecto(proyecto))
        elif opcion == "3":
            proyecto = self.gestion.obtener_proyecto(int(input("ID proyecto: ")))
            if proyecto is None: raise ValueError("El proyecto no existe.")
            proyecto.cambiar_estado(input("Estado: PLANIFICADO / EN_CURSO / FINALIZADO / CANCELADO: ").upper())
            self.gestion.actualizar_proyecto(proyecto)
            print("Proyecto actualizado.")
        elif opcion == "4": print(self.gestion.eliminar_proyecto(int(input("ID proyecto: "))))
        else: print("Opcion no valida.")

    def gestionar_asignaciones(self):
        self.exigir_permiso("sistema.leer")
        opcion = input("1. Crear | 2. Listar | 3. Finalizar | 4. Eliminar sin horas | 0. Volver: ")
        if opcion == "2":
            for asignacion in self.gestion.listar_asignaciones(): asignacion.mostrar_info()
            return
        if opcion == "0": return
        self.exigir_permiso("gestion.editar")
        if opcion == "1":
            asignacion = Asignacion(None, int(input("ID empleado: ")), int(input("ID proyecto: ")),
                                    input("Inicio (AAAA-MM-DD): "), input("Rol en el proyecto: "))
            print("ID creado:", self.gestion.crear_asignacion(asignacion))
        elif opcion == "3":
            self.gestion.finalizar_asignacion(int(input("ID asignacion: ")), input("Fin (AAAA-MM-DD): "))
            print("Asignacion finalizada.")
        elif opcion == "4":
            self.gestion.eliminar_asignacion(int(input("ID asignacion: ")))
            print("Asignacion eliminada.")
        else: print("Opcion no valida.")

    def gestionar_horas(self):
        self.exigir_permiso("sistema.leer")
        opcion = input("1. Registrar | 2. Listar | 3. Actualizar | 4. Eliminar | 0. Volver: ")
        if opcion == "2":
            id = int(input("ID empleado: "))
            registros = self.gestion.listar_horas(id, input("Desde (AAAA-MM-DD): "), input("Hasta (AAAA-MM-DD): "))
            for registro in registros: registro.mostrar_info()
            print("Total de horas:", sum(r.horas for r in registros))
            return
        if opcion == "0": return
        self.exigir_permiso("gestion.editar")
        if opcion in ("1", "3"):
            id = None if opcion == "1" else int(input("ID registro: "))
            registro = RegistroTiempo(id, int(input("ID asignacion: ")), input("Fecha (AAAA-MM-DD): "),
                                      float(input("Horas: ")), input("Descripcion: "))
            print("Registro guardado:", self.gestion.registrar_tiempo(registro))
        elif opcion == "4":
            self.gestion.eliminar_registro(int(input("ID registro: ")))
            print("Registro eliminado.")
        else: print("Opcion no valida.")

    def crear_usuario(self):
        self.exigir_permiso("usuario.crear")
        id = int(input("ID empleado existente: "))
        nombre = input("Usuario nuevo: ")
        rol = input("Rol (Administrador / Consulta): ")
        if rol not in ("Administrador", "Consulta"): raise ValueError("El rol no es valido.")
        clave = getpass("Clave nueva: ")
        if clave != getpass("Repita la clave: "): raise ValueError("Las claves no coinciden.")
        cuenta = Usuario(None, id, nombre, self.contrasenas.generar_hash(clave), roles=[Rol(None, rol)])
        print("Usuario creado:", self.usuarios.crear(cuenta))

    def exportar_informe(self):
        self.exigir_permiso("informe.exportar")
        formato = input("Formato (pdf / excel): ").lower()
        datos = [["ID", "Nombre", "Email", "Salario", "Activo"]]
        for empleado in self.gestion.listar_empleados():
            datos.append([empleado.id, empleado.nombre, empleado.email, empleado.salario_base, empleado.activo])
        carpeta = Path(__file__).resolve().parent / "informes"
        carpeta.mkdir(exist_ok=True)
        nombre = "empleados_" + datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        if formato == "pdf":
            informe = InformePDF("Empleados de EcoTech")
            ruta = carpeta / (nombre + ".pdf")
        elif formato == "excel":
            informe = InformeExcel("Empleados de EcoTech")
            ruta = carpeta / (nombre + ".xlsx")
        else: raise ValueError("Seleccione pdf o excel.")
        print("Informe creado:", informe.generar(datos, ruta))
