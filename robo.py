import requests
import asyncio
from telegram import Bot

# =======================
# 🔴 CONFIGURAÇÃO TELEGRAM
# =======================
TELEGRAM_TOKEN = "8774968598:AAEZ2UpYCSXK9L25TrSvqlIgb2T0I6KSiYs"
CHAT_ID = "7156481953"

bot = Bot(token=TELEGRAM_TOKEN)


# =======================
# 📡 PEGAR JOGOS AO VIVO
# =======================
def pegar_jogos():
    url = "https://api.sofascore.com/api/v1/sport/football/events/live"
    r = requests.get(url)
    data = r.json()
    return data.get("events", [])


# =======================
# 📊 PEGAR ESTATÍSTICAS
# =======================
def pegar_stats(event_id):
    url = f"https://api.sofascore.com/api/v1/event/{event_id}/statistics"
    r = requests.get(url)
    data = r.json()

    stats = {}

    try:
        for group in data["statistics"]:
            for item in group["groups"]:
                stats[item["name"]] = item["homeValue"], item["awayValue"]
    except:
        pass

    return stats


# =======================
# 🔥 ANALISADOR DE GREEN
# =======================
def analisar_jogo(jogo):
    event_id = jogo["id"]

    home = jogo["homeTeam"]["name"]
    away = jogo["awayTeam"]["name"]

    stats = pegar_stats(event_id)

    ataques = stats.get("Attacks", (0, 0))
    perigosos = stats.get("Dangerous attacks", (0, 0))
    chutes = stats.get("Shots on target", (0, 0))

    total_attacks = ataques[0] + ataques[1]
    total_danger = perigosos[0] + perigosos[1]
    total_shots = chutes[0] + chutes[1]

    greens = []

    # 🔥 PRESSÃO DE JOGO
    if total_attacks >= 35:
        greens.append("🔥 Pressão Alta")

    # ⚡ ATAQUES PERIGOSOS
    if total_danger >= 18:
        greens.append("⚡ Ataques Perigosos")

    # 🎯 FINALIZAÇÕES
    if total_shots >= 6:
        greens.append("🎯 Finalizações Ativas")

    # 🔥 REGRA FINAL (SÓ ENVIA SE FOR BOM MESMO)
    if len(greens) >= 2:
        return f"""
🚨 GREEN DETECTADO 🚨

⚽ {home} vs {away}

📊 Indicadores:
- {', '.join(greens)}

━━━━━━━━━━━━━━━
"""

    return None


# =======================
# 📲 ENVIAR TELEGRAM
# =======================
async def enviar(msg):
    await bot.send_message(chat_id=CHAT_ID, text=msg)


# =======================
# 🚀 MAIN DO ROBÔ
# =======================
async def main():
    jogos = pegar_jogos()

    sinais = []

    for jogo in jogos[:25]:
        try:
            sinal = analisar_jogo(jogo)
            if sinal:
                sinais.append(sinal)
        except:
            continue

    if sinais:
        await enviar("🚀 ROBÔ GREEN ATIVO 🚀\n\n" + "\n".join(sinais))
    else:
        await enviar("❌ Nenhum GREEN encontrado no momento.")


# =======================
# ▶️ EXECUTAR
# =======================
asyncio.run(main())
