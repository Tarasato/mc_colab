install_server(
    proxy={
      "service": "ngrok", # Elige ngrok o playit o "ngrok-playit"

      "token": "", # <- Insert your ngrok token here, you can get it at https://dashboard.ngrok.com/auth.
        # AVAILABLE REGIONS
        # ap - Asia/Pacific (Singapore)
        # au - Australia (Sydney)
        # eu - Europa (Frankfurt - Alemania)
        # in - India (Mumbai)
        # jp - Japan (Tokyo)
        # sa - America del sur (São Paulo - Brasil)
        # us - United States (Ohio)
      "region": "in" # <- Change this to the region you prefer.
    },
    path="Minecraft-server", # <- Directory / Name of the server container folder in drive
    version="1.20.1", # <- Minecraft server version

    # TYPES OF SERVERS AVAILABLE
    # VANILLA:
    # vanilla  1.20.1 - 1.2.5
    # snapshot 23w35a - 1.3
    # SERVERS:
    # paper 1.20.1 - 1.8.8
    # purpur 1.20.1 - 1.14.1
    # sponge 1.12.2 - 1.8.9
    # MODDED:
    # forge 1.20.1 - 1.5.2
    # fabric 1.20.1 - 1.14
    # mohist 1.20.1 - 1.7.10
    # magma 1.20.1 - 1.12.2
    # catserver 1.18.2 - 1.12.2
    # PROXIES:
    # waterfall 1.19 - 1.11
    # bungeecord 1.20 - 1.19
    # velocity (No minecraft version) 3.2.0 - 1.0.10
    type_="forge", # <- Type of Server

    custom_url=""
)