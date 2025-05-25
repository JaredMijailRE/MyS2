import simpy
import random
import numpy as np
import statistics

# Parámetros exactos del problema 2.7
SEMILLA = 42
DIAS_SIMULACION = 100
MINUTOS_TRABAJO_DIA = 480  # 8 horas
COSTO_HORA_EXTRA = 50.0

# Probabilidades de grosor por color
PROB_THICK = [0.2, 0.5, 0.7]  # [azul, rojo, blanco]

def ejecutar_simulacion_simple():
    """Simulación simplificada para comparar con SIMLIB"""
    random.seed(SEMILLA)
    np.random.seed(SEMILLA)
    
    costos_diarios = []
    
    for dia in range(DIAS_SIMULACION):
        # Generar órdenes del día
        num_ordenes = random.randint(80, 110)
        
        # Simular procesamiento
        tiempo_total_filamento = [0, 0, 0]  # Por color
        tiempo_total_tejido_delgado = 0
        tiempo_total_tejido_grueso = 0
        
        for _ in range(num_ordenes):
            # Determinar color (equiprobable)
            color = random.randint(0, 2)
            
            # Determinar grosor
            grosor = 1 if random.random() < PROB_THICK[color] else 0  # 1=grueso, 0=delgado
            
            # Tiempo de filamento
            if grosor == 1:  # grueso
                tiempo_fil = np.random.exponential(20.0)
            else:  # delgado
                tiempo_fil = np.random.exponential(15.0)
            
            tiempo_total_filamento[color] += tiempo_fil
            
            # Tiempo de tejido
            if grosor == 1:  # grueso
                tiempo_tej = np.random.exponential(30.0)
                tiempo_total_tejido_grueso += tiempo_tej
            else:  # delgado
                tiempo_tej = np.random.exponential(20.0)
                tiempo_total_tejido_delgado += tiempo_tej
        
        # Calcular horas extras
        horas_extra_total = 0
        
        # Filamento (3 máquinas, una por color)
        for i in range(3):
            if tiempo_total_filamento[i] > MINUTOS_TRABAJO_DIA:
                horas_extra = (tiempo_total_filamento[i] - MINUTOS_TRABAJO_DIA) / 60.0
                horas_extra_total += horas_extra
        
        # Tejido delgado (2 máquinas)
        tiempo_por_maquina_delgada = tiempo_total_tejido_delgado / 2
        if tiempo_por_maquina_delgada > MINUTOS_TRABAJO_DIA:
            horas_extra = (tiempo_por_maquina_delgada - MINUTOS_TRABAJO_DIA) / 60.0
            horas_extra_total += horas_extra * 2  # 2 máquinas
        
        # Tejido grueso (2 máquinas)
        tiempo_por_maquina_gruesa = tiempo_total_tejido_grueso / 2
        if tiempo_por_maquina_gruesa > MINUTOS_TRABAJO_DIA:
            horas_extra = (tiempo_por_maquina_gruesa - MINUTOS_TRABAJO_DIA) / 60.0
            horas_extra_total += horas_extra * 2  # 2 máquinas
        
        costo_dia = horas_extra_total * COSTO_HORA_EXTRA
        costos_diarios.append(costo_dia)
        
        if costo_dia > 0:
            print(f"Día {dia+1}: {num_ordenes} órdenes, ${costo_dia:.2f}")
    
    return costos_diarios

def main():
    print("=== SIMULACIÓN SIMPY SIMPLIFICADA ===")
    print("Comparación directa con SIMLIB")
    
    costos = ejecutar_simulacion_simple()
    
    if costos:
        costo_promedio = statistics.mean(costos)
        desv_std = statistics.stdev(costos) if len(costos) > 1 else 0
        
        print(f"\n=== RESULTADOS ===")
        print(f"Costo promedio por día: ${costo_promedio:.2f}")
        print(f"Desviación estándar: ${desv_std:.2f}")
        print(f"Días con horas extras: {sum(1 for c in costos if c > 0)}")
        print(f"Total de días simulados: {len(costos)}")
        
        # Intervalo de confianza
        n = len(costos)
        margen_error = 1.96 * desv_std / (n ** 0.5) if n > 0 else 0
        print(f"Intervalo de confianza (95%): ${costo_promedio:.2f} ± ${margen_error:.2f}")
        
        print(f"\n=== COMPARACIÓN CON SIMLIB ===")
        simlib_resultado = 0.39
        print(f"SIMLIB: ${simlib_resultado:.2f}")
        print(f"SimPy:  ${costo_promedio:.2f}")
        diferencia = abs(costo_promedio - simlib_resultado)
        print(f"Diferencia: ${diferencia:.2f}")

if __name__ == "__main__":
    main() 