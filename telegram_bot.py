import asyncio
import sys
import telebot
import os
from dotenv import load_dotenv

load_dotenv()

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not TOKEN or not CHAT_ID:
    print("❌ ERROR GRAVE: Faltan credenciales en el archivo .env")
    sys.exit(1)

bot = telebot.TeleBot(TOKEN)

def enviar_alerta_paso1(partido, equipo_valor, cuota, probabilidad, casa="Desconocida"):
    """Envía instrucciones para una apuesta simple con valor detectado"""
    mensaje = (
        "📊 [VALOR DETECTADO - PASO 1]\n"
        f"⚽ Partido: {partido}\n"
        f"🏛️ Casa: {casa}\n"
        f"🎯 Apostar a: [{equipo_valor}]\n"
        f"💎 Cuota: {cuota}\n"
        f"🎯 Prob. Calculada: {probabilidad}%\n\n"
        f"💡 Instrucción: Apuesta SIMPLE solo a [{equipo_valor}] en {casa}."
    )
    try:
        bot.send_message(CHAT_ID, mensaje)
        print("✅ Alerta Paso 1 enviada correctamente.")
    except Exception as e:
        print(f"❌ Error al enviar Paso 1: {e}")

def enviar_alerta_paso2(partido, s1, s2, c1, c2, ganancia, roi, mercado_a, mercado_b, casa_a, casa_b):
    """Envía instrucciones con los nombres reales de las casas de apuestas"""
    total = s1 + s2
    mensaje = (
        "🔥 [SUREBET ENCONTRADA - PASO 2]\n"
        f"⚽ Partido: {partido}\n"
        f"💰 Inversión Total: ${total}\n\n"
        f"🏛️ {casa_a}: Apuesta ${s1} a [{mercado_a}] (Cuota {c1})\n"
        f"🏛️ {casa_b}: Apuesta ${s2} a [{mercado_b}] (Cuota {c2})\n\n"
        f"✅ Ganancia Asegurada: ${ganancia:.2f} ({roi:.2f}%)\n"
        "🚀 Instrucción: Realiza ambas apuestas SIMULTÁNEAMENTE."
    )
    try:
        bot.send_message(CHAT_ID, mensaje)
        print("✅ Alerta Paso 2 enviada correctamente.")
    except Exception as e:
        print(f"❌ Error al enviar Paso 2: {e}")