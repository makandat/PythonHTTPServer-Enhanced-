# PythonHTTPServer-Enhanced-

## Overview

Python has a built-in HTTP server, which can be used to run CGI.
However, this HTTP server is low-functioning and difficult to use as is, so it cannot be used as an application server.
"Python http-server (Enhanced)" is based on Python's http-server and can be used as an application server.
Currently (2024/11), the latest version is 1.2.x, but the differences from v1.0.x are as follows.

* In v1.2.x, the host, port, and folder name can be set using a configuration file. (Fixed in v1.0.x)
* In v1.2.x, Cheetah template files are supported. (pip install CT3)
* In v1.2.x, Added some methods.

Therefore, it is necessary to install the Cheetah template engine, and if you do not use it, such as when using it exclusively for web services, it is better to use v1.0.x.
In v1.0.x, these are handled as follows.

* Not available in config file, modify server.py source if necessary.
* Construct entire HTML by embedding strings in '{{variable}}' locations in HTML file.

## Development
### Folder structure
 Create a parent project folder and create the following subfolders in it.

* Project folder (parent): server.py, request.py, response.py, handlers.py, config.json
* html: Subfolder for static files
* templates: Subfolder for template files

### Python files

* server.py: HTTP server that inherits Python's standard HTTP server (SimpleHTTPRequestHandler). Launch this file to run it.
* request.py: Request class
* response.py: Response class
* handlers.py: User's request handler. This file needs to be customized by the user.

### Other files

* config.json: Configuration file. Keys are "host", "port", "static", "templates". This file is optional, and if omitted, default values ​​will be used.
* Static files: HTML and image files are placed in the ./html folder by default.
* Template files: HTML files that need to be rendered are placed in the ./templates folder by default.

### config.json example

```
{
   "host": "localhost",
   "port": 4040,
   "static": "./html",
   "templates": "./templates"
 }
```

## Customizing handlers.py

handlers.py describes the request handlers for the application, so customization is essential. 
This file also contains a map that specifies which request handler to call for the request route.

### Request Handler Mapping
To determine which handler to call for the route, use GET_MAP for the GET method, 
and POST_MAP for the POST method. These are dictionary-type constants 
whose keys are the routes and whose values ​​are the handler names. An example is shown below.

```
# GET method handler mapping
GET_MAP = {
  "/", default
  "/download": download,
  "/upload": upload,
  "/copy": copy,
  "/delete": delete,
  "/prefix": prefix
}

# POST method handler mapping
POST_MAP = {
  "/options": options,
  "/edit": edit
}
```

### Example of a request handler
A request handler must take parameters of type Request and type Response, and output HTML or other response. 
Output is done using methods of the Response class. 
Parameters coming from the client are obtained using methods of the Request class. An example is shown below.

```
# GET /get_list_items
def get_list_items(req, res):
  title = "Keys of Bucket '"
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
```

### Startup

Startup is as follows. If you have a config.json file, 
the host and port may be different from the following. You can terminate it by pressing Ctrl+C.

```
> python server.py
Starting HTTP Server ...
http://localhost:4040
```

## Reference
### server.py
This file contains the following methods, classes, and global variables.

* **settings:**
Contents of config.json (dict type global variable)
* **def get_static(file):**
If the file name is a static file, returns the full path name.
* **def get_template(file):**
If the file name is a template file, returns the full path name.
* **class CustomRequestHander(SimpleHTTPRequestHandler):**
Request handler class based on SimpleHTTPRequestHandler
* **def run(server_class=HTTPServer, handler_class=CustomRequestHander):**
Initialize settings, start the HTTP server, and start listening.

## request.py

request.py contains the Request class. The main methods of the Request class are shown below.

