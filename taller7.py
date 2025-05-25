import simpy
import random
import numpy as np
from dataclasses import dataclass


# parametros simulación
SEMILLA = 34
DIAS = 30
HORAS = 24
MINUTOS = 60

THICK = 1
THIN = 0

BLUE = 0
RED = 1
WHITE = 2

num_arrival_orders_day = lambda: random.randint(80, 110)

lambda_15min = 1 / 15
lambda_20min = 1 / 20
lambda_30min = 1 / 30

time_process_filamento = lambda tipo: (\
    np.random.exponential(1 / lambda_20min) 
    if tipo == THICK 
    else np.random.exponential(1 / lambda_15min))
time_process_tela = lambda tipo: (
    np.random.exponential(1 / lambda_30min) 
    if tipo == THICK 
    else np.random.exponential(1 / lambda_20min))

probability_blue_machine_thick = 0.2
is_blue_machine_thick = lambda: random.random() < probability_blue_machine_thick
probability_red_machine_thick = 0.5
is_red_machine_thick = lambda: random.random() < probability_red_machine_thick
probability_white_machine_thick = 0.7
is_white_machine_thick = lambda: random.random() < probability_white_machine_thick

    # variables gloabales
@dataclass
class global_variables:
    ordenes_hoy: list[list]
    ordenes_ayer: list[list]
    
# variables de estado


# varaibles estadisticas


# funciones auxiliares
def agendar_final_maquina_filamento_azul():
    pass
def agendar_final_maquina_filamento_roja():
    pass
def agendar_final_maquina_filamento_blanca():
    pass

def generar_lista_pedidos():
    ordenes = [[],[],[]]
    num_today = num_arrival_orders_day()
    for i in range(num_today):
        color = random.randint(0, 2)
        ordenes[color].append(0)
    return ordenes


# eventos
def inicio_dia(global_vars: global_variables):
    ayer_esta_vacio = all(not sublist for sublist in global_vars.ordenes_ayer)


    # cargar ordenes para hoy
    if ayer_esta_vacio: 
        global_vars.ordenes_hoy = global_vars.ordenes_ayer
    else: 
        for i in range(len(global_vars.ordenes_ayer)):
            global_vars.ordenes_hoy[i].extend(global_vars.ordenes_ayer[i])

    # agendar eventos iniciales por color
    


    # agendar eventos para mañana
    global_vars.ordenes_ayer = generar_lista_pedidos()






if __name__ == "__main__":
    random.seed(SEMILLA)

    env = simpy.Environment()

    env.run(until = DIAS * HORAS * MINUTOS)

