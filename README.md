# 📈 Arbitrage Scanner

Bot automatizado en **Python** para el escaneo diario de cuotas deportivas en tiempo real mediante **API-Football**, detección de *Value Bets* (comparando casas de apuestas contra **Pinnacle**) y cálculo de oportunidades de arbitraje (*Surebets*) con alertas automáticas vía **Telegram**.

---

## ⚙️ Arquitectura del Pipeline

```text
ejecutar_sistema.py
  ├── 1. main.py              → Descarga fixtures/cuotas del día y las guarda en SQLite (apuestas.db)
  ├── 2. procesar_valor.py    → Detecta Value Bets comparando cuotas soft vs Pinnacle (Edge > 3%)
  ├── 3. motor_arbitraje.py   → Busca cruces de arbitraje (P < 1), calcula stakes y alerta en Telegram
  └── telegram_bot.py         → Envía notificaciones formateadas para Paso 1 (Valor) y Paso 2 (Surebet)
```

### Base de datos local (`apuestas.db`)
- **`Matches`**: `Id`, `LeagueName`, `HomeTeam`, `AwayTeam`, `MatchDate`, `Status`
- **`Odds`**: `Id`, `MatchId`, `BookmakerName`, `HomeWin`, `Draw`, `AwayWin`, `IsValueBet`, `ProbabilityCalculated`

---

## 🛠️ Requisitos e Instalación

- **Python 3.10+**
- Clave de [API-Sports (Football v3)](https://www.api-sports.io/)
- Token y Chat ID de un bot de **Telegram**

```bash
# 1. Clonar el repositorio
git clone https://github.com/Pandxk/arbitrage-scanner.git
cd arbitrage-scanner

# 2. Crear entorno virtual e instalar dependencias
python -m venv .venv
source .venv/bin/activate   # En Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 3. Configurar variables de entorno
cp .env.example .env
```

Completa `.env` con tus credenciales:

```env
API_SPORTS_KEY=tu_api_key
TELEGRAM_TOKEN=tu_bot_token
TELEGRAM_CHAT_ID=tu_chat_id
```

---

## 🚀 Uso

Ejecuta el ciclo completo (recolección → detección de valor → arbitraje):

```bash
python ejecutar_sistema.py
```

También puedes ejecutar cada módulo por separado:

```bash
python main.py
python procesar_valor.py
python motor_arbitraje.py
```

---

## 📄 Licencia

Este proyecto está bajo la licencia **MIT**. Consulta el archivo [LICENSE](./LICENSE) para más detalles.
