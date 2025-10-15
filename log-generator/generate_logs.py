import time
import json
import random
import sys
from datetime import datetime
from faker import Faker

fake = Faker()

def generate_distributed_ip():
    """Generate IP addresses from various countries for better geographic distribution."""
    # IP ranges organized by region with equal representation
    ip_ranges = [
        # Europe (10 ranges)
        ("2.16.0.0", "2.31.255.255"),      # Europe
        ("5.0.0.0", "5.255.255.255"),      # Europe
        ("31.0.0.0", "31.255.255.255"),    # Netherlands/Europe
        ("37.0.0.0", "37.255.255.255"),    # Europe
        ("46.0.0.0", "46.255.255.255"),    # Europe
        ("62.0.0.0", "62.255.255.255"),    # Europe
        ("78.0.0.0", "78.255.255.255"),    # Europe
        ("80.0.0.0", "80.255.255.255"),    # Europe
        ("82.0.0.0", "82.255.255.255"),    # UK/Europe
        ("88.0.0.0", "88.255.255.255"),    # Europe
        
        # Asia (10 ranges)
        ("1.0.0.0", "1.255.255.255"),      # Asia Pacific
        ("14.0.0.0", "14.255.255.255"),    # Japan/Asia
        ("27.0.0.0", "27.255.255.255"),    # Asia
        ("36.0.0.0", "36.255.255.255"),    # China
        ("42.0.0.0", "42.255.255.255"),    # Asia
        ("58.0.0.0", "58.255.255.255"),    # China/Asia
        ("103.0.0.0", "103.255.255.255"),  # Asia Pacific
        ("110.0.0.0", "110.255.255.255"),  # China/Asia
        ("116.0.0.0", "116.255.255.255"),  # China
        ("125.0.0.0", "125.255.255.255"),  # Japan/Korea
        
        # South America (10 ranges)
        ("177.0.0.0", "177.255.255.255"),  # Brazil
        ("179.0.0.0", "179.255.255.255"),  # Brazil
        ("181.0.0.0", "181.255.255.255"),  # South America
        ("186.0.0.0", "186.255.255.255"),  # South America
        ("189.0.0.0", "189.255.255.255"),  # Mexico/South America
        ("190.0.0.0", "190.255.255.255"),  # South America
        ("191.0.0.0", "191.255.255.255"),  # Brazil
        ("200.0.0.0", "200.255.255.255"),  # South America
        ("201.0.0.0", "201.255.255.255"),  # South America
        ("187.0.0.0", "187.255.255.255"),  # Brazil
        
        # Africa (10 ranges)
        ("41.0.0.0", "41.255.255.255"),    # Africa
        ("102.0.0.0", "102.255.255.255"),  # Africa
        ("105.0.0.0", "105.255.255.255"),  # Africa
        ("154.0.0.0", "154.255.255.255"),  # Africa
        ("196.0.0.0", "196.255.255.255"),  # Africa
        ("197.0.0.0", "197.255.255.255"),  # Africa
        ("129.0.0.0", "129.255.255.255"),  # South Africa
        ("155.0.0.0", "155.255.255.255"),  # Africa
        ("160.0.0.0", "160.255.255.255"),  # Africa
        ("169.0.0.0", "169.255.255.255"),  # Africa
        
        # Australia/Oceania (5 ranges)
        ("1.128.0.0", "1.159.255.255"),    # Australia
        ("27.32.0.0", "27.47.255.255"),    # Australia
        ("49.0.0.0", "49.255.255.255"),    # Australia/Asia
        ("101.0.0.0", "101.255.255.255"),  # Australia
        ("203.0.0.0", "203.255.255.255"),  # Australia/Asia Pacific
        
        # North America - US (5 ranges, reduced)
        ("8.0.0.0", "8.255.255.255"),      # US
        ("12.0.0.0", "12.255.255.255"),    # US
        ("24.0.0.0", "24.255.255.255"),    # US/Canada
        ("50.0.0.0", "50.255.255.255"),    # US
        ("66.0.0.0", "66.255.255.255"),    # US
    ]
    
    # Select a random IP range
    start_ip, end_ip = random.choice(ip_ranges)
    
    # Convert IP to integer
    start_parts = [int(x) for x in start_ip.split('.')]
    end_parts = [int(x) for x in end_ip.split('.')]
    
    # Generate random IP within the range
    ip_parts = []
    for i in range(4):
        if i < 3:
            ip_parts.append(random.randint(start_parts[i], end_parts[i]))
        else:
            ip_parts.append(random.randint(1, 254))
    
    return '.'.join(map(str, ip_parts))

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
        "client_ip": generate_distributed_ip(),
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
        print(json.dumps(log_entry), flush=True)
        
        # Wait for a random interval to simulate real traffic
        time.sleep(random.uniform(0.2, 1.5))

