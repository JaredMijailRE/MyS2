import simpy
import random
import numpy as np
from scipy import stats as sp_stats
import math

# --- Parámetros del Modelo (en minutos donde aplique) ---
HORAS_DIA_NORMAL = 8
MINUTOS_POR_HORA = 60
JORNADA_NORMAL_MINUTOS = HORAS_DIA_NORMAL * MINUTOS_POR_HORA
COSTO_HORA_EXTRA_MAQUINA = 50  # $/hora-máquina

COLORES = ['azul', 'rojo', 'blanco']
GROSORES = ['delgado', 'grueso']

# Probabilidades de grosor por color
PROB_GRUESO = {'azul': 0.20, 'rojo': 0.50, 'blanco': 0.70}

# Tiempos de proceso (media exponencial en minutos)
TIEMPO_FILAMENTO_MEDIO = {'delgado': 15, 'grueso': 20}
TIEMPO_TEJIDO_MEDIO = {'delgado': 20, 'grueso': 30}

# Recursos
NUM_MAQUINAS_FILAMENTO_POR_COLOR = 1
NUM_MAQUINAS_TEJIDO_DELGADO = 2
NUM_MAQUINAS_TEJIDO_GRUESO = 2

# Parámetros de Simulación
NUM_DIAS_SIMULACION = 250
PERIODO_TRANSITORIO_DIAS = 50
RANDOM_SEED = 42

# --- Estadísticas Globales ---
estadisticas_globales = {
    'costos_diarios_horas_extras': [],
    'overtime_total_acumulado_minutos': 0,
    'ordenes_completadas_total_global': 0,
    'orden_id_counter': 0
}

# --- Funciones Auxiliares ---
def calcular_overtime_tarea(t_inicio_trabajo_abs, t_fin_trabajo_abs):
    """Calcula los minutos de overtime para una tarea específica,
    basado en días calendario fijos de JORNADA_NORMAL_MINUTOS."""
    dia_indice_inicio = math.floor(t_inicio_trabajo_abs / JORNADA_NORMAL_MINUTOS)
    dia_norm_cutoff_time_abs_para_tarea = (dia_indice_inicio + 1) * JORNADA_NORMAL_MINUTOS
    
    overtime_minutos = 0
    if t_inicio_trabajo_abs >= dia_norm_cutoff_time_abs_para_tarea: 
        overtime_minutos = t_fin_trabajo_abs - t_inicio_trabajo_abs
    elif t_fin_trabajo_abs > dia_norm_cutoff_time_abs_para_tarea: 
        overtime_minutos = t_fin_trabajo_abs - dia_norm_cutoff_time_abs_para_tarea
    return max(0, overtime_minutos)

# --- Procesos de SimPy ---

def proceso_filamento(env, orden, maquinas_filamento, colas_tejido):
    """Proceso para una orden en una máquina de filamento."""
    color_orden = orden['color']
    grosor_orden = orden['grosor']

    with maquinas_filamento[color_orden].request() as req:
        yield req
        t_inicio_trabajo_abs = env.now
        
        tiempo_proceso = random.expovariate(1.0 / TIEMPO_FILAMENTO_MEDIO[grosor_orden])
        yield env.timeout(tiempo_proceso)
        
        t_fin_trabajo_abs = env.now

        overtime_esta_tarea = calcular_overtime_tarea(t_inicio_trabajo_abs, t_fin_trabajo_abs)
        estadisticas_globales['overtime_total_acumulado_minutos'] += overtime_esta_tarea
        
        colas_tejido[grosor_orden].put(orden)

def proceso_tejido(env, orden, maquinas_tejido_delgado, maquinas_tejido_grueso):
    """Proceso para una orden en una máquina de tejido."""
    grosor_orden = orden['grosor']
    
    recurso_tejido_usar = maquinas_tejido_delgado if grosor_orden == 'delgado' else maquinas_tejido_grueso
    
    with recurso_tejido_usar.request() as req:
        yield req
        t_inicio_trabajo_abs = env.now
        
        tiempo_proceso = random.expovariate(1.0 / TIEMPO_TEJIDO_MEDIO[grosor_orden])
        yield env.timeout(tiempo_proceso)
        
        t_fin_trabajo_abs = env.now

        overtime_esta_tarea = calcular_overtime_tarea(t_inicio_trabajo_abs, t_fin_trabajo_abs)
        estadisticas_globales['overtime_total_acumulado_minutos'] += overtime_esta_tarea
        
        estadisticas_globales['ordenes_completadas_total_global'] += 1


