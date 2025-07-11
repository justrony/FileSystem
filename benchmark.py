import time
import matplotlib.pyplot as plt
import random
import string

# ------------------- Funções de Escrita e Leitura -------------------

# Simulação com array (Inode com blocos em lista)
class InodeArray:
    def __init__(self):
        self.blocos = []
        self.tamanho = 0

    def escrever(self, dados, TAMANHO_BLOCO=16):
        self.blocos.clear()
        self.tamanho = 0
        for i in range(0, len(dados), TAMANHO_BLOCO):
            parte = dados[i:i+TAMANHO_BLOCO]
            self.blocos.append(parte)
            self.tamanho += len(parte)

    def ler(self):
        return ''.join(self.blocos)

# Simulação com lista encadeada (Bloco com ponteiro para o próximo)
class Bloco:
    def __init__(self, dados):
        self.dados = dados
        self.proximo = None

class InodeEncadeado:
    def __init__(self):
        self.primeiro_bloco = None
        self.tamanho = 0

    def escrever(self, dados, TAMANHO_BLOCO=16):
        self.primeiro_bloco = None
        self.tamanho = 0
        ultimo = None
        for i in range(0, len(dados), TAMANHO_BLOCO):
            parte = dados[i:i+TAMANHO_BLOCO]
            novo_bloco = Bloco(parte)
            if not self.primeiro_bloco:
                self.primeiro_bloco = novo_bloco
            else:
                ultimo.proximo = novo_bloco
            ultimo = novo_bloco
            self.tamanho += len(parte)

    def ler(self):
        atual = self.primeiro_bloco
        resultado = ''
        while atual:
            resultado += atual.dados
            atual = atual.proximo
        return resultado

# ------------------- Função de Benchmark -------------------

def tempo_medio_execucao(func, *args, repeticoes=10):
    tempos = []
    for _ in range(repeticoes):
        inicio = time.perf_counter()
        func(*args)
        fim = time.perf_counter()
        tempos.append(fim - inicio)
    return sum(tempos) / len(tempos)

# ------------------- Gerador de texto aleatório -------------------

def gerar_texto(n_palavras):
    palavras = [''.join(random.choices(string.ascii_lowercase, k=random.randint(3, 8))) for _ in range(n_palavras)]
    return ' '.join(palavras)

# ------------------- Benchmark Principal -------------------

palavras_testes = list(range(100, 2100, 200))
resultados_array = {'escrita': [], 'leitura': []}
resultados_lista = {'escrita': [], 'leitura': []}

for n in palavras_testes:
    texto = gerar_texto(n)

    inode_array = InodeArray()
    inode_lista = InodeEncadeado()

    # Array
    tempo_array_write = tempo_medio_execucao(inode_array.escrever, texto)
    tempo_array_read = tempo_medio_execucao(inode_array.ler)
    resultados_array['escrita'].append(tempo_array_write)
    resultados_array['leitura'].append(tempo_array_read)

    # Lista Encadeada
    tempo_lista_write = tempo_medio_execucao(inode_lista.escrever, texto)
    tempo_lista_read = tempo_medio_execucao(inode_lista.ler)
    resultados_lista['escrita'].append(tempo_lista_write)
    resultados_lista['leitura'].append(tempo_lista_read)

# ------------------- Plotagem dos Gráficos -------------------

plt.figure(figsize=(14, 6))

plt.subplot(1, 2, 1)
plt.plot(palavras_testes, resultados_array['escrita'], label='Inode com Lista', marker='o')
plt.plot(palavras_testes, resultados_lista['escrita'], label='Lista Encadeada', marker='s')
plt.title("Tempo médio de Escrita")
plt.xlabel("Número de Palavras")
plt.ylabel("Tempo (s)")
plt.legend()
plt.grid(True)

plt.subplot(1, 2, 2)
plt.plot(palavras_testes, resultados_array['leitura'], label='Inode com Lista', marker='o')
plt.plot(palavras_testes, resultados_lista['leitura'], label='Lista Encadeada', marker='s')
plt.title("Tempo médio de Leitura")
plt.xlabel("Número de Palavras")
plt.ylabel("Tempo (s)")
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()