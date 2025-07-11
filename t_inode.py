import time
import uuid

class Inode:
    def __init__(self, nome, is_diretorio=False):
        self.id = str(uuid.uuid4())
        self.nome = nome
        self.is_diretorio = is_diretorio
        self.tamanho = 0
        self.blocos = []  
        self.filhos = {} if is_diretorio else None 
        self.pai = None

    def __str__(self):
        if self.is_diretorio:
            return f"[DIR] {self.nome} (inode: {self.id})"
        else:
            return f"[ARQ] {self.nome} (inode: {self.id}, tam: {self.tamanho} bytes)"

class SistemaArquivos:
    def __init__(self):
        self.raiz = Inode("/", is_diretorio=True)
        self.atual = self.raiz
        self.inode = {self.raiz.id: self.raiz}

    def criar_diretorio(self, nome):
        if nome in self.atual.filhos:
            print("Erro: já existe algo com esse nome.")
            return
        novo = Inode(nome, is_diretorio=True)
        novo.pai = self.atual
        self.atual.filhos[nome] = novo
        self.inode[novo.id] = novo

    def criar_arquivo(self, nome):
        if nome in self.atual.filhos:
            print("Erro: já existe algo com esse nome.")
            return
        novo = Inode(nome, is_diretorio=False)
        novo.pai = self.atual
        self.atual.filhos[nome] = novo
        self.inode[novo.id] = novo

    def listar(self):
        for filho in self.atual.filhos.values():
            print(filho)

    def mudar_diretorio(self, nome):
        if nome == "..":
            if self.atual.pai:
                self.atual = self.atual.pai
        elif nome == ".":
            pass
        elif nome in self.atual.filhos:
            destino = self.atual.filhos[nome]
            if destino.is_diretorio:
                self.atual = destino
            else:
                print("Erro: não é um diretório.")
        else:
            print("Erro: diretório não encontrado.")

    def escrever(self, nome_arquivo, dados):
        inicio = time.perf_counter()
        TAMANHO_BLOCO = 16
        if nome_arquivo in self.atual.filhos:
            arquivo = self.atual.filhos[nome_arquivo]
            if arquivo.is_diretorio:
                print("Erro: isso é um diretório.")
                return
            for i in range(0, len(dados), TAMANHO_BLOCO):
                parte = dados[i:i+TAMANHO_BLOCO]
                arquivo.blocos.append(dados)
                arquivo.tamanho += len(parte)
        else:
            print("Erro: arquivo não encontrado.")
        fim = time.perf_counter()
        print(f"[Tempo] escrever('{nome_arquivo}') executado em {fim - inicio:.6f} segundos\n")

    def ler(self, nome_arquivo):
        inicio = time.perf_counter()

        if nome_arquivo in self.atual.filhos:
            arquivo = self.atual.filhos[nome_arquivo]
            if arquivo.is_diretorio:
                print("Erro: isso é um diretório.")
                return
            for bloco in arquivo.blocos:
                print(bloco)
        else:
            print(f"Erro: {nome_arquivo} não existe.")

        fim = time.perf_counter()
        print(f"[Tempo] ler('{nome_arquivo}') executado em {fim - inicio:.6f} segundos\n")

    def mover(self, nome_arquivo, nome_diretorio_destino):
        if nome_arquivo not in self.atual.filhos:
            print(f"Erro: {nome_arquivo} não existe.")
            return
        if nome_diretorio_destino not in self.atual.filhos or not self.atual.filhos[nome_diretorio_destino].is_diretorio:
            print("Erro: diretório de destino inválido.")
            return
        arquivo = self.atual.filhos.pop(nome_arquivo)
        destino = self.atual.filhos[nome_diretorio_destino]
        destino.filhos[nome_arquivo] = arquivo
        arquivo.pai = destino

    def remover(self, nome):
        if nome not in self.atual.filhos:
            print(f"Erro: {nome} não existe.")
            return
        node = self.atual.filhos[nome]
        if node.is_diretorio and node.filhos:
            print("Erro: diretório não está vazio.")
            return
        del self.inode[node.id]
        del self.atual.filhos[nome]
        print(f"{nome} removido com sucesso.")

    def prompt(self):
        return f"{self.obter_caminho()}$ "

    def obter_caminho(self):
        caminho = []
        atual = self.atual
        while atual.pai:
            caminho.insert(0, atual.nome)
            atual = atual.pai
        return "/" + "/".join(caminho)

def terminal():
    sistema = SistemaArquivos()

    while True:
        try:
            comando = input(sistema.prompt()).strip()
        except (EOFError, KeyboardInterrupt):
            print("\n^C")
            break

        if comando == "exit":
            break
        elif comando.startswith("mkdir "):
            sistema.criar_diretorio(comando.split(" ", 1)[1])
        elif comando.startswith("touch "):
            sistema.criar_arquivo(comando.split(" ", 1)[1])
        elif comando == "ls":
            sistema.listar()
        elif comando.startswith("cd "):
            sistema.mudar_diretorio(comando.split(" ", 1)[1])
        elif comando.startswith("echo "):
            partes = comando.split(" ", 2)
            if len(partes) < 3:
                print("Uso: echo <arquivo> <conteúdo>")
                continue
            sistema.escrever(partes[1], partes[2])
        elif comando.startswith("cat "):
            sistema.ler(comando.split(" ", 1)[1])
        elif comando.startswith("mv "):
            partes = comando.split(" ", 2)
            if len(partes) < 3:
                print("Uso: mv <arquivo> <diretório>")
                continue
            sistema.mover(partes[1], partes[2])
        elif comando.startswith("rm "):
            sistema.remover(comando.split(" ", 1)[1])
        else:
            print("Comando inválido.")

if __name__ == "__main__":
    terminal()
