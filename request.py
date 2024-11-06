# request.py v1.1 (2024-01-30)
from http.server import *
import os
import json
import urllib.parse as urlp

# Request クラス
class Request:
  # Request コンストラクタ
  def __init__(self, base_handler):
    self.__base = base_handler
    self.__Method = base_handler.command
    self.__Headers = base_handler.headers
    self.__Path = self._getPath(base_handler.path)
    self.__Query, self.__HttpVersion = self._getQuery(base_handler.requestline)
    self.__Body = self._getBody()
    self.__Form = dict()
    if len(self.__Query) > 0 or self._isMultipartForm() == False: # データ形式が x-www-urlencoded のとき
      self._parseQuery()  # self.form が更新される。
    if self._isJSON():
      self._parseJSON()
    self.__Cookies = self._getCookies(base_handler.headers)
    self.__Files = list()
    self._parseBody()  # POST & multipart/form-data, json, octed-stream の場合以外は何もしない。
    return

  # クエリー文字列とHTTPバージョンを得る。
  def _getQuery(self, reqline:str) -> tuple:
    parts = reqline.split(" ")
    http_version = parts[2]
    if parts[1].find("?") > 0:
      pathparts = parts[1].split("?")
      query_string = pathparts[1]
      return (query_string, http_version)
    else:
      return ("", http_version)
    
  # パラメータを含む可能性のあるパスからパス部分だけを取り出す。
  def _getPath(self, path) -> str:
    if path.find("?") > 0:
      parts = path.split("?", 1)
      return parts[0]
    else:
      return path

  # ヘッダ "cookie" の内容からクッキーの辞書を作成する。
  def _getCookies(self, headers:dict) -> dict:
    cookies = dict()
    if "cookie" in headers:
      cookie = headers["cookie"]
      parts = cookie.split("; ")
      for p in parts:
        kv = p.split("=")
        cookies[kv[0]] = kv[1]
    return cookies

  # POST された生データを取得する。
  def _getBody(self):
    buff = b""
    KEY = "Content-Length"
    if KEY in self.__Headers.keys():
      n = int(self.__Headers[KEY])
      if self.__Method == "POST" and n > 0:
        buff = self.__base.rfile.read(n)
    return buff

  # リクエストデータがマルチパートフォームかどうかを返す。
  def _isMultipartForm(self) -> bool:
    if "Content-Type" in self.__Headers:
      content_type = self.headers["Content-Type"]
      b = content_type.find("multipart") >= 0
      return b
    else:
      return False
      
  # リクエストデータが JSON かどうかを返す。
  def _isJSON(self):
    if "Content-Type" in self.__Headers:
       mime = self.__Headers["Content-Type"]
       return mime.startswith("application/json")
    else:
      return False
      
  # リクエストデータが BLOB (octed-stream) かどうかを返す。
  def _isBLOB(self):
    if "Content-Type" in self.__Headers:
       mime = self.__Headers["Content-Type"]
       return mime.startswith("application/octed-stream")
    else:
      return False
  
  # クエリーデータ (x-www-urlencoded) を辞書に変換する。(POSTの場合も可能)
  def _parseQuery(self):
    if self._isJSON() or self._isBLOB():
      return
    data = dict()
    src = ""
    if self.__Method == "POST" and self._isMultipartForm() == False:
      src = self.__Body.decode()
    elif self.__Method == "GET":
      src = self.__Query
    else:
      return data
    # & で分割する。
    if src == "":
      return
    parts = src.split("&")
    for p in parts:
      q = p.split("=")
      key = q[0]
      val = q[1]
      if key in data:
        data[key] += f",{val}"
      else:
        data[key] = val
    self.__Form = data
    return

  # Body が JSON の場合、辞書に変換して self.__Form に格納する。
  def _parseJSON(self):
    s = self.__Body.decode()
    self.__Form = json.loads(s)
    return

  # マルチパートのブロックにファイルが含まれているか？
  def _isChunkBlock(self, block) -> bool:
    lines = block.split(b"\r\n", 3)
    if lines[0] == b"":
      lines.pop(0)
    b = lines[0].startswith(b"Content-Disposition: ") and lines[0].find(b"filename=") > 0
    return b
    
  # マルチパートのブロックに単純な文字列 (データ) が含まれているか？
  def _isValueBlock(self, block) -> bool:
    lines = block.split(b"\r\n", 2)
    if lines[0] == b"":
      lines.pop(0)
    return lines[0].startswith(b"Content-Disposition: ") and lines[0].find(b"filename=") < 0
    
  # マルチパートのブロックの name を得る。
  def _getBlockName(self, block):
    lines = block.split(b"\r\n", 2)
    if lines[0] == b"":
      lines.pop(0)
    ss = lines[0].split(b'name="')
    s = ss[1]
    p = s.find(b'"')
    name = s[0:p]
    return name

  # マルチパートのブロックの filename を得る。
  def _getBlockFileName(self, block):
    lines = block.split(b"\r\n", 2)
    if lines[0] == b"":
      lines.pop(0)
    ss = lines[0].split(b'; filename="')
    s = ss[1]
    p = s.find(b'"')
    filename = s[0:p]
    return filename

  # マルチパートのブロックの chunk を得る。
  def _getBlockChunk(self, block):
    lines = block.split(b"\r\n", 3)
    if lines[0] == b"":
      lines.pop(0)
    chunk = lines[2]
    if chunk.startswith(b"\r\n"):
      chunk = chunk[2:]
    if chunk.endswith(b"\r\n"):
      chunk = chunk[0:-2]
    return chunk

  # マルチパートのブロックの value を得る。
  def _getBlockValue(self, block):
    lines = block.split(b"\r\n", 3)
    if lines[0] == b"":
      lines.pop(0)
    value = lines[2]
    if value.endswith(b"\r\n"):
      value = value[0:-2]
    return value

  # マルチパートフォームデータ (multipart/form-data) を辞書 (self.Form) とアップロードファイル (self.Files) に変換する。
  def _parseBody(self):
    if self.__Method != "POST":
      return
    if self._isMultipartForm() == False or self._isJSON() or self._isBLOB():
      return
    self.__Form.clear()
    blocks = self._getDispositions()
    for block in blocks:
      if self._isChunkBlock(block):
        name = self._getBlockName(block)
        filename = self._getBlockFileName(block)
        chunk = self._getBlockChunk(block)
        self.__Files.append((name.decode(), filename.decode(), chunk))
      elif self._isValueBlock(block):
        name = self._getBlockName(block)
        value = self._getBlockValue(block)
        self.__Form[name.decode()] = value.decode()
      else:
        pass
    return

  # マルチパートフォームデータの境界を得る。
  def _getBoundary(self) -> bytes:
    boundary = b""
    content_type = self.__Headers["Content-Type"]
    if "boundary=" in content_type:
      p = content_type.split("boundary=")
      boundary = b"--" + p[1].encode(encoding="utf-8", errors="replace")
    return boundary

  # マルチパートフォームを境界で分割したブロックの配列を得る。
  def _getDispositions(self) -> list:
    boundary = self._getBoundary()
    blocks = self.__Body.split(boundary)
    if blocks[len(blocks) - 1] == b"--\r\n":
      blocks.pop()
    if blocks[0] == b"":
      blocks.pop(0)
    return blocks

  # クエリーデータ (GET) またはフォームデータ (POST) を得る。(キーが存在しない場合は空文字を返す)
  def getParam(self, name:str, unEsc=True) -> str:
    if self.__Method == "GET":
      if name in self.__Form.keys():
        if unEsc and type(self.__Form[name]) is str:
          val = self.__Form[name].replace("%3D", "=").replace("%3C", "<").replace("%3E", ">").replace("%20", " ").replace('%25', '%')
          return urlp.unquote_plus(val)
        else:
          return self.__Form[name]
      else:
        return ""
    elif self.__Method == "POST" and type(self.__Form) == dict:  # x-www-urlencoded
      if name in self.__Form.keys():
        if unEsc and type(self.__Form[name]) is str:
          val = self.__Form[name].replace("%3D", "=").replace("%3C", "<").replace("%3E", ">").replace("%20", " ").replace('%25', '%')
          return urlp.unquote_plus(val)
        else:
          return self.__Form[name]
      else:
        return ""
    else:  # multipart/form-data
      for block in self.__Form.keys():
        if name in block:
          return block[name]
        else:
          continue
      return ""

  # チェックボックスやラジオボタンが on かどうかを返す。
  def getCheck(self, name) -> bool:
    if name in self.__Form.keys():
      val = self.__Form[name]
      if type(val) is bool:
        return val
      elif val == 'false':
        return False
      elif val == 'true':
        return True
      else:
        return (val != "")
    else:
      return False

  # リクエストクッキーを得る。(キーが存在しない場合は空文字を返す)
  def getCookie(self, name: str) -> str:
    if name in self.__Cookies:
      return self.__Cookies[name]
    else:
      return ""

  # パスパラメータを得る。(パスパラメータが存在しない場合は空文字を返す)
  def getPathParam(self) -> str:
    p = self.__Path[1:].find("/")
    if p < 0:
      return ""
    return self.__Path[p + 2:]

  # アップロードファイルの内容を得る。
  def getChunk(self, name: str, filename="") -> bytes:
    file = tuple()
    if filename == "":
      file = self.__Files[0]
    else:
      for f in self.__Files:
        if f[0] == name and f[1] == filename:
          file = f
    if len(file) == 0:
      return b""
    return file[2]

  # アップロードされたファイル名 (ファイル名の配列) を得る。
  def getFileNames(self, name) -> list:
    flist = self.getFileList()
    result = list()
    for f in flist:
      if f[0] == name:
        result.append(f[1])
    return result

  # アップロードファイルのタプル (name, filename) の一覧を得る。
  def getFileList(self):
    flist = list()
    for f in self.__Files:
      flist.append((f[0], f[1]))
    return flist

  # HTTP メソッド
  @property
  def method(self) -> str:
    return self.__Method
    
  # リクエストヘッダの一覧
  @property
  def headers(self) -> dict:
    return self.__Headers
    
  # リクエストクッキー一覧
  @property
  def cookies(self) -> dict:
    return self.__Cookies

  # リクエストデータの mime タイプ
  def content_type(self):
    if "content_type" in self.__Headers.keys():
      s = self.__Headers["content_type"]
      if s.find("; ") > 0:
         parts = s.split("; ")
         return parts[0] 
      else:
        return s
    else:
      return ""

  # フォームデーター一覧
  @property
  def form(self) -> dict:
    return self.__Form

  # クエリー文字列
  @property
  def query(self) -> bytes:
    return self.__Query
    
  # POST された生データ
  @property
  def body(self) -> bytes:
    return self.__Body
    
  # アップロードされたファイル一覧
  @property
  def files(self) -> list:
    return self.__Files

  # リクエストパス
  @property
  def path(self) -> str:
    return self.__Path
    
  # HTTP バージョン
  @property
  def httpVersion(self):
    return self.__HttpVersion
