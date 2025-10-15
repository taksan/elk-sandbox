"""
Log generation module - handles all log generation logic
"""
import time
import json
import random
from datetime import datetime
from faker import Faker

fake = Faker()


class LogGeneratorConfig:
    """Configuration for log generator."""
    def __init__(self):
        self.min_interval = 0.2
        self.max_interval = 1.5
        self.ddos_active = False
        self.ddos_end_time = 0
        self.ddos_region = None


def get_region_ip_ranges():
    """Return IP ranges organized by region."""
    return {
        "Europe": [
            ("2.16.0.0", "2.31.255.255"),
            ("5.0.0.0", "5.255.255.255"),
            ("31.0.0.0", "31.255.255.255"),
            ("37.0.0.0", "37.255.255.255"),
            ("46.0.0.0", "46.255.255.255"),
            ("62.0.0.0", "62.255.255.255"),
            ("78.0.0.0", "78.255.255.255"),
            ("80.0.0.0", "80.255.255.255"),
            ("82.0.0.0", "82.255.255.255"),
            ("88.0.0.0", "88.255.255.255"),
        ],
        "Asia": [
            ("1.0.0.0", "1.255.255.255"),
            ("14.0.0.0", "14.255.255.255"),
            ("27.0.0.0", "27.255.255.255"),
            ("36.0.0.0", "36.255.255.255"),
            ("42.0.0.0", "42.255.255.255"),
            ("58.0.0.0", "58.255.255.255"),
            ("103.0.0.0", "103.255.255.255"),
            ("110.0.0.0", "110.255.255.255"),
            ("116.0.0.0", "116.255.255.255"),
            ("125.0.0.0", "125.255.255.255"),
        ],
        "South America": [
            ("177.0.0.0", "177.255.255.255"),
            ("179.0.0.0", "179.255.255.255"),
            ("181.0.0.0", "181.255.255.255"),
            ("186.0.0.0", "186.255.255.255"),
            ("189.0.0.0", "189.255.255.255"),
            ("190.0.0.0", "190.255.255.255"),
            ("191.0.0.0", "191.255.255.255"),
            ("200.0.0.0", "200.255.255.255"),
            ("201.0.0.0", "201.255.255.255"),
            ("187.0.0.0", "187.255.255.255"),
        ],
        "Africa": [
            ("41.0.0.0", "41.255.255.255"),
            ("102.0.0.0", "102.255.255.255"),
            ("105.0.0.0", "105.255.255.255"),
            ("154.0.0.0", "154.255.255.255"),
            ("196.0.0.0", "196.255.255.255"),
            ("197.0.0.0", "197.255.255.255"),
            ("129.0.0.0", "129.255.255.255"),
            ("155.0.0.0", "155.255.255.255"),
            ("160.0.0.0", "160.255.255.255"),
            ("169.0.0.0", "169.255.255.255"),
        ],
        "Australia": [
            ("1.128.0.0", "1.159.255.255"),
            ("27.32.0.0", "27.47.255.255"),
            ("49.0.0.0", "49.255.255.255"),
            ("101.0.0.0", "101.255.255.255"),
            ("203.0.0.0", "203.255.255.255"),
        ],
        "North America": [
            ("8.0.0.0", "8.255.255.255"),
            ("12.0.0.0", "12.255.255.255"),
            ("24.0.0.0", "24.255.255.255"),
            ("50.0.0.0", "50.255.255.255"),
            ("66.0.0.0", "66.255.255.255"),
        ],
    }


