from datetime import datetime #imporação da função de data e hora
from abc import ABC, abstractclassmethod, abstractmethod, abstractproperty
import textwrap
class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)
    
    @property
    def saldo(self):
        return self._saldo
    
    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia
    
    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico
    
    def sacar(self, valor):
        saldo = self.saldo
        excede_saldo = valor > saldo

        if excede_saldo:
            print("Saldo insuficiente para saque! Operação Negada")
        elif valor > 0:
            self._saldo -= valor
            print(f"\nOperação realizada com sucesso!\nValor sacado R${valor:5.2f}")            
            return True
        else:
            print("Valor informado é inválido! Operação Negada.")

        return False
    
    def depositar(self, valor):
        if valor <= 0 :
            print("Valor informado é inválido! Operação Negada.")
            return False
        else:
            self._saldo += valor                
            print(f"Operação realizada com sucesso!\nValor depositado R${valor:5.2f}")

        return True

class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite = 500, limite_saques=3):
        super().__init__(numero, cliente)
        self.limite = limite
        self.limite_saques = limite_saques

    def sacar(self, valor):
        nro_saques = len([
            transacao for transacao in self.historico.transacoes if transacao["tipo"] == Saque.__name__]
            )
        
        excede_limite = valor > self.limite
        excede_saque  =  nro_saques >= self.limite_saques

        if excede_saque:
            print("Número de saques diarios excedido! Operação Negada")
        elif excede_limite:
             print("Valor limite para saques excedido! Operação Negada")
        else:
            return super().sacar(valor)
        return False
    
    def __str__(self):
        return f"""\
            Agencia:\t{self.agencia}
            C/C:\t\t{self.numero}
            Titular:\t{self.cliente.nome}
            """

class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []
        self.indice_conta = 0
        
    def realizar_transacao(self, conta, transacao):
        if len(conta.historico.transacoes_do_dia()) >= 10:
            print("Você excedeu o número de transações permitidas para hoje!")
            return
            
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)

class PessoaFisica(Cliente):
    def __init__(self, endereco, nome, cpf, data_nasc):
        super().__init__(endereco)
        self.nome = nome
        self.cpf = cpf
        self.data_nasc = data_nasc        

class Transacao(ABC):
    @property
    @abstractproperty
    def valor(self):
        pass

    @abstractclassmethod
    def registrar(self, conta):
        pass

class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes
    
    def add_transacao(self, transacao):        
        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.now().strftime('%d/%m/%Y %H:%M:%S'),                
            }
        )
    def gerar_relatorio(self, tipo_transacao=None):
        for transacao in self._transacoes:
            if tipo_transacao is None or transacao["tipo"].lower() == tipo_transacao.lower():
                yield transacao

    def transacoes_do_dia(self):
        data_atual = datetime.now().date()
        transacoes = []
        for transacao in self._transacoes:
            data_transacao = datetime.strptime(transacao["data"], "%d/%m/%Y %H:%M:%S").date()
            if data_atual == data_transacao:
                transacoes.append(transacao)
        return transacoes

def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print("Cliente não possui conta!")
        return
    
    return cliente.contas[0]

def menu(): #Menu de Opções com o nome do Banco
    print('*' * 80)
    print(' U.R. MONEY BANK MENU '.center(80, '*'))
    print('*' * 80)
    menu ="""*                                 [1] - Saque                                  *
*                                 [2] - Extrato                                *
*                                 [3] - Depósitar                              *
*                                 [4] - Nova Conta                             *
*                                 [5] - Listar Contas                          *
*                                 [6] - Novo Usuário                           *
*                                 [7] - Encerrar                               *"""
    print(menu)
    print('*' * 80)
    return input('Digite a opção desejada: ')

class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.sacar(self.valor)

        if sucesso_transacao:
            conta.historico.add_transacao(self)


class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor
    
    @property
    def valor(self):
        return self._valor
    
    def registrar(self, conta):
        sucesso_transacao = conta.depositar(self.valor)

        if sucesso_transacao:
            conta.historico.add_transacao(self)

def saque(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = pesquisa_cliente(cpf, clientes)

    if not cliente:
        print("Cliente não encontrado!")
        return
    
    print('Saque'.center(30))

    saque = float(input('Digite o valor para o saque!\nR$ '))
    transacao = Saque(saque)
    
    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return
    
    cliente.realizar_transacao(conta, transacao)
    
def imprime_extrato(clientes):    
    cpf = input("Informe o CPF do cliente: ")
    cliente = pesquisa_cliente(cpf, clientes)

    if not cliente:
        print("Cliente não encontrado!")
        return
    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return
    
    transacoes = conta.historico.transacoes

    extrato = ""
    if not transacoes:
        extrato = "Não foram realizadas movimentações."
    else:
        for transacao in transacoes:
            extrato += f"\n{transacao['tipo']}\tR${transacao['valor']:.2f}\t{transacao['data']}"
    
    print(extrato)
    print(f"\nSaldo:\n\tR$ {conta.saldo:.2f}")    

def depositar(clientes):    
    cpf = input('Informe o CPF do cliente: ')
    cliente = pesquisa_cliente(cpf, clientes)

    if not cliente:
        print("Cliente não encontrado!")
        return
        
    valor = float(input('Digite o valor para depositar \nR$ '))
    transacao = Deposito(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)
    
def novo_cliente(clientes):
    cpf = input('Digite o número do cpf.\n(Apenas números): ')
    cliente = pesquisa_cliente(cpf, clientes)

    if cliente:
        print('Cliente já cadastrado com esse CPF')
        return
        
    nome = input('Digite o nome do usuário:\n')
    endereco = input('Digite o Endereço do usuário.\n(obs:. log, nº, cidade/uf):\n')
    data_nascimento = input('Data de Nascimento.\n(obs.: dd/mm/aaaa):\n')

    cliente = PessoaFisica(nome=nome, data_nasc=data_nascimento, cpf=cpf, endereco=endereco)

    clientes.append(cliente)

    print("Cliente cadastrado com Sucesso!")

def pesquisa_cliente(cpf, clientes):
    clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None

def criar_conta(numero_conta, clientes, contas):
    cpf = input('Digite o número do cpf.\n(Apenas números):')
    cliente = pesquisa_cliente(cpf, clientes)

    if cliente:
        conta = ContaCorrente.nova_conta(cliente=cliente, numero=numero_conta)
        contas.append(conta)
        cliente.contas.append(conta)

        print(' Conta Criada com Sucesso! '.center(80, '*'))       
    else:
        print('Cliente não encontrado, criação de conta negada.')

def listar_contas(contas):
    for conta in contas:        
        print(textwrap.dedent(str(conta)))           
              
def main():    
    clientes = []
    contas = []

    while True:        
        while True:
            operacao = menu()            
            if not operacao in ('1234567890'): # Verifica se as opções foram digitadas corretamente
                print(('Opção inválida').center(80,'*'))
                print(('Digite novamente!').center(80,'*'))            
            else:
               break

        print('*' * 80)
     
        match operacao: # Opções de Operações case 1 = Saque case 2 = Extrato case 3 = Depósito case 4 Encerrar
            case '1': #opç saque
                print('Saque'.center(80))
                saque(clientes)

            case '2':# opç extrato
                print('Extrato'.center(80))
                imprime_extrato(clientes)

            case '3': #opç depósito
                print('Depósito'.center(80))
                depositar(clientes)

            case '4': #opç Criar Nova Conta
                print('Nova Conta'.center(80))

                numero_conta = len(contas) + 1
                conta = criar_conta(numero_conta, clientes, contas)
                
            case '5': #opç Listar Contas
                print('Listar Contas'.center(80))
                listar_contas(contas)
                                               
            case '6': #opç Novo Cliente
                print('Novo Ciente'.center(80))
                novo_cliente(clientes)

            case '7': #opç Sair/Encerrar
                print('Volte sempre!'.center(80))
                print(('*' * 13).center(80))
                break
            case _:
                print('Opção inválida!')
    
main()