def consumidor_filamento(env, color, maquinas_filamento, colas_filamento, colas_tejido):
    """Proceso demonio que consume órdenes de la cola de filamento para un color."""
    while True:
        orden = yield colas_filamento[color].get()
        env.process(proceso_filamento(env, orden, maquinas_filamento, colas_tejido))

def consumidor_tejido(env, grosor, maquinas_tejido_delgado, maquinas_tejido_grueso, colas_tejido):
    """Proceso demonio que consume órdenes de la cola de tejido para un grosor."""
    while True:
        orden = yield colas_tejido[grosor].get()
        env.process(proceso_tejido(env, orden, maquinas_tejido_delgado, maquinas_tejido_grueso))


def simulation_orchestrator(env, num_sim_days, colas_filamento):
    print(f"Orchestrator: Simulating for {num_sim_days} days of operations.")
    for dia_num in range(num_sim_days):
        overtime_at_start_of_this_day_accounting_period = estadisticas_globales['overtime_total_acumulado_minutos']
        
        current_day_orders_start_time = env.now 

        num_ordenes_hoy = random.randint(80, 110)
        
        for _ in range(num_ordenes_hoy):
            estadisticas_globales['orden_id_counter'] += 1
            orden_id = estadisticas_globales['orden_id_counter']
            color = random.choice(COLORES)
            es_grueso = random.random() < PROB_GRUESO[color]
            grosor = 'grueso' if es_grueso else 'delgado'
            
            orden = {
                'id': orden_id, 
                'color': color, 
                'grosor': grosor,
                't_llegada_sim_abs': env.now 
            }
            colas_filamento[color].put(orden)

        yield env.timeout(JORNADA_NORMAL_MINUTOS) 
        
        overtime_this_accounting_period = estadisticas_globales['overtime_total_acumulado_minutos'] - overtime_at_start_of_this_day_accounting_period
        costo_overtime_this_day = (overtime_this_accounting_period / MINUTOS_POR_HORA) * COSTO_HORA_EXTRA_MAQUINA
        estadisticas_globales['costos_diarios_horas_extras'].append(costo_overtime_this_day)
        

    print(f"Orchestrator: Finished generating orders for {num_sim_days} days. Sim_time: {env.now:.2f}")
    print("Simulation will continue until all generated orders are processed.")


# --- Ejecución de la Simulación ---
print("Iniciando simulación de la planta textil (Modelo Revisado)...")
random.seed(RANDOM_SEED)
env = simpy.Environment()

# Crear recursos (máquinas)
maquinas_filamento = {color: simpy.Resource(env, capacity=NUM_MAQUINAS_FILAMENTO_POR_COLOR) for color in COLORES}
maquinas_tejido_delgado = simpy.Resource(env, capacity=NUM_MAQUINAS_TEJIDO_DELGADO)
maquinas_tejido_grueso = simpy.Resource(env, capacity=NUM_MAQUINAS_TEJIDO_GRUESO)

# Crear colas (stores)
colas_filamento = {color: simpy.Store(env) for color in COLORES}
colas_tejido = {grosor: simpy.Store(env) for grosor in GROSORES}

# Iniciar procesos consumidores (demonios)
for color in COLORES:
    env.process(consumidor_filamento(env, color, maquinas_filamento, colas_filamento, colas_tejido))
for grosor in GROSORES:
    env.process(consumidor_tejido(env, grosor, maquinas_tejido_delgado, maquinas_tejido_grueso, colas_tejido))

# Iniciar proceso generador de lotes diarios
env.process(simulation_orchestrator(env, NUM_DIAS_SIMULACION, colas_filamento))

# Correr la simulación
env.run()

print("\n--- Simulación Finalizada ---")
print(f"Tiempo de simulación total: {env.now:.2f} minutos ({env.now/MINUTOS_POR_HORA:.2f} horas)")
print(f"Total de órdenes completadas: {estadisticas_globales['ordenes_completadas_total_global']}")
print(f"Total de minutos de overtime acumulado (todas las máquinas): {estadisticas_globales['overtime_total_acumulado_minutos']:.2f} min")

# --- Análisis de Resultados ---

# 1. Costo promedio de horas extras
costos_diarios_estado_estable = []
if len(estadisticas_globales['costos_diarios_horas_extras']) > PERIODO_TRANSITORIO_DIAS:
    costos_diarios_estado_estable = estadisticas_globales['costos_diarios_horas_extras'][PERIODO_TRANSITORIO_DIAS:]
