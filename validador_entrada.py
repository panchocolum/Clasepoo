from datetime import date
from decimal import Decimal, InvalidOperation


class ValidadorEntrada:
    def texto_obligatorio(self, valor, max_longitud=150):
        if not isinstance(valor, str) or not valor.strip() or len(valor.strip()) > max_longitud:
            raise ValueError("Ingrese un texto no vacio dentro del largo permitido.")
        return valor.strip()

    def email_valido(self, valor):
        return isinstance(valor, str) and valor.count("@") == 1 and " " not in valor and bool(valor.split("@")[0]) and "." in valor.split("@")[-1]

    def fecha_valida(self, valor):
        try:
            return date.fromisoformat(valor).isoformat() == valor
        except (ValueError, TypeError):
            return False

    def decimal_positivo(self, valor):
        try:
            numero = Decimal(str(valor))
        except InvalidOperation:
            raise ValueError("Ingrese un numero valido.") from None
        if not numero.is_finite() or numero <= 0:
            raise ValueError("El numero debe ser finito y mayor que cero.")
        return numero
