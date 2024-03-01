# @title # **Run this code** {display-mode: "form"}
# markdown Recuerda ejecutar primero este codigo para que todas las demas celdas funcionen.
import requests
from google.colab import drive
import requests
import json
import os
import glob
from types import FunctionType
import base64
import subprocess
import sys
try:
  from pyngrok import conf, ngrok
  from pyngrok.conf import PyngrokConfig
except:
  !pip install -q pyngrok --quiet --upgrade
  from pyngrok import conf, ngrok
  from pyngrok.conf import PyngrokConfig
from google.colab import runtime
try:from rich import print
except:
  !pip install rich --quiet --upgrade
  from rich import print
try:import semver
except:
  !pip install semver --quiet --upgrade
  import semver

!command -v filebrowser &>/dev/null || curl -fsSL https://raw.githubusercontent.com/filebrowser/get/master/get.sh | bash &>/dev/null
!command -v dig &>/dev/null || sudo apt install dnsutils
!sudo apt update >/dev/null
!sudo apt upgrade >/dev/null

def log(text:str):
  print("[bold green][LOG][/bold green] "+text)

def exit():
  runtime.unassign()

AIKAR_FLAGS="--add-modules=jdk.incubator.vector -XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:MaxGCPauseMillis=200 -XX:+UnlockExperimentalVMOptions -XX:+DisableExplicitGC -XX:+AlwaysPreTouch -XX:G1HeapWastePercent=5 -XX:G1MixedGCCountTarget=4 -XX:InitiatingHeapOccupancyPercent=15 -XX:G1MixedGCLiveThresholdPercent=90 -XX:G1RSetUpdatingPauseTimePercent=5 -XX:SurvivorRatio=32 -XX:+PerfDisableSharedMem -XX:MaxTenuringThreshold=1 -Dusing.aikars.flags=https://mcflags.emc.gs -Daikars.new.flags=true -XX:G1NewSizePercent=30 -XX:G1MaxNewSizePercent=40 -XX:G1HeapRegionSize=8M -XX:G1ReservePercent=20"
SERVERJARS_URLS=[
    ["https://launchermeta.mojang.com/mc/game/version_manifest.json", "vanilla"],
    ["https://launchermeta.mojang.com/mc/game/version_manifest.json", "snapshot"],
    ["https://papermc.io/api/v2/projects/paper/", "paper"],
    ["https://papermc.io/api/v2/projects/waterfall/", "waterfall"],
    ["https://api.purpurmc.org/v2/purpur/", "purpur"],
    ["modded/forge", "forge"],
    ["proxies/bungeecord","bungeecord"],
    ["proxies/velocity","velocity"],
    ["modded/fabric", "fabric"],
    ["modded/catserver", "catserver"],
    ["servers/sponge", "sponge"],
    ["https://mohistmc.com/api/versions", "mohist"],
    ["https://api.magmafoundation.org/api/v2/allVersions", "magma"]
]

def view_available_versions():
  txt=""
  for url in SERVERJARS_URLS:
    versions=[]
    if url[0].startswith("http"):
      req=requests.get(url[0])
      res=json.loads(req.content.decode())
      if url[1] in ["paper","purpur","waterfall"]:versions=res["versions"][::-1]
      if url[1] in ["magma","mohist"]:versions=res
      if url[1] == "vanilla":
        for o in res["versions"]:
          if o["type"][0]=="r":
              if o["id"] == "1.2.4":
                  break
              versions.append(o["id"])
      if url[1]=="snapshot":
        for o in res["versions"]:
          if o["type"][0]=="s":
              if o["id"] == "1.3":
                  versions.append(o["id"])
                  break
              versions.append(o["id"])
    else:
      req=requests.get(f"https://serverjars.com/api/fetchAll/{url[0]}/200")
      res=json.loads(req.content.decode())
      versions=[version["version"] for version in res["response"]]
    txt+=url[1].upper()+":\n"+"\n".join([' '.join(versions[i:i+10]) for i in range(0, len(versions), 10)])+"\n"
  print(txt)

def connect_ngrok(port, type_, config):
  log("Starting ngrok...")
  tok=config["token"]
  log("Configuring ngrok...")
  ! ngrok authtoken $tok
  ngrokc:PyngrokConfig=conf.get_default()
  ngrokc.region = config["region"]
  log("Configured.")
  url=""
  try:
    if type_=="tcp":
      url = ngrok.connect(port, 'tcp')
    else:
      url = ngrok.connect(port)
    log("Ngrok connected.")
  except Exception as e:
    log("Hubo un problema al iniciar ngrok porfavor revise su token.")
    exit()
  url=[e.replace('"',"") for e in str(url)[13:].split(" -> ")]
  if config.get("ip") and type_=="tcp":
    u=url[0].replace("tcp://","").split(":")[0]
    result=subprocess.check_output(["dig","+short",u]).decode().replace("\n","")
    url[0]=url[0].replace(u,result)
  return url

