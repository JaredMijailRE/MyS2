/*
 * jobshop_simlib.c
 * Simulación Job Shop (Problema 2.7) usando SIMLIB
 * Tres máquinas de filamento (azul, rojo, blanco)
 * Cuatro máquinas de tejido (2 delgadas, 2 gruesas)
 * Llegada de pedidos uniformes [80,110] en 8h de jornada, procesan al día siguiente
 * Horas extras: pago $50/hora-máquina más allá de 8h/día
 */

#include "simlib.h"

#define MIN_PER_DAY 480.0     /* 8h * 60min */
#define PAY_RATE 50.0         /* $50 / hora-máquina */

/* Instalación de recursos */
FACILITY FilBlue, FilRed, FilWhite;
STORAGE WeavThin, WeavThick;

/* Variables estadísticas */
double OT_Filament = 0.0, OT_Weave = 0.0;

/* Proporciones de grueso por color */
const double P_THICK[3] = {0.2, 0.5, 0.7};

/* Función de generación de pedidos diarios */
void Arrivals() {
    double t; int n, i, c;
    /* Generar entre 80 y 110 pedidos uniformes durante la jornada */
    n = (int)(80 + (110-80) * Uniform(0,1));
    for (i = 0; i < n; i++) {
        /* tiempos aleatorios dentro de [0, MIN_PER_DAY] no necesario en batch */
        /* Encolamos directamente al siguiente día */
        /* Aquí generamos todos hoy, pero serán atendidos en StartShift */
        /* Usaremos una cola global: QPedidos[color][thickness]++ */
        c = (int)Uniform(0,3);
        /* thickness definido en StartShift */
        /* Incrementar contadores ... */
    }
}

/* Proceso de inicio de turno: atiende pedidos atrasados (batch) */
void StartShift() {
    int c;
    double now = simtime;
    /* Para cada pedido acumulado de color c */
    /* lanzamos un proceso Filamento(c) por pedido */
    for (c = 0; c < 3; c++) {
        /* Para cada pedido: */
        /* Create a FILAMENTO process passing color c */
        /* EVENT: schedule at time now */
    }
    /* Al final del día, generar nuevos pedidos para el siguiente ciclo */
    InsertEvent(MIN_PER_DAY * (int)(now/MIN_PER_DAY + 1), 1, Arrivals);
    /* y reschedule StartShift al siguiente MIN_PER_DAY */
    InsertEvent(MIN_PER_DAY * (int)(now/MIN_PER_DAY + 1), 2, StartShift);
}

/* Proceso de producción de filamento */
void Filamento(int c) {
    Thickness th;
    Facility *machine;
    /* Seleccionar máquina según color */
    if (c == 0) machine = &FilBlue;
    else if (c == 1) machine = &FilRed;
    else machine = &FilWhite;
    /* Decidir grosor */
    th = (Uniform(0,1) < P_THICK[c]) ? THICK : THIN;
    /* Reservar máquina */
    seizable(machine);
    rv(time = simtime);
    /* Tiempo de servicio exponencial */
    t = -log(Uniform(0,1)) / (th==THICK ? (1.0/20.0) : (1.0/15.0));
    use(machine, t);
    release(machine);
    /* Contabilizar horas extras si simtime % MIN_PER_DAY > MIN_PER_DAY */
    if (fmod(simtime, MIN_PER_DAY) > MIN_PER_DAY) OT_Filament += t - MIN_PER_DAY;
    /* Crear proceso Tela(c, th) para etapa siguiente */
    Create("Weaving", Weaving, c * 2 + th);
}

/* Proceso de tejido */
void Weaving(int param) {
    int c = param / 2;
    Thickness th = param % 2;
    double t;
    /* Reservar espacio en STORAGE según grosor */
    if (th == THIN) Get(&WeavThin, 1);
    else Get(&WeavThick, 1);
    /* Tiempo de servicio exponencial */
    t = -log(Uniform(0,1)) / (th==THICK ? (1.0/30.0) : (1.0/20.0));
    /* Simular uso */
    Hold(t);
    /* Liberar */
    if (th == THIN) Release(&WeavThin, 1);
    else Release(&WeavThick, 1);
    /* Contabilizar horas extras */
    if (fmod(simtime, MIN_PER_DAY) > MIN_PER_DAY) OT_Weave += t - MIN_PER_DAY;
}

int main() {
    /* Inicializar SIMLIB */
    Init(0, "Job Shop Simulation");
    /* Definir recursos */
    CreateFacility("FilBlue", 1);
    CreateFacility("FilRed", 1);
    CreateFacility("FilWhite", 1);
    CreateStorage("WeavThin", 2);
    CreateStorage("WeavThick", 2);
    /* Agregar eventos de arranque */
    InsertEvent(0.0, 1, Arrivals);
    InsertEvent(0.0, 2, StartShift);
    /* Correr simulación hasta convergencia o N días */
    Run();
    /* Reportar resultados */
    printf("Horas extra filamento: %.2f\n", OT_Filament/60.0);
    printf("Horas extra tejido: %.2f\n", OT_Weave/60.0);
    printf("Pago total: $%.2f\n", (OT_Filament+OT_Weave)/60.0 * PAY_RATE);
    return 0;
}
