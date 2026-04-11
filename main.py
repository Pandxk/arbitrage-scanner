import requests
import sqlite3
import os
from datetime import datetime
import time
from dotenv import load_dotenv

#Carga las llaves maestras desde el archivo .env
load_dotenv()

DB_NAME = "apuestas.db"

def inicializar_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Matches (
            Id INTEGER PRIMARY KEY,
            LeagueName TEXT,
            HomeTeam TEXT,
            AwayTeam TEXT,
            MatchDate TEXT,
            Status TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Odds (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            MatchId INTEGER,
            BookmakerName TEXT,
            HomeWin REAL,
            Draw REAL,
            AwayWin REAL,
            IsValueBet INTEGER DEFAULT 0,
            ProbabilityCalculated REAL,
            FOREIGN KEY(MatchId) REFERENCES Matches(Id)
        )
    """)
    conn.commit()
    conn.close()

def obtener_diccionario_equipos(fecha, headers):
    print("📡 Obteniendo nombres reales de los equipos...")
    url = "https://v3.football.api-sports.io/fixtures"
    querystring = {"date": fecha}
    mapa_equipos = {}
    
    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        data = response.json()
        
        for partido in data.get('response', []):
            f_id = partido['fixture']['id']
            home = partido['teams']['home']['name']
            away = partido['teams']['away']['name']
            mapa_equipos[f_id] = (home, away)
            
        print(f"✅ Se cargaron {len(mapa_equipos)} partidos en memoria.")
    except Exception as e:
        print(f"❌ Error al obtener fixtures: {e}")
        
    return mapa_equipos

def guardar_en_bd(partido, casa_apuestas, mapa_equipos):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        match_id = partido["fixture"]["id"]
        league = partido["league"]["name"]
        
        # Buscamos los nombres en nuestro diccionario usando el ID 
        # Si por alguna razón el ID no está, usamos un valor por defecto para que no crashee
        nombres = mapa_equipos.get(match_id, ("Equipo Local", "Equipo Visitante"))
        home_team = nombres[0]
        away_team = nombres[1]
        
        raw_date = partido["fixture"]["date"]
        match_date = raw_date[:19].replace('T', ' ') 

        # Insertar partido (Ignora si ya existe gracias a OR IGNORE)
        cursor.execute("""
            INSERT OR IGNORE INTO Matches (Id, LeagueName, HomeTeam, AwayTeam, MatchDate, Status)
            VALUES (?, ?, ?, ?, ?, 'NS')
        """, (match_id, league, home_team, away_team, match_date))

        home_win, draw, away_win = 0.0, 0.0, 0.0
        bookmaker_name = casa_apuestas["name"]

        for apuesta in casa_apuestas.get("bets", []):
            if apuesta["name"] == "Match Winner":
                for valor in apuesta["values"]:
                    if valor["value"] == "Home": home_win = valor["odd"]
                    elif valor["value"] == "Draw": draw = valor["odd"]
                    elif valor["value"] == "Away": away_win = valor["odd"]

        cursor.execute("""
            INSERT INTO Odds (MatchId, BookmakerName, HomeWin, Draw, AwayWin)
            VALUES (?, ?, ?, ?, ?)
        """, (match_id, bookmaker_name, home_win, draw, away_win))

        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"❌ Error al guardar en BD: {e}")
        
def fetch_odds_for_today():
    inicializar_db() 
    
    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
    api_key = os.getenv("API_SPORTS_KEY")
    
    if not api_key:
        print("❌ ERROR GRAVE: No se encontró API_SPORTS_KEY en el archivo .env")
        return

    headers = {
        "x-apisports-key": api_key
    }

    mapa_equipos = obtener_diccionario_equipos(fecha_hoy, headers)

    print(f"\n🚀 Iniciando captura masiva de cuotas para hoy: {fecha_hoy}")
    url_odds = "https://v3.football.api-sports.io/odds"
    
    for pagina in range(1, 6):
        querystring = {"date": fecha_hoy, "page": str(pagina)}
        
        try:
            print(f"📡 Descargando página de cuotas {pagina}...")
            response = requests.get(url_odds, headers=headers, params=querystring)
            response.raise_for_status() 
            data = response.json()
            
            partidos = data.get('response', [])
            
            if not partidos:
                print(f"🏁 Fin de datos en la página {pagina}.")
                break
                
            for partido in partidos:
                bookmakers = partido.get("bookmakers", [])
                if bookmakers:
                    guardar_en_bd(partido, bookmakers[0], mapa_equipos)
            
            print(f"✅ Página {pagina} procesada.")
            time.sleep(1) 

        except Exception as e:
            print(f"❌ Error en página {pagina}: {e}")
            break

    print("\n🎉 ¡Recolección terminada! Sistema cargado con los nombres reales de los equipos.")

if __name__ == "__main__":
    fetch_odds_for_today()