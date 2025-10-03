import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import errorcode
import hashlib
from datetime import datetime

load_dotenv()

class BancoDeDados():
    def __init__(self):
        self.__user = os.getenv("DB_USER")
        self.__senha = os.getenv("DB_PASSWORD")
        self.__host = os.getenv("DB_HOST")
        self.__db = os.getenv("DB_NAME")


        self.config = {
            'user': self.__user,
            'password': self.__senha,
            'host': self.__host,
            'charset': 'utf8mb4'
        }

    def setup_inicial(self):
        # Cria o banco e as tabelas se não existirem
        conn, cursor = self.conectar()
        
        try:
            db = cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.__db}")
        
        except mysql.connector.Error as err:
            print(f'Erro: {err}')

        finally:
            cursor.close()
            conn.close()
        
        self.config['database'] = self.__db
        conn, cursor =self.conectar()
        
        try:
            tabelas = {
                "mesas": """
                CREATE TABLE IF NOT EXISTS mesas(
                    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                    numero INT NOT NULL UNIQUE,
                    status ENUM('livre', 'ocupada') DEFAULT 'livre'
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """,

                "cardapio":"""
                CREATE TABLE IF NOT EXISTS cardapio(
                    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                    item VARCHAR(100) NOT NULL UNIQUE,
                    preco DECIMAL(10, 2) NOT NULL    
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """,

                "pedidos": """
                CREATE TABLE IF NOT EXISTS pedidos(
                    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                    id_mesa INT NOT NULL,
                    id_cardapio INT NOT NULL,
                    quantidade INT NOT NULL DEFAULT 1,
                    preco_unitario DECIMAL(10, 2) NOT NULL,
                    total_item DECIMAL(10 ,2) AS (quantidade * preco_unitario) STORED, 
                    status VARCHAR(15) DEFAULT 'aberto',
                    data_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (id_mesa) REFERENCES mesas(id),
                    FOREIGN KEY (id_cardapio) REFERENCES cardapio(id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """,

                "usuarios": """
                CREATE TABLE IF NOT EXISTS usuarios(
                    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                    usuario VARCHAR(255) NOT NULL UNIQUE,
                    senha_hash VARCHAR(64) NOT NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """
                }
            
            for nome, sql in tabelas.items():
                cursor.execute(sql)

            cursor.execute("SELECT COUNT(*) AS total FROM cardapio")
            quantidade = cursor.fetchone()["total"]

            cardapio_inicial = [{"item": "fritas com queijo", "preco": 29.90},
                        {"item": "contrafilé com fritas", "preco": 79.90},
                        {"item": "torresmo de barriga", "preco": 24.99},
                        {"item": "pernil com mandioca", "preco": 64.99},
                        {"item": "fígado com jiló", "preco": 37.98},
                        {"item": "x-tudo", "preco": 14.99},
                        {"item": "bolo de pote", "preco": 9.90},
                        {"item": "cerveja 600ml", "preco": 9.90},
                        {"item": "suco natural 300ml", "preco": 7.98},
                        {"item": "refrigerante 350ml", "preco": 5.90}]

            if quantidade == 0:

                for item in cardapio_inicial:
                    cursor.execute("INSERT INTO cardapio (item, preco) VALUES (%s, %s)",
                                (item["item"], item["preco"]))
                conn.commit()
                
            conn.commit()
            return True

        except mysql.connector.Error as err:
            print(f'Erro: {err}')

        finally:
            cursor.close()
            conn.close()

    def conectar(self):
        try:
            conn = mysql.connector.connect(**self.config)
            cursor = conn.cursor(dictionary=True)
            return conn, cursor
        except mysql.connector.Error as err:
            return False, f'Erro de conexão com o banco de dados: {err}'

    def hash_senha(self, senha):
        return hashlib.sha256(senha.encode()).hexdigest()

    def cadastrar_usuario(self, usuario, senha):
        conn, cursor = self.conectar()

        try:
            senha_hash = self.hash_senha(senha)
            print(f"Tentando cadastrar: {usuario}")
            print(f"Tamanho do hash: {len(senha_hash)} caracteres")
            print(f"Hash: {senha_hash}")
            
            sql = "INSERT INTO usuarios (usuario, senha_hash) VALUES (%s, %s)"
            values = (usuario, senha_hash)

            cursor.execute(sql, values)
            conn.commit()
            
            id_usuario = cursor.lastrowid
            return True, id_usuario
        
        except mysql.connector.Error as err:
            print(f"Erro no banco: {err}")
            return False, f'Erro: {err}'

        finally:
            cursor.close()
            conn.close()

    def login(self, usuario, senha):
        conn, cursor = self.conectar()

        try:
            senha_hash = self.hash_senha(senha)

            cursor.execute("SELECT * FROM usuarios WHERE usuario = %s AND senha_hash = %s", (usuario, senha_hash))
            resultado = cursor.fetchone()

            if resultado:
                return True, "Login realizado com sucesso!"
            
            else:
                return False, "Usuário ou senha incorretos!"

        except mysql.connector.Error as err:
            return False, f'Erro: {err}'

        finally:
            cursor.close()
            conn.close()
           
    def adicionar_mesa(self, numero_mesa, status='livre'):
        conn, cursor = self.conectar()
        
        try:
            sql = "INSERT INTO mesas (numero, status) VALUES (%s, %s)"
            values = (numero_mesa, status)

            cursor.execute(sql, values)
            conn.commit()

            id_mesa = cursor.lastrowid
            return True, id_mesa
        

        except mysql.connector.IntegrityError as err:
            return False, f'\033[1;31mA mesa {numero_mesa} já existe!\033[0m'
        
        except mysql.connector.DataError as err:
            return False, f'\033[1;31mDado inválido! {err}\033[0m'
        
        except mysql.connector.ProgrammingError as err:
            return False, f'\033[1;31mErro de sintaxe SQL: {err}\033[0m'

        except mysql.connector.Error as err:
            print(f'\033[1;31mErro ao adicionar mesa {numero_mesa} - Erro: {err}\033[0m')
            return None
        
        finally:
            cursor.close()
            conn.close()

    def adicionar_item_cardapio(self, nome_item, preco):
        conn, cursor = self.conectar()
        if not conn:
            return None
        
        try:
            sql = "INSERT INTO cardapio (item, preco) VALUES (%s, %s)"
            values = (nome_item, preco)

            cursor.execute(sql, values)
            conn.commit()

            id_cardapio = cursor.lastrowid
            return True, id_cardapio
        
        except mysql.connector.IntegrityError as err:
            return False, f'O item {nome_item} já existe!'
        
        except mysql.connector.DataError as err:
            return False, f'Dado inválido! {err}'
        
        except mysql.connector.ProgrammingError as err:
            return False, f'Erro de sintaxe SQL: {err}'

        except mysql.connector.Error as err:
            return False, f'Erro no banco: {err}'

        finally:
            cursor.close()
            conn.close()

    def adicionar_pedido(self, numero_mesa, id_item, quantidade=1):
        conn, cursor = self.conectar()
        if not conn:
            return None
        
        try:
            # Busca o id_mesa
            cursor.execute("SELECT id from mesas WHERE numero = %s", (numero_mesa,))
            row = cursor.fetchone()
            if not row:
                print(f'Mesa {numero_mesa} não encontrada.')
                return False
            id_mesa = row['id']

            # Busca o id_cardapio
            cursor.execute("SELECT id, preco FROM cardapio WHERE id = %s", (id_item,))
            row = cursor.fetchone()

            if not row:
                print(f'Item ID {id_item} não encontrado.')
                return False
            
            id_cardapio = row['id']
            preco_unitario = row['preco']

            sql = """INSERT INTO pedidos (id_mesa, id_cardapio, quantidade, preco_unitario)
                    VALUES (%s, %s, %s, %s)
                  """
            cursor.execute(sql, (id_mesa, id_cardapio, quantidade, preco_unitario))
            conn.commit()

            last_id = cursor.lastrowid

            cursor.execute("SELECT total_item FROM pedidos WHERE id = LAST_INSERT_ID()")
            row = cursor.fetchone()
            total = row['total_item'] if row and 'total_item' in row else None

            if total is not None:
                return True, last_id
                #print(f'{self.negrito}Pedido inserido com sucesso! Total R${total:.2f}')
            else:
                print('Pedido inserido, mas não foi possível recuperar o total!')
            return True, last_id
        
        except mysql.connector.DataError as err:
            return False, f'Dado inválido! {err}'
        
        except mysql.connector.ProgrammingError as err:
            return False, f'Erro de sintaxe SQL: {err}'

        except mysql.connector.Error as err:
            print(f'Erro: {err}')
            return False

        finally:
            cursor.close()
            conn.close()

    def atualizar_mesa(self, status, numero_mesa):
        conn, cursor = self.conectar()
        if not conn:
            return None
        
        try:
            sql = "UPDATE mesas SET status = %s WHERE numero = %s"
            values =  (status, numero_mesa)

            cursor.execute(sql, values)
            conn.commit()

            return True
        
        except mysql.connector.Error as err:
            return False, str(err)

        finally:
            cursor.close()
            conn.close()

    def atualizar_cardapio(self, preco, id_item):
        conn, cursor = self.conectar()

        try:
            cursor.execute("SELECT * FROM cardapio WHERE id = %s", (id_item,))
            item = cursor.fetchone()

            if not item:
                return None
            
            sql = "UPDATE cardapio SET preco = %s WHERE id = %s"
            values = (preco, id_item)

            cursor.execute(sql, values)
            conn.commit()
            return True
       
        except mysql.connector.Error as err:
            return False, str(err)

        finally:
            cursor.close()
            conn.close()
    
    def atualizar_pedido(self, numero_mesa, status, id_pedido=None):
        conn, cursor = self.conectar()
        
        try:
            if id_pedido and id_pedido != 0:
                sql = """UPDATE pedidos SET status = %s WHERE id = %s AND id_mesa = (
                SELECT id FROM mesas WHERE numero = %s
                )"""

                cursor.execute(sql, (status, id_pedido, numero_mesa))
            else:
                sql = "UPDATE pedidos SET status = %s WHERE id_mesa = (SELECT id FROM mesas WHERE numero = %s)"

                cursor.execute(sql, (status, numero_mesa))

            conn.commit()
            return True
        
        except mysql.connector.Error as err:
            print(f'Erro ao atualizar pedido da mesa {numero_mesa} - Erro: {err}')

        finally:
            cursor.close()
            conn.close()

    def excluir_mesa(self, numero_mesa):
        conn, cursor = self.conectar()

        try:
            sql = "DELETE FROM mesas WHERE numero = %s"
            value = (numero_mesa,)

            cursor.execute(sql, value)
            conn.commit()
            return True, numero_mesa
        
        except mysql.connector.Error as err:
            return False, f'Err: {err}'

        finally:
            cursor.close()
            conn.close()

    def excluir_item(self, id_item):
        conn, cursor = self.conectar()

        try:
            sql_check = "SELECT COUNT(*) as total FROM pedidos WHERE id_cardapio = %s"
            cursor.execute(sql_check, (id_item,))
            resultado = cursor.fetchone()

            count = resultado.get('total', 0)

            if count > 0:
                return False, f'Erro: O item (ID {id_item}) está associado a {count} pedidos. Não é possível excluir para evitar perda de dados.'

            sql = "DELETE FROM cardapio WHERE id = %s"
            value = (id_item,)

            cursor.execute(sql, value)
            linhas_afetadas = cursor.rowcount

            if linhas_afetadas == 0:
                return False, f'Erro: Item (ID {id_item}) não encontrado na tabela cardapio ou não pode ser excluído (verifique associações em outras tabelas).'

            conn.commit()
            return True, id_item

        except mysql.connector.IntegrityError as err:  # Específico para erros de FOREIGN KEY/constraint
            return False, f'Erro de integridade: O item (ID {id_item}) está em uso em outra tabela (ex.: pedidos ou mesas). Detalhes: {err}'
        
        except mysql.connector.Error as err:
            return False, f'Erro: {err}'

        finally:
            cursor.close()
            conn.close()

    def buscar_mesas_ocupadas(self):
        conn, cursor = self.conectar()

        try:
            sql = "SELECT * FROM mesas WHERE status = 'ocupada' ORDER BY numero"
            cursor.execute(sql)
            resultados = cursor.fetchall()

            return [row['numero'] for row in resultados] if resultados else []
        
        except mysql.connector.Error as err:
            return False, f'Erro: {err}'

        finally:
            cursor.close()
            conn.close()

    def buscar_status_mesa(self, numero_mesa=None):
        conn, cursor = self.conectar()

        try:

            sql = "SELECT status FROM mesas WHERE numero = %s"
            cursor.execute(sql, (numero_mesa,))
            resultado = cursor.fetchone()

            status = resultado.get('status', None)

            if status is None:
                print(f'\033[1;31mMesa {numero_mesa} não encontrada.\033[0m')
                return None
            
            return status.lower()
        
        except mysql.connector.Error as err:
            return False, f'Erro: {err}'
    
        finally:
            cursor.close()
            conn.close()

    def buscar_item_cardapio(self, id_item):
        conn, cursor = self.conectar()

        try:
            sql = "SELECT * FROM cardapio WHERE id = %s"
            cursor.execute(sql, (id_item,))
            return cursor.fetchone()
        
        except mysql.connector.Error as err:
            return False, f'Erro: {err}'
        
        finally:
            cursor.close()
            conn.close()

    def buscar_preco(self, nome_item):
        conn, cursor = self.conectar()

        if not conn:
            return None
        
        try:
            sql = "SELECT preco FROM cardapio WHERE item = %s"
            cursor.execute(sql, (nome_item,))
            resultado = cursor.fetchone()

            if resultado:
                return resultado['preco']
            else:
                return None
        except mysql.connector.Error as err:
            print(f'Err: {err}')

        finally:
            cursor.close()
            conn.close()
    
    def _buscar_todos_pedidos(self):
        conn, cursor = self.conectar()
        try:
            sql = """
            SELECT 
                p.*,
                m.numero AS mesa_numero,
                c.item,
                COALESCE(p.total_item, 0) AS total_item,
                COALESCE(p.status, 'n/a') AS status
            FROM pedidos p
            INNER JOIN mesas m ON p.id_mesa = m.id
            INNER JOIN cardapio c ON p.id_cardapio = c.id
            WHERE DATE(p.data_hora) = CURDATE()
            ORDER BY m.numero ASC, p.data_hora  ASC
            """
            cursor.execute(sql)  # Sem parâmetros, pois é global (todas as mesas)
            resultados = cursor.fetchall()
            
            if not resultados:
                return []  # Lista vazia se sem pedidos
            
            # Converte para lista de dicts (compatível com tupla ou dict do cursor)
            if isinstance(resultados[0], dict):
                return resultados
            else:
                colunas = [desc[0] for desc in cursor.description]  # Pega nomes das colunas
                pedidos_list = [dict(zip(colunas, row)) for row in resultados]
                return pedidos_list
                
        except mysql.connector.Error as err:
            print(f'Erro ao buscar pedidos: {err}')
            return []
        
        finally:
            cursor.close()
            conn.close()

    def buscar_pedidos_detalhados(self, numero_mesa):
        conn, cursor = self.conectar()

        try:
            sql = """
                SELECT p.id, 
                    m.numero as mesa_numero, 
                    c.item, 
                    COALESCE(p.quantidade, 0) AS quantidade,
                    COALESCE(p.preco_unitario, 0.0) AS preco_unitario,
                    COALESCE(p.total_item, 0.0) AS total_item,
                    COALESCE(p.status, 'n/a') AS status
                FROM pedidos p
                INNER JOIN mesas m ON p.id_mesa = m.id
                INNER JOIN cardapio c ON p.id_cardapio = c.id
                WHERE m.numero = %s
                ORDER BY p.id ASC
                """
            
            cursor.execute(sql, (numero_mesa,))
            resultados = cursor.fetchall()

            if not resultados:
                return  []
            
            if isinstance(resultados[0], dict):
                pedidos_list = resultados
            else:
                colunas = [desc[0] for desc in cursor.description]  # Pega nomes das colunas
                pedidos_list = [dict(zip(colunas, row)) for row in resultados]

            return pedidos_list

        except mysql.connector.Error as err:
            print(f'Erro: {err}')
            return []

        finally:
            cursor.close()
            conn.close()

    def buscar_pedidos_n_pagos(self, numero_mesa=None):
        conn, cursor = self.conectar()

        data = datetime.now().strftime("%Y-%m-%d")

        try:
            sql = """SELECT p.id, c.item, p.quantidade,
            p.preco_unitario, p.total_item, p.status,
            m.numero as numero_mesa
            FROM pedidos p
            JOIN mesas m ON p.id_mesa = m.id
            JOIN cardapio c ON p.id_cardapio = c.id
            WHERE p.status = 'aberto'
            AND DATE(p.data_hora) = %s
            """

            value = [data]

            if numero_mesa is not None:
                sql += " AND m.numero = %s"
                value.append(numero_mesa)


            sql += " ORDER BY m.numero, p.id"

            cursor.execute(sql, value)
            resultados = cursor.fetchall()
            return resultados if resultados else []
        
        except mysql.connector.Error as err:
            print(f'Erro: {err}')

        finally:
            cursor.close()
            conn.close()   

    def calcular_faturamento(self):
        conn, cursor = self.conectar()

        data = datetime.now().strftime("%Y-%m-%d")

        try:
            sql = "SELECT SUM(p.total_item) AS faturamento_total FROM pedidos p WHERE p.status = 'pago' AND DATE(p.data_hora) = %s"

            cursor.execute(sql, (data,))
            resultado = cursor.fetchone()

            faturamento = resultado['faturamento_total'] if resultado and resultado['faturamento_total'] else 0

            return round(float(faturamento), 2) if faturamento else 0
        
        except mysql.connector.Error as err:
            return False, f'Erro: {err}'

        finally:
            cursor.close()
            conn.close()

    def contar_pedidos_n_pagos(self, numero_mesa=None):
        conn, cursor = self.conectar()
        
        data = datetime.now().strftime("%Y-%m-%d")
        
        try:
            if numero_mesa:
                sql = """SELECT COUNT(*) AS total FROM pedidos p
                JOIN mesas m on p.id_mesa = m.id 
                WHERE p.status = 'aberto' AND m.numero = %s AND DATE(p.data_hora) = %s"""

                cursor.execute(sql, (numero_mesa, data,))

            else:
                sql = "SELECT COUNT(*) AS total FROM pedidos p WHERE p.status = 'aberto' AND DATE(p.data_hora) = %s"

                cursor.execute(sql, (data,))

            resultado = cursor.fetchone()

            if resultado:
                return resultado['total']
            else:
                print(f'Nenhum pedido encontrado para a mesa {numero_mesa}')
                return 0

        except mysql.connector.Error as err:
            print(f'Erro: {err}')
        
        finally:
            cursor.close()
            conn.close()

    def contar_mesas_disponiveis(self):
        conn, cursor = self.conectar()

        try:
            sql = "SELECT COUNT(*) AS total FROM mesas WHERE status = 'livre'"
            cursor.execute(sql)

            resultado = cursor.fetchone()

            if resultado:
                return resultado['total']
            else:
                return 0
        
        except mysql.connector.Error as err:
            return False, f'Erro: {err}'

        finally:
            cursor.close()
            conn.close()
            
    @property
    def mesas(self):
        conn, cursor = self.conectar()
        if not conn:
            return None
        try:
            sql = "SELECT * FROM mesas ORDER BY numero"
            cursor.execute(sql)
            resultados = cursor.fetchall()
            return resultados
        except mysql.connector.Error as err:
            print(f'Erro: {err}')
        
        finally:
            cursor.close()
            conn.close()

    @property
    def cardapio(self):
        conn, cursor = self.conectar()
        if not conn:
            return None
        try:
            sql = "SELECT * FROM cardapio"
            cursor.execute(sql)
            return cursor.fetchall()
        except mysql.connector.Error as err:
            print(f'Erro: {err}')

        finally:
            cursor.close()
            conn.close()



