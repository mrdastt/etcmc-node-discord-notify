import datetime
import json
import os.path
import time
import easyocr
import pyautogui
import requests
from PIL import Image
from discord_webhook import DiscordWebhook, DiscordEmbed

###################################################################################################################################################
# Super simple script. Uses OCR via screenshot to grab the ETCMC balance, converts the value using data from coingecko API & sends a discord notification via webhook. 
# Gives you an estimated withdraw date (100 - <your tokens>)
# Does not modify any aspect or integrate with your node, strictly screenshots -> text & convert -> discord
#
# You are prompted to configure on first launch with details, or you can create a config.json in the same directory as this script, containing these values:
#
#    {
#        "fiat": "usd",
#        "discordWebhook": "<your-channel-webhook-url>",
#        "node_name": "<any-name-to-identify>",
#        "delay": <time-in-seconds> IE: 7200.00,
#        "estimated_daily_earnings": <est-number-of-tokens-mined-per-day> IE: 8.2
#    }
#
# Notes: Requires python3.11 installed & requirements.txt
# - 'fullSetup.ps1' is a powershell script that will install chocolatey and python3.11, install the required packages, and start the script.
#   You should not need to run 'setup.bat' if you run the powershell script.
# - Setup: click 'setup.bat' OR in terminal: pip install -r requirements.txt 
# - Run: click 'run.bat' OR in terminal: python main.py
# - 'Earnings' values may change in the future, keep this in mind, you can update this in the config.json
# 
# ETCMC GETH GUI SHOULD BE RAN IN FULLSCREEN
#
# Get discord webhook guide (copy from channel): https://support.discord.com/hc/en-us/articles/228383668-Intro-toWebhooks
#
# - If this helped you, tips are always appreciated & optional: 0x1E9a43e2fA3d962DDbeEFf58ee67F0997EEbCFa5 (ETC)
#
# Future (WIP): 
# - Easier multi-node setup, caching & api routing
# - Possible web-ui & task automations
###################################################################################################################################################


def post_message_to_discord(embed, mined_value, fiat, webhook_url, user_id=None):
    content = f"<@{user_id}>" if user_id else ""
    webhook = DiscordWebhook(url=webhook_url, content=content)
    with open("./cropped.png", "rb") as f:
        webhook.add_file(file=f.read(), filename=f"{mined_value}_{fiat}.png")
    embed.set_image(url=f"attachment://{mined_value}_{fiat}.png")
    webhook.add_embed(embed)
    webhook.execute()

def get_balance():
    is_floatable = False
    while not is_floatable:
        reader = easyocr.Reader(['en'], verbose=False)
        pyautogui.screenshot().save('screen.png')
        image = Image.open('./screen.png')
        width, height = image.size
        cropped_image = image.crop((width-200, 27, width, 58))
        cropped_image.save("cropped.png")
        results = reader.readtext("./cropped.png")
        ocr_text = " ".join([result[1] for result in results])
        balance_text = ocr_text.strip().replace("ETCPOW Balance: ", "")
        try:
            balance = float(balance_text)
            is_floatable = True
        except Exception as e:
            print(e)
            time.sleep(10)
    return balance

def convert_to_fiat(balance, fiat):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids=etcpow&vs_currencies={fiat}&include_market_cap=true&include_24hr_vol=true&include_24hr_change=true&include_last_updated_at=true&precision=2"
    response = requests.get(url)
    data = response.json()["etcpow"]
    return round(balance * float(data[fiat]), 3), data

def get_withdraw_estimate(node_etcpow_tokens, est_daily_earnings):
    remaining_tokens = 100 - node_etcpow_tokens
    estimated_days = remaining_tokens / est_daily_earnings
    estimated_payout_time = (datetime.datetime.now() + datetime.timedelta(days=estimated_days)).strftime('%I:%M%p, %m-%d-%y')
    return estimated_payout_time, remaining_tokens

def main():
    config = get_config()
    embed = DiscordEmbed(title=f"Monitoring Node Status", color=0xFFA500, description=f"Balance updates will be sent every {config['delay']/3600} hours")
    embed.set_author(name=f"{config['node_name'].upper()} ✅", url="https://www.coingecko.com/en/coins/etcpow", icon_url="https://images.squarespace-cdn.com/content/v1/64189e78e28fe362e04402a3/4acfcefe-68b5-444f-9ac7-b7ee4392ceb3/ETCMC_LOGO-removebg-preview.png")
    webhook = DiscordWebhook(url=config['discordWebhook'])
    webhook.add_embed(embed)
    webhook.execute()
    while True:
        node_etcpow_tokens = get_balance()
        withdraw_date, remaining_tokens = get_withdraw_estimate(node_etcpow_tokens, config['estimated_daily_earnings'])
        mined_value, data = convert_to_fiat(node_etcpow_tokens, config['fiat'])
        next_update = (datetime.datetime.now() + datetime.timedelta(seconds=config['delay'])).strftime('%I:%M%p, %m-%d-%y')
        if float(node_etcpow_tokens) >= 100:
            embed = create_embed_withdraw_ready(config, mined_value, node_etcpow_tokens, data, next_update)
        else:
            embed = create_embed_current_balance(config, mined_value, node_etcpow_tokens, remaining_tokens, data, withdraw_date, next_update)
        post_message_to_discord(embed, mined_value, config['fiat'], config['discordWebhook'], config['discord_user_id'])
        time.sleep(config["delay"])

def get_config():
    if os.path.isfile("./config.json"):
        with open("./config.json", "r") as f:
            config = json.load(f)
    else:
        config = create_config()
    return config

def create_config():
    available_fiat = ["usd", "aud", "brl", "cad", "chf", "clp", "cny", "eur", "gbp"]
    config = {}
    curr_fiat = "none"
    while curr_fiat not in available_fiat:
        print("Please enter the name of the fiat you want the price to be converted")
        curr_fiat = input(f"Available fiats {available_fiat} :")
    config["fiat"] = curr_fiat
    config["node_name"] = input("Enter a name for your node:")
    config["discordWebhook"] = input("Enter the link of discord webhook : ")
    config['estimated_daily_earnings'] = float(input("Enter the estimated daily ETCPOW Token earnings (Example: 8.2): "))
    config['discord_user_id'] = input("Enter your Discord User ID for @ pings (optional): ") or None
    curr_delay = 0
    while curr_delay == 0:
        try:
            tmp_delay = input("Please enter the refresh time in minutes : ")
            curr_delay = float(tmp_delay) * 60
        except Exception as e:
            print(e)
    config["delay"] = curr_delay
    with open("./config.json", "w") as fp:
        json.dump(config, fp, indent=4)
    return config

def create_embed_withdraw_ready(config, mined_value, node_etcpow_tokens, data, next_update):
    embed = DiscordEmbed(title=f"Withdraw Ready! **{mined_value} {config['fiat'].upper()}**", color=0x00FF00)
    embed.set_author(name=f"{config['node_name'].upper()} 💰", url="https://www.coingecko.com/en/coins/etcpow", icon_url="https://images.squarespace-cdn.com/content/v1/64189e78e28fe362e04402a3/4acfcefe-68b5-444f-9ac7-b7ee4392ceb3/ETCMC_LOGO-removebg-preview.png")
    embed.add_embed_field(name="ETCPOW Tokens", value=f"**{node_etcpow_tokens}**", inline=True)
    embed.add_embed_field(name="Token Price", value=f"**{data[config['fiat']]} {config['fiat'].upper()}**", inline=True)
    embed.add_embed_field(name="Trading Volume", value=f"{data['usd_24h_vol']:,.2f} {config['fiat'].upper()}", inline=True)
    embed.add_embed_field(name="Total Value", value=f"**{mined_value} {config['fiat'].upper()}**", inline=True)
    embed.add_embed_field(name="Next Update:", value=f"{next_update}", inline=True)
    return embed

def create_embed_current_balance(config, mined_value, node_etcpow_tokens, remaining_tokens, data, withdraw_date, next_update):
    embed = DiscordEmbed(title=f"Current Balance: **{mined_value} {config['fiat'].upper()}**", color=0x00FFFF)
    embed.set_author(name=f"{config['node_name'].upper()} ⛏️", url="https://www.coingecko.com/en/coins/etcpow", icon_url="https://images.squarespace-cdn.com/content/v1/64189e78e28fe362e04402a3/4acfcefe-68b5-444f-9ac7-b7ee4392ceb3/ETCMC_LOGO-removebg-preview.png")
    embed.add_embed_field(name="POW Tokens:", value=f"**{node_etcpow_tokens}**", inline=True)
    embed.add_embed_field(name="Remaining Tokens:", value=f"**{remaining_tokens}**", inline=True)
    embed.add_embed_field(name="Token Price:", value=f"**{data[config['fiat']]} {config['fiat'].upper()}**", inline=True)
    embed.add_embed_field(name="24h Change:", value=f"**{data['usd_24h_change']:.2f}%**", inline=True)
    embed.add_embed_field(name="Trading Volume:", value=f"{data['usd_24h_vol']:,.2f} {config['fiat'].upper()}")
    embed.add_embed_field(name="Market Cap:", value=f"{data['usd_market_cap']} {config['fiat'].upper()}", inline=True)
    embed.add_embed_field(name="~Estimated Withdraw:", value=f"{withdraw_date}", inline=True)
    embed.add_embed_field(name="Next Update:", value=f"{next_update}", inline=True)
    return embed

if __name__ == "__main__":
    main()