import hashlib
import hmac
import secrets


class ServicioContrasenas:
    def __init__(self):
        self.iteraciones = 600000

    def validar_politica(self, clave):
        if not isinstance(clave, str) or not 10 <= len(clave) <= 128 or not clave.strip():
            raise ValueError("La clave debe tener entre 10 y 128 caracteres y no ser solo espacios.")

    def generar_hash(self, clave):
        self.validar_politica(clave)
        sal = secrets.token_hex(16)
        resumen = hashlib.pbkdf2_hmac("sha256", clave.encode(), bytes.fromhex(sal), self.iteraciones)
        return f"pbkdf2_sha256${self.iteraciones}${sal}${resumen.hex()}"

    def verificar(self, clave, hash_codificado):
        if not isinstance(clave, str) or len(clave) > 128:
            return False
        try:
            algoritmo, vueltas, sal, esperado = hash_codificado.split("$")
            if algoritmo != "pbkdf2_sha256" or not 100000 <= int(vueltas) <= 2000000:
                return False
            obtenido = hashlib.pbkdf2_hmac("sha256", clave.encode(), bytes.fromhex(sal), int(vueltas))
            return hmac.compare_digest(obtenido.hex(), esperado)
        except (ValueError, TypeError):
            return False
