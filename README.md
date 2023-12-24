# ETCMC Node Discord Notifier
(WIP) Quick Simple script to setup balance status/notifications via discord webhooks. Utilizes Coingecko API, modified base from https://github.com/BaLaurent/ETCMC_discord_balance.

Details balance of ETCPOW nodes and sends notifications to discord.
## Features

- **Automatic Balance Detection**: Utilizes OCR to detect the ETCMC node's balance from a screenshot.
- **Currency Conversion**: Converts the ETC balance to a specified fiat currency using CoinGecko's API.
- **Discord Integration**: Sends balance updates to a Discord channel via webhooks.
- **Estimates Withdraw Dates**: Calculates the estimated date of withdrawal based on the current balance and daily earnings.
- **Market details**: Provides the current price of ETCPOW, volume, and other market details.

## Requirements

- Python 3.11
- Pillow (PIL)
- easyocr
- requests
- discord_webhook
- pyautogui

## Installation 

**Full Helper Setup:**
   - Use the 'fullSetup.ps1' powershell script to install chocolatey and python3.11, install the required packages, and start the script. You do not need to run 'setup.bat' if you run the script.
   - This method assumes you don't have python installed and will install it for you with chocolatey.

**Normal Setup:**
   - Assuming you already have git & python 3.11 installed
1. **Clone the Repository:**
   ```bash
      git clone https://github.com/mrdastt/etcmc-node-discord-notify
   ```

2. **Install Dependencies:**

   Click & execute:
   ```
   setup.bat
   ```

      **OR** 
      
   Run one of the commands below manually:
   ```bash
      pip install pillow easyocr requests discord_webhook pyautogui
      pip install -r requirements.txt
   ```


## Usage
Click & execute:
```
run.bat
```
**OR**

Run the script manually:
```bash
python main.py
```



## Configuration
You will be prompted when you first run the script to enter these values, or you can create the config.json file yourself.
- `fiat`: The target fiat currency for conversion (e.g., USD, EUR).
- `discordWebhook`: The Discord webhook URL for posting updates.
- `delay`: The time interval (stored in seconds) for balance checking and posting updates.
- `node_name`: The name of the node you are running.
- `estimated_daily_earnings`: The estimated daily earnings of the node.

## Example Messages:

## Support 🍵
- If this helped you, tips are always appreciated & optional (ETC):  **0x1E9a43e2fA3d962DDbeEFf58ee67F0997EEbCFa5** 

## References:
- Get discord webhook: https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks