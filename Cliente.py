import tkinter as tk
import stomp
import threading

class Cliente(stomp.ConnectionListener):
    def __init__(self, id):
        self.id = id
        self.conn = stomp.Connection([('localhost', 61613)])
        self.conn.set_listener('', self)
        self.conn.connect('admin', 'admin', wait=True)

        self.opcoes_disponiveis = []
        self.opcoes_selecionadas = []
        self.mensagens = []

        self.root = tk.Tk()
        self.root.title(f"Cliente {self.id}")

        self.lb_opcoes_disponiveis = tk.Listbox(self.root, selectmode=tk.MULTIPLE)
        self.lb_opcoes_disponiveis.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.lb_opcoes_selecionadas = tk.Listbox(self.root)
        self.lb_opcoes_selecionadas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        frame_mensagens = tk.Frame(self.root)
        frame_mensagens.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.lb_mensagens = tk.Listbox(frame_mensagens)
        self.lb_mensagens.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar_mensagens = tk.Scrollbar(frame_mensagens, orient="vertical", command=self.lb_mensagens.yview)
        self.scrollbar_mensagens.pack(side=tk.RIGHT, fill=tk.Y)

        self.lb_mensagens.config(yscrollcommand=self.scrollbar_mensagens.set)

        self.btn_assinar = tk.Button(self.root, text="Assinar", command=self.assinar)
        self.btn_assinar.pack(side=tk.BOTTOM, fill=tk.X)

        self.btn_remover_assinatura = tk.Button(self.root, text="Remover Assinatura", command=self.remover_assinatura)
        self.btn_remover_assinatura.pack(side=tk.BOTTOM, fill=tk.X)

        self.btn_atualizar = tk.Button(self.root, text="Atualizar Sensores", command=self.carregar_topicos_disponiveis)
        self.btn_atualizar.pack(side=tk.BOTTOM, fill=tk.X)

        self.conn.subscribe(destination='/topic/discovery', id=f"{self.id}-discovery", ack='auto')
        self.carregar_topicos_disponiveis()

    def carregar_topicos_disponiveis(self):
        self.lb_opcoes_disponiveis.delete(0, tk.END)
        self.opcoes_disponiveis = list(set(self.opcoes_disponiveis))  # Remover duplicatas
        for opcao in self.opcoes_disponiveis:
            self.lb_opcoes_disponiveis.insert(tk.END, opcao)

    def on_message(self, frame):
        if frame.headers['destination'] == '/topic/discovery':
            novo_topico = f"/topic/{frame.body}"
            if novo_topico not in self.opcoes_disponiveis:
                self.opcoes_disponiveis.append(novo_topico)
                self.carregar_topicos_disponiveis()
        else:
            mensagem = f"{frame.headers['destination']} mediu: {frame.body}"
            self.mensagens.append(mensagem)
            self.lb_mensagens.insert(tk.END, mensagem)

    def assinar(self):
        selecao = self.lb_opcoes_disponiveis.curselection()
        for index in selecao:
            topico = self.opcoes_disponiveis[index]
            if topico not in self.opcoes_selecionadas:
                self.conn.subscribe(destination=topico, id=f"{self.id}-{index + 1}", ack='auto')
                self.opcoes_selecionadas.append(topico)
                self.lb_opcoes_selecionadas.insert(tk.END, topico)

    def remover_assinatura(self):
        selecao = self.lb_opcoes_selecionadas.curselection()
        for index in selecao:
            topico = self.opcoes_selecionadas[index]
            self.conn.unsubscribe(destination=topico, id=f"{self.id}-{index + 1}")
            self.opcoes_selecionadas.remove(topico)
            self.lb_opcoes_selecionadas.delete(index)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    cliente = Cliente(1)
    cliente.run()
