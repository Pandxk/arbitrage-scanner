import os
import sys
from datetime import datetime

def correr_ciclo_completo():
    hora_actual = datetime.now().strftime("%H:%M:%S")
    print(f"\n🚀 [{hora_actual}] INICIANDO RASTREO AUTOMÁTICO DE LIGAS MENORES...")

    python_path = sys.executable

    print("-> Ejecutando main.py (Scraper)...")
    os.system(f'"{python_path}" main.py')

    print("-> Ejecutando procesar_valor.py (Búsqueda de Valor)...")
    os.system(f'"{python_path}" procesar_valor.py')

    print("-> Ejecutando motor_arbitraje.py (Calculadora de Arbitraje)...")
    os.system(f'"{python_path}" motor_arbitraje.py')

    print(f"✅ [{datetime.now().strftime('%H:%M:%S')}] CICLO COMPLETADO. Servidor en reposo.")

if __name__ == "__main__":
    correr_ciclo_completo()