from db import BancoDeDados
from restaurante import Restaurante
from interface import Interface

b1 = BancoDeDados()
r1 = Restaurante()
i1 = Interface()

b1.setup_inicial()
i1.menu_pedidos()