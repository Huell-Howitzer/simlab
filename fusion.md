Awesome idea — you’re creating a local GitLab notification system that pushes updates to your desktop via Synology Chat and Zenity. Here’s how you can wire it all together step-by-step:

⸻

Goal Recap
	1.	GitLab sends TODO or issue events to Synology Chat via webhooks.
	2.	Synology Chat receives those messages in a dedicated channel.
	3.	A local script monitors this chat channel (via API or webhooks).
	4.	The script uses Zenity to show desktop notifications.

⸻

Step-by-Step Setup

1. Set Up GitLab Webhooks to Synology Chat

You’ll need an Incoming Webhook in Synology Chat.

a. In Synology Chat:
	•	Go to Settings > Integration > Webhook > Incoming Webhook > Create.
	•	Name it something like “GitLab Events”, choose a channel (e.g. #gitlab), and copy the webhook URL.

b. In GitLab:
	•	Go to your project > Settings > Webhooks.
	•	Paste the Synology Chat webhook URL.
	•	Select the events you want (e.g., Todo, Issue, Merge Request).
	•	Optional: Add a secret token.

c. Format Message (optional):

If GitLab lets you set a custom payload or if you use an intermediate server, you can make the message pretty:

{
  "text": "New TODO assigned to you: [Check it out](https://gitlab.com/project/issue/123)",
  "username": "GitLab Bot"
}



⸻

2. Monitor Synology Chat Messages Locally

You’ll create a polling script that checks messages in a certain channel using the Synology Chat API.

a. Enable API access:
	•	In Synology Chat: Settings > Integration > Chatbot > Create.
	•	Get your bot token.

b. Script Example (Python):

import requests
import time
import subprocess

# Configuration
BASE_URL = 'https://your-nas:5001'
TOKEN = 'your_bot_token'
CHANNEL_ID = 'your_channel_id'  # You can find this via API too
LAST_MESSAGE_ID = None

def get_latest_messages():
    url = f"{BASE_URL}/webapi/entry.cgi"
    payload = {
        'api': 'SYNO.Chat.External',
        'method': 'list',
        'version': '2',
        'channel_id': CHANNEL_ID,
        'limit': 5,
        'token': TOKEN
    }
    response = requests.post(url, data=payload, verify=False)
    return response.json().get('messages', [])

def notify(message):
    subprocess.run(['zenity', '--notification', '--text', message])

while True:
    messages = get_latest_messages()
    if messages:
        latest = messages[-1]
        msg_id = latest['id']
        if msg_id != LAST_MESSAGE_ID:
            LAST_MESSAGE_ID = msg_id
            notify(latest['text'])
    time.sleep(10)

Note: This script polls every 10 seconds. You could also build a webhook server if you want to avoid polling.

⸻

3. (Alternative) Direct GitLab → Zenity via Local Script

If you don’t want to go through Synology Chat, you could expose a local webhook listener (e.g., Flask or Node.js), receive GitLab data directly, and pop a Zenity alert.

But using Synology Chat as the central log is nice, especially if you want a history of GitLab events.

⸻

Optional Enhancements
	•	Add filters so only your TODOs trigger Zenity.
	•	Use systemd to run the Python script as a background service.
	•	Add clickable links in Zenity (zenity --info --text="..." can contain URLs).
	•	Log each notification for audit or replay.

⸻

Want a ready-to-run Python or Bash version of the whole script? Or help with the Chat channel ID lookup/API login?



---



Perfect — let’s make this into a background service using systemd, so it starts automatically on boot and keeps running in the background.

⸻

1. Save Your Python Script

Save the notifier script to a permanent location, for example:

sudo mkdir -p /opt/synology-chat-notifier
sudo nano /opt/synology-chat-notifier/notifier.py

Paste the script in, save, and then:

sudo chmod +x /opt/synology-chat-notifier/notifier.py



⸻

2. Create a systemd Service File

Now create a systemd unit file:

sudo nano /etc/systemd/system/synology-chat-notifier.service

Paste the following content:

[Unit]
Description=Synology Chat Desktop Notifier
After=network.target

[Service]
ExecStart=/usr/bin/python3 /opt/synology-chat-notifier/notifier.py
Restart=on-failure
RestartSec=5
User=your-username
Environment=DISPLAY=:0
Environment=XAUTHORITY=/home/your-username/.Xauthority

[Install]
WantedBy=default.target

Important:
	•	Replace your-username with your actual Linux username.
	•	DISPLAY=:0 assumes you’re running a graphical session on display :0 (standard for local X sessions).
	•	If Zenity notifications don’t work, make sure the service has permission to access your user session.

⸻

3. Enable and Start the Service

sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable synology-chat-notifier.service
sudo systemctl start synology-chat-notifier.service

To check logs:

journalctl -u synology-chat-notifier.service -f



⸻

4. Test It Works on Reboot

Reboot your system:

sudo reboot

Once logged into your desktop, wait a moment — you should get Zenity popups when messages come into your Synology Chat channel.

⸻

Optional Enhancements
	•	Add logging to a file for auditing (StandardOutput and StandardError in the unit file).
	•	Add message filtering in the Python script (e.g., only show TODOs or mentions).
	•	Auto-check channel_id or fetch it dynamically if you rotate channels often.

⸻

Want help with any of these extras? Or adding GitLab-specific message parsing so it only notifies on TODOs assigned to you?
