import sqlite3
import telegram_bot
import time

DB_NAME = "apuestas.db"

def calculate_p_value(cuota_a, cuota_b):
    """Paso 1: Calcula si existe una ineficiencia en el mercado (P < 1)"""
    return (1 / cuota_a) + (1 / cuota_b)

def calculate_exact_stakes(inversion_base, cuota_a, cuota_b, p_value):
    """Paso 2: Calcula la matemática pura (con decimales)"""
    stake_a = (inversion_base * (1 / cuota_a)) / p_value
    stake_b = (inversion_base * (1 / cuota_b)) / p_value
    return stake_a, stake_b

def apply_camouflage(stake_a, stake_b):
    """Paso 3: Sistema Anti-Baneo (Múltiplos de $5)"""
    cam_a = max(5, round(stake_a / 5) * 5)
    cam_b = max(5, round(stake_b / 5) * 5)
    return cam_a, cam_b

def recalculate_profit(cam_a, cam_b, cuota_a, cuota_b):
    """Paso 4: Verificador de Peor Escenario"""
    inversion_real = cam_a + cam_b
    retorno_a = cam_a * cuota_a
    retorno_b = cam_b * cuota_b
    
    peor_escenario = min(retorno_a, retorno_b)
    ganancia_neta = peor_escenario - inversion_real
    roi = (ganancia_neta / inversion_real) * 100
    
    return ganancia_neta, roi, inversion_real

def evaluar_partido_y_alertar(partido, casa_a, casa_b, cuota_a, cuota_b, equipo_local, equipo_visitante, presupuesto=100):
    """Ejecuta la matemática y dispara a Telegram si hay ganancia real"""
    p = calculate_p_value(cuota_a, cuota_b)
    
    if p >= 1:
        return False # No hay arbitraje
        
    # Ejecución del pipeline
    ex_a, ex_b = calculate_exact_stakes(presupuesto, cuota_a, cuota_b, p)
    cam_a, cam_b = apply_camouflage(ex_a, ex_b)
    ganancia, roi, inv_real = recalculate_profit(cam_a, cam_b, cuota_a, cuota_b)
    
    if ganancia > 0:
        print(f"🔥 SUREBET ENCONTRADA: {partido} | Ganancia: ${ganancia:.2f}")
        
        telegram_bot.enviar_alerta_paso2(
            partido=partido,
            s1=cam_a,
            s2=cam_b,
            c1=cuota_a,
            c2=cuota_b,
            ganancia=ganancia,
            roi=roi,
            mercado_a=f"Gana {equipo_local}",
            mercado_b=f"Gana {equipo_visitante}",
            casa_a=casa_a,  
            casa_b=casa_b   
        )
        return True
    
    return False

def buscar_arbitraje_en_db():
    print("\n🔍 Buscando cruces de Arbitraje entre casas de apuestas...")
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        query = """
            SELECT 
                m.HomeTeam, m.AwayTeam,
                o1.BookmakerName AS CasaA, o1.HomeWin AS CuotaA,
                o2.BookmakerName AS CasaB, o2.AwayWin AS CuotaB
            FROM Matches m
            JOIN Odds o1 ON m.Id = o1.MatchId
            JOIN Odds o2 ON m.Id = o2.MatchId
            WHERE o1.BookmakerName != o2.BookmakerName
            AND o1.HomeWin > 0 AND o2.AwayWin > 0
        """
        
        cursor.execute(query)
        filas = cursor.fetchall()
        
        alertas = 0
        for fila in filas:
            home_team, away_team, casa_a, cuota_a, casa_b, cuota_b = fila
            partido = f"{home_team} vs {away_team}"
            
            exito = evaluar_partido_y_alertar(partido, casa_a, casa_b, cuota_a, cuota_b, home_team, away_team)
            
            if exito:
                alertas += 1
                time.sleep(2) # Pausa anti-spam para Telegram
                
        if alertas == 0:
            print("⏳ Análisis completado. El mercado está estable, no hay Surebets en este momento.")
        else:
            print(f"✅ ¡Búsqueda finalizada! Se enviaron {alertas} alertas de Surebets a Telegram.")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ Error en el motor de arbitraje: {e}")

if __name__ == "__main__":
    buscar_arbitraje_en_db()