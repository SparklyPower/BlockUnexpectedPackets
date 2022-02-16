import time
import subprocess
import select
from sh import tail
import os
import threading
from discord_webhook import DiscordWebhook

DISCORD_WEBHOOK = "discord webhook url here"

print("Starting Script...")

read_timeout_map = {}

def restart_script():
  print("Exiting script to avoid issues when BungeeCord restarts...")

  try:
    webhook = DiscordWebhook(
      url=DISCORD_WEBHOOK,
      rate_limit_retry=True,
      content='Restarting the `block_unexpected.py` script to avoid issues when BungeeCord restarts or when the log file rotates...'
    )
    response = webhook.execute()
  except:
    # nothing
    print("Something went wrong while trying to send the script restarting message")

  # quit()
  os._exit(1)

threading.Timer(1800.0, restart_script).start()

def substring_after(s, delim):
    return s.partition(delim)[2]

# runs forever
for line in tail("-f", "latest.log", _iter=True):
    if "InitialHandler - read timed out" in line:
        print("Matched InitialHandler - read timed out!")
        ip = substring_after(line, "]: [/").split(':')[0]
        print(line)
        print(ip)

        read_timeout_current_count = read_timeout_map.get(ip, 0) + 1
        print("Current Read Timeout Count for ", ip, " is ", read_timeout_current_count)
        read_timeout_map[ip] = read_timeout_current_count
        if read_timeout_current_count >= 250:
            os.system("ipset add badips " + ip)

            try:
                webhook = DiscordWebhook(
                   url=DISCORD_WEBHOOK,
                   rate_limit_retry=True,
                   content='IP `' + ip + '` had a lot of read timeouts in a short period of time, so the IP was blocked in the firewall because so many read timeouts in a short period of time is sus, yay!'
                )
                response = webhook.execute()
            except:
                # nothing, keep going, this is to avoid unresolved exceptions not adding bad IPs to our list
                print("Something went wrong while trying to send the Bad IP message")
    if "Unexpected packet received during login process" in line:
        print("Matched unexpected packet!")
        ip = substring_after(line, "]: [/").split(':')[0]
        print(line)
        print(ip)

        os.system("ipset add badips " + ip)
        try:
          webhook = DiscordWebhook(
              url=DISCORD_WEBHOOK,
              rate_limit_retry=True,
              content='IP `' + ip + '` sent a unexpected packet during login, so the IP was blocked in the firewall because people sending a unexpected packet is sus, yay!'
          )
          response = webhook.execute()
        except:
          # nothing, keep going, this is to avoid unresolved exceptions not adding bad IPs to our list
          print("Something went wrong while trying to send the Bad IP message")