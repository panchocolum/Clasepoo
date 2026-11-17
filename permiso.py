class Permiso:
    def __init__(self, codigo, modulo, accion):
        self.codigo = codigo
        self.modulo = modulo
        self.accion = accion

    def mostrar_info(self):
        print(f"Permiso: {self.codigo}")
