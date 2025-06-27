# handlers.py
import os, random, subprocess
from response import Response
import pyhtml, pycgigw, pyrmcr, pylistdir, deletegomi, pypixivrename, smalls, pydump, folder_summary, pyxcopy
import MariaDB as maria
import SQLite3
import pathlib
from datetime import datetime
import pandas as pd

SQLITE3 = "./SQLite3.db"
PWSH_FILEPATH = "pyapp_pwsh_filepath"
RENAME_FILEPATH = "pyapp_rename_filepath"
DUMP_FILEPATH = "pyapp_dump_filepath"
SHOWTEXT_FILEPATH = "pyapp_showtext_filepath"
EDIT_FILEPATH = "pyapp_edit_filepath"
XCOPY_SRC = "pyapp_xcopy_src"
XCOPY_DEST = "pyapp_xcopy_dest"

# ----------------- GET handlers --------------------

# GET /pyhtml
def get_pyhtml(req, res):
  res.sendHtml("./templates/pyhtml.html", embed={"message":"", "savefile":""})
  return

# GET /pycgigw
INTERPRETERS = ["/usr/bin/env python3", "C:/Python3/python.exe", "/usr/bin/env perl", "C:/Perl/perl.exe"]
def get_pycgigw(req, res):
  res.sendHtml("./templates/pycgigw.html", embed={"message":"", "folder":"", "savefile":"", "Gw1":INTERPRETERS[0], "Gw2":INTERPRETERS[1], "Gw3":INTERPRETERS[2], "Gw4":INTERPRETERS[3]})
  return

# GET /pyrmcr
def get_pyrmcr(req, res):
  res.sendHtml("./templates/pyrmcr.html", embed={"message":"", "path":""})
  return

# GET /pylistdir
def get_pylistdir(req, res):
  res.sendHtml("./templates/pylistdir.html", embed={"message":"", "folder":"", "savefile":"", "files":""})
  return

# GET /pypath
def get_pypath(req, res):
  envpath = os.getenv("PATH")
  sep = ":"
  if os.name == "nt":
    sep = ";"
  items = envpath.split(sep)
  items.sort()
  paths = ""
  for p in items:
    if p != "":
      paths += f"<li>{p}</li>"
  res.sendHtml("./templates/pypath.html", embed={"paths":paths})
  return

# GET /pygetenv
def get_pygetenv(req, res):
  env = ""
  for key, val in os.environ.items():
    env += f"<li><b>{key}:</b> {val}</li>"
  res.sendHtml("./templates/pygetenv.html", embed={"env":env})
  return

# GET /edit
def get_edit(req, res):
  if os.name == "nt":
    res.sendStatus(500, "Only for Linux")
    return
  name = "." + req.getParam("name")
  if name == ".":
    res.sendStatus(500, Response.INTERNAL_SERVER_ERROR)
    return
  content = ""
  path = os.environ['HOME'] + "/" + name
  with open(path, "r") as f:
    content = f.read()
  res.sendHtml("./templates/edit.html", embed={"name":name, "content":content, "message":""})
  return

# GET /pyshuffle
def get_pyshuffle(req, res):
  res.sendHtml("./templates/pyshuffle.html", embed={"path":"", "message":""})
  return

# GET /pycginew
def get_pycginew(req, res):
  res.sendHtml("./templates/pycginew.html", embed={"path":"", "message":""})
  return

# GET /pyipaddr
def get_pyipaddr(req, res):
  cmd = ['ip', '-4', 'a']
  if os.name == "nt":
    res.sendStatus(400, Response.BAD_REQUEST + " (Linux only)")
    return
  cp = subprocess.run(cmd, encoding='utf-8', stdout=subprocess.PIPE)
  content = cp.stdout
  res.sendHtml("./templates/pyipaddr.html", embed={"content":content})
  return

# GET /pypictures
def get_pypictures(req, res):
  res.sendHtml("./templates/pypictures.html", embed={"message":"", "dirpath":"", "album":"0", "title":"", "creator":"", "media":"", "mark":"", "info":""})
  return

# GET /pyvideos
def get_pyvideos(req, res):
  res.sendHtml("./templates/pyvideos.html", embed={"message":"", "dirpath":"", "album":"0", "title":"", "series":"", "media":"", "mark":"", "info":""})
  return

# GET /pymusic
def get_pymusic(req, res):
  res.sendHtml("./templates/pymusic.html", embed={"message":"", "dirpath":"", "album":"0", "title":"", "creator":"", "media":"", "mark":"", "info":""})
  return

# GET /pycheck
def get_pycheck(req, res):
  res.sendHtml("./templates/pycheck.html", embed={"message":"", "result":"", "criteria":"", "delete":"true"})
  return

# GET /pyfolders
def get_pyfolders(req, res):
  rows = SQLite3.query(SQLITE3, "SELECT id, title, path FROM folders")
  folderlist = ""
  for (id, title, path) in rows:
    dirname = path.replace("\\", "/")
    folderlist += f"<tr><td>{id}</td><td>{title}</td><td><a href=\"javascript:showContent('{dirname}')\">{path}</a></td></tr>\n"
  res.sendHtml("./templates/pyfolders.html", embed={"message":"", "folderlist":folderlist})
  return

