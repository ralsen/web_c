import config as cfg
from http.server import BaseHTTPRequestHandler, HTTPServer
import cgi
import sys
import ast
import time
import datetime
import DataStore as ds
import yaml
import logging
import socket

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
    except Exception as err:
      self.send_error(404, "{}".format(sys.exc_info()[0]))
      print(sys.exc_info(), " - ", err)

  def update(self, data):
# ------------------------------------------------
    """
    conf = ds.pick("AC_0B_FB_D6_41_74", "Configuration", "Infos")
    print(conf)
    if "Sensor1" in conf:
        print("is drin")
    else:
        print("is NICHT drin")
    for info in conf:
        #print("---> Info: ", info)
        try:
            for key, val in conf[info].items():
                print(key, " - ", val)
        except: pass
    """
# ------------------------------------------------

    try:
      DataSet = dict()
      DataSet[data["MAC"].replace(":", "_")] = data
      ds.handle_DataSet(DataSet)      
    except Exception as err:
      logging.info("update went wrong: ")
      print ("update went wrong: ", err, " - ", type(err))

def main():
  cfg.init()
  logging.info("---------- starting ServESP - server ----------")
  try:
      server = HTTPServer((hostName, serverPort), webserverHandler)
      print("Server started http://%s:%s" % (hostName, serverPort))
      server.serve_forever()

  except KeyboardInterrupt:
      print(" ^C entered stopping web server...")
      server.socket.close()


if __name__ == '__main__':
    main()

