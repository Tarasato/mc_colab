run_server(
    path="Minecraft-server", # <- Directory / Name of the server containing folder in drive
    ngrok_tunnels=[
          # Add your custom ngrok tunnels here
          #         {
          #             "port": 4711,
          #             "type": "tcp",
          #             "callback":lambda urls: log("Extra TCP Tunnel: "+urls[0].replace("tcp://",""))
          #         }
      ],
       )