from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi

# import CRUD Operations
from database_setup import Base, Restaurant, MenuItem
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind=engine
DBSession = sessionmaker(bind = engine)
session = DBSession()


class WebServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:       
            if self.path.endswith("/restaurants/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<h1>Make a new restaurant</h1>"
                output += "</br></br>"
                output += "<form method='POST' enctype='multipart/form-data' action = '/restaurants/new'>"
                output += "<input type='text' name='restaurant' placeholder='Enter Restaurant'>"
                output += "<input type='submit' value='Create'>" 
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return

            if self.path.endswith("/edit"):
                rest_id = self.path.split('/')[2]
                rest_name = session.query(Restaurant).filter_by(
                    id=rest_id).one()
                if rest_name:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()                
                    
                    output = ""
                    output += "<html><body>"
                    output += "<h1>"
                    output += rest_name.name
                    output += "</h1>"
                    output += "</br></br>"
                    output += "<form method='POST' enctype='multipart/form-data' action = '/restaurants/%s/edit'>" % rest_id
                    output += "<input type='text' name='restaurant' placeholder='%s'>" % rest_name.name
                    output += "<input type='submit' value='Edit'>" 
                    output += "</body></html>"
                    self.wfile.write(output)
                    print output

            if self.path.endswith("/delete"):
                rest_id = self.path.split('/')[2]
                rest_name = session.query(Restaurant).filter_by(
                    id=rest_id).one()
                if rest_name:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()                
                    
                    output = ""
                    output += "<html><body>"
                    output += "<h1>"
                    output += "Are you sure you want to delete "
                    output += rest_name.name
                    output += "?"
                    output += "</h1>"
                    output += "</br></br>"
                    output += "<form method='POST' enctype='multipart/form-data' action = '/restaurants/%s/delete'>" % rest_id
                    output += "<input type='submit' value='Delete'>" 
                    output += "</body></html>"
                    self.wfile.write(output)
                    print output

            if self.path.endswith("/restaurants"):
                restaurants = session.query(Restaurant).all()
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<a href='/restaurants/new'>Click to add a new restaurant</a>"
                output += "</br></br>"
                for restaurant in restaurants:
                    output += restaurant.name
                    output += "</br>"
                    output += "<a href='/restaurants/%s/edit'>Edit</a></br>"  % restaurant.id
                    output += "<a href='/restaurants/%s/delete'>Delete</a></br></br>" % restaurant.id
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return
        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)
    
    def do_POST(self):
        try:
            if self.path.endswith("/restaurants/new"):
                ctype, pdict = (
                    cgi.parse_header(self.headers.getheader('content-type'))
                    )
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    userInput = fields.get('restaurant')

                    addRestaurant = Restaurant(name=userInput[0])
                    session.add(addRestaurant)
                    session.commit()

                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()

            if self.path.endswith("/edit"):
                ctype, pdict = (
                    cgi.parse_header(self.headers.getheader('content-type'))
                    )
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    userInput = fields.get('restaurant')
                    rest_id = self.path.split('/')[2]
                    rest_name = session.query(Restaurant).filter_by(
                        id=rest_id).one()

                    if rest_name != []:
                        rest_name.name = userInput[0]
                        session.add(rest_name)
                        session.commit()
                        self.send_response(301)
                        self.send_header('Content-type', 'text/html')
                        self.send_header('Location', '/restaurants')
                        self.end_headers()

            if self.path.endswith("/delete"):
                ctype, pdict = (
                    cgi.parse_header(self.headers.getheader('content-type'))
                    )
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    userInput = fields.get('restaurant')
                    rest_id = self.path.split('/')[2]
                    rest_name = session.query(Restaurant).filter_by(
                        id=rest_id).one()

                    if rest_name != []:
                        session.delete(rest_name)
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
        server = HTTPServer(('',port), WebServerHandler)
        print "Web server running on port %s" % port
        server.serve_forever()

    except KeyboardInterrupt:
        print "^C entered, stopping web server..."
        server.socket.close()

if __name__ == '__main__':
    main()