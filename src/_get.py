from http.server import BaseHTTPRequestHandler, HTTPServer
import cgi
import sys
import ast
import time
import threading

devices = dict()

hostName = "192.168.1.53"
serverPort = 8080

class webserverHandler(BaseHTTPRequestHandler):
  def do_GET(self):
    try:
      if self.path.endswith("/hello"):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        site = ""
        site += ' <html> \
                  <head> \
                  <meta http-equiv="refresh" content="2"> \
                  <TITLE>Python Web-Server</TITLE> \
                    <style type="text/css">body{FONT-FAMILY: Arial, Helvetica, sans-serif} \
                    p         {FONT-FAMILY: Arial, Helvetica, sans-serif} \
                    a:link    {color:#000000; text-decoration:none} \
                    a:hover   {color:#000000; text-decoration:none; background-color:#C0C0C0;} \
                    a:visited {color:#000000; text-decoration:none} \
                    a:active  {color:#000000; text-decoration:none} \
                    .oben     {vertical-align:top;   } \
                    .mittig   {vertical-align:middle;} \
                    .unten    {vertical-align:bottom;} \
                    </style> \
                    </head> \
                    <body \
                      bgcolor="#d0d0d0" text="#434343" link="#1a1a1a" alink="#1a1a1a" vlink="#1a1a1a"> \
                      <center> \
                      <h2> Hello, this is the ESPNode Webserver</h2></form> \
                      </center> \
                      <center> \
                        {TABLE} \
                      </center>'
        table = ""
        for ident, value in devices.items():
          table += "<table cellSpacing=2 cellPadding=10 border=1>"
          table += "<thead><tr><th width=\"1271\"><h3>" + str(ident) + "</h3></th></tr></thead>"
          table += "<table cellSpacing=2 cellPadding=10 border=1><tbody><tr>"
          for varname, varval in value.items():
            table += "<td width=\"300\">" + str(varname) + ": " + str(varval) + "</td>"
          table += "</table></tr></tbody></br>"  
        table += "</table>"
        output = site.replace("{TABLE}", table)
        output += '</body></html>'
        self.wfile.write(output.encode())
        return
    except IOError:
      self.send_error(404, "File not found %s" % self.path)

  def do_POST(self):
    try:
      content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
      post_data = self.rfile.read(content_length) # <--- Gets the data itself
      dict_str = post_data.decode("UTF-8")
      mydata = ast.literal_eval(dict_str)
      self.update(mydata)
      self.send_response(301)
      self.send_header('Content-Type', 'text/html')
      self.end_headers()
      ctype, pdict = cgi.parse_header(self.headers.get('Content-Type'))
      content_len = int(self.headers.get('Content-length'))
      output = ''
      output += '<html><body>'
      output += '<h2> Okay, got the data at: ' + str((time.time())) +'</h2>'
      output += '</body></html>'
      self.wfile.write(output.encode())
    except:
      self.send_error(404, "{}".format(sys.exc_info()[0]))
      print(sys.exc_info())

  def update(self, data):
    try:
      devices[data["name"]].update(data)
      devices[data["name"]]["cnt"] += 1
      devices[data["name"]]["TransmitCycle"] = int(devices[data["name"]]["TransmitCycle"]) * 2
      print("got message from: ", data["name"])
    except Exception as err:
      print ("unknown device: ", err)
      devices[data["name"]] = dict()
      devices[data["name"]].update(data)
      devices[data["name"]]["cnt"] = 1
      devices[data["name"]]["TransmitCycle"] = int(devices[data["name"]]["TransmitCycle"]) * 2
      devices[data["name"]]["service"] = Service(data["name"])
      print("generating: ", err)

class Service():
  MyName = ""
  def __init__(self, DeviceName):
      self.MyName = DeviceName
      threading.Thread(target=self._monitoring_thread, daemon=True).start()

  def _monitoring_thread(self):
    while True:
      if devices[self.MyName]["TransmitCycle"]:
        devices[self.MyName]["TransmitCycle"] -= 1
      else:
        print("Device: ", self.MyName, " sendet nicht mehr")
      time.sleep(1)

def main():
    try:
        server = HTTPServer((hostName, serverPort), webserverHandler)
        print("Server started http://%s:%s" % (hostName, serverPort))
        server.serve_forever()

    except KeyboardInterrupt:
        print(" ^C entered stopping web server...")
        server.socket.close()


if __name__ == '__main__':
    main()

