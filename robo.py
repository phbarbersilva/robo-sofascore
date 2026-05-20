import requests
import asyncio
from telegram import Bot

# =========================
# 🔑 TELEGRAM
# =========================
TOKEN = "8774968598:AAEZ2UpYCSXK9L25TrSvqlIgb2T0I6KSiYs"
CHAT_ID = "7156481953"

bot = Bot(token=TOKEN)


# =========================
# 📡 PEGAR JOGOS AO VIVO
# =========================
def pegar_jogos():
    url = "https://api.sofascore.com/api/v1/sport/football/events/live"
    r = requests.get(url)
    data = r.json()
    return data.get("events", [])


# =========================
# 📊 ESTATÍSTICAS
# =========================
def pegar_stats(event_id):
    url = f"https://api.sofascore.com/api/v1/event/{event_id}/statistics"
    r = requests.get(url)

    try:
        data = r.json()
    except:
        return {}

    stats = {}

    try:
        for group in data.get("statistics", []):
            for item in group.get("groups", []):
                name = item.get("name")
                home = item.get("homeValue", 0)
                away = item.get("awayValue", 0)
                stats[name] = (home, away)
    except:
        pass

    return stats


# =========================
# 🔥 ANALISAR JOGO (FILTRO REALISTA)
# =========================
def analisar_jogo(jogo):
    try:
        event_id = jogo.get("id")

        home = jogo["homeTeam"]["name"]
        away = jogo["awayTeam"]["name"]

        stats = pegar_stats(event_id)

        ataques = stats.get("Attacks", (0, 0))
        perigosos = stats.get("Dangerous attacks", (0, 0))
        chutes = stats.get("Shots on target", (0, 0))

        total_att = ataques[0] + ataques[1]
        total_dan = perigosos[0] + perigosos[1]
        total_ch = chutes[0] + chutes[1]

        sinais = []

        if total_att >= 20:
            sinais.append("🔥 Pressão boa")

        if total_dan >= 10:
            sinais.append("⚡ Ataques perigosos")

        if total_ch >= 3:
            sinais.append("🎯 Finalizações no alvo")

        if len(sinais) >= 2:
            return f"""
🚨 POSSÍVEL GREEN 🚨

⚽ {home} vs {away}

📊 Indicadores:
- {', '.join(sinais)}

━━━━━━━━━━━━━━━
"""

    except:
        return None4


# =========================
# 📲 ENVIAR TELEGRAM
# =========================
async def enviar(msg):
    await bot.send_message(chat_id=CHAT_ID, text=msg)


# =========================
# 🚀 MAIN
# =========================
async def main():
    jogos = pegar_jogos()

    sinais = []

    for jogo in jogos[:20]:
        resultado = analisar_jogo(jogo)
        if resultado:
            sinais.append(resultado)

    if sinais:
        await enviar("🚀 ROBÔ ATIVO 🚀\n\n" + "\n".join(sinais))
    else:
        await enviar("❌ Nenhum green no momento.")


asyncio.run(main())
