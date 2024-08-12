## Steps to run:

- Install the required dependencies from the requirements.txt using 'pip install -r requirements.txt'

**Part 1:**

- Navigate inside src folder using 'cd src'
- Run the front end server using the command 'python3 frontend_service/front_end.py'
- Run the order service using the command 'python3 order_service/order.py'
- Run the catalog service using the command 'python3 catalog_service/catalog.py'
- Note the frontend IP address after running the frontend server
- Use the frontend IP addresss obtained from the frontend server and update the 'front_end_ip' variable in the client file
- Run the client using 'python3 client.py'
- Ensure that both the frontend server and client are using the same port for communication

**Part 2:**

- Run the microservices using docker using the command './build.sh' (If the build.sh file isn't executable, you may need to make it executable using the chmod command: 'chmod +x build.sh')
- Use the frontend IP addresss obtained from the frontend server and update the 'front_end_ip' variable in the client file
- Run the client using 'python3 client.py'
- Ensure both the server and client use the same port for communication

**Part 3:**

- Change the variables 'order_probability' and 'no_of_client_processes' in the client.py file as needed and run the microservices and client using one of the above 2 ways.

## How to run tests:
- Navigate to test directory inside src using 'cd src/test'
- Run all the tests using the command 'python3 all_tests.py'

## Work distribution:
- Both of us collaborated closely throughout the lab for all the parts. We implented all the parts of the lab together and have made equal contributions. Our joint efforts were instrumental in successfully completing all aspects of the lab.
- Together, we worked collaboratively to ensure the success of the lab, leveraging our complementary skills and expertise to deliver a comprehensive solution.

## Where to find Docker Files and Docker Compose
- The docker image corresponding to each microservice can be found in the respective microservice's directory inside src. Ex: Dockerfile for frontend_service is at src/frontend_service/Dockerfile
- Docker Compose file is at src/docker-compose.yml