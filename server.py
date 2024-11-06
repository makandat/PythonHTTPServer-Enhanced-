#!/usr/bin/env python3
from http.server import *
from handlers import *
from request import Request
from response import Response
import os, json, re

# v1.2.0 2024-11-05
VERSION = "1.2.0"
CONFIG = "./config.json"
HOST = "localhost"
PORT = 4040
STATIC = "./html"
TEMPLATES = "./templates"
DOWNLOAD = "c:/temp"

# v1.2.0
settings ={"host":HOST, "port":PORT, "static":STATIC, "templates":TEMPLATES, "download":DOWNLOAD}

# スタティックなファイルのパスを得る。
def get_static(file):
  global settings
  filepath = settings["static"] + "/" + file
  return filepath

# テンプレートファイルのパスを得る。
def get_template(file):
  global settings
  filepath = settings["templates"] + "/" + file
  return filepath

# 設定ファイルを読む。
def read_conf(conffile):
  if os.path.exists(conffile):
    with open(conffile, "rt", encoding="utf-8") as f:
      settings = json.load(f)
      return settings
  else:
    return None


# リクエストハンドラ
class CustomRequestHander(SimpleHTTPRequestHandler):
  # コンストラクタ
  def __init__(self, request, client_address, server):
    # 初期化動作が必要な場合は、ここに書く。
    super().__init__(request, client_address, server)
    # ここにコードを書いても実行されない。
    return
  
  # GET メソッドハンドラ
  def do_GET(self):
    req, res = (Request(self), Response(self))
    path = req.path
    m = re.match(r"^\/\w+\/\w+", path)
    if path in GET_MAP.keys():  # ルートがあるか?
      on_get = GET_MAP[path]
      on_get(req, res)
    elif os.path.isfile(get_static(path)):  # 静的ファイルがあるか？
      res.sendFile("./html" + path)
    elif path == "" or path == "/":  # / のみなら index.html
      res.sendHtml(get_static("index.html"))
    elif not (m is None):  # パスパラメータがあるか？
      parts = path.split("/")
      path1 = "/" + parts[1] + "/@"
      on_get = GET_MAP[path1]
      on_get(req, res)
    else:
      res.sendStatus(404, Response.NOT_FOUND)
    return
    
  # POST メソッドハンドラ
  def do_POST(self):
    req, res = (Request(self), Response(self))
    path = self.path
    if path in POST_MAP.keys():  # ルートがあるか?
      on_post = POST_MAP[path]
      on_post(req, res)
    else:  # ルートがない場合
      res.sendStatus(404, Response.NOT_FOUND)
      return
    return

# HTTP サーバの起動
def run(server_class=HTTPServer, handler_class=CustomRequestHander):
  # v1.1.1
  conf = read_conf(CONFIG)
  if conf != None:
     global settings
     settings = conf
  server_address = (settings["host"], settings["port"])
  print(f"http://{server_address[0]}:{server_address[1]}")
  httpd = server_class(server_address, handler_class)
  httpd.serve_forever()

# スタート
if __name__ == "__main__":
  print("Starting HTTP Server ...")
  try:
    run()
  except:
    print("Closed HTTP Server.")
