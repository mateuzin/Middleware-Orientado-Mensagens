import tkinter as tk
import stomp
import threading
import time

class Sensor:
    def __init__(self, nome):
        self.nome = nome
        self.ativo = False
        self.parametro = "temperatura"
        self.min = None
        self.max = None
        self.valor_atual = None
        self.conn = stomp.Connection([('localhost', 61613)])
        self.conn.connect('admin', 'admin', wait=True)

        # Registrar o sensor no tópico de descoberta
        self.conn.send(body=nome, destination='/topic/discovery')

        self.root = tk.Toplevel()
        self.root.title(f"Sensor {self.nome}")

        self.lbl_parametro = tk.Label(self.root, text="Parâmetro:")
        self.lbl_parametro.pack()
        self.parametro_var = tk.StringVar(self.root)
        self.parametro_var.set("temperatura")  # valor padrão
        self.option_parametro = tk.OptionMenu(self.root, self.parametro_var, "temperatura", "umidade", "velocidade")
        self.option_parametro.pack()

        self.lbl_valor_atual = tk.Label(self.root, text="Valor Atual:")
        self.lbl_valor_atual.pack()
        self.entry_valor_atual = tk.Entry(self.root)
        self.entry_valor_atual.pack()
        self.entry_valor_atual.bind("<KeyRelease>", self.atualizar_valor_atual)

        self.lbl_min = tk.Label(self.root, text="Valor Mínimo:")
        self.lbl_min.pack()
        self.entry_min = tk.Entry(self.root)
        self.entry_min.pack()

        self.lbl_max = tk.Label(self.root, text="Valor Máximo:")
        self.lbl_max.pack()
        self.entry_max = tk.Entry(self.root)
        self.entry_max.pack()

        self.btn_ativar = tk.Button(self.root, text="Ativar", command=self.ativar)
        self.btn_ativar.pack()

        self.btn_desativar = tk.Button(self.root, text="Desativar", command=self.desativar)
        self.btn_desativar.pack()

    def desativar(self):
        self.ativo = False

    def atualizar_valor_atual(self, event):
        self.valor_atual = self.entry_valor_atual.get()

    def iniciar_leituras(self):
        while self.ativo:
            if self.valor_atual is not None and self.min is not None and self.max is not None:
                mensagem = ''
                if float(self.valor_atual) == float(self.min):
                    mensagem = str(self.valor_atual) + " (MIN)"
                elif float(self.valor_atual) == float(self.max):
                    mensagem = str(self.valor_atual) + " (MAX)"
                elif float(self.valor_atual) > float(self.max):
                    mensagem = str(self.valor_atual) + " (>MAX)"
                elif float(self.valor_atual) < float(self.min):
                    mensagem = str(self.valor_atual) + " (<MIN)"
                if mensagem:
                    self.conn.send(body=mensagem + f" de {self.parametro}", destination=f'/topic/{self.nome}')
                    print(f"Enviando mensagem: {mensagem} de {self.parametro}")
            time.sleep(1)

    def ativar(self):
        self.parametro = self.parametro_var.get()
        self.valor_atual = self.entry_valor_atual.get()
        self.min = self.entry_min.get()
        self.max = self.entry_max.get()
        if self.min and self.max:
            self.ativo = True
            thread_envio = threading.Thread(target=self.iniciar_leituras)
            thread_envio.start()
        else:
            print("Defina valores máximo e mínimo para ativar o sensor.")

    def run(self):
        self.root.mainloop()

class MainApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Gerenciador de Sensores")
        self.sensor_count = 0
        self.sensors = []

        self.btn_novo_sensor = tk.Button(self.root, text="Novo Sensor", command=self.novo_sensor)
        self.btn_novo_sensor.pack()

    def novo_sensor(self):
        self.sensor_count += 1
        sensor = Sensor(f'sensor/{self.sensor_count}')
        self.sensors.append(sensor)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = MainApp()
    app.run()
