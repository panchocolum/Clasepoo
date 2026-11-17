from datetime import datetime, timedelta, timezone


class Sesion:
    def __init__(self, usuario, duracion_minutos=30):
        self.usuario = usuario
        self.creada_en = datetime.now(timezone.utc)
        self.expira_en = self.creada_en + timedelta(minutes=duracion_minutos)
        self.activa = True

    def esta_vigente(self):
        return self.activa and datetime.now(timezone.utc) < self.expira_en

    def cerrar(self):
        self.activa = False