else:
    print(f"Advertencia: No hay suficientes días simulados ({len(estadisticas_globales['costos_diarios_horas_extras'])}) para descartar el periodo transitorio ({PERIODO_TRANSITORIO_DIAS}). Usando todos los datos.")
    costos_diarios_estado_estable = estadisticas_globales['costos_diarios_horas_extras']

if costos_diarios_estado_estable:
    costo_promedio_diario_overtime = np.mean(costos_diarios_estado_estable)
    print(f"\n1. Costo promedio diario de horas extras (estado estable): ${costo_promedio_diario_overtime:.2f}")
else:
    costo_promedio_diario_overtime = 0
    print("\n1. No hay datos suficientes para calcular el costo promedio diario de horas extras en estado estable.")


# 2. Intervalo de confianza y días a simular
print("\n2. Intervalo de Confianza y Días de Simulación:")
if len(costos_diarios_estado_estable) > 1:
    confianza = 0.95
    media = np.mean(costos_diarios_estado_estable)
    sem = sp_stats.sem(costos_diarios_estado_estable)
    grados_libertad = len(costos_diarios_estado_estable) - 1
    
    # Usamos t de Student porque la desviación estándar poblacional es desconocida
    intervalo_conf = sp_stats.t.interval(confianza, grados_libertad, loc=media, scale=sem)
    
    print(f"   Para los {len(costos_diarios_estado_estable)} días en estado estable:")
    print(f"   Intervalo de confianza del {confianza*100}% para el costo promedio diario de horas extras: (${intervalo_conf[0]:.2f}, ${intervalo_conf[1]:.2f})")
    
    # Para determinar cuántos días simular (gráfica de estabilización):
    print(f"\n   Para determinar el número adecuado de días a simular y el período transitorio:")
    print(f"   - Se debería graficar el costo diario de horas extras (o una media móvil de este) contra el número de día.")
    print(f"   - El período transitorio se identifica como el lapso inicial antes de que la media de la métrica se estabilice.")
    print(f"   - La simulación debe correr hasta que la métrica de interés (costo promedio) muestre convergencia.")
    print(f"   - Con {NUM_DIAS_SIMULACION} días simulados y {PERIODO_TRANSITORIO_DIAS} de transitorio, se usaron {len(costos_diarios_estado_estable)} puntos para el IC.")
    print(f"   - Si el ancho del IC es muy grande, se necesitarían más replicaciones (correr toda la simulación múltiples veces con diferentes semillas) o una simulación más larga.")

else:
    print("   No hay suficientes datos en estado estable para calcular un intervalo de confianza.")


# 3. Sugerencias para mejorar el comportamiento del sistema
print("\n3. Sugerencias para Mejorar el Comportamiento del Sistema:")
print(f"   Basado en la simulación, si el costo de horas extras de ${costo_promedio_diario_overtime:.2f} es considerado alto, se podrían explorar las siguientes opciones:")
print(f"   a) Aumentar capacidad de máquinas cuello de botella:")
print(f"      - Analizar las utilizaciones y longitudes de cola (no implementado explícitamente aquí, pero se podrían añadir contadores) para identificar cuellos de botella.")
print(f"      - Por ejemplo, si las máquinas de tejido grueso tienen alta utilización y largas colas, se podría simular el efecto de añadir una máquina adicional (cambiar `NUM_MAQUINAS_TEJIDO_GRUESO` a 3) y observar el impacto en el costo de horas extras.")
print(f"   b) Evaluar la política de aceptación de órdenes o priorización:")
print(f"      - Si ciertos tipos de órdenes (color/grosor específico) contribuyen desproporcionadamente al overtime, se podría considerar su gestión.")
print(f"   c) Optimizar tiempos de proceso (si es posible tecnológicamente):")
print(f"      - Reducir los `TIEMPO_FILAMENTO_MEDIO` o `TIEMPO_TEJIDO_MEDIO` en el simulador para ver su impacto.")
print(f"   d) Política de horas extras:")
print(f"      - Considerar si es más económico, por ejemplo, subcontratar parte de la producción en lugar de pagar extensas horas extras, aunque esto requeriría añadir más lógica al modelo.")
print(f"\n   Para sustentar estas afirmaciones, se modificarían los parámetros relevantes del modelo (ej. número de máquinas, tiempos de proceso) y se re-ejecutaría la simulación para comparar los resultados (principalmente el costo promedio de horas extras y el intervalo de confianza).") 