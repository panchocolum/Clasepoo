from enum import Enum


class EstadoProyecto(Enum):
    PLANIFICADO = "PLANIFICADO"
    EN_CURSO = "EN_CURSO"
    FINALIZADO = "FINALIZADO"
    CANCELADO = "CANCELADO"
