# handlers.py
from response import Response
import boto3
import os
import json
import mimetypes
import server

# 設定ファイルを読む。 v1.2.0
def read_conf(conffile=server.CONFIG):
  if os.path.exists(conffile):
    with open(conffile, "rt", encoding="utf-8") as f:
      settings = json.load(f)
      return settings
  else:
    return server.settings

# ----------------- GET handlers --------------------

# GET /get_list_buckets
def get_list_buckets(req, res):
  TITLE = "AWS S3 Buckets"
  try:
    client = boto3.client('s3')
    buckets = client.list_buckets()['Buckets']
    message = f"OK: {len(buckets)} buckets found."
    res.render(server.get_template("get_list_buckets.html"), {"title":TITLE, "buckets":buckets, "message":message})
  except Exception as e:
    res.render(server.get_template("get_list_buckets.html"), {"title":TITLE, "buckets":[], "message":"エラー： " + str(e)})
  return

# GET /get_list_items
def get_list_items(req, res):
  title = "Keys of S3 Bucket '"
  try:
    bucket = req.getParam("path")
    title += bucket + "'"
    client = boto3.client('s3')
    files = client.list_objects_v2(Bucket=bucket)['Contents']
    message = f"OK: {len(files)} keys found."
    res.render(server.get_template("get_list_items.html"), {"bucket":bucket, "title":title, "files":files, "message":message})
  except Exception as e:
    res.render(server.get_template("get_list_items.html"), {"bucket":bucket, "title":title, "files":[], "message":"エラー： " + str(e)})
  return

# GET /get_show
def get_show(req, res):
  text = ""
  bucket = req.getParam("bucket")
  key = req.getParam("key")
  mime = mimetypes.guess_type(key)[0]
  img_show = "none"
  text_show = "none"
  if mime == "image/jpeg" or mime == "image/png" or mime == "image/gif":
    img_show = "block"
  else:
    text_show = "block"
  try:
    if text_show == "block":
      client = boto3.client('s3')
      obj = client.get_object(Bucket=bucket, Key=key)
      stream = obj['Body']
      content = stream.read()
      s = content.decode()
      text = Response.html_escape(s)
    res.render(server.get_template("get_show.html"), {"title":f"{bucket}:{key}", "bucket":bucket, "key":key, "text_show":text_show, "img_show":img_show, "content":text})
  except Exception as e:
    res.sendStatus(500, Response.INTERNAL_SERVER_ERROR)
  return

# GET /get_image
def get_image(req, res):
  bucket = req.getParam("bucket")
  key = req.getParam("key")
  mime_type = mimetypes.guess_type(key)[0]
  try:
    client = boto3.client('s3')
    obj = client.get_object(Bucket=bucket, Key=key)
    stream = obj['Body']
    blob = stream.read()
    res.sendBLOB(blob, mime_type)
  except Exception as e:
    res.sendStatus(500, Response.INTERNAL_SERVER_ERROR)
  return

# GET /get_download
def get_download(req, res):
  bucket = req.getParam("bucket")
  key = req.getParam("key")
  settings = read_conf()
  try:
    client = boto3.client('s3')
    files = client.list_objects_v2(Bucket=bucket)['Contents']
    message = f"OK: {len(files)} keys found."
    if key == "":
      res.render(server.get_template("get_download.html"), {"title":f"Download from {bucket}", "bucket":bucket, "key":key, "files":files, "message":message})
    else:
      filename = os.path.basename(key)
      download = settings["download"]
      download_file = download + "/" + filename
      with open(download_file, "wb") as f:
        client.download_fileobj(bucket, key, f)
        message = f"Downloaded to '{download_file}'"
      res.render(server.get_template("get_download.html"), {"title":f"Download {bucket}:{key}", "bucket":bucket, "key":key, "files":files, "message":message})
  except Exception as e:
    res.sendStatus(500, Response.INTERNAL_SERVER_ERROR)
  return

# GET /get_upload
def get_upload(req, res):
  res.render(server.get_template("get_upload.html"), {"title":"Upload file", "message":"", "bucket":"", "key":"", "path":""})
  return

# GET /get_copy
def get_copy(req, res):
  res.render(server.get_template("get_copy.html"), {"title":"Copy file", "message":"", "s_bucket":"", "s_key":"", "d_bucket":"", "d_key":""})
  return

# GET /get_delete
def get_delete(req, res):
  res.render(server.get_template("get_delete.html"), {"title":"Delete file", "message":"", "bucket":"", "key":""})
  return

# GET /get_prefix_new
def get_prefix_new(req, res):
  res.render(server.get_template("get_prefix_new.html"), {"title":"Prefix New", "message":"", "bucket":"", "key":""})
  return


# ----------------- POST handlers --------------------

# POST /post_upload
def post_upload(req, res):
  bucket = req.getParam("bucket")
  key = req.getParam("key")
  path = req.getParam("path")
  if path.startswith('"') and path.endswith('"'):
    path = path[1:-1]
  try:
    client = boto3.client('s3')
    client.upload_file(path, bucket, key)
    res.render(server.get_template("get_upload.html"), {"title":"Upload file", "message":f"OK: Uploaded the file '{path}'", "bucket":bucket, "key":key, "path":path})
  except Exception as e:
    res.sendStatus(500, Response.INTERNAL_SERVER_ERROR + ": " + str(e))
  return

# POST /post_copy
def post_copy(req, res):
  s_bucket = req.getParam("s_bucket")
  d_bucket = req.getParam("d_bucket")
  s_key = req.getParam("s_key")
  d_key = req.getParam("d_key")
  source = {"Bucket":s_bucket, "Key":s_key}
  try:
    client = boto3.client('s3')
    client.copy(source, d_bucket, d_key)
    res.render(server.get_template("get_copy.html"), {"title":"Copy file", "message":"OK: Copied the file.", "s_bucket":s_bucket, "s_key":s_key, "d_bucket":d_bucket, "d_key":d_key})
  except Exception as e:
    res.sendStatus(500, Response.INTERNAL_SERVER_ERROR + ": " + str(e))
  return

# POST /post_delete
def post_delete(req, res):
  bucket = req.getParam("bucket")
  key = req.getParam("key")
  try:
    client = boto3.client('s3')
    client.delete_object(Bucket=bucket, Key=key)
    res.render(server.get_template("get_delete.html"), {"title":"Delete file", "message":"OK: Deleted the file.", "bucket":bucket, "key":key})
  except Exception as e:
    res.sendStatus(500, Response.INTERNAL_SERVER_ERROR + ": " + str(e))
  return

# POST /post_prefix_new
def post_prefix_new(req, res):
  bucket = req.getParam("bucket")
  key = req.getParam("key")
  if not key.endswith("/"):
    key += "/"
  try:
    client = boto3.client('s3')
    client.put_object(Bucket=bucket, Key=key, Body='')
    res.render(server.get_template("get_prefix_new.html"), {"title":"Prefix New", "message":"OK: Created the new prefix.", "bucket":bucket, "key":key})
  except Exception as e:
    res.sendStatus(500, Response.INTERNAL_SERVER_ERROR + ": " + str(e))
  return


# ----------------- Handlers mapping --------------------

# GET メソッドのパスに対するハンドラマッピング
GET_MAP = {
  "/get_list_buckets": get_list_buckets,
  "/get_list_items": get_list_items,
  "/get_show": get_show,
  "/get_image": get_image,
  "/get_download": get_download,
  "/get_upload": get_upload,
  "/get_copy": get_copy,
  "/get_delete": get_delete,
  "/get_prefix_new": get_prefix_new
}

# POST メソッドのパスに対するハンドラマッピング
POST_MAP = {
  "/post_upload": post_upload,
  "/post_copy": post_copy,
  "/post_delete": post_delete,
  "/post_prefix_new": post_prefix_new
}
