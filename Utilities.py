remove_server(
    path="Minecraft-server"
)

start_http_files(
    path="Minecraft-server"
)

server_directory_shell(
    path="Minecraft-server"
)

start_filebrowser(
    path="Minecraft-server"
)

view_available_versions()

apply_custom_props(
    path="Minecraft-server",
    props={
        "online-mode": "false",
        "motd": "\u00A72The best minecraft server!\u00A7r\n\u00A7424/7 Server!"
    }
)