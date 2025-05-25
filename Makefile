# Makefile para el Proyecto Job Shop - Problema 2.7
# Estructura organizada con directorios separados

# Directorios
SRC_DIR = src
BUILD_DIR = build
DOCS_DIR = docs
OUTPUTS_DIR = outputs

# Compilador y flags
CC = gcc
CFLAGS = -Wall -Wextra -std=c99 -O2 -g

# Archivos fuente
SIMLIB_SOURCES = $(SRC_DIR)/simlib.c
SIMLIB_HEADERS = $(SRC_DIR)/simlib.h $(SRC_DIR)/simlibdefs.h
MAIN_SOURCE = $(SRC_DIR)/taller7_simlib.c
MULTIPLE_SOURCE = $(SRC_DIR)/run_multiple_simulations.c

# Archivos objeto
SIMLIB_OBJ = $(BUILD_DIR)/simlib.o
MAIN_OBJ = $(BUILD_DIR)/taller7_simlib.o
MULTIPLE_OBJ = $(BUILD_DIR)/run_multiple_simulations.o

# Ejecutables
MAIN_EXEC = $(BUILD_DIR)/jobshop_simulation
MULTIPLE_EXEC = $(BUILD_DIR)/multiple_analysis

# Regla principal
all: $(MAIN_EXEC) $(MULTIPLE_EXEC)

# Crear directorios si no existen
$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

$(OUTPUTS_DIR):
	mkdir -p $(OUTPUTS_DIR)

# Compilar biblioteca SIMLIB
$(SIMLIB_OBJ): $(SIMLIB_SOURCES) $(SIMLIB_HEADERS) | $(BUILD_DIR)
	$(CC) $(CFLAGS) -c $(SIMLIB_SOURCES) -o $(SIMLIB_OBJ)

# Compilar programa principal
$(MAIN_OBJ): $(MAIN_SOURCE) $(SIMLIB_HEADERS) | $(BUILD_DIR)
	$(CC) $(CFLAGS) -c $(MAIN_SOURCE) -o $(MAIN_OBJ)

# Compilar análisis múltiple
$(MULTIPLE_OBJ): $(MULTIPLE_SOURCE) $(SIMLIB_HEADERS) | $(BUILD_DIR)
	$(CC) $(CFLAGS) -c $(MULTIPLE_SOURCE) -o $(MULTIPLE_OBJ)

# Enlazar programa principal
$(MAIN_EXEC): $(MAIN_OBJ) $(SIMLIB_OBJ)
	$(CC) $(MAIN_OBJ) $(SIMLIB_OBJ) -o $(MAIN_EXEC) -lm

# Enlazar análisis múltiple
$(MULTIPLE_EXEC): $(MULTIPLE_OBJ) $(SIMLIB_OBJ)
	$(CC) $(MULTIPLE_OBJ) $(SIMLIB_OBJ) -o $(MULTIPLE_EXEC) -lm

# Ejecutar simulación principal
run: $(MAIN_EXEC) | $(OUTPUTS_DIR)
	$(MAIN_EXEC) | tee $(OUTPUTS_DIR)/simulacion_principal.txt

# Ejecutar análisis múltiple
run-multiple: $(MULTIPLE_EXEC) | $(OUTPUTS_DIR)
	$(MULTIPLE_EXEC) | tee $(OUTPUTS_DIR)/analisis_multiple.txt

# Ejecutar simulación Python
run-python: | $(OUTPUTS_DIR)
	sudo uv run python $(SRC_DIR)/taller7_simpy.py | tee $(OUTPUTS_DIR)/simulacion_python.txt

# Limpiar archivos compilados
clean:
	rm -rf $(BUILD_DIR)/*.o $(BUILD_DIR)/jobshop_simulation $(BUILD_DIR)/multiple_analysis

# Limpiar todo (incluyendo outputs)
clean-all: clean
	rm -rf $(OUTPUTS_DIR)/*

# Mostrar estructura del proyecto
structure:
	@echo "=== ESTRUCTURA DEL PROYECTO ==="
	@echo "📁 Directorio raíz:"
	@ls -la --color=auto
	@echo ""
	@echo "📁 src/ (código fuente):"
	@ls -la src/ --color=auto
	@echo ""
	@echo "📁 build/ (archivos compilados):"
	@ls -la build/ --color=auto 2>/dev/null || echo "  (vacío)"
	@echo ""
	@echo "📁 docs/ (documentación):"
	@ls -la docs/ --color=auto 2>/dev/null || echo "  (vacío)"
	@echo ""
	@echo "📁 outputs/ (resultados):"
	@ls -la outputs/ --color=auto 2>/dev/null || echo "  (vacío)"

# Ayuda
help:
	@echo "=== MAKEFILE PARA PROYECTO JOB SHOP ==="
	@echo ""
	@echo "Comandos disponibles:"
	@echo "  make all          - Compilar todo"
	@echo "  make run          - Ejecutar simulación SIMLIB"
	@echo "  make run-multiple - Ejecutar análisis múltiple SIMLIB"
	@echo "  make run-python   - Ejecutar simulación SimPy"
	@echo "  make clean        - Limpiar archivos compilados"
	@echo "  make clean-all    - Limpiar todo"
	@echo "  make structure    - Mostrar estructura del proyecto"
	@echo "  make help         - Mostrar esta ayuda"
	@echo ""
	@echo "Archivos principales:"
	@echo "  📄 $(MAIN_SOURCE)     - Simulación SIMLIB"
	@echo "  📄 $(SRC_DIR)/taller7_simpy.py    - Simulación SimPy"
	@echo "  📄 README.md                      - Documentación principal"

.PHONY: all run run-multiple run-python clean clean-all structure help 