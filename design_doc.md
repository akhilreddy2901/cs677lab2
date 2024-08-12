# Design Document: Microservices-Based Toy Store

**Introduction:**
The Microservices-Based Toy Store is an innovative distributed system designed to offer an engaging online shopping experience for purchasing toys. The architecture is modular, comprising microservices that independently manage different aspects of the toy store operations, such as product catalog management, order processing, and client interactions. This document outlines the system's design, focusing on its microservices architecture, communication protocols, concurrency, and containerization.

**Objective:**
The system aims to provide a robust, scalable, and efficient online platform for browsing and purchasing toys. It is designed to handle concurrent user requests effectively, ensuring seamless access to product information and purchase capabilities while maintaining data consistency and system integrity. The system is designed to be containerized for easy deployment and scalability.

**Solutions Overview/Architecture:**
The architecture is divided into three primary microservices: Catalog Service, Order Service, and Front-End Service. These services communicate over the network, using HTTP-based REST APIs for interactions, which allows for a decoupled and scalable system design.

- **Catalog Service**: Manages the toy product catalog, including toy details, pricing, and stock levels. It supports query operations and updates to product information. This service maintains the catalog data and handles requests from the front-end service and the order service. It exposes an interface for updating and querying the catalog. Synchronization mechanisms like read-write locks are used to ensure concurrent access safety in an efficient way as there are both read and write operations being executed on the database. The catalog service also checks if there is enough stock in the database and returns an error to order service if there's insufficient stock. If there is sufficient stock, it updates the database immediately as soon as it executes an update request from the order service. The remaining stock is calculated and the database is updated. When the server starts, if there's no toys_db.csv file present at the required location, a new toys_db.csv file is generated. A default toy items database is created in memory and it is dumped into the created toys_db.csv file.
- **Order Service**: Processes purchase orders by interacting with the catalog for stock management and maintaining a log of all orders. This generates an order number everytime the user does a buy request which is unique and keeps increasing consistently. Even if the services are restarted, the highest executed order number is calculated from the orders.csv file and the new orders henceforth will be assigned order numbers greater than this.
When the server starts, if there's no orders.csv file present at the required location, a new orders.csv file is generated.  The order service updates the order log(orders.csv) immediately once an order is executed and an order number is generated. Synchronization mechanisms like normal locks are used to ensure concurrent access safety as there are only write operations being executed on the order log file.
- **Front-End Service**: Acts as the interface between the clients and the backend services (Catalog and Order), routing client requests and responses. This service handles client requests and communicates with the back-end services. It listens for HTTP requests, processes them, and sends requests to the catalog or order service depending on whether its a buy or query request. It implements GET and POST endpoints.
- **Client Overview**: The client component of the Microservices-Based Toy Store plays a critical role in interacting with the Front-End service, sending queries for toy information and making purchase requests. The client is designed to simulate real-world user interactions with the store, capable of conducting a sequence of actions in a session, reflecting typical browsing and shopping activities.

Each service is designed to operate independently, with its own database (if necessary) to ensure loose coupling and high cohesion within the system.

**Communication Protocol:**
- The system leverages HTTP-based REST APIs for communication between the front-end and backend services. This choice promotes interoperability, simplicity, and the efficient use of resources.
- The Front-End Service also communicates with clients over HTTP, offering RESTful endpoints for product queries and order placements.
- JSON is used for data serialization, offering lightweight data interchange between clients and services.

**Concurrency Management:**
- Threads are used to manage concurrent client requests in all services, ensuring efficient resource use and scalability. We use http.server.ThreadingHTTPServer which listens for incoming requests over HTTP and assigns them to a new thread for each client and this connection will be kept alive untill the client closes the connection (one thread per each client session)
- Synchronization mechanisms (e.g., locks in Order service and read-write locks in the Catalog Service) are employed to ensure data consistency during concurrent read and write operations.

**Note:** 
- We incorporated a simulated processing time of 200 ms while reading and writing to databases(both toys_db.csv and orders.csv). This choice aimed to emulate the realistic processing time typically encountered when handling read and write requests on an actual database. By introducing this delay, we mimicked the scenario where concurrent client requests contend for server resources, leading to queuing and increased response time.

- The inclusion of the sleep time not only provided a more realistic simulation but also underscored the importance of efficient resource utilization and concurrency management in distributed systems. As clients make requests to access or modify the shared database, the server must contend with processing each request sequentially, leading to potential delays and queuing as the load increases.

- By incorporating this simulated processing time, our evaluation captured the impact of contention for threads and the queuing phenomenon on response time. This refinement adds a layer of realism to our analysis, highlighting the challenges and considerations involved in designing and optimizing distributed systems for real-world scenarios. Moreover, without the inclusion of the sleep time, the differences in network speed exert a more pronounced influence on the observed latencies from the client side. This occurs because the actual processing time of the query and buy functions on the server side is significantly shorter in comparison to the time taken to transmit and receive requests over the network. In essence, the absence of a simulated processing time accentuates the impact of network latency on overall response times.

**Microservices Design Choices:**
- **Decoupled Architecture**: Each microservice is developed, deployed, and scaled independently, enhancing the system's scalability and fault tolerance.
- **Data Management**: The Catalog and Order services each maintain their own data storage, promoting data encapsulation and service autonomy.
- **Statelessness**: The front-end service is designed to be stateless, facilitating scalability and simplifying the handling of client requests.

**Client Implementation Details**

- **Connection Management:** The client establishes an HTTP connection with the Front-End service, utilizing the `http.client` Python module. This choice ensures a low-level, efficient communication channel suitable for RESTful API interactions.
  
- **Request Generation:** For querying product details, a `GET` request is sent, while purchase actions are initiated via `POST` requests. These requests are constructed dynamically, with product names derived from predetermined lists and order quantities randomly generated to simulate varied user behavior.
  
- **Concurrency Simulation:** Utilizing Python's `multiprocessing` library, the client simulates concurrent users by spawning multiple processes. Each process represents an individual client session (thread-per-session model), capable of making sequential requests to simulate real user interaction patterns.
  
- **Performance Metrics Collection:** The client measures the latency for both query and buy requests, recording the time taken from sending the request to receiving a response. These latencies are collected across all client sessions, providing a dataset for performance analysis.
  
- **Configuration Flexibility:** The client's operation, including the number of requests per session and the probability of making a purchase after querying a product, can be adjusted. This flexibility allows for testing the system under various load conditions and user interaction scenarios.

**Containerization with Docker**

Each microservice is containerized using Docker, enabling isolated environments for service deployment. A Docker Compose file orchestrates the deployment of all services, ensuring they are networked correctly and can communicate seamlessly.

**Docker Configuration**
- **Dockerfile** for each microservice: Specifies the environment, dependencies, and entry points for the services.
- **Docker Compose**: Automates the deployment of the microservices, handling network configurations and dependencies between services.

**Volume Mounting**
To ensure data persistence across container restarts or removals, host directories are mounted as volumes for the Catalog and Order services, safeguarding the product catalog and order logs.

**APIs:**
- **Front-End Service**:
  - `GET /products/<product_name>`: Queries the details of a product.
  - `POST /orders`: Submits an order for a product.
- **Catalog Service**: Internal API supporting query operations from the Front-End and Order services.
  - `GET /query/<product_name>`: Used for querying the details of a product.
  - `POST /buy_qty`: Used for updating the quantity of a product after an order is placed (if its in stock)
- **Order Service**: Internal API supporting order processing requests from the Front-End service.
- `POST /order`: Used to make an order for a product and generates order number.

**Testing:**
- **Unit Testing**: Ensures the functionality of individual components and methods within the microservices.
- **Integration Testing**: Validates the interactions and data flow between the microservices.
- **Load Testing**: Assesses the system's performance and scalability under simulated high-load conditions. Evaluates system performance with varying numbers of client processes, measuring latency for different request types.
- We used the ‘time’ library in python to systematically measure the latency between the moment a client initiates a query and the time it receives a response from the server. As each client is programmed to execute 5 queries, we compute the average latency across these 5 queries for each individual client. This process is replicated across all five clients to gather comprehensive latency data.

**List of Known Issues/Alternatives:**
- **Database Integration:** Migrating from file-based persistence to a database could improve performance and scalability.
- **Network Latency:** It is susceptible to variations in network latency, which can affect response times observed by clients. In our implementation, we added a 0.2s delay using time.sleep while accessing databases to simulate processing time and make it more practical. This added offset reduces the impact of variations in network latency too. Implementing caching mechanisms or using content delivery networks (CDNs) could help alleviate this issue. Optimization techniques, such as caching, could be employed to mitigate the impact of network latency. 

**Error Handling:**
- Data Consistency: Synchronization mechanisms such as locks are crucial to prevent conflicts that may arise from concurrent access to shared resources. For instance, consider a scenario where a request from Client A is reading a particular piece of data from the database while another request from Client B is simultaneously updating the same data. Without proper synchronization, Client A may access an inconsistent or intermediate state of the data, resulting in potential inconsistencies. To address this issue, we have implemented locks while accessing shared data. These locks ensure mutual exclusion, preventing concurrent modifications and maintaining data integrity. 
- The system implements comprehensive error handling to manage exceptions and errors gracefully. This includes input validation, handling of non-existent resources, and communication errors between services.
- When the catalog service starts, if there's no toys_db.csv file present at the required location, a new toys_db.csv file is generated. A default toy items database is created in memory and it is dumped into the created toys_db.csv file.When the order service starts, if there's no orders.csv file present at the required location, a new orders.csv file is generated.

**Conclusion:**
The Microservices-Based Toy Store represents a forward-thinking approach to designing scalable and maintainable software architectures for e-commerce platforms. By leveraging a microservices architecture, the system ensures scalability, resilience, flexibility, containerization for easy deployment, and a strategic approach to testing and performance evaluation.

**References:**
- Reused code from Lab1
- Docker Official Documentation. https://docs.docker.com/
- Python `http.server` Documentation. https://docs.python.org/3/library/http.server.html
- Python `http.client` Documentation. https://docs.python.org/3/library/http.client.html
- Docker Compose Documentation: https://docs.docker.com/compose/
- Used ChatGPT to understand the working of HTTP REST APIs.
- Reused some part of design documentation from Lab1
- Used ChatGPT to debug issues faced due to port and ip address inconsistency while deploying with Docker and other errors.
- Implemented Read Write locks using this https://gist.github.com/tylerneylon/a7ff6017b7a1f9a506cf75aa23eacfd6 
