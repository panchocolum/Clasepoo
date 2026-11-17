from generador_informe import GeneradorInforme


class InformeExcel(GeneradorInforme):
    def __init__(self, titulo):
        super().__init__(titulo)
        self.nombre_hoja = "Empleados"

    def generar(self, datos, ruta):
        from openpyxl import Workbook
        from openpyxl.styles import Font

        libro = Workbook()
        hoja = libro.active
        hoja.title = self.nombre_hoja
        hoja.append([self.titulo])
        hoja.append([self.fecha_generacion.strftime("%Y-%m-%d %H:%M")])
        for fila in datos:
            # Un nombre ingresado por una persona no debe ejecutarse como formula.
            segura = []
            for valor in fila:
                if isinstance(valor, str) and valor.startswith(("=", "+", "-", "@")):
                    valor = "'" + valor
                segura.append(valor)
            hoja.append(segura)
        for celda in hoja[3]:
            celda.font = Font(bold=True)
        for letra in ("A", "B", "C", "D", "E"):
            hoja.column_dimensions[letra].width = 25
        libro.save(ruta)
        libro.close()
        return str(ruta)