def disconnect_ngrok(tunnel):
  ngrok.disconnect(tunnel.public_url)

def exit_ngrok():
  log("Closing ngrok...")
  tunnels = ngrok.get_tunnels()
  for tunnel in tunnels:
    disconnect_ngrok(tunnel)
  ngrok.kill()
  log("Ngrok closed.")

def load_server_props(path:str):
  folder=server_folder(path)
  with open("server.properties","r") as f:
    lines=f.read().split("\n")
    if lines[-1]=='':
      del lines[-1]
  props={}
  for line in lines:
    if line[0]=="#":continue
    l=line.split("=")
    props[l[0]]=l[1]
  return props

def save_server_props(path:str,props:dict):

  folder=server_folder(path)

  txt=""
  for prop in props:
    txt+=prop+"="+props[prop]+"\n"

  with open("server.properties","w") as f:
    f.write(txt)

def apply_custom_props(path:str,props:dict):
  fileprops=load_server_props(path)
  for prop in props:
    fileprops[prop]=props[prop]
  save_server_props(path,fileprops)

def get_url_version(version, type_) -> str:
  url = ""
  if type_ in [u[1] for u in SERVERJARS_URLS]:
    if type_=="magma":
      return f"https://api.magmafoundation.org/api/v2/{version}/latest/download"
    if type_=="mohist":
      return f"https://mohistmc.com/api/{version}/latest/download"
    if type_=="purpur":
      return f"https://api.purpurmc.org/v2/purpur/{version}/latest/download"
    if type_=="paper":
      latest_build = requests.get("https://papermc.io/api/v2/projects/paper/versions/" + version)
      filename = requests.get("https://papermc.io/api/v2/projects/paper/versions/" + version + "/builds/" + str(latest_build.json()["builds"][-1]))
      return "https://papermc.io/api/v2/projects/paper/versions/" + version + "/builds/" + str(latest_build.json()["builds"][-1]) + "/downloads/" + filename.json()["downloads"]["application"]["name"]
    if type_ in ["vanilla","snapshot"]:
      versionsw = requests.get("https://launchermeta.mojang.com/mc/game/version_manifest.json")
      versions=json.loads(versionsw.content.decode())["versions"]
      versionw=requests.get([o for o in versions if o["id"]==version][0]["url"])
      version=json.loads(versionw.content.decode())
      return version["downloads"]["server"]["url"]
    versions=[u[1] for u in SERVERJARS_URLS]
    url="https://serverjars.com/api/fetchJar/"+SERVERJARS_URLS[versions.index(type_)][0]+"/"+version
  else:
    exit()
  return url

def install_jar(path, url, filename, type_, version):
  log("Downloading jar file...")
  r = requests.get(url)
  if r.status_code == 200:
    with open(os.path.join(path,filename), 'wb') as f:
      f.write(r.content)
  else:
    print('Error '+ str(r.status_code))
  log("Downloaded jar file.")
  if type_ == 'fabric':
    log("Installing fabric...")
    !java -jar $filename server -mcversion $version -downloadMinecraft &>/dev/null
  if type_ == 'forge':
    log("Installing forge...")
    !java -jar $filename --installServer &>/dev/null
    if "1.17">version:
      !mv $filename installer-$filename
      forgefile=glob.glob(os.path.join(path,f"forge-{version}-*.jar"))[0]
      !mv $forgefile $filename
  log("Jar file installed successfully.")

def remove_server(path):
  server_folder(path)
  os.chdir("..")
  !rm -rf $path

def server_folder(path, check=False, cd=True):
  back_path=os.getcwd()
  os.chdir("/content/")
  if not os.path.exists("drive"):
    log("Mounting google drive...")
    drive.mount('/content/drive')
    log("Mounted")
  if check:
    if not os.path.exists(os.path.join("/content/drive/MyDrive/",path)):
      print("ERROR Invalid Server path - Not found "+path)
      exit()
  path=os.path.join("/content/drive/MyDrive/",path)
  if not os.path.exists(path):
    ! mkdir "$path"
  if cd:
    os.chdir(path)
  else:
    os.chdir(back_path)
  return path

def start_filebrowser(path:str):
  server_path=server_folder(path)
  config=import_config()
  urls=connect_ngrok(8005, "http", config["proxy"])
  log(f"Filebrowser: [link={urls[0]}]{urls[0]}[/link]")
  !filebrowser -r "$server_path" -p 8005

def server_directory_shell(path):
  path=server_folder(path="Minecraft-server")
  while True:
    path=os.getcwd().split("/")
    path.pop(0)
    prompt="/server/"
    code=None
    if len(path)==4:
      try:code=input(prompt+" >>")
      except:print("exit")
    else:
      for i in range(len(path)-4):
        prompt+=path[4+i]+"/"
      try:code=input(prompt+" >>")
      except:print("exit")

    if code:
      if code.startswith("cd"):
        os.chdir(code[3:])
        continue

      if code=="exit":
        break

      !$code
    else:
      break

