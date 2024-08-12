import http.server
import http.client
import json
import time
import threading
import socket
# Initial toy database
toys_db = {
    "Tux": {"name": "Tux","price": 25.99, "stock": 8},
    "Whale": {"name": "Whale","price": 19.99, "stock": 5},
    "Elephant": {"name": "Elephant","price": 29.99, "stock": 8},
    "Fox": {"name": "Fox","price": 29.99, "stock": 8},
    "Python": {"name": "Python","price": 29.99, "stock": 8},
    "Dolphin": {"name": "Dolphin","price": 22.99, "stock": 3}
}

import os
# Get environment variables for catalog and order service hosts
catalog_service_host = os.getenv('CATALOG_SERVICE_HOST', 'localhost')
order_service_host = os.getenv('ORDER_SERVICE_HOST', 'localhost')

class CustomHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        # Handle HTTP GET requests
        path = self.path
        print(path)
        contents = path.split('/')
        product_name = contents[len(contents)-1]
        
        thread_id  = threading.get_ident()
        print("Front end checking for ",product_name)
        print("thread_id=",thread_id)
        # time.sleep(5)

        # Send a GET request to the catalog service
        conn = http.client.HTTPConnection(catalog_service_host,8081)
        conn.request("GET", f"/query/{product_name}")
        resp = conn.getresponse()
        print("Catalog Response is:",resp.status, resp.reason)
        data = resp.read()
        print("Catalog Service replied: ",data.decode())

        self.send_response(200) # Send the response back to the client
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(data)
    
    def do_POST(self):
        # Handle HTTP POST requests
        data = json.loads(self.rfile.read(int(self.headers["Content-Length"])).decode())
        # print("POST data = ",data)
        # toy_name = data["name"]
        # toy_q = data["quantity"]
        # print("toy_name=",toy_name)
        # print("toy_q=",toy_q)

        # Send a POST request to the order service
        conn = http.client.HTTPConnection(order_service_host,8082)
        headers = {"Content-type":"application/json"}
        str_data = json.dumps(data)
        conn.request("POST", "/order", str_data, headers)

        resp = conn.getresponse()  # Get and print the response from the order service
        print("Response is:",resp.status, resp.reason)

        self.send_response(200) 
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(resp.read())

def start_server():
    # Start the HTTP server
    server_address = ('', 8080)
    # httpd = http.server.HTTPServer(server_address, CustomHTTPRequestHandler)
    httpd = http.server.ThreadingHTTPServer(server_address, CustomHTTPRequestHandler)
    local_ip = socket.gethostbyname(socket.gethostname())
    print("local addr:",local_ip)
    httpd.serve_forever()


if __name__ == '__main__':
    start_server()