import sqlite3
import time
import telegram_bot

DB_NAME = "apuestas.db"

CASA_SHARP = "Pinnacle"

def analizar_cuotas():
    print("🧠 Cerebro Matemático REAL activado. Buscando ineficiencias (Sharp vs Soft)...")
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 
                o_soft.Id, 
                m.HomeTeam, 
                m.AwayTeam, 
                o_soft.BookmakerName, 
                o_soft.HomeWin AS Cuota_Soft, 
                o_sharp.HomeWin AS Cuota_Sharp
            FROM Matches m
            JOIN Odds o_soft ON m.Id = o_soft.MatchId
            JOIN Odds o_sharp ON m.Id = o_sharp.MatchId
            WHERE o_sharp.BookmakerName = ? 
              AND o_soft.BookmakerName != ?
              AND o_soft.IsValueBet = 0
        """, (CASA_SHARP, CASA_SHARP))
        
        filas = cursor.fetchall()
        alertas_enviadas = 0

        for fila in filas:
            odd_id, home_team, away_team, bookmaker_soft, cuota_soft, cuota_sharp = fila

            if not cuota_soft or not cuota_sharp or cuota_soft <= 0 or cuota_sharp <= 0:
                continue

            prob_real = (1 / cuota_sharp) / 1.03
            
            edge = (prob_real * cuota_soft) - 1
            
            if edge > 0.03: 
                prob_porcentaje = round(prob_real * 100, 2)
                
                cursor.execute("""
                    UPDATE Odds 
                    SET IsValueBet = 1, ProbabilityCalculated = ? 
                    WHERE Id = ?
                """, (prob_porcentaje, odd_id))
                
                partido_str = f"{home_team} vs {away_team}"
                telegram_bot.enviar_alerta_paso1(
                    partido=partido_str,
                    equipo_valor=home_team, 
                    cuota=cuota_soft,
                    probabilidad=prob_porcentaje,
                    casa=bookmaker_soft
                )
                alertas_enviadas += 1
                print(f"💰 VALOR! {partido_str} | Casa: {bookmaker_soft} | Edge: {edge*100:.2f}%")
                time.sleep(2)
            else:
                cursor.execute("UPDATE Odds SET IsValueBet = 1 WHERE Id = ?", (odd_id,))

        conn.commit()
        cursor.close()
        conn.close()
        
        if alertas_enviadas > 0:
            print(f"✅ Se enviaron {alertas_enviadas} alertas de ALTO VALOR a Telegram.")
        else:
            print("⏳ Análisis completado. No se encontró valor real (Edge > 3%) en el mercado actual.")

    except Exception as e:
        print(f"❌ Error al analizar: {e}")

if __name__ == "__main__":
    analizar_cuotas()