# GET /deletegomi
def get_deletegomi(req, res):
  res.sendHtml("./templates/deletegomi.html", embed={"message":"", "folder":""})
  return

# GET /pysmalls
def get_pysmalls(req, res):
  folder = "/home/makandat/temp"
  cookie1 = req.getCookie("pysmalls_folder")
  if cookie1 != "":
    folder = cookie1
  savepath = folder + "/small"
  cookie1 = req.getCookie("pysmalls_savepath")
  if cookie1 != "":
    savepath = cookie1
  cookie1 = req.getCookie("pysmalls_size")
  size = "1600"
  if cookie1 != "":
    size = int(cookie1)
  if os.name == "nt":
    folder = "C:/temp"
    savepath = folder + "/small"
  res.sendHtml("./templates/pysmalls.html", embed={"message":"", "folder":folder, "savepath":savepath, "size":str(size)})
  return

# GET /pypixivrename
def get_pypixivrename(req, res):
  folder = "/home/makandat/temp"
  if os.name == "nt":
    folder = "C:/temp"
  cookie1 = req.getCookie(RENAME_FILEPATH)
  if cookie1 != "":
    folder = cookie1
  res.sendHtml("./templates/pypixivrename.html", embed={"message":"", "folder":folder})
  return

# GET /pygetfiles
def get_pygetfiles(req, res):
  folder = req.getParam("folder")
  fileonly = req.getCheck("fileonly")
  pathobj = pathlib.Path(folder)
  s = ""
  for p in pathobj.iterdir():
    if fileonly:
      if p.is_file():
        pname = p.name
        pstat = p.stat()
        pmode = "{:05o}".format(pstat.st_mode)
        psize = pstat.st_size
        pdate = pstat.st_mtime
        dt = datetime.fromtimestamp(pdate)
        pmtime = dt.strftime("%Y/%m/%d %H:%M:%S")
        s += f"<li><b>{pname}':</b>{pmode}:{psize}:{pmtime}</li>\n"
    else:
      pname = p.name
      if p.is_dir():
        pname = p.name + "/"
      pstat = p.stat()
      pmode = "{:05o}".format(pstat.st_mode)
      psize = pstat.st_size
      pdate = pstat.st_mtime
      dt = datetime.fromtimestamp(pdate)
      pmtime = dt.strftime("%Y/%m/%d %H:%M:%S")
      s += f"<li><b>'{pname}':</b>{pmode}:{psize}:{pmtime}</li>\n"
  res.sendText(s)
  return

# GET /powershell
def get_powershell(req, res):
  filepath = req.getCookie(PWSH_FILEPATH)
  if filepath.startswith('"') and filepath.endswith('"'):
    filepath = filepath[1:-1]
  res.sendHtml("./templates/powershell.html", embed={"message":"", "filepath":filepath, "content":"", "result":""})
  return

# GET /pydump
def get_pydump(req, res):
  path = ""
  message = ""
  content = ""
  if req.query != "":
    path = req.getParam("path")
    if path.startswith('"') and path.endswith('"'):
      path = path[1:-1]
    if os.path.isfile(path) == False:
      res.sendStatus(500, Response.INTERNAL_SERVER_ERROR)
      return
    content = pydump.dump(path)
  res.sendHtml("./templates/pydump.html", embed={"path":path, "message":message, "content":content})
  return

