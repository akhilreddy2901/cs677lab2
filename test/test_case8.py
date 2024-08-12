import http.client
import json

def test_order_place_order():
    conn = http.client.HTTPConnection('localhost', 8082)
    order_details = json.dumps({
        "name": "Tux",
        "quantity": 1
    })
    headers = {'Content-type': 'application/json'}
    conn.request("POST", "/order", order_details, headers)
    response = conn.getresponse()
    data = json.loads(response.read().decode())
    assert response.status == 200
    assert 'data' in data, "Expected 'data' field in response"
    assert 'order_number' in data['data'], "Order number is missing"
    print("Test Case 8 Passed: Order Service - Place Order Test")
    conn.close()

if __name__ == '__main__':
    test_order_place_order()