* **def getParam(self, name:str, unEsc=True) -> str:**
Gets the parameter specified by name. unEsc specifies whether to escape HTML special characters. (If the key does not exist, returns a null string.)
* **def getCheck(self, name) -> bool:**
Gets the parameter when a BOOL value is taken, such as a checkbox.
* **def getCookie(self, name: str) -> str:**
Gets the request cookie. (If the key does not exist, returns a null string.)
* **def getPathParam(self) -> str:**
Gets the path parameter. (If the path parameter does not exist, returns a null string.)
* **def getChunk(self, name: str, filename="") -> bytes:**
Gets the contents of the uploaded file.
* **def getFileNames(self, name) -> list:**
Gets the uploaded file name (array of file names).
* **def getFileList(self):**
Gets a list of uploaded file tuples (name, filename).
* **Property method:**
Returns "GET" or "POST".
* **Property headers:**
Returns a list of request headers.
* **Property cookies:**
Returns a list of request cookies.
* **Property content_type:**
MIME type of request data
* **Property form:**
List of form data
* **Property query:**
Query string
* **Property body:**
Raw POSTed data
* **Property files:**
List of uploaded files
* **Property path:**
Request path
* **Property httpVersion:**
HTTP version

## response.py

response.py contains the Response class. The main methods of the Response class are shown below.

* **def sendHtml(self, filepath, embed=None):**
Sends an HTML file. embed defines the embedded string in a dict type.
* **def sendText(self, content, mime="text/plain"):**
Sends a string. By changing mime, it can also be used to send XML and other documents.
* **def render(self, path, embed=None):**
Renders and sends a Cheetah template. Added in v1.1.x.
* **def sendJSON(self, data):**
Converts the object data to JSON and sends it.
* **def sendStatus(self, code, message=""):**
Sends the error status specified by code.
* **def sendFile(self, path):**
Sends the file specified by path. The MIME type is determined from the extension.
* **Static Method def saveFile(filename, content, dir="./upload"):**
Saves the uploaded file specified by filename and content in the folder specified by dir.
* **def sendBLOB(self, blob, mime_type):**
Sends a BLOB (Binary Large Object). mime_type is the MIME type. (Example) "image/jpeg". Added in v1.2.0.
* **Static Method def redirect(res, url):**
Redirects to url.
* **def setCookie(self, name, value):**
Add (or overwrite) a cookie
* **def setHeader(self, name, value):**
Add (or overwrite) a response header
* **Property status:**
Response status code (Read/Write)
* **Property cookies:**
List of response cookies
* **Property headers:**
List of response headers
* **Static Method def htmlList(data, ol=False, list=None, li=None):**
Creates an HTML list.
* **Static Method def htmlTable(data, header=None, table=None, th=None, tr=None, td=None):**
Creates an HTML table.
* **Static Method def htmlAnchor(url, caption, target=None):**
Creates an HTML anchor.
* **Static Method def html_escape(s)**
Replaces '&', '<', and '>' with HTML escape sequences in the string s and returns the function value. 
Added in v1.2.0.

### handlers.py
This file must be customized by the user. It defines the handler body and the route:handler map. See the previous section on customizing handlers.py for an example.

## Sample
A sample handlers.py is shown below.

```
# handlers.py
from response import Response
import boto3
import server

# ----------------- GET handlers --------------------

# GET /get_list_buckets
def get_list_buckets(req, res):
  TITLE = "AWS Buckets"
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
  title = "Keys of Bucket '"
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

# GET /download
def download(req, res):
  return

# GET /upload
def upload(req, res):
  return

# GET /copy
def copy(req, res):
  return

# GET /delete
def delete(req, res):
  return

# GET prefix
def prefix(req, res):
  return


# ----------------- POST handlers --------------------


# ----------------- Handlers mapping --------------------

# GET メソッドのパスに対するハンドラマッピング
GET_MAP = {
  "/get_list_buckets": get_list_buckets,
  "/get_list_items": get_list_items,
  "/download": download,
  "/upload": upload,
  "/copy": copy,
  "/delete": delete,
  "/prefix": prefix
}

# POST メソッドのパスに対するハンドラマッピング
POST_MAP = {
}
```
/