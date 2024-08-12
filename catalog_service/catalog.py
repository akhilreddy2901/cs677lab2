import http.server
import json
import csv
import os
from locks import RWLock # Importing custom RWLock for managing concurrent access
import time

toys_db_file = "data/toys_db.csv" # File path for storing toy database
toys_db = {}
my_obj_rwlock = RWLock() # Initialize RWLock object for thread-safe access

#Save the toy database to a CSV file.
def save_database():
    print("writing to db")
    with open(toys_db_file, mode='w', newline='') as file:
        print("toys_db=",toys_db)
        col_names = ['name', 'price', 'stock']
        csv_writer = csv.DictWriter(file, fieldnames=col_names)

        csv_writer.writeheader()
        for toy_name, toy_data in toys_db.items():
            print("writing row:",toy_data)
            csv_writer.writerow({'name': toy_name, 'price': toy_data['price'], 'stock': toy_data['stock']})

#Load the toy database from a CSV file.
def load_database():
    global toys_db
    if os.path.exists(toys_db_file):
        with open(toys_db_file, mode='r') as db:
            csv_reader = csv.DictReader(db)
            for entry in csv_reader:
                toy_name = entry['name']
                toys_db[toy_name] = {
                    'name': entry['name'],
                    'price': float(entry['price']),
                    'stock': int(entry['stock'])
                }
    else:
        print("file not found")
        #Create default toy database if the file doesn't exist
        toys_db =   {
                        "Tux": {"name": "Tux","price": 25.99, "stock": 10000},
                        "Whale": {"name": "Whale","price": 19.99, "stock": 10000},
                        "Elephant": {"name": "Elephant","price": 29.99, "stock": 10000},
                        "Fox": {"name": "Fox","price": 29.99, "stock": 10000},
                        "Python": {"name": "Python","price": 29.99, "stock": 10000},
                        "Dolphin": {"name": "Dolphin","price": 22.99, "stock": 10000}
                    }
        save_database()
        pass

class CatalogHTTPRequestHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        """Handle HTTP GET requests."""
        path = self.path
        print(path)
        contents = path.split('/')
        product_name = contents[len(contents)-1]
        print(product_name)

        # Check if the product exists in the database
        if product_name in toys_db:
            # Send a successful response with product details
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            # Read the product details under a read lock to ensure thread safety
            with my_obj_rwlock.r_locked():
                time.sleep(0.2)
                resp = {"data":toys_db[product_name]}
            self.wfile.write(json.dumps(resp).encode())
            
        else:
             # Send a response indicating product not found
            self.send_response(200)
            resp = {
                        "error": {
                            "code": 404,
                            "message": "product not found"
                        }
                    }
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(resp).encode())
    
    def do_POST(self):
        """Handle HTTP POST requests."""
        print("inside post of catalog")
        # Read and parse the JSON data from the request body
        data = json.loads(self.rfile.read(int(self.headers["Content-Length"])).decode())
        print("POST data = ",data)
        toy_name = data["name"]
        order_qty = data["quantity"]
        print("toy_name=",toy_name)
        print("order_qty=",order_qty)
        # Check if the product exists in the database
        if toy_name in toys_db:
            # Update the stock if there's sufficient quantity
            with my_obj_rwlock.w_locked():
                if toys_db[toy_name]["stock"]>=order_qty:
                    print("Catalog Updating toy ",toy_name)
                    print("Start time=",time.time())
                    time.sleep(0.2) # Simulate processing delay
                    toys_db[toy_name]["stock"] = toys_db[toy_name]["stock"] - order_qty
                    resp = {"data":toys_db[toy_name]}
                    # Send a successful response with updated product details
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(resp).encode())
                    save_database() # Save the updated database to file
                    print("End time=",time.time())
                elif toys_db[toy_name]["stock"]<order_qty:
                    # Send a response indicating insufficient stock
                    time.sleep(0.2) # Simulate processing delay
                    resp = {
                                "error": {
                                    "code": 404,
                                    "message": "not enough stock"
                                }
                            }
                    self.send_response(200)

                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(resp).encode())
        else:
            
            self.send_response(200)
            resp = {
                        "error": {
                            "code": 404,
                            "message": "product not found"
                        }
                    }
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(resp).encode())
            

def start_catalog_service():
    load_database()
    server_address = ('', 8081)
    # httpd = http.server.HTTPServer(server_address, CatalogHTTPRequestHandler)
    httpd = http.server.ThreadingHTTPServer(server_address, CatalogHTTPRequestHandler)
    httpd.serve_forever()

if __name__ == '__main__':
    start_catalog_service()