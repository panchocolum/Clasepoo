from html import escape
from generador_informe import GeneradorInforme


class InformePDF(GeneradorInforme):
    def __init__(self, titulo):
        super().__init__(titulo)
        self.plantilla = "tabla"

    def generar(self, datos, ruta):
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

        estilos = getSampleStyleSheet()
        filas = [[Paragraph(escape(str(celda)), estilos["BodyText"]) for celda in fila] for fila in datos]
        documento = SimpleDocTemplate(str(ruta), pagesize=landscape(A4))
        tabla = Table(filas, repeatRows=1, colWidths=[documento.width / len(datos[0])] * len(datos[0]))
        tabla.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                                   ("VALIGN", (0, 0), (-1, -1), "TOP")]))
        documento.build([Paragraph(escape(self.titulo), estilos["Title"]),
                         Paragraph(self.fecha_generacion.strftime("%Y-%m-%d %H:%M"), estilos["Normal"]),
                         Spacer(1, 15), tabla])
        return str(ruta)
