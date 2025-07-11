import uuid
import time  # Adicionado para medir o tempo

class Bloco:
    def __init__(self, dados):
        self.dados = dados
        self.proximo = None

class Inode:
    def __init__(self, nome, is_diretorio=False):
        self.id = str(uuid.uuid4())
        self.nome = nome
        self.is_diretorio = is_diretorio
        if not is_diretorio:
            self.tamanho = 0
            self.primeiro_bloco = None
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
        inicio = time.perf_counter()  # Início da medição

        TAMANHO_BLOCO = 16
        arquivo = self.atual.filhos.get(nome_arquivo)
        if arquivo:
            if arquivo.is_diretorio:
                print("Erro: isso é um diretório.")
                return

            for i in range(0, len(dados), TAMANHO_BLOCO):
                parte = dados[i:i+TAMANHO_BLOCO]
                novo_bloco = Bloco(parte)

                if not arquivo.primeiro_bloco:
                    arquivo.primeiro_bloco = novo_bloco
                else:
                    atual = arquivo.primeiro_bloco
                    while atual.proximo:
                        atual = atual.proximo
                    atual.proximo = novo_bloco

                arquivo.tamanho += len(parte)
        else:
            print("Erro: arquivo não encontrado.")

        fim = time.perf_counter()
        print(f"[Tempo] escrever('{nome_arquivo}') executado em {fim - inicio:.6f} segundos")

    def ler(self, nome_arquivo):
        inicio = time.perf_counter()  # Início da medição

        arquivo = self.atual.filhos.get(nome_arquivo)
        if arquivo:
            if arquivo.is_diretorio:
                print("Erro: isso é um diretório.")
            else:
                atual = arquivo.primeiro_bloco
                while atual:
                    print(atual.dados)
                    atual = atual.proximo
        else:
            print("Erro: arquivo não encontrado.")

        fim = time.perf_counter()
        print(f"[Tempo] ler('{nome_arquivo}') executado em {fim - inicio:.6f} segundos")

    def mover(self, nome_arquivo, nome_diretorio_destino):
        if nome_arquivo not in self.atual.filhos:
            print("Erro: arquivo não encontrado.")
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
            print("Erro: nome não encontrado.")
            return
        no = self.atual.filhos[nome]
        if no.is_diretorio and no.filhos:
            print("Erro: diretório não está vazio.")
            return
        del self.inode[no.id]
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
                print("Uso: write <arquivo> <conteúdo>")
                continue
            sistema.escrever(partes[1], partes[2])
        elif comando.startswith("cat"):
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