def start_http_files(path):
  print("Starting http server...")
  server_folder(path=path)
  config=import_config()
  urls=connect_ngrok(8000, "http", config["proxy"])
  print("Files web in "+urls[0])
  !python -m http.server >/dev/null

def install_server(proxy:dict={},version:str="1.20.1", type_:str="vanilla", path:str="Minecraft-Server", custom_url:str=""):
  log("Installing server...")
  path=server_folder(path)
  if type_=="custom":
    url=custom_url
  else:
    url=get_url_version(version,type_)

  filename=type_+"-"+version+".jar"
  install_jar(path, url, filename,type_,version)

  json.dump({"version":version,"type":type_,"filename":filename,"proxy": proxy}, open("colabconfig.json",'w'))
  !echo "eula=true" > eula.txt
  log("Successfully installed server.")

def import_config() -> dict:
  if os.path.isfile("colabconfig.json"):
    return json.load(open("colabconfig.json"))
  else:
    print("Error: colabconfig.json not found.")
    exit()

def install_java(version:str, type_:str):
  if semver.compare(version if len(version.split("."))==3 else version+".0", "1.17.0")==-1:
    log("Installing JRE 8...")
    java_path="/usr/lib/jvm/java-8-openjdk-amd64/bin/java"
    !sudo apt-get install openjdk-8-jre-headless &>/dev/null || echo "Failed to install OpenJdk8."
  else:
    log("Installing JRE 17...")
    java_path="/usr/lib/jvm/java-17-openjdk-amd64/bin/java"
    !sudo apt-get install openjdk-17-jre-headless &>/dev/null || echo "Failed to install OpenJdk17."

  log("JRE installed.")

  return java_path

def get_methods(clss):
  return [x for x, y in clss.__dict__.items() if type(y) == FunctionType and str(x)!="__init__"]

class RunCommand:

  def __init__(self, config):
    self.version=config["version"]
    self._type=config["type"]

  def get(self,args,jarname) -> str:
    list_of_types=get_methods(RunCommand)
    list_of_types.remove("get")
    self.args=args
    self.jarname=jarname
    if self._type in list_of_types:
      # The custom starts for servers
      return getattr(self, self._type)().format(
          args=args,
          jarname=jarname
      )
    else:
      # The default start
      return '{args} -jar {jarname} nogui'.format(
          args=args,
          jarname=jarname
      )

  def forge(self):
    if self.version < "1.17":
        return '{args} -jar "{jarname}" nogui'
    else:
      pathtoforge = glob.glob(f"libraries/net/minecraftforge/forge/{self.version}-*/unix_*.txt")
      args=self.args
      !echo $args > user_jvm_args.txt
      if pathtoforge:
        return '@user_jvm_args.txt "@'+pathtoforge[0]+'" nogui "$@"'
      else:
        log("No unix_args.txt found.")

  def purpur(self):
    return AIKAR_FLAGS+" {args} -jar {jarname} nogui"

  def paper(self):
    return AIKAR_FLAGS+" {args} -jar {jarname} nogui"

def install_playit():
  ! curl -SsL https://playit-cloud.github.io/ppa/key.gpg | sudo apt-key add -
  ! sudo curl -SsL -o /etc/apt/sources.list.d/playit-cloud.list https://playit-cloud.github.io/ppa/playit-cloud.list
  ! sudo apt update &>/dev/null && sudo apt install playit &>/dev/null && echo "Playit.gg installed" || echo "Failed to install playit"

def run_server(path:str,ngrok_tunnels:list=[]):
  log("Starting server...")
  !sudo apt update &>/dev/null || echo "apt cache update failed"
  server_path=server_folder(path, True)
  log("Loading config...")
  configfile=import_config()
  log("Config loaded")
  jpath=install_java(configfile["version"],configfile["type"])
  args="-Xms8704M -Xmx8704M"

  if configfile["proxy"]["service"]=="ngrok":
    configfile["proxy"]["ip"]=True
    urls=connect_ngrok(25565,"tcp",configfile["proxy"])
    log("Minecraft IP Server: "+urls[0].replace("tcp://",""))



  if configfile["proxy"]["service"] in ["ngrok","ngrok-playit"]:
    for tunnel in ngrok_tunnels:
        tunnel_urls=connect_ngrok(tunnel["port"],tunnel["type"],configfile["proxy"])
        if tunnel.get("callback"):
          tunnel["callback"](tunnel_urls)

  if configfile["proxy"]["service"] in ["playit","ngrok-playit"]:
    install_playit()

  command=RunCommand(configfile)
  cmd=command.get(jarname=configfile["filename"],args=args)

  log("Starting jar file...")
  if configfile["proxy"]["service"] in ["playit","ngrok-playit"]:
    !playit & $jpath $cmd
  else:
    !$jpath $cmd
  log("Finalized server.")
  exit_ngrok()