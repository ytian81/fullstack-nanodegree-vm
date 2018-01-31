from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi

from database import Restaurant, Base, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)
session = DBSession()

class WebServiceHandler(BaseHTTPRequestHandler):

  def do_GET(self):
    try:
      if self.path.endswith("/edit"):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        id = self.path.split('/')[1]
        restaurant = session.query(Restaurant).filter_by(id = int(id)).one()
        output = ""
        output += "<html><body>"
        output += "<form method='POST' enctype='multipart/form-data' action="+self.path+"><h1>"+restaurant.name+"</h1><input name='message' type='text' placeholder="+restaurant.name+"><input type='submit' value='Change'></form>"
        output += "</body></html>"
        self.wfile.write(output)
        return

      if self.path.endswith("/delete"):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        id = self.path.split('/')[1]
        restaurant = session.query(Restaurant).filter_by(id = int(id)).one()
        output = ""
        output += "<html><body>"
        output += "<form method='POST' enctype='multipart/form-data' action="+self.path+"><h1>Are you sure you want to delete "+restaurant.name+"?</h1><input type='submit' value='Delete'></form>"
        output += "</body></html>"
        self.wfile.write(output)
        return

      if self.path.endswith("/restaurants"):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        output = ""
        output += "<html><body>"
        output += "<h1><a href='/restaurants/new'>Make a New Restaurant Here</a></h1>"
        for restaurant in session.query(Restaurant).all():
          output += restaurant.name
          output += "</br>"
          output += "<a href=/"+str(restaurant.id)+"/edit>Edit</a>"
          output += "</br>"
          output += "<a href=/"+str(restaurant.id)+"/delete>Delete</a>"
          output += "</br>"
        output += "</body></html>"
        self.wfile.write(output)
        return

      if self.path.endswith("/restaurants/new"):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        output = ""
        output += "<html><body>"
        output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/new'><h1>Make a New Restaurant</h1><input name='message' type='text' placeholder='new restaurant name'><input type='submit' value='Create'></form>"
        output += "</body></html>"
        self.wfile.write(output)
        return

    except IOError:
      self.send_error(404, 'File Not Found: %s' % self.path)

  def do_POST(self):
    try:
      if self.path.endswith("/restaurants/new"):
        ctype, pdict = cgi.parse_header(
          self.headers.getheader('content-type'))
        if ctype == 'multipart/form-data':
          fields = cgi.parse_multipart(self.rfile, pdict)
          messagecontent = fields.get('message')
        new_restaurant = Restaurant(name=messagecontent[0])
        session.add(new_restaurant)
        session.commit()
        self.send_response(301)
        self.send_header('Content-type', 'text/html')
        self.send_header('Location', '/restaurants')
        self.end_headers()

      if self.path.endswith("/edit"):
        id = self.path.split('/')[1]
        restaurant = session.query(Restaurant).filter_by(id = int(id)).one()
        restaurant.name = messagecontent[0]
        session.add(restaurant)
        session.commit()
        self.send_response(301)
        self.send_header('Content-type', 'text/html')
        self.send_header('Location', '/restaurants')
        self.end_headers()

      if self.path.endswith("/delete"):
        id = self.path.split('/')[1]
        ctype, pdict = cgi.parse_header(
          self.headers.getheader('content-type'))
        if ctype == 'multipart/form-data':
          fields = cgi.parse_multipart(self.rfile, pdict)
          messagecontent = fields.get('message')
        restaurant = session.query(Restaurant).filter_by(id = int(id)).one()
        session.delete(restaurant)
        session.commit()
        self.send_response(301)
        self.send_header('Content-type', 'text/html')
        self.send_header('Location', '/restaurants')
        self.end_headers()
    except:
      pass

def main():
  try:
    port = 8080
    server = HTTPServer(('', port), WebServiceHandler)
    print "Web server is running on port %s" % port
    server.serve_forever()
  except KeyboardInterrupt:
    print "Web server is terminated by user..."
    server.socket.close()

if __name__ == '__main__':
  main()