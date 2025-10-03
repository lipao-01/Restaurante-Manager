from db import BancoDeDados
from restaurante import Restaurante
from datetime import datetime
import os
from dotenv import load_dotenv
import time
from pwinput import pwinput

load_dotenv()

class Interface(Restaurante):

    reset = '\033[0m'
    negrito = '\033[1m'
    ciano = '\033[96m'
    amarelo = '\033[93m'
    verde = '\033[92m'
    vermelho = '\033[91m'
    branco = '\033[97m'

    def __init__(self):
        BancoDeDados.__init__(self)
        self.config['database'] = os.getenv("DB_NAME")

    def sistema(self):
        self.tela_login_resgistro()
        self.tela_home()

    def tela_login_resgistro(self):

        self.print_titulo('TELA LOGIN')
        print()
        print(f'[{self.negrito}{self.ciano}1{self.reset}] Criar conta')
        print(f'[{self.negrito}{self.ciano}2{self.reset}] Entrar')
        print('-' * 70)

        opc = self.ler_num_inteiro('👉 Digite uma opção: ')
        print()

        if opc == 1:
            usuario = input('Insira o nome de usuário: ')
            senha = pwinput(prompt='Insira a sua senha: ', mask='*')
            print()

            sucesso, resultado = self.cadastrar_usuario(usuario=usuario, senha=senha)

            if sucesso:
                print(f'{self.negrito}{self.verde}Usuário {usuario} cadastrado com sucesso! (ID: {resultado}){self.reset}')
                time.sleep(1)


            else:
                print(f'{self.negrito}{self.vermelho}Não foi possível cadastrar o usuário {usuario}! Erro: {resultado}{self.reset}')
                time.sleep(1)

        elif opc == 2:
            while True:
                usuario = input('Usuário: ').lower().strip()
                senha = pwinput(prompt='Senha: ', mask='*').strip()

                sucesso, mensagem = self.login(usuario, senha)

                if sucesso:
                    time.sleep(1)
                    print(f'{self.negrito}{self.verde}{mensagem}{self.reset}')
                    print()
                    time.sleep(0.5)
                    break

                else:
                    print(f'{self.negrito}{self.vermelho}{mensagem}{self.reset}')
                    print()
                    time.sleep(1)

        else:
            print(f'{self.negrito}{self.vermelho}Opção inválida!{self.reset}')

    def tela_home(self):
        while True:
            self.print_titulo('HOME')

            data_hoje = datetime.today()
            data_hoje_formatada = data_hoje.strftime("%d/%m")


            pedidos_abertos = self.buscar_pedidos_n_pagos()
            pedidos_abertos_count = len(pedidos_abertos)

            mesas_ocupadas = list(set(pedido['numero_mesa'] for pedido in pedidos_abertos))
            mesas_ocupadas.sort()

            mesas_ocupadas_sem_pedidos = self.buscar_mesas_ocupadas()


            try:
                faturamento = self.calcular_faturamento() or 0
            except:
                faturamento = 0

            print()
            print(f'{self.negrito}{"Data: ":>65}{data_hoje_formatada:>5}{self.reset}')
            
            print(f'{self.negrito}Pedidos em andamento:{self.reset} {self.ciano}{pedidos_abertos_count} pedidos em {len(mesas_ocupadas)} mesas{self.reset}')
            print()

            if mesas_ocupadas_sem_pedidos:
                print(f'{self.negrito}Mesas ocupadas:{self.reset}{self.ciano} {mesas_ocupadas_sem_pedidos}{self.reset}')
                print()
            else:
                print(f'{self.negrito}Mesas ocupadas:{self.reset}{self.ciano}Nenhuma{self.reset}')
                print()
            
        
            print(f'{self.negrito}Mesas disponíveis:{self.reset} {self.ciano}{self.contar_mesas_disponiveis()}{self.reset}')
            print()

            print(f'{self.negrito}Faturamento:{self.reset} {self.ciano}R$ {faturamento:.2f}{self.reset}')
            print()
            print('-' * 70)

            print(f'[{self.negrito}{self.ciano}1{self.reset}] Menu inicial')
            print(f'[{self.negrito}{self.ciano}2{self.reset}] Ver mesas')
            print(f'[{self.negrito}{self.ciano}3{self.reset}] Ver pedidos')
            print(f'[{self.negrito}{self.ciano}0{self.reset}] Sair')
            print()

            print('=' * 70)
            opc = self.ler_num_inteiro('👉 Digite uma opção: ')

            if opc == 0:
                print(f'{self.negrito}{self.branco}Saindo do sistema...{self.reset}')
                break

            elif opc == 1:
                self.menu_principal()

            elif opc == 2:
                self.menu_mesas()

            elif opc == 3:
                self.menu_pedidos()

            else:
                print(f'{self.negrito}{self.vermelho}Digite uma opção válida!!{self.reset}')
        
    def print_titulo(self, titulo):
        print(f'\n{self.negrito}{'=' * 70}')
        print(f'\n{titulo:^70}')
        print(f'\n{"=" * 70}{self.reset}')

    def print_subtitulo(self, subtitulo):
        print(f'\n{self.negrito}{subtitulo}{self.reset}')
        print('-' * 70)

    def ler_num_inteiro(self, msg='Digite um número: '):
        while True:
            try:
                valor = int(input(msg))
                return valor
            except ValueError:
                print(f'{self.negrito}{self.vermelho}Entrada inválida! Digite um número inteiro.{self.reset}')

    def menu_principal(self):
        while True:
            self.print_titulo(f'SISTEMA DO RESTAURANTE')
            print(f'[{self.negrito}{self.ciano}1{self.reset}] Cardápio')
            print(f'[{self.negrito}{self.ciano}2{self.reset}] Mesas')
            print(f'[{self.negrito}{self.ciano}3{self.reset}] Pedidos')
            print(f'[{self.negrito}{self.ciano}0{self.reset}] Voltar')
            print(f'=' * 70)

            opc = self.ler_num_inteiro(f'👉 Digite uma opção: ')
            print()

            if opc == 0:
                print(f'{self.negrito}{self.branco}Voltando para home...{self.reset}')
                break

            elif opc == 1:
                self.menu_cardapio()
            
            elif opc == 2:
                self.menu_mesas()
            
            elif opc == 3:
                self.menu_pedidos()

            else:
                print(f'{self.negrito}{self.vermelho}Digite uma opção válida!!{self.reset}')

    def menu_cardapio(self):
        while True:
            self.mostrar_cardapio()
            self.print_subtitulo('Menu Cardápio')
            print(f'[{self.negrito}{self.ciano}1{self.reset}] Adicionar item')
            print(f'[{self.negrito}{self.ciano}2{self.reset}] Atualizar preço')
            print(f'[{self.negrito}{self.ciano}3{self.reset}] Excluir item')
            print(f'[{self.negrito}{self.ciano}0{self.reset}] Voltar')
            print('=' * 70)

            opc = self.ler_num_inteiro('👉 Digite uma opção: ')
            print()

            if opc == 0:
                time.sleep(0.5)
                print(f'{self.negrito}{self.branco}Voltando para home...{self.reset}')
                time.sleep(1)
                break

            elif opc == 1:
                while True:
                    nome_item = input('Insira o nome do item: ').lower()
                    if nome_item == '':
                        print(f'{self.negrito}{self.vermelho}Você não pode cadastrar um item com nome vazio!{self.reset}')
                        
                    else:
                        break
                    
                while True:
                    preco_item = input('Insira o preço do item: ').replace(',', '.')
                    try:
                        preco_float = float(preco_item)
                        if preco_float < 0:
                            time.sleep(0.5)
                            print(f'{self.negrito}{self.vermelho}Você não pode cadastrar um item com preço negativo!{self.reset}')
                        else:
                            break
                    
                    except ValueError:
                        time.sleep(0.5)
                        print(f'{self.negrito}{self.vermelho}Preço inválido! Insira um número válido.')
               
                print('-' * 70)

                sucesso, resposta = self.adicionar_item_cardapio(nome_item=nome_item, preco=preco_float)
            
                if sucesso:
                    time.sleep(1)
                    print(f'{self.negrito}{self.verde}Item {nome_item} inserido com sucesso! (ID: {resposta}){self.reset}')
                    time.sleep(0.5)
                else:
                    time.sleep(1)
                    print(f'{self.negrito}{self.vermelho}Não é possível inserir o item {nome_item} no cardápio.{self.reset}')
                    print(f'{resposta}')
                    time.sleep(0.5)

            elif opc == 2: # atualizar preco
                id_item = self.ler_num_inteiro('Insira o id do item: ')
                preco = input('Insira o novo preço: ').replace(',', '.')
                print('-' * 70)

                try:
                    preco_float = float(preco)
                    if preco_float < 0:
                        print(f'{self.negrito}{self.vermelho}Preço não pode ser negativo!{self.reset}')
                        continue

                except ValueError:
                    print(f'{self.negrito}{self.vermelho}Preço inválido!{self.reset}')
                    continue

                resultado  = self.atualizar_cardapio(preco=preco, id_item=id_item)

                if resultado is True:
                    item = self.buscar_item_cardapio(id_item=id_item)
                    if item:
                        time.sleep(1)
                        print(f'{self.negrito}{self.verde}Preço do item {item['item']} alterado com sucesso!{self.reset}')
                        time.sleep(0.5)
                    else:
                        time.sleep(1)
                        print(f'{self.negrito}{self.verde}Preço atualizado, mas não consegui buscar o nome do item (ID {id_item}).{self.reset}')
                        time.sleep(0.5)

                elif resultado is None:
                    time.sleep(0.5)
                    print(f'{self.negrito}{self.vermelho}Item com ID {id_item} não existe!{self.reset}')

            elif opc == 3: # excluir item
                id_item = self.ler_num_inteiro('👉 Digite o ID do item para excluir: ')
                print('-' * 70)
                sucesso, info = self.excluir_item(id_item=id_item)

                if sucesso:
                    time.sleep(1)
                    print(f'{self.negrito}{self.verde}Item {id_item} excluído com sucesso!{self.reset}')
                    time.sleep(0.5)

                else:
                    time.sleep(1)
                    print(f'{self.negrito}{self.vermelho}Não foi possível excluir o item {id_item}!{self.reset}')
                    print(f'{self.negrito}{self.vermelho}Motivo -> {info}{self.reset}')
                    time.sleep(0.5)

            
            else:
                print(f'{self.negrito}{self.vermelho}Digite uma opção válida!!{self.reset}')

    def menu_mesas(self):
        while True:
            self.motrar_mesas()
            self.print_subtitulo('Menu Mesas')
            print(f'[{self.negrito}{self.ciano}1{self.reset}] Adicionar mesa')
            print(f'[{self.negrito}{self.ciano}2{self.reset}] Reservar mesa')
            print(f'[{self.negrito}{self.ciano}3{self.reset}] Excluir mesa')
            print(f'[{self.negrito}{self.ciano}4{self.reset}] Liberar mesa')
            print(f'[{self.negrito}{self.ciano}5{self.reset}] Ver pedidos')
            print(f'[{self.negrito}{self.ciano}0{self.reset}] Voltar')
            print('=' * 70)

            opc = self.ler_num_inteiro('👉 Digite uma opção: ')
            print()

            if opc == 0:
                time.sleep(0.5)
                print(f'{self.negrito}{self.branco}Voltando para home...{self.reset}')
                time.sleep(1)
                break

            elif opc == 1:
                numero_mesa = self.ler_num_inteiro('Insira o número da mesa: ')
                print('-' * 70)
                sucesso, resposta = self.adicionar_mesa(numero_mesa=numero_mesa)

                if sucesso:
                    time.sleep(1)
                    print(f'{self.negrito}{self.verde}Mesa {numero_mesa} adicionada com sucesso! (ID: {resposta}){self.reset}')
                    time.sleep(0.5)

                else:
                    time.sleep(1)
                    print(f'{self.negrito}{self.vermelho}Não é possível inserir a mesa {numero_mesa}.{self.reset}')
                    print(f'{resposta}')
                    time.sleep(0.5)
            
            elif opc == 2:
                self.reservar_mesa()

            elif opc == 3:
                numero_mesa = self.ler_num_inteiro('Insira o número da mesa que deseja excluir: ')
                print('-' * 70)
                sucesso, resposta = self.excluir_mesa(numero_mesa=numero_mesa)

                if sucesso:
                    time.sleep(1)
                    print(f'{self.negrito}{self.verde}Mesa {numero_mesa} excluída com sucesso! (ID: {resposta}){self.reset}')
                    time.sleep(0.5)

                else:
                    time.sleep(1)
                    print(f'{self.negrito}{self.vermelho}Não é possível excluir a mesa {numero_mesa}.{self.reset}')
                    print(f'{self.negrito}{self.vermelho}{resposta}{self.reset}')
                    time.sleep(0.5)

            elif opc == 4:
                print(f'{self.negrito}{self.branco}OBS: PARA LIBERAR A MESA ELA NÃO PODE TER PEDIDOS ABERTOS{self.reset}')
                self.liberar_mesa()

            elif opc == 5:
                self.menu_pedidos()

            else:
                print(f'{self.negrito}{self.vermelho}Digite uma opção válida!!{self.reset}')

    def menu_pedidos(self):
        while True:
            self.mostrar_pedidos()
            self.print_subtitulo('Menu Pedidos')
            print(f'[{self.negrito}{self.ciano}1{self.reset}] Adicionar novo pedido')
            print(f'[{self.negrito}{self.ciano}2{self.reset}] Fechar conta')
            print(f'[{self.negrito}{self.ciano}3{self.reset}] Cancelar pedido')
            print(f'[{self.negrito}{self.ciano}4{self.reset}] Buscar pedidos detalhados da mesa')
            print(f'[{self.negrito}{self.ciano}0{self.reset}] Voltar')
            print('=' * 70)

            opc = self.ler_num_inteiro('👉 Digite uma opção: ')
            print()

            if opc == 0:
                time.sleep(0.5)
                print(f'{self.negrito}{self.branco}Voltando para home...{self.reset}')
                time.sleep(1)
                break

            elif opc == 1:
                
                self.lancar_pedido()
            
            elif opc == 2:
                self.fechar_conta()

            elif opc == 3:
                numero_mesa = self.ler_num_inteiro('👉 Digite o número da mesa: ')
                self.mostrar_pedidos_detalhados(numero_mesa=numero_mesa)

                id_pedido = self.ler_num_inteiro('Digite o id do pedido para cancelar [0 para todos]: ')

                self.atualizar_pedido(numero_mesa=numero_mesa, status='cancelado', id_pedido=id_pedido)

                time.sleep(1)
                print(f'{self.negrito}{self.verde}Pedido da mesa {numero_mesa} cancelado com sucesso!{self.reset}')
                time.sleep(0.5)

            elif opc == 4:
                while True:
                    numero_mesa = self.ler_num_inteiro('Digite o número da mesa: ')
                    self.mostrar_pedidos_detalhados(numero_mesa)

                    self.print_subtitulo('Menu Pedidos Detalhados') 
                   
                    print(f'[{self.negrito}{self.ciano}1{self.reset}] Adicionar pedido')
                    print(f'[{self.negrito}{self.ciano}2{self.reset}] Cancelar pedido')
                    print(f'[{self.negrito}{self.ciano}0{self.reset}] Voltar')

                    print('=' * 70)
                    opc = self.ler_num_inteiro('👉 Digite uma opção: ')

                    if opc == 0:
                        time.sleep(0.5)
                        print(f'{self.negrito}{self.branco}Voltando para o menu pedidos...{self.reset}')
                        time.sleep(1)
                        break
                        
                    elif opc == 1:
                        numero_mesa = 0
                        self.adicionar_pedido()

            else:
                print(f'{self.negrito}{self.branco}Digite uma opção válida!!{self.reset}')
            
    def motrar_mesas(self):
        mesas = self.mesas
        if mesas:
            self.print_titulo('MESAS DISPONÍVEIS')
            print(f'{self.negrito}{"NÚMERO":<10}{"STATUS":<20}{self.reset}')
            print('-' * 70)

            for mesa in mesas:
                print(f'{mesa['numero']:<10}{mesa['status']:<20}')
            print('-' * 70)
    
        else:
            print('-' * 70)
            print(f'{self.negrito}{self.branco}Nenhuma mesa encontrada.{self.reset}')
            print('-' * 70)
    
    def mostrar_cardapio(self):
        cardapio = self.cardapio
        if cardapio:
            self.print_titulo('CARDÁPIO')
            print(f'{"ID":<5} {"ITEM":<40} {"PREÇO":>10}')
            print('-' * 70)
            
            for item in cardapio:
                print(f'{item["id"]:<5} {item["item"]:<40} R${item["preco"]:>10.2f}')
            print('-' * 70)

        else:
            print('-' * 70)
            print(f'{self.negrito}{self.branco}Nenhum item cadastrado no cardápio.{self.reset}')
            print('-' * 70)

    def mostrar_pedidos(self):
        pedidos = self._buscar_todos_pedidos()

        if pedidos:
            self.print_titulo('PEDIDOS')
            print(f'{"MESA":<8} {"ITENS":<20} {"TOTAL":>10} {"STATUS":>10} {"DATA HORA":>15}')
            print('-' * 70)

            mesas = {}
            for pedido in pedidos:
                mesa = pedido.get("mesa_numero", "n/a")
                if mesa not in mesas:
                    mesas[mesa] = []
                mesas[mesa].append(pedido)

            for mesa, lista_pedidos in mesas.items():
                primeiro = lista_pedidos[0]
                total_formatado = f"R$ {primeiro.get('total_item', 0):.2f}"
                status_formatado = primeiro.get('status', 'N/A').lower()

                data_hora = primeiro.get('data_hora')
                if data_hora:
                    if isinstance(data_hora, str):
                        data_hora = datetime.strptime(data_hora, '%Y-%m-%d %H:%M')
                    data_hora_str = data_hora.strftime('%d/%m %H:%M')
                else:
                    data_hora_str = 'n/a'


                print(f'{mesa:<8} {primeiro.get("item", "n/a"):<20} {total_formatado:>10} {status_formatado:>10} {data_hora_str:>15}')

                if len(lista_pedidos) > 1:
                    print(f'{self.negrito}{self.ciano}{"":<10} + {len(lista_pedidos)-1} pedido(s) a mais...{self.reset}')
                
                print('-' * 70)


        else:
            print('-' * 70)
            print(f'{self.negrito}{self.branco}Nenhum pedido encontrado!{self.reset}')
            print('-' * 70)

    def mostrar_pedidos_detalhados(self, numero_mesa):
        pedidos = self.buscar_pedidos_detalhados(numero_mesa=numero_mesa)

        if pedidos:
            self.print_titulo(f'PEDIDOS DA MESA {numero_mesa}')
            print(f'{"ID":<5} {"ITEM":<20} {"QTD":>5} {"UNITÁRIO":>12} {"TOTAL":>12} {"STATUS":>10}')
            print("-" * 70)

            for pedido in pedidos:
                unitario_formatado = f"R$ {pedido['preco_unitario']:>5.2f}"
                total_formatado = f"R$ {pedido['total_item']:>5.2f}"

                print(f'{pedido["id"]:<5} '
                    f'{pedido["item"]:<20} '
                    f'{pedido["quantidade"]:>5} '
                    f'{unitario_formatado:>12} '
                    f'{total_formatado:>12}'
                    f'{pedido['status']:>10}')
            print("-" * 70)

        else:
            print(f'{self.negrito}{self.branco}Nenhum pedido encontrado para a mesa {numero_mesa}.{self.reset}')
        
        self.calcular_total_mesa(numero_mesa)



