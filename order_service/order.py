import http.server
import json
import csv
import os
import threading
import time
import os

# Get environment variable for catalog service host
catalog_service_host = os.getenv('CATALOG_SERVICE_HOST', 'localhost')

# Define the file path for storing orders and initialize variables
orders_db_file = "data/orders.csv"
order_no = 0
orders_db = {}

# Lock for synchronizing access to the order log
order_log_lock = threading.Lock()

#Function to save order log to disk
def save_order_log():
    print("writing to order log")
    with open(orders_db_file, mode='w', newline='') as file:
        print("orders_db=",orders_db)
        col_names = ['order_no', 'name', 'quantity', 'price']
        csv_writer = csv.DictWriter(file, fieldnames=col_names)

        csv_writer.writeheader()
        for o_no, order_data in orders_db.items():
            print("writing row:",o_no)
            csv_writer.writerow({'order_no': o_no, 'name': order_data['name'], 'price': order_data['price'], 'quantity': order_data['quantity']})

# Function to load order log from disk
def load_order_log():
    global orders_db
    if os.path.exists(orders_db_file):
        with open(orders_db_file, mode='r') as db:
            csv_reader = csv.DictReader(db)
            for entry in csv_reader:
                curr_order_no = entry['order_no']
                global order_no
                if int(curr_order_no) > order_no:
                    order_no = int(curr_order_no)
                orders_db[curr_order_no] = {
                    'name': entry['name'],
                    'price': float(entry['price']),
                    'quantity': int(entry['quantity'])
                }
    else:
        print("file not found")
        pass

# Define the HTTP request handler for handling order requests
class OrderHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        # Handle HTTP POST requests for placing orders
        data = json.loads(self.rfile.read(int(self.headers["Content-Length"])).decode()) # Parse JSON data from request
        print("POST data = ",data)
        toy_name = data["name"]
        toy_q = data["quantity"]
        
        # Send a request to the catalog service to buy the specified quantity of the item
        headers = {"Content-type":"application/json"}
        conn = http.client.HTTPConnection(catalog_service_host,8081)
        conn.request("POST", "/buy_qty", json.dumps(data), headers)
        resp = conn.getresponse()
        print("Response is:",resp.status, resp.reason)
        # Print order details
        print("toy_name=",toy_name)
        print("toy_q=",toy_q)
        result = resp.read()
        # Get the result from the catalog service response
        json_result = json.loads(result.decode())
        if "error" in json_result: # Check if there is an error in the response
            # If there's an error, send the error response to the client
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(result)
        else :
            # If the order is successful, update the order log with the new order

            with order_log_lock:
                print("Order service Updating order log ",toy_name)
                print("Start time=",time.time())
                time.sleep(0.2)
                global order_no
                order_no+=1
                orders_db[order_no] = {"name":toy_name,"price":json_result["data"]["price"],"quantity":toy_q}
                save_order_log()
                resp = {
                        "data": {
                            "order_number": order_no
                        }
                    }
                print("End time=",time.time())
            # Send the order number response to the client
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(resp).encode())

# Function to start the order service
def start_order_service():
    server_address = ('', 8082)
    # httpd = http.server.HTTPServer(server_address, OrderHTTPRequestHandler)
    httpd = http.server.ThreadingHTTPServer(server_address, OrderHTTPRequestHandler)
    load_order_log() # Load order log from disk
    httpd.serve_forever()

if __name__ == '__main__':
    start_order_service()