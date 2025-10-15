import time
import json
import random
from datetime import datetime
from faker import Faker

fake = Faker()

def generate_log_entry():
    """Generates a single, structured log entry."""
    
    # Simulate different HTTP methods
    method = random.choice(["GET", "POST", "PUT", "DELETE", "PATCH"])
    
    # Simulate common status codes, with a higher probability for 2xx and 4xx
    status_code = random.choices(
        [200, 201, 204, 301, 400, 401, 403, 404, 500, 503], 
        weights=[15, 5, 2, 3, 5, 3, 2, 10, 4, 1], 
        k=1
    )[0]
    
    # Generate a fake URL path
    uri = fake.uri_path()
    
    # Add product or user context to some URLs
    if random.random() < 0.3:
        uri = f"/products/{fake.word()}/{random.randint(1000, 9999)}"
    elif random.random() < 0.2:
        uri = f"/users/{fake.user_name()}/profile"
        
    log_data = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "level": "INFO" if status_code < 400 else ("ERROR" if status_code >= 500 else "WARN"),
        "client_ip": fake.ipv4(),
        "user_id": f"user_{random.randint(1, 100)}",
        "http": {
            "request": {
                "method": method,
                "referrer": fake.uri()
            },
            "response": {
                "status_code": status_code,
                "bytes": random.randint(50, 50000)
            },
            "url": uri,
            "version": "1.1"
        },
        "user_agent": {
            "original": fake.user_agent()
        },
        "message": f'{method} {uri} - {status_code}'
    }
    
    return log_data

if __name__ == "__main__":
    while True:
        log_entry = generate_log_entry()
        # Print the log entry as a JSON string to stdout
        print(json.dumps(log_entry))
        
        # Wait for a random interval to simulate real traffic
        time.sleep(random.uniform(0.2, 1.5))

