import zenoh
import time

class ZenohPub:
    def __init__(self, key_expr, encoding=zenoh.Encoding.APPLICATION_JSON):
        self.key_expr = key_expr
        self.encoding = encoding
        self.session = zenoh.open()
        self.publisher = self.session.declare_publisher(self.key_expr, encoding=self.encoding)

    def send_message(self, message):
        """Envia uma mensagem para o tópico especificado."""
        self.publisher.put(message)
        print(f"Mensagem enviada para '{self.key_expr}': {message}")

    def close(self):
        """Fecha a sessão Zenoh."""
        self.session.close()
        print("Sessão Zenoh fechada.")