# GET /pyshowtext
def get_pyshowtext(req, res):
  path = req.getCookie(SHOWTEXT_FILEPATH)
  message = ""
  content = ""
  if req.query != "":
    path = req.getParam("path")
    if path.startswith('"') and path.endswith('"'):
      path = path[1:-1]
    with open(path, "r", encoding="utf-8") as f:
      content = f.read()
    content = content.replace("\r", "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    res.setCookie(SHOWTEXT_FILEPATH, path)
  res.sendHtml("./templates/pyshowtext.html", embed={"path":path, "message":message, "content":content})
  return

# GET /pyeditor
def get_pyeditor(req, res):
  path = req.getCookie(EDIT_FILEPATH)
  res.sendHtml("./templates/pyeditor.html", embed={"path":path, "message":"", "content":""})
  return

# GET /pyapacheerror
def get_pyapacheerror(req, res):
  error_log = "/var/log/apache2/error.log" # TO BE CHANGED
  if os.name == "nt":
    error_log = "C:/Apps/Apache24/logs/error.log" # TO BE CHANGED
  content = ""
  try:
    f = open(error_log, "r")
    content = f.read()
    f.close()
    lines = content.split("\n")
    n = len(lines)
    if n >= 16:
      n = n - 16
    else:
      n = 0
    lines2 = lines[n:]
    content = "\n".join(lines2)
  except:
    content = "Failed to read error.log. (Check mode.)"
  res.sendHtml("./templates/pyapacheerror.html", embed={"content":content})
  return

# GET /pyfoldersummary
def get_pyfoldersummary(req, res):
  res.sendHtml("./templates/pyfoldersummary.html", embed={"folder":"", "message":"", "result":""})
  return

# GET /pyxcopy
def get_pyxcopy(req, res):
  srcfolder = req.getCookie(XCOPY_SRC)
  destfolder = req.getCookie(XCOPY_DEST)
  res.sendHtml("./templates/pyxcopy.html", embed={"message":"", "result":"", "srcfolder":srcfolder, "destfolder":destfolder})
  return

# GET /pysmbc
def get_pysmbc(req, res):
  res.sendHtml("./templates/pysmbc.html", embed={"message":"", "csvfile":"", "table":"", "summary":""})
  return

# GET /pyvisa
def get_pyvisa(req, res):
  res.sendHtml("./templates/pyvisa.html", embed={"message":"", "csvfile":"", "table":"", "summary":""})
  return

# GET /pysbinet
def get_pysbinet(req, res):
  res.sendHtml("./templates/pysbinet.html", embed={"message":"", "csvfile":"", "table":"", "summary":""})
  return

# GET /pymusashino
def get_pymusashino(req, res):
  res.sendHtml("./templates/pymusashino.html", embed={"message":"", "csvfile":"", "table":"", "summary":""})
  return

# GET /pytkapp
def get_pytkapp(req, res):
  if os.name == 'nt':
    basedir = "C:/workspace/Python3/Tkinter"
  else:
    basedir = "/home/user/workspace/Python3/Tkinter"
  apps = [
    "TkSimpleMaker/pysimple_maker.py",
    "TkHTMLMaker/TkHTML.py",
    "TkCGIMaker/tkcginew.py",
    "TkAppMaker/tkappmaker.py",
    "TkCGI_Interp/cgi_interp.py",
    "TkCSharpMaker/csharp_maker.py",
    "TkCursesMaker/curses_maker.py",
    "TkFlaskMaker/tk_flask_maker.py",
    "TkHttpSeverMaker/httpserver_maker.py",
    "TkRubyMaker/ruby_maker.py",
    "TkSinatraMaker/tk_sinatra_maker.py",
    "TkInsVideos/tk_insvideos.py"
  ]
  TEMPL = "./templates/pytkapp.html"
  #with open(TEMPL, "rt", encoding="utf-8") as f:
  #  html = f.read()
  #res.render(html, embed={"basedir":basedir, "apps":apps})
  res.render(TEMPL, embed={"basedir":basedir, "apps":apps})
  return

# GET /pytkapp_run
def get_pytkapp_run(req, res):
  if os.name == 'nt':
    basedir = "C:/workspace/Python3/Tkinter"
    cmd = ["python.exe"]
  else:
    basedir = "/home/user/workspace/Python3/Tkinter"
    cmd = ["python3"]
  apps = [
    "TkSimpleMaker/pysimple_maker.py",
    "TkHTMLMaker/TkHTML.py",
    "TkCGIMaker/tkcginew.py",
    "TkAppMaker/tkappmaker.py",
    "TkCGI_Interp/cgi_interp.py",
    "TkCSharpMaker/csharp_maker.py",
    "TkCursesMaker/curses_maker.py",
    "TkFlaskMaker/tk_flask_maker.py",
    "TkHttpSeverMaker/httpserver_maker.py",
    "TkRubyMaker/ruby_maker.py",
    "TkSinatraMaker/tk_sinatra_maker.py",
    "TkInsVideos/tk_insvideos.py"
  ]
  app = basedir + "/" + req.getParam("app")
  print(app)
  cmd.append(app)
  print(cmd)
  subprocess.Popen(cmd)
  TEMPL = "./templates/pytkapp.html"
  res.render(TEMPL, embed={"basedir":app, "apps":apps})
  return

# ---------------------------- Handler Mapping ----------------------------------

# GET メソッドのパスに対するハンドラマッピング
GET_MAP = {
  "/pyhtml": get_pyhtml,
  "/pycgigw": get_pycgigw,
  "/pyrmcr": get_pyrmcr,
  "/pylistdir": get_pylistdir,
  "/pypath": get_pypath,
  "/pygetenv": get_pygetenv,
  "/edit": get_edit,
  "/pyshuffle": get_pyshuffle,
  "/pycginew": get_pycginew,
  "/pypictures": get_pypictures,
  "/pyvideos": get_pyvideos,
  "/pymusic": get_pymusic,
  "/pyipaddr": get_pyipaddr,
  "/pycheck": get_pycheck,
  "/pyfolders":get_pyfolders,
  "/deletegomi":get_deletegomi,
  "/pysmalls":get_pysmalls,
  "/pypixivrename":get_pypixivrename,
  "/pygetfiles":get_pygetfiles,
  "/powershell":get_powershell,
  "/pydump":get_pydump,
  "/pyshowtext":get_pyshowtext,
  "/pyeditor":get_pyeditor,
  "/pyapacheerror":get_pyapacheerror,
  "/pyfoldersummary": get_pyfoldersummary,
  "/pyxcopy":get_pyxcopy,
  "/pysmbc":get_pysmbc,
  "/pyvisa":get_pyvisa,
  "/pysbinet":get_pysbinet,
  "/pymusashino":get_pymusashino,
  "/pytkapp":get_pytkapp,
  "/pytkapp_run":get_pytkapp_run
}









#
# ----------------- POST handlers --------------------
#

# POST /pyhtml
def post_pyhtml(req, res):
  savefile = req.getParam("savefile")
  if savefile == "":
    res.sendStatus(400, Response.BAD_REQUEST)
    return
  if savefile.startswith('~'):
    savefile = os.path.expanduser(savefile)
  contenttype = req.getParam("contenttype")
  n = int(contenttype)
  content = ""
  if n == 1:
    content = pyhtml.HTML_Simple
  elif n == 2:
    content = pyhtml.HTML_Bootstrap5
  elif n == 3:
    content = pyhtml.HTML_Bootstrap5_Form
  elif n == 4:
    content = pyhtml.HTML_Vue3
  else:
    res.sendStatus(400, Response.BAD_REQUEST)
    return
  try:
    with open(savefile, "w", encoding="utf-8") as f:
      f.write(content)
  except:
    res.sendStatus(500, Response.INTERNAL_SERVER_ERROR)
  res.sendHtml("./templates/pyhtml.html", embed={"message":f"HTML ファイル '{savefile}' を作成しました。", "savefile":savefile})
  return

# POST /pycgigw
def post_pycgigw(req, res):
  folder = req.getParam("folder")
  if folder.startswith('~'):
    folder = os.path.expanduser(folder)
  interpreter = req.getParam("interpreter")
  if not os.path.isdir(folder):
    res.sendStatus(500, Response.INTERNAL_SERVER_ERROR)
    return
  if interpreter == "null":
    res.sendStatus(500, Response.INTERNAL_SERVER_ERROR)
    return
  pycgigw.updateGw(folder, interpreter)
  message = f"'{folder}' の CGI の先頭行を '{interpreter}' に更新しました。"
  res.sendHtml("./templates/pycgigw.html", embed={"message":message, "folder":folder, "Gw1":INTERPRETERS[0], "Gw2":INTERPRETERS[1], "Gw3":INTERPRETERS[2], "Gw4":INTERPRETERS[3]})
  return

# POST /pyrmcr
def post_pyrmcr(req, res):
  path = os.path.expanduser(req.getParam("path"))
  if os.path.isfile(path):
    removeCR(path)
  elif os.path.isdir(path):
    files = os.listdir(path)
    for f in files:
      p = path + "/" + f
      pyrmcr.removeCR(p)
  else:
    res.sendStatus(500, Response.INTERNAL_SERVER_ERROR)
    return
  res.sendHtml("./templates/pyrmcr.html", embed={"message":f"{path} の行末を変換しました。", "path":path})
  return

# POST /pylistdir
def post_pylistdir(req, res):
  folder = req.getParam("folder")
  if os.name == "nt":
    folder = folder.replace("\\", "/")
  if folder.startswith('~'):
    folder = os.path.expanduser(folder)
  if not os.path.isdir(folder):
    res.sendStatus(500, Response.INTERNAL_SERVER_ERROR)
    return
  savefile = req.getParam("savefile")
  if os.name == "nt":
    savefile = savefile.replace("\\", "/")
  if savefile.startswith('~'):
    savefile = os.path.expanduser(savefile)
  if savefile.startswith('"') and savefile.endswith('"'):
    savefile = savefile[1:-1]
  filetype = req.getParam("filetype")
  nameonly = req.getCheck("nameonly")
  shuffle = req.getCheck("shuffle")
  files = pylistdir.getFiles(folder, filetype, nameonly)
  if shuffle:
    random.shuffle(files)
  sfiles = ""
  for f in files:
    sfiles += f + "\n"
  message = f"'{folder}' のファイル一覧を取得しました。"
  if savefile != "":
    with open(savefile, "w", encoding="utf-8") as f:
      f.write(sfiles)
      message = f"'{folder}' のファイル一覧を取得し、'{savefile}' にファイル保存しました。"
  res.sendHtml("./templates/pylistdir.html", embed={"message":message, "folder":folder, "savefile":savefile, "files": sfiles})
  return

# POST /edit
def post_edit(req, res):
  name = req.getParam("name")
  content = req.getParam("content")
  path = os.environ['HOME'] + "/" + name
  with open(path, "w") as f:
    f.write(content)
  message = f"{path} にファイル保存しました。"
  res.sendHtml("./templates/edit.html", embed={"content":content, "name":name, "message":message})
  return

# POST /pyshuffle
def post_pyshuffle(req, res):
  path = req.getParam("path")
  if path == "":
    res.sendStatus(500, Response.INTERNAL_SERVER_ERROR)
    return
  if path.startswith('"') and path.endswith('"'):
    path =path[1:-1]
  lines = list()
  with open(path, encoding="utf-8") as f:
    lines = f.readlines()
  random.shuffle(lines)
  lines2 = list()
  for l in lines:
    lines2.append(l)
  with open(path, "w", encoding="utf-8") as f:
    f.writelines(lines2)
  res.sendHtml("./templates/pyshuffle.html", embed={"path":path, "message":"シャッフルが終わりました。"})
  return

# POST /pycginew
def post_pycginew(req, res):
  CGI = '''#!/usr/bin/env python3
import CGI365Lib as CGI

# GET method
def on_GET(req, res):
  res.sendHtml("./templates/test.html", embed={"a":""})
  return

# POST method
def on_POST(req, res):
  a = req.getParam("a")
  # ....
  res.sendHtml("./templates/test.html", embed={"a":a})
  return

# Start
if __name__ == '__main__':
  req, res = (CGI.Request(), CGI.Response())
  if req.method == "GET":
    on_GET(req, res)
  elif req.method == "POST":
    on_POST(req, res)
  else:
    CGI.Response.status(405, CGI.METHOD_NOT_ALLOWED)
'''
  path = req.getParam("path")
  with open(path, "w") as f:
    f.write(CGI)
  if os.name != "nt":
    os.chmod(path, 0o755)
  res.sendHtml("./templates/pycginew.html", {"path":path, "message":"OK"})
  return

# POST /pypictures
def post_pypictures(req, res):
  # id, album, title, creator, path, media, mark, info, fav, count, bindata, date
  SQL = "INSERT INTO Pictures VALUES(NULL, {}, '{}', '{}', '{}', '{}', '{}', '{}', 0, 0, 0, CURRENT_DATE)"
  dirpath = req.getParam("dirpath")
  if os.name == "nt":
    dirpath = dirpath.replace("\\", "/")
  subdir = req.getCheck("subdir")
  album = req.getParam("album")
  title = req.getParam("title")
  if title == "":
    title = dirpath.split("/").pop()
  creator = req.getParam("creator")
  media = req.getParam("media")
  mark = req.getParam("mark")
  info = req.getParam("info")
  items = list()
  db = maria.MariaDB()
  if subdir:
    ls = os.listdir(dirpath)
    for p in ls:
      p = dirpath + "/" + p
      if os.path.isdir(p):
        items.append(p)
  else:
    items.append(dirpath)
  for path in items:
    sql = f"SELECT count(*) FROM Pictures WHERE path = '{path}'"
    n = db.getValue(sql)
    if n > 0:
      continue
    sql = SQL.format(album, title, creator, path, media, mark, info)
    try:
      db.execute(sql)
    except Exception as e:
      res.sendStatus(500, Response.INTERNAL_SERVER_ERROR + " " + str(e))
      return
  db.close()
  res.sendHtml("./templates/pypictures.html", {"dirpath":dirpath, "message":"OK: " + title, "album":album, "title":title, "creator":creator, "media":media, "mark":mark, "info":info})
  return

# POST /pyvideos
def post_pyvideos(req, res):
  # id, album, title, path, media, series, mark, info, fav, count, bindata, date
  SQL = "INSERT INTO Videos VALUES(NULL, {}, '{}', '{}', '{}', '{}', '{}', '{}', 0, 0, 0, CURRENT_DATE)"
  dirname = req.getParam("dirpath").replace("\\", "/")
  album = req.getParam("album")
  title = req.getParam("title")
  addnumber = req.getCheck("addnumber")
  series = req.getParam("series")
  media = req.getParam("media")
  mark = req.getParam("mark")
  info = req.getParam("info")
  items = list()
  ls = os.listdir(dirname)
  for p in ls:
    filepath = dirname + "/" + p
    if os.path.isfile(filepath):
      items.append(filepath)
  number = 1
  title1 = title
  db = maria.MariaDB()
  for path in items:
    n = db.getValue(f"SELECT count(*) FROM Videos WHERE path='{path}'")
    if n > 0:
      continue
    if title == "":
      title = os.path.splitext(os.path.basename(path))[0]
    if addnumber:
      title = title1 + "-{:02d}".format(number)
      number += 1
    sql = SQL.format(album, title, path, media, series, mark, info)
    db.execute(sql)
  db.close()
  res.sendHtml("./templates/pyvideos.html", {"dirpath":dirname, "message":"OK: " + title, "album":album, "title":title, "series":series, "path":path, "media":media, "mark":mark, "info":info})
  return

# POST /pymusic
def post_pymusic(req, res):
  # id, album, title, path, artist, media, mark, info, fav, count, bindata, date
  SQL = "INSERT INTO Music VALUES(NULL, {}, '{}', '{}', '{}', '{}', '{}', '{}', 0, 0, 0, CURRENT_DATE)"
  dirpath = req.getParam("dirpath").replace("\\", "/")
  album = req.getParam("album")
  title = req.getParam("title")
  artist = req.getParam("artist")
  media = req.getParam("media")
  mark = req.getParam("mark")
  info = req.getParam("info")
  ls = os.listdir(dirpath)
  items = list()
  for p in ls:
    filepath = dirpath + "/" + p
    if os.path.isfile(filepath):
      items.append(filepath)
  db = maria.MariaDB()
  for path in items:
    ext = os.path.splitext(os.path.basename(filepath))[1]
    if not (ext == ".mp3" or ext == "m4a" or ext == "wma"):
      continue
    n = db.getValue(f"SELECT count(*) FROM Music WHERE path='{filepath}'")
    if n > 0:
      continue
    if title == "":
      title = os.path.splitext(os.path.basename(filepath))[0]
    sql = SQL.format(album, title, filepath, artist, media, mark, info)
    db.execute(sql)
  db.close()
  res.sendHtml("./templates/pymusic.html", {"dirpath":dirpath, "message":"OK: " + title, "album":album, "title":title, "artist":artist, "media":media, "mark":mark, "info":info})
  return

# POST /pycheck
def post_pycheck(req, res):
  criteria = req.getParam("criteria")
  table = req.getParam("table")
  if table == "0":
    res.sendStatus(500, Response.INTERNAL_SERVER_ERROR)
    return
  delete = req.getCheck("delete")
  sql = f"SELECT id, path FROM {table}"
  if criteria != "":
    sql = f"SELECT id, path FROM {table} WHERE {criteria}"
  db = maria.MariaDB()
  rs = db.query(sql)
  result = ""
  count = 0
  for row in rs:
    if os.path.exists(row[1]):
      continue
    else:
      sql = f"DELETE FROM {table} WHERE id={row[0]};"
      result += sql + "\n"
      count += 1
      if delete:
        db.execute(sql)
  db.close()
  message = f"OK 件数={count}"
  sdel = "false"
  if delete:
    sdel = "true"
  res.sendHtml("./templates/pycheck.html", embed={"message":message, "criteria":criteria, "delete":sdel, "result":result})
  return

# POST /pyfolders
def post_pyfolders(req, res):
  id = req.getParam("id")
  if id == "":
    id = "0"
  title = req.getParam("title").replace("'", "''")
  path = req.getParam("dirname")
  if path.startswith('"') and path.endswith('"'):
    path = path[1:-1]
  if os.name == "nt":
    path = path.replace("\\", "/")
  if os.name != "nt" and path.startswith("~"):
    path = pathlib.Path(path).expanduser()
  message = "OK"
  try:
    n = SQLite3.getValue(SQLITE3, f"SELECT count(*) FROM folders WHERE id='{id}'")
    if n == 0:
      if title == "" or path == "":
        message = "Error: title or path is empty."
      else:
        SQLite3.execute(SQLITE3, f"INSERT INTO folders(title, path) VALUES('{title}', '{path}')")
    else:
      sql = ""
      if title == "" and path == "":
        message = "No operation"
      elif title != "" and path == "":
        sql = f"UPDATE folders SET title='{title}' WHERE id='{id}'"
        message = "OK title changed."
      elif title == "" and path != "":
        sql = f"UPDATE folders SET path='{path}' WHERE id='{id}'"
        message = "OK path changed."
      else:
        sql = f"UPDATE folders SET title='{title}', path='{path}' WHERE id='{id}'"
        message = "OK title and path changed."
      if sql != "":
        SQLite3.execute(SQLITE3, sql)
    rows = SQLite3.query(SQLITE3, "SELECT id, title, path FROM folders")
    folderlist = ""
    for row in rows:
      folderlist += f"<tr><td>{row[0]}</td><td>{row[1]}</td><td><a href=\"javascript:showContent('{row[2]}')\">{row[2]}</a></td></tr>\n"
  except Exception as e:
    message = "Fatal Error: " + str(e)
  res.sendHtml("./templates/pyfolders.html", embed={"message":message, "folderlist":folderlist})
  return

# POST /deletegomi
def post_deletegomi(req, res):
  folder = req.getParam("folder")
  if folder == "":
    res.sendStatus(500, Response.INTERNAL_SERVER_ERROR)
    return
  # 実行する。
  files = deletegomi.listFilesRecursively(folder, asstr=True)
  i = 0
  for f in files:
    f = f.replace('\\', '/')
    fn = os.path.basename(f).lower()
    if fn == "thumbs.db" or fn == "desktop.ini" :
      os.remove(f)
      i += 1
    else :
      pass
  res.sendHtml("./templates/deletegomi.html", embed={"message":f"{i} 個のファイルを削除しました。", "folder":""})
  return

# POST /pysmalls
def post_pysmalls(req, res):
  folder = req.getParam("folder")
  if folder == "":
    res.sendStatus(500, Response.INTERNAL_SERVER_ERROR)
    return
  size = req.getParam("size")
  if size == "":
    size = 1600
  else:
    size = int(size)
  savepath = req.getParam("savepath")
  n = 0
  try:
    n = smalls.small(folder, savepath, size)
  except:
    res.sendStatus(500, Response.INTERNAL_SERVER_ERROR)
    return
  res.setCookie("pysmalls_folder", folder)
  res.setCookie("pysmalls_savepath", savepath)
  res.setCookie("pysmalls_size", str(size))
  res.sendHtml("./templates/pysmalls.html", embed={"message":f"OK count={n}", "folder":folder, "size":str(size), "savepath":savepath})
  return

# POST /pypixivrename
def post_pypixivrename(req, res):
  folder = req.getParam("folder")
  if folder == "":
    res.sendStatus(500, Response.INTERNAL_SERVER_ERROR)
    return
  n = pypixivrename.rename_files(folder)
  res.setCookie(RENAME_FILEPATH, folder)
  res.sendHtml("./templates/pypixivrename.html", embed={"message":f"OK count={n}", "folder":folder})
  return

# POST /powershell/@
def post_powershell(req, res):
  filepath = req.getParam("filepath")
  content = req.getParam("content")
  message = ""
  result = ""
  cmd = req.getPathParam()
  if cmd == "load":
    if os.path.isfile(filepath) == False:
      res.sendStatus(500, Response.INTERNAL_SERVER_ERROR)
      return
    with open(filepath, "r", encoding="utf-8") as f:
      content = f.read()
    message = "OK loaded"
  elif cmd == "save":
    if filepath == "":
      res.sendStatus(500, Response.INTERNAL_SERVER_ERROR)
      return
    with open(filepath, "w", encoding="utf-8") as f:
      content = content.replace("\r", "")
      f.write(content)
    message = "OK saved."
  elif cmd == "execute":
    cmd = ["pwsh", "-file", filepath]
    try:
      cp = subprocess.run(cmd, encoding='utf-8', stdout=subprocess.PIPE)
      result = cp.stdout
      message = "OK executed."
      res.setCookie(PWSH_FILEPATH, filepath)
    except:
      res.sendStatus(500, Response.INTERNAL_SERVER_ERROR)
      return
  else:
    res.sendStatus(500, Response.INTERNAL_SERVER_ERROR)
    return
  res.sendHtml("./templates/powershell.html", embed={"message":message, "filepath":filepath, "content":content, "result":result})
  return

# POST /pyeditor
def post_pyeditor(req, res):
  path = req.getParam("path")
  content = req.getParam("content")
  message = "OK"
  if path.startswith('"') and path.endswith('"'):
    path = path[1:-1]
  cmd = req.getPathParam()
  if cmd == "load":
    with open(path, "r", encoding="utf-8") as f:
      content = f.read()
    message = "OK loaded"
  elif cmd == "save":
    try:
      with open(path, "w", encoding="utf-8") as f:
        content = content.replace("\r", "")
        f.write(content)
      message = "OK saved"
      res.setCookie(EDIT_FILEPATH, path)
    except:
      message = "Fatal error"
  else:
    res.sendStatus(500, Response.INTERNAL_SERVER_ERROR)
    return
  res.sendHtml("./templates/pyeditor.html", embed={"message":message, "path":path, "content":content})
  return

# POST /pyfoldersummary
def post_pyfoldersummary(req, res):
  folder = req.getParam("folder").replace("\\", "/")
  if not os.path.isdir(folder):
    res.sendStatus(500, Response.INTERNAL_SERVER_ERROR)
    return
  summary = folder_summary.getSummary(folder)
  result = ""
  for sm in summary:
    result += f"<tr><td>{sm[0]}</td><td>{sm[1]}</td><td>{sm[2]}</td><td>{sm[3]}</td><td>{sm[4]}</td></tr>"
  message = "OK " + folder
  res.sendHtml("./templates/pyfoldersummary.html", embed={"message":message, "result":result, "folder":folder})
  return

# POST /pyxcopy
def post_pyxcopy(req, res):
  srcfolder = req.getParam("srcfolder")
  srcfolder = srcfolder.replace("\\", "/")
  destfolder = req.getParam("destfolder")
  destfolder = destfolder.replace("\\", "/")
  sync = req.getCheck("sync")
  try:
    result = pyxcopy.xcopy(srcfolder, destfolder)
    if sync:
      sync_delete(destfolder, result)
    res.setCookie(XCOPY_SRC, srcfolder)
    res.setCookie(XCOPY_DEST, destfolder)
    sr = ""
    for r in result:
      sr += f"<li>{r}</li>"
    res.sendHtml("./templates/pyxcopy.html", embed={"message":"OK", "result":sr, "srcfolder":srcfolder, "destfolder":destfolder})
  except:
    res.sendStatus(500, Response.INTERNAL_SERVER_ERROR)
  return

# POST /pysmbc
def post_pysmbc(req, res):
  # CSV ファイルを読む。
  csvfile = req.getParam("csvfile")
  try:
    df = pd.read_csv(csvfile, header=0)
  except:
    res.sendHtml("./templates/pysmbc.html", embed={"message":"CSV ファイル読み込みに失敗。ファイルの文字コードが UTF-8かどうか確認してください。", "csvfile":csvfile, "table":"", "summary":""})
    return
  # HTML に変換
  table = df.to_html().replace('NaN', '')
  # 支払先ごとに集計
  result = df.groupby('お取り扱い内容').sum('お引出し')
  summary = result[result['お引出し'] > 0].to_string() + "<br>"
  # 預入元ごとに集計
  result = df.groupby('お取り扱い内容').sum('お預入れ')
  if not (result is None):
    positive_sums = result[result['お預入れ'] > 0]
    summary += positive_sums.iloc[:,[1]].to_string()
  # 残高
  summary += f"<br>残高<br>{df['残高'].min()}"
  res.sendHtml("./templates/pysmbc.html", embed={"message":"OK", "csvfile":csvfile, "table":table, "summary":summary})
  return

# POST /pyvisa
def post_pyvisa(req, res):
  # CSV ファイルを読む。
  csvfile = req.getParam("csvfile")
  with open(csvfile, "rt", encoding="utf-8") as f:
    arr = f.readlines()
  i = 1
  data = dict()
  n = len(arr)
  while i < n - 1:
    print(arr[i])
    row = arr[i].split(',')
    shop = row[1].replace('\u3000', ' ')
    try:
      pay = int(row[5])
    except:
      pay = 0
    if shop in data:
      data[shop] += pay
    else:
      data[shop] = pay
    i += 1
  table = f"<p>--------- {csvfile} -------------</p>\n<table><tr><th>ショップ</th><th>購入額</th></tr>\n"
  for key, value in data.items():
    table += f"<tr><td>{key}</td><td>{value}</td></tr>\n"
  table += "</table>\n"
  items = arr[n - 1].split(',')
  total = int(items[5])
  summary = "   {0:,}円\n".format(total)
  res.sendHtml("./templates/pyvisa.html", embed={"message":"OK", "csvfile":csvfile, "table":table, "summary":summary})
  return

# POST /pysbitnet
def post_pysbinet(req, res):
  # CSV ファイルを読む。
  csvfile =req.getParam('csvfile')
  try:
    df = pd.read_csv(csvfile, header=0)
  except:
    message ="CSV ファイルの読み込みに失敗。文字コードが UTF-8 でない可能性があります。"
    res.sendHtml("./templates/pyvsbitnet.html", embed={"message":message, "csvfile":csvfile, "table":"", "summary":""})
    return
  # HTML に変換してファイル保存
  table = df.to_html().replace('NaN', '')
  # 「フリカエ　ペイペイ ・・・」を「ペイペイ」にする。
  df["内容"] = df["内容"].replace(r'フリカエ.*', 'PayPay', regex=True)
  # 入金
  summary = "======= 入金 =======\n"
  df1 = df.dropna(subset=['入金金額(円)'])
  df1 = df1.drop('出金金額(円)', axis=1)
  summary += df1.to_string()
  # 出金
  summary += "\n\n======= 出金 =======\n"
  df2 = df.dropna(subset=['出金金額(円)'])
  df2 = df2.drop('入金金額(円)', axis=1)
  summary += df2.to_string() + "\n"
  res.sendHtml("./templates/pysbinet.html", embed={"message":"OK", "csvfile":csvfile, "table":table, "summary":summary})
  return

# POST /pymusashino
def post_pymusashino(req, res):
  # CSV ファイルを読む。
  csvfile = req.getParam('csvfile')
  try:
    df = pd.read_csv(csvfile, header=0, sep='\t')
  except:
    message = "CSV ファイルの読み込みに失敗。文字コードが UTF-8 でない可能性があります。"
    res.sendHtml("./templates/pymusashino.html", embed={"message":message, "csvfile":csvfile, "table":"", "summary":""})
    return
  # HTML に変換してファイル保存
  table = df.to_html()
  # 残高
  result = df['差引残高'].min()
  summary = f'\n** 残高の最小値 = {result}'
  res.sendHtml("./templates/pymusashino.html", embed={"message":"OK", "csvfile":csvfile, "table":table, "summary":summary})
  return






# ----------------- Handlers mapping --------------------

# POST メソッドのパスに対するハンドラマッピング
POST_MAP = {
  "/pyhtml": post_pyhtml,
  "/pycgigw": post_pycgigw,
  "/pyrmcr": post_pyrmcr,
  "/pylistdir": post_pylistdir,
  "/edit": post_edit,
  "/pyshuffle": post_pyshuffle,
  "/pycginew": post_pycginew,
  "/pypictures": post_pypictures,
  "/pyvideos": post_pyvideos,
  "/pymusic": post_pymusic,
  "/pycheck": post_pycheck,
  "/pyfolders":post_pyfolders,
  "/deletegomi":post_deletegomi,
  "/pysmalls":post_pysmalls,
  "/pypixivrename":post_pypixivrename,
  "/powershell/@":post_powershell,
  "/pyeditor/@":post_pyeditor,
  "/pyfoldersummary": post_pyfoldersummary,
  "/pyxcopy":post_pyxcopy,
  "/pysmbc":post_pysmbc,
  "/pyvisa":post_pyvisa,
  "/pysbinet":post_pysbinet,
  "/pymusashino":post_pymusashino
}
