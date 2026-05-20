import requests
from telegram import Bot

# =========================
# 🔑 TELEGRAM
# =========================
TOKEN = "8774968598:AAEZ2UpYCSXK9L25TrSvqlIgb2T0I6KSiYs"
CHAT_ID = "7156481953"

bot = Bot(token=TOKEN)


# =========================
# 📡 JOGOS AO VIVO
# =========================
def pegar_jogos():
    url = "https://api.sofascore.com/api/v1/sport/football/events/live"
    r = requests.get(url, timeout=20)
    return r.json().get("events", [])


# =========================
# 📊 STATS
# =========================
def pegar_stats(event_id):
    url = f"https://api.sofascore.com/api/v1/event/{event_id}/statistics"
    r = requests.get(url, timeout=20)

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
# 🔥 ANALISE SIMPLES (ESTÁVEL)
# =========================
def analisar_jogo(jogo):
    try:
        event_id = jogo["id"]

        home = jogo["homeTeam"]["name"]
        away = jogo["awayTeam"]["name"]

        stats = pegar_stats(event_id)

        ataques = stats.get("Attacks", (0, 0))
        perigosos = stats.get("Dangerous attacks", (0, 0))
        chutes = stats.get("Shots on target", (0, 0))

        total_att = ataques[0] + ataques[1]
        total_dan = perigosos[0] + perigosos[1]
        total_ch = chutes[0] + chutes[1]

        if total_att >= 20 and total_dan >= 10:
            return f"""
🚨 POSSÍVEL GREEN 🚨

⚽ {home} vs {away}

📊 Pressão:
- Attacks: {total_att}
- Dangerous: {total_dan}
- Shots: {total_ch}

━━━━━━━━━━━━━━
"""

    except:
        return None


# =========================
# 📲 ENVIAR
# =========================
def enviar(msg):
    bot.send_message(chat_id=CHAT_ID, text=msg)


# =========================
# 🚀 MAIN (SEM ASYNC)
# =========================
def main():
    jogos = pegar_jogos()

    sinais = []

    for jogo in jogos[:20]:
        res = analisar_jogo(jogo)
        if res:
            sinais.append(res)

    if sinais:
        enviar("🚀 ROBÔ ATIVO 🚀\n\n" + "\n".join(sinais))
    else:
        enviar("❌ Nenhum green no momento.")


if _name_ == "_main_":
    main()
