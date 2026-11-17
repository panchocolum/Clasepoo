from abc import ABC, abstractmethod
from validador_entrada import ValidadorEntrada


class Persona(ABC):
    # Clase base: estos datos tambien pertenecen a empleados y gerentes.
    def __init__(self, id, nombre, direccion, telefono, email):
        validador = ValidadorEntrada()
        nombre = validador.texto_obligatorio(nombre)
        if not validador.email_valido(email):
            raise ValueError("El email debe tener un formato valido.")
        self.id = id
        self.nombre = nombre.strip()
        self.direccion = direccion.strip()
        self.telefono = telefono.strip()
        self.email = email.strip()

    def actualizar_contacto(self, email, telefono):
        if not ValidadorEntrada().email_valido(email):
            raise ValueError("El email no es valido.")
        self.email = email.strip()
        self.telefono = telefono.strip()

    @abstractmethod
    def obtener_resumen(self):
        pass

    def mostrar_info(self):
        print(f"ID: {self.id}")
        print(f"Nombre: {self.nombre}")
        print(f"Direccion: {self.direccion}")
        print(f"Telefono: {self.telefono}")
        print(f"Email: {self.email}")
