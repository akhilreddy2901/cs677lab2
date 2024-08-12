import http.client
import json
import random
import multiprocessing
import time

front_end_ip = "127.0.0.1" # IP address of front end server
# front_end_ip = "10.0.0.26"
# front_end_ip = "128.119.243.177"
front_end_port_no = 8080

# Function to send a query request to the front-end server
def query(toy_name):
    conn = http.client.HTTPConnection(front_end_ip,front_end_port_no)
    conn.request("GET", f"/products/{toy_name}")
    resp = conn.getresponse()
    print("Response is:",resp.status, resp.reason)
    data = resp.read()
    print("Server replied: ",data.decode())
    return json.loads(data.decode())
    # print(data)

# Function to send a buy request to the front-end server
def buy(toy_name, quantity):
    conn = http.client.HTTPConnection(front_end_ip,front_end_port_no)
    headers = {"Content-type":"application/json"}
    json_data = {
                    "name": toy_name,
                    "quantity": quantity
                }
    str_data = json.dumps(json_data)
    conn.request("POST", "/orders", str_data, headers)
    resp = conn.getresponse()
    print("Response is:",resp.status, resp.reason)
    data = resp.read()
    print("Server replied: ",data.decode())
    # print(data)
    
# Function to start a single client with multiple requests
def start_single_client(no_of_req, order_probability,q_latencies,b_latencies):

    for _ in range(no_of_req):
    # while True:
    #     message = input("please input your message, type exit to stop\n")

    #     if message.lower() == "exit":
    #         break
        
    #     toy_name = message
        toy_name = random.choice(['Tux', 'Fox', 'Python','Whale','Elephant','Dolphin'])#List of toys
        print("Querying for ",toy_name)
        start_time = time.time()
        toy_details = query(toy_name)
        end_time = time.time()
        quantity_available = toy_details['data']['stock']
        print("Query response time:",end_time-start_time)
        q_latencies.append(end_time-start_time) # record the latency for querying

        if quantity_available > 0: #Checks the quantity before proceeding to make buy request
            if random.random() < order_probability: # Generates a random number between 0 and 1
                quantity_to_order = random.randint(1, quantity_available)# Generates a random number between 1 and quantity_available
                # quantity_to_order = random.randint(1, 10)
                start_time = time.time()
                buy(toy_name, quantity_to_order)
                end_time = time.time()
                print("Buy response time:",end_time-start_time)
                b_latencies.append(end_time-start_time)     # record the latency for buying    

# Main function to generate multiple client processes
def main():
    no_of_requests_per_client = 5
    order_probability = 1
    processes= []  # List to store the client processes
    manager = multiprocessing.Manager() # Manager for sharing data between processes
    q_latencies = manager.list()  # List to store query latencies across processes
    b_latencies = manager.list() #  List to store buy latencies across processes
    no_of_client_processes = 1  # Number of client processes to spawn

    # Create and start the client processes

    for _ in range(no_of_client_processes):
        process = multiprocessing.Process(target=start_single_client,args=(no_of_requests_per_client, order_probability,q_latencies,b_latencies))
        processes.append(process)
        process.start()
    
    # Wait for all client processes to finish
    for process in processes:
        process.join()
    
    print("No of client processess = ",no_of_client_processes)
    print("Order probability = ",order_probability)
    if len(q_latencies) > 0:
        print("Average query latency = ",sum(q_latencies)/len(q_latencies))
    if len(b_latencies) > 0:
        print("Average buy latency = ",sum(b_latencies)/len(b_latencies))

if __name__ == '__main__':
    main()