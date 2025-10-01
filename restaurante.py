from db import BancoDeDados
import os
from dotenv import load_dotenv

load_dotenv()

class Restaurante(BancoDeDados):

    reset = '\033[0m'
    negrito = '\033[1m'
    ciano = '\033[96m'
    amarelo = '\033[93m'
    verde = '\033[92m'
    vermelho = '\033[91m'
    branco = '\033[97m'

    def __init__(self):
        super().__init__()
        self.config['database'] = os.getenv("DB_NAME")

    # ================ GERENCIAR MESAS ================

    def reservar_mesa(self, status='ocupada'):
        numero_mesa = int(input('Por favor digite o número da mesa que deseja reservar: '))
        print('-' * 70)

        status_atual = self.buscar_status_mesa(numero_mesa)
        if status_atual == 'ocupada':
            print(f'{self.negrito}{self.ciano}A mesa {numero_mesa} já está reservada!{self.reset}')
            return

        self.atualizar_mesa(status, numero_mesa)
        print(f'{self.negrito}{self.verde}Mesa {numero_mesa} reservada com sucesso!{self.reset}')
        return True

    def liberar_mesa(self):
        numero_mesa = int(input('Por favor digite o número da mesa que deseja liberar: '))

        status_atual = self.buscar_status_mesa(numero_mesa)
        if status_atual is None:
            return

        pedidos = self.buscar_pedidos_detalhados(numero_mesa)

        if pedidos is None:
            print(f'{self.negrito}{self.vermelho}Erro ao acessar o banco de dados.{self.reset}')
            return

        if not pedidos:
            if status_atual == 'livre':
                print(f'{self.negrito}{self.branco}A mesa {numero_mesa} já está liberada!{self.reset}')
                return
            self.atualizar_mesa(status='livre', numero_mesa=numero_mesa)
            print(f'{self.negrito}{self.verde}Mesa {numero_mesa} liberada com sucesso!{self.reset}')
            return False
        
        todos_pagos = all(row['status'].lower() == 'pago' for row in pedidos) #voltar com all

        if todos_pagos:
            if status_atual == 'livre':
                print(f'{self.negrito}{self.ciano}A mesa {numero_mesa} já está liberada!{self.reset}')
                return 
            self.atualizar_mesa(status='livre', numero_mesa=numero_mesa)
            print(f'{self.negrito}{self.verde}Mesa {numero_mesa} liberada com sucesso!{self.reset}')
        else:
            print(f'{self.negrito}{self.vermelho}Não é possível liberar a mesa {numero_mesa}, ainda tem pedidos pendentes.{self.reset}')

    def calcular_total_mesa(self, numero_mesa):
        pedidos = self.buscar_pedidos_detalhados(numero_mesa=numero_mesa)

        if pedidos:
            total = sum(pedido['total_item'] for pedido in pedidos)
            print(f'{self.negrito}{self.ciano}Total da mesa {numero_mesa} - R$ {total:.2f}{self.reset}')

        else:
            print(f'{self.negrito}{self.branco}Nenhum pedido encontrado para a mesa {numero_mesa}{self.reset}')

    # ================ GERENCIAR PEDIDOS ================

    def lancar_pedido(self):
        mesas = self.mesas
        
        print(f'{self.negrito}{"MESAS DISPONÍVEIS":^70}{self.reset}')
        print('-' * 70)
        mesas_str = ' | '. join(str(mesa['numero']) for mesa in mesas)
        print(mesas_str.center(70))
        print('-' * 70)
                
        numero_mesa = int(input('Digite o número da mesa que deseja inserir pedido: '))

        cardapio = self.cardapio
        
        if cardapio:
            print(f'{self.negrito}=' * 70)
            print(f'{"CARDÁPIO":^70}')
            print('=' * 70)
            print(f'{"ID":<5} {"ITEM":<20}')
            print('-' * 70)
            print(f'{self.reset}')
            
            for item in cardapio:
                print(f'{item["id"]:<5} {item["item"]:<20}')
            print('=' * 70)

        id_item = input(f'Digite o id do item que deseja inserir na mesa {numero_mesa}: ')
        quant_input = input('Digite a quantidade [Enter para 1]: ').strip()
        print('-' * 70)
        quantidade = int(quant_input) if quant_input else 1
        
        pedido = self.adicionar_pedido(numero_mesa, id_item, quantidade)
        self.atualizar_mesa(status='ocupada', numero_mesa=numero_mesa)

        if pedido:
            print(f'{self.negrito}{self.verde}Pedido realizado com sucesso para a mesa {numero_mesa}{self.reset}')
        else:
            print(f'{self.negrito}{self.vermelho}Verifique se a mesa {numero_mesa} ou o item {id_item} existem para continuar!{self.reset}')

    def pedidos_n_pagos(self):
        numero_mesa = int(input('Digite o número da mesa para ver pedidos não pagos: '))
        quantidade = self.contar_pedidos_n_pagos(numero_mesa=numero_mesa)
        pedidos_n_pagos = self.buscar_pedidos_n_pagos(numero_mesa=numero_mesa)

        print(f'Mesa {numero_mesa} tem {quantidade} pedido(s) em aberto.')
        
        if pedidos_n_pagos:
            for pedido in pedidos_n_pagos:
                print(f"ID: {pedido['id']} | Item: {pedido['item']} | Qtd: {pedido['quantidade']} | Unit: R${pedido['preco_unitario']:.2f} | Total: R${pedido['total_item']:.2f}")

    def fechar_conta(self):
        numero_mesa = int(input('Digite o número da mesa que deseja fechar: '))

        pedidos = self.buscar_pedidos_detalhados(numero_mesa)
        if len(pedidos) == 0:
            print(f'{self.negrito}{self.vermelho}Não existe pedidos para a mesa {numero_mesa}{self.reset}')
            return
        
        self.atualizar_pedido(numero_mesa=numero_mesa, status='pago')
        self.atualizar_mesa(status='livre', numero_mesa=numero_mesa)
        print(f'{self.negrito}{self.verde}Pedido da mesa {numero_mesa} fechado com sucesso!{self.reset}')
