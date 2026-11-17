import sqlite3
from base_datos import BaseDatos
from repositorio_gestion import RepositorioGestion
from repositorio_usuarios import RepositorioUsuarios
from servicio_contrasenas import ServicioContrasenas
from servicio_autenticacion import ServicioAutenticacion
from aplicacion_cli import AplicacionCLI


def main():
    base = BaseDatos()
    try:
        base.inicializar()
        gestion = RepositorioGestion(base)
        usuarios = RepositorioUsuarios(base)
        contrasenas = ServicioContrasenas()
        autenticacion = ServicioAutenticacion(usuarios, contrasenas)
        AplicacionCLI(gestion, usuarios, contrasenas, autenticacion).iniciar()
    except sqlite3.Error:
        print("No se pudo iniciar la base de datos. Revise la carpeta y sus permisos.")
    except (KeyboardInterrupt, EOFError):
        print("\nPrograma finalizado.")
    finally:
        base.cerrar()


if __name__ == "__main__":
    main()
