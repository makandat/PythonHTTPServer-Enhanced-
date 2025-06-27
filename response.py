# response.py v1.2.1
from http.server import *
import os
import json
import mimetypes
from Cheetah.Template import Template

# Response クラス
class Response:
  OK = "200 OK"
  BAD_REQUEST = "400 Bad Request"
  FORBIDDEN = "403 Forbidden"
  NOT_FOUND = "404 Not_Found"
  METHOD_NOT_ALLOWED = "405 Method Not Allowed"
  INTERNAL_SERVER_ERROR = "500 Internal Server Error"
  NOT_IMPLEMENTED = "501 Not Implemented"
  
  # コンストラクタ
  def __init__(self, base_handler):
    self.base = base_handler
    self.__Status = 200       # レスポンス・ステータス
    self.__Headers = dict()  # Content-Type, Set-Cookie 以外の追加ヘッダ
    self.__Cookies = dict()  # 送信するクッキー
    return
    
  # HTML ファイルを送信する。
  def sendHtml(self, filepath, embed=None):
    res = self.base
    if not os.path.isfile(filepath):
      self.sendStatus(404, Response.NOT_FOUND)
      return
    with open(filepath, "r", encoding="utf-8") as f:
      content = f.read()
    if not (embed is None):
      for key, val in embed.items():
        content = content.replace("{{" + key + "}}", val)
        content = content.replace("{{ " + key + " }}", val)
    res.send_response(self.__Status)
    res.send_header(f"Content-Type", f"text/html; charset=utf-8")
    if len(self.__Headers):
      for key, val in self.__Headers.items():
        if val != "":
          res.send_header(key, val)
    if len(self.__Cookies):
      for key, val in self.__Cookies.items():
        if val == "":
          res.send_header("Set-Cookie", f"{key}=; Max-Age=0")
        else:
          res.send_header("Set-Cookie", f"{key}={val}")
    res.end_headers()
    res.wfile.write(content.encode())
    return

  # 文字列を送信する。
  def sendText(self, content, mime="text/plain"):
    res = self.base
    res.send_response(self.__Status)
    res.send_header("Content-Type", f"{mime}; charset=utf-8")
    res.end_headers()
    res.wfile.write(content.encode())
    return
    
  # v1.1 で追加。
  # Cheetah テンプレートをレンダリングして送信する。
  def render(self, path, embed=None):
    res = self.base
    template = ""
    if os.path.isfile(path):
      with open(path, "rt", encoding="utf-8") as f:
        template = f.read()
      html = str(Template(template, searchList=[embed]))
    else:
      html = path  # パスでなく HTML そのものの場合
    self.sendText(html, mime="text/html")
    return
  
  # JSON を送信する。
  def sendJSON(self, data):
    res = self.base
    content = json.dumps(data)
    res.send_response(self.__Status)
    res.send_header("Content-Type", "application/json; charset=utf-8")
    res.end_headers()
    res.wfile.write(content.encode())
    return
   

  # エラーステータスを返す。
  def sendStatus(self, code, message=""):
    res = self.base
    res.send_response(code)
    res.send_header("Content-Type", "text/html")
    res.end_headers()
    res.wfile.write(message.encode())
    return
    
  # ファイルを送信する。
  def sendFile(self, path):
    res = self.base
    CEXTS = [".html", ".txt", ".xml", ".json", ".jpg", ".png", ".gif", ".svg", ".pdf", ".mp3", ".mp4", ".wav"]
    mime = mimetypes.guess_type(path)[0]
    filename = os.path.basename(path)
    ext = os.path.splitext(path)[1]
    res.send_response(self.__Status)
    charset = ""
    if ext == ".html":
      self.sendHtml(path)
      return
    elif ext == ".txt":
      self.sendText(path)
      return
    elif ext == ".xml" or ext == ".json":
      charset = "; charset=utf-8"
    res.send_header("Content-Type", mime + charset)
    if not (ext in CEXTS):
      res.send_header("Content-Disposition", "attachment; filename=" + filename)
    with open(path, mode="rb") as f:
      buff = f.read()
    res.wfile.write(buff)
    return
  
  # BLOB を送信する。v1.2.0 で追加
  def sendBLOB(self, blob, mime_type):
    res = self.base
    res.send_response(self.__Status)
    res.send_header("Content-Type", mime_type)
    res.wfile.write(blob)
    return
    
  # アップロードされたファイルを保存する。
  @staticmethod
  def saveFile(filename, content, dir="./upload"):
    filepath = f"{dir}/{filename}"
    with open(filepath, "wb") as f:
      f.write(content)
    return

  # リダイレクト v1.1.1
  @staticmethod
  def redirect(res, url):
    res.wfile.write(b"Location: " + url.encode() + b"\n")

  # ステータス
  @property 
  def status(self):
    return self.__Status

  # ステータス変更
  @status.setter
  def status(self, status):
    self.__Status = status
    return

  # クッキーを追加 (あるいは上書き)
  def setCookie(self, name, value):
    self.__Cookies[name] = value
    return

  # レスポンスヘッダの追加 (あるいは上書き)
  def setHeader(self, name, value):
    self.__Headers[name] = value
    return

  # レスポンスクッキー一覧
  @property
  def cookies(self):
    return self.__Cookies

  # レスポンス・ヘッダ一覧
  @property
  def headers(self):
    return self.__Headers

  # HTML リストを作成する。
  @staticmethod
  def htmlList(data, ol=False, list=None, li=None):
    html = "<ul>\n"
    if not (list is None):
      html = f"<ul class=\"{list}\">\n"
    if ol:
      html = "<ol>\n"
      if not (list is None):
        html = f"<ol class=\"{list}\">\n"
    for s in data:
      if li:
        html += f"<li class=\"{li}\">{s}</li>\n"  
      else:
        html += f"<li>{s}</li>\n"
    if ol:
      html += "</ol>\n"
    else:
      html += "</ul>\n"
    return html

  # HTML テーブルを作成する。
  @staticmethod
  def htmlTable(data, header=None, table=None, th=None, tr=None, td=None):
    html = "<table>\n"
    if not (table is None):
      html = f"<table class=\"{table}\">\n"
    if not (header is None):
      if not (tr is None):
        html += f"<tr class=\"{tr}\">"
      else:
        html += "<tr>"
      for h in header:
        if th is None: 
          html += f"<th>{h}</th>"
        else:
          html += f"<th class=\"{th}\">{h}</th>"
      html += "</tr>\n"
    for row in data:
      if not (tr is None):
        html += f"<tr class=\"{tr}\">"
      else:
        html += "<tr>"
        for datumn in row:
          if td is None:
            html += f"<td>{datumn}</td>"
          else:
            html += f"<td class=\"{td}\">{datumn}</td>"
        html += "</tr>\n"
    html += "<table>\n"
    return html
  
  # HTML アンカーを作成する。
  @staticmethod
  def htmlAnchor(url, caption, target=None):
    anchor = f"<a href=\"{url}\""
    if not (target is None):
      anchor += f" target=\"{target}\">"
    else:
      anchor += ">"
    anchor += caption
    anchor += "</a>"
    return anchor
  
  # '&', '<', '>' をエスケープする。  v1.2.0 で追加
  @staticmethod
  def html_escape(s):
    s1 = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return s1