def generate_distributed_ip():
    """Generate IP addresses from various countries for better geographic distribution."""
    # IP ranges organized by region with equal representation
    ip_ranges = [
        # Europe (10 ranges)
        ("2.16.0.0", "2.31.255.255"),
        ("5.0.0.0", "5.255.255.255"),
        ("31.0.0.0", "31.255.255.255"),
        ("37.0.0.0", "37.255.255.255"),
        ("46.0.0.0", "46.255.255.255"),
        ("62.0.0.0", "62.255.255.255"),
        ("78.0.0.0", "78.255.255.255"),
        ("80.0.0.0", "80.255.255.255"),
        ("82.0.0.0", "82.255.255.255"),
        ("88.0.0.0", "88.255.255.255"),
        
        # Asia (10 ranges)
        ("1.0.0.0", "1.255.255.255"),
        ("14.0.0.0", "14.255.255.255"),
        ("27.0.0.0", "27.255.255.255"),
        ("36.0.0.0", "36.255.255.255"),
        ("42.0.0.0", "42.255.255.255"),
        ("58.0.0.0", "58.255.255.255"),
        ("103.0.0.0", "103.255.255.255"),
        ("110.0.0.0", "110.255.255.255"),
        ("116.0.0.0", "116.255.255.255"),
        ("125.0.0.0", "125.255.255.255"),
        
        # South America (10 ranges)
        ("177.0.0.0", "177.255.255.255"),
        ("179.0.0.0", "179.255.255.255"),
        ("181.0.0.0", "181.255.255.255"),
        ("186.0.0.0", "186.255.255.255"),
        ("189.0.0.0", "189.255.255.255"),
        ("190.0.0.0", "190.255.255.255"),
        ("191.0.0.0", "191.255.255.255"),
        ("200.0.0.0", "200.255.255.255"),
        ("201.0.0.0", "201.255.255.255"),
        ("187.0.0.0", "187.255.255.255"),
        
        # Africa (10 ranges)
        ("41.0.0.0", "41.255.255.255"),
        ("102.0.0.0", "102.255.255.255"),
        ("105.0.0.0", "105.255.255.255"),
        ("154.0.0.0", "154.255.255.255"),
        ("196.0.0.0", "196.255.255.255"),
        ("197.0.0.0", "197.255.255.255"),
        ("129.0.0.0", "129.255.255.255"),
        ("155.0.0.0", "155.255.255.255"),
        ("160.0.0.0", "160.255.255.255"),
        ("169.0.0.0", "169.255.255.255"),
        
        # Australia/Oceania (5 ranges)
        ("1.128.0.0", "1.159.255.255"),
        ("27.32.0.0", "27.47.255.255"),
        ("49.0.0.0", "49.255.255.255"),
        ("101.0.0.0", "101.255.255.255"),
        ("203.0.0.0", "203.255.255.255"),
        
        # North America - US (5 ranges, reduced)
        ("8.0.0.0", "8.255.255.255"),
        ("12.0.0.0", "12.255.255.255"),
        ("24.0.0.0", "24.255.255.255"),
        ("50.0.0.0", "50.255.255.255"),
        ("66.0.0.0", "66.255.255.255"),
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


def generate_ip_from_region(region_name):
    """Generate IP from a specific region."""
    regions = get_region_ip_ranges()
    if region_name not in regions:
        region_name = random.choice(list(regions.keys()))
    
    ip_ranges = regions[region_name]
    start_ip, end_ip = random.choice(ip_ranges)
    
    start_parts = [int(x) for x in start_ip.split('.')]
    end_parts = [int(x) for x in end_ip.split('.')]
    
    ip_parts = []
    for i in range(4):
        if i < 3:
            ip_parts.append(random.randint(start_parts[i], end_parts[i]))
        else:
            ip_parts.append(random.randint(1, 254))
    
    return '.'.join(map(str, ip_parts))


def generate_log_entry(override_ip=None):
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
    
    # Use override IP if in DDoS mode, otherwise generate distributed IP
    client_ip = override_ip if override_ip else generate_distributed_ip()
        
    log_data = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "level": "INFO" if status_code < 400 else ("ERROR" if status_code >= 500 else "WARN"),
        "client_ip": client_ip,
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


def run_log_generator(config: LogGeneratorConfig):
    """Main log generation loop."""
    print("Log generator started", flush=True)
    while True:
        # Check if DDoS simulation is active
        if config.ddos_active and time.time() < config.ddos_end_time:
            # Generate DDoS traffic - many requests from same region
            ddos_ip = generate_ip_from_region(config.ddos_region)
            for _ in range(random.randint(50, 100)):
                log_entry = generate_log_entry(override_ip=ddos_ip)
                print(json.dumps(log_entry), flush=True)
            time.sleep(0.1)  # Short burst interval during DDoS
        elif config.ddos_active and time.time() >= config.ddos_end_time:
            # DDoS simulation ended
            config.ddos_active = False
            config.ddos_region = None
            print(f"DDoS simulation ended", flush=True)
        else:
            # Normal traffic generation
            log_entry = generate_log_entry()
            print(json.dumps(log_entry), flush=True)
            time.sleep(random.uniform(config.min_interval, config.max_interval))
