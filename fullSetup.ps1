# Install Chocolatey
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
Import-Module $env:ChocolateyInstall\helpers\chocolateyProfile.psm1
refreshenv

# Install Python 3.11 via Chocolatey
choco install python --version=3.11.0 -y
refreshenv

# Install Git
choco install git -y
refreshenv

# Clone the project
git clone https://github.com/mrdastt/etcmc-node-discord-notify

# Navigate to the project directory
cd .\etcmc-node-discord-notify

# Install the project requirements
pip install -r requirements.txt
refreshenv

# echo to terminal "Open the folder cloned and click run.bat to start!"
echo "Open the folder cloned and click run.bat to start!"
