# ELK Stack with Advanced Traffic Generation

A complete ELK (Elasticsearch, Logstash, Kibana) stack with an advanced traffic generator featuring realistic user flows, error simulation, and real-time traffic control.

## Overview

This project provides a ready-to-use logging infrastructure that:
- Collects logs using GELF (Graylog Extended Log Format)
- Processes and enriches logs with GeoIP and User-Agent parsing
- Stores logs in Elasticsearch with daily indices
- Visualizes data through Kibana dashboards
- Generates realistic web traffic logs from multiple geographic regions
- **Simulates realistic user flows and journeys** (browse, purchase, profile checks, etc.)
- **Provides a REST API to control log generation in real-time**
- **Simulates DDoS attacks for testing and demonstration**

## Architecture

```
┌─────────────────────────┐
│   Traffic Generator     │ ──(GELF/UDP)──┐
│  Port 8000 (API)        │                │
└─────────────────────────┘                │
         ▲                                 ▼
         │                          ┌──────────────┐         ┌────────────────┐
    Management API                  │  Logstash    │ ──────► │ Elasticsearch  │
  (update_interval,                 │ Port 5044    │         │  (Port 9200)   │
   simulate_ddos)                   │ Port 12201   │         └────────────────┘
         │                          └──────────────┘                 │
         │                                 ▲                         │
         │                                 │                         ▼
┌─────────────────────────┐                │                  ┌──────────┐
│   User Database         │ ──(logs)──► Filebeat              │  Kibana  │
│  Port 8500 (API)        │                                   │Port 5601 │
└─────────────────────────┘                                   └──────────┘
```

## Prerequisites

- Docker (20.10+)
- Docker Compose (1.29+)
- At least 4GB of available RAM

## Quick Start

### 1. Start the Stack

```bash
docker-compose up -d
```

This will start all services:
- **Elasticsearch** on port 9200
- **Logstash** on ports 5044 (Beats) and 12201 (UDP/GELF)
- **Kibana** on port 5601
- **Traffic Generator** on port 8000 (API)
- **User Database** on port 8500 (API)
- **Filebeat** (collects user database logs)

### 2. Access Kibana

Open your browser and navigate to:
```
http://localhost:5601
```

Wait a few moments for Kibana to initialize (usually 30-60 seconds).

### 3. Create Data Views

**For Web Application Logs:**
1. In Kibana, go to **Management** → **Stack Management** → **Data Views**
2. Click **Create data view**
3. Enter the pattern: `webapp-logs-*`
4. Select `@timestamp` as the time field
5. Click **Save data view**

**For User Database Logs:**
1. Click **Create data view** again
2. Enter the pattern: `user-database-logs-*`
3. Select `@timestamp` as the time field
4. Click **Save data view**

### 4. View Logs

1. Go to **Analytics** → **Discover**
2. Select the `webapp-logs-*` index pattern
3. You should see logs flowing in real-time

### 5. Try the Traffic Generator API (Optional)

Test the management API:
```bash
# Check API status
curl http://localhost:8000/

# Control traffic generation
./traffic-stop.sh       # Stop traffic
./traffic-start.sh      # Start traffic
./traffic-status.sh     # Check status

# Speed up log generation
./update-interval.sh 0.1 0.3

# Simulate a 30-second DDoS attack from Asia
./simulate-ddos.sh 30 Asia
```

## Services

### Elasticsearch
- **Port**: 9200
- **Purpose**: Stores and indexes all log data
- **Data Persistence**: Volume `es_data` (persists data between restarts)
- **Health Check**: `http://localhost:9200/_cluster/health`

### Logstash
- **Beats Port**: 5044 (Filebeat input)
- **UDP Port**: 12201 (GELF input)
- **Purpose**: Processes, enriches, and routes logs
- **Features**:
  - GeoIP enrichment for geographic data
  - User-Agent parsing
  - Timestamp normalization
  - JSON parsing for structured logs
  - Routes logs to different indices based on source

### Kibana
- **Port**: 5601
- **Purpose**: Visualization and exploration interface
- **URL**: http://localhost:5601

### Traffic Generator
- **Port**: 8000 (Management API)
- **Purpose**: Generates realistic web application traffic and logs
- **Log Format**: JSON with structured fields
- **User Management**: Fetches users from User Database service
- **User Flows**: Simulates realistic user journeys (see `USER_FLOWS.md`)
  - Purchase flows
  - Browse-only sessions
  - Profile management
  - Support interactions
  - Abandoned carts
  - 30% random traffic, 70% flow-based
- **Geographic Distribution**: 
  - Europe: 20%
  - Asia: 20%
  - South America: 20%
  - Africa: 20%
  - Australia/Oceania: 10%
  - North America: 10%
- **Log Rate**: ~1-5 logs per second (configurable via API)
- **API Documentation**: http://localhost:8000/docs

### User Database
- **Port**: 8500 (API)
- **Purpose**: Manages up to 100 users for log generation
- **Storage**: Persistent JSON file in Docker volume
- **Logging**: Logs all requests to file for Filebeat collection
- **Endpoints**:
  - `GET /user/random` - Get or create a user
  - `GET /users` - List all users
  - `GET /health` - Health check
  - `POST /users/reset` - Reset all users

### Filebeat
- **Purpose**: Collects logs from User Database service
- **Input**: Reads `/data/user_database.log`
- **Output**: Sends to Logstash on port 5044
- **Index**: Logs are stored in `user-database-logs-*`

## Log Structure

Each generated log entry contains:

```json
{
  "timestamp": "2025-10-15T19:00:00.000Z",
  "level": "INFO",
  "client_ip": "177.123.45.67",
  "user_id": "user_42",
  "http": {
    "request": {
      "method": "GET",
      "referrer": "https://example.com"
    },
    "response": {
      "status_code": 200,
      "bytes": 12345
    },
    "url": "/products/example/1234",
    "version": "1.1"
  },
  "user_agent": {
    "original": "Mozilla/5.0..."
  },
  "message": "GET /products/example/1234 - 200"
}
```

After Logstash processing, additional fields are added:
- `client.geo.*` - Geographic information (country, city, coordinates)
- `user_agent.parsed.*` - Parsed browser and OS information

### User Database Log Structure

User database logs have a simpler structure:

```json
{
  "timestamp": "2025-10-15T19:00:00.000Z",
  "service": "user-database",
  "action": "created_new",
  "user_id": 42,
  "user_name": "John Doe"
}
```

**Actions:**
- `created_new` - A new user was created
- `returned_existing` - An existing user was returned
- `returned_existing_max_reached` - Max users (100) reached, returned existing user

## Traffic Generator API

The traffic generator exposes a REST API on port 8000 for runtime configuration and simulation.

### API Endpoints

#### GET /
Get API status and current configuration.

```bash
curl http://localhost:8000/
```

#### GET /status
Get detailed generator status including DDoS simulation state and active flows.

```bash
curl http://localhost:8000/status
```

#### POST /traffic/start
Start traffic generation.

```bash
curl -X POST http://localhost:8000/traffic/start
# Or use the script
./traffic-start.sh
```

#### POST /traffic/stop
Stop traffic generation.

```bash
curl -X POST http://localhost:8000/traffic/stop
# Or use the script
./traffic-stop.sh
```

#### POST /traffic/pause
Pause traffic generation (alias for stop).

```bash
curl -X POST http://localhost:8000/traffic/pause
```

#### POST /traffic/resume
Resume traffic generation (alias for start).

```bash
curl -X POST http://localhost:8000/traffic/resume
```

#### POST /update_interval
Update the log generation interval (time between log entries).

**Using the shell script:**
```bash
./update-interval.sh <min_interval> <max_interval>

# Example: Generate logs every 0.1 to 0.5 seconds (faster)
./update-interval.sh 0.1 0.5

# Example: Generate logs every 1 to 3 seconds (slower)
./update-interval.sh 1.0 3.0
```

**Using curl directly:**
```bash
curl -X POST http://localhost:8000/update_interval \
  -H "Content-Type: application/json" \
  -d '{"min_interval": 0.1, "max_interval": 0.5}'
```

#### POST /simulate_ddos
Simulate a DDoS attack with thousands of requests from a single region.

**Using the shell script:**
```bash
./simulate-ddos.sh <duration_seconds> [region]

# Example: 30-second DDoS from random region
./simulate-ddos.sh 30

# Example: 60-second DDoS from Asia
./simulate-ddos.sh 60 Asia
```

**Available regions:**
- Europe
- Asia
- South America
- Africa
- Australia
- North America

**Using curl directly:**
```bash
# Random region
curl -X POST http://localhost:8000/simulate_ddos \
  -H "Content-Type: application/json" \
  -d '{"duration_seconds": 30}'

# Specific region
curl -X POST http://localhost:8000/simulate_ddos \
  -H "Content-Type: application/json" \
  -d '{"duration_seconds": 60, "region": "Asia"}'
```

### Interactive API Documentation

FastAPI provides automatic interactive documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Common Operations

### View Logs
```bash
# View all container logs
docker-compose logs

# View specific service logs
docker-compose logs logstash
docker-compose logs log-generator

# Follow logs in real-time
docker-compose logs -f
```

### Stop the Stack
```bash
docker-compose down
```

### Stop and Remove Volumes (Delete All Data)
```bash
# Using the provided script
./remove-volumes.sh

# Or manually
docker-compose down -v
```

### Restart a Specific Service
```bash
docker-compose restart logstash
docker-compose restart traffic-generator
```

### Rebuild Traffic Generator
If you modify the traffic generator code:
```bash
docker-compose up --build -d traffic-generator
```

### Check Service Health
```bash
# Elasticsearch
curl http://localhost:9200/_cluster/health?pretty

# Logstash
curl http://localhost:9600/_node/stats?pretty

# Check running containers
docker-compose ps
```

## Kibana Visualizations

### Suggested Visualizations to Create

1. **Geographic Map**
   - Type: Maps
   - Field: `client.geo.location`
   - Shows traffic distribution across the world

2. **HTTP Status Codes**
   - Type: Pie Chart
   - Field: `http.response.status_code`
   - Shows distribution of response codes

3. **Top URLs**
   - Type: Data Table
   - Field: `http.url`
   - Shows most accessed endpoints

4. **Traffic Over Time**
   - Type: Line Chart
   - X-axis: `@timestamp`
   - Y-axis: Count
   - Shows request volume over time

5. **User Agent Breakdown**
   - Type: Pie Chart
   - Field: `user_agent.parsed.name`
   - Shows browser distribution

## Troubleshooting

### Logs Not Appearing in Kibana

1. Check if log-generator is running:
   ```bash
   docker-compose ps log-generator
   docker-compose logs log-generator
   ```

2. Verify Logstash is receiving logs:
   ```bash
   docker-compose logs logstash | grep "message"
   ```

3. Check Elasticsearch indices:
   ```bash
   curl http://localhost:9200/_cat/indices?v
   ```

### Elasticsearch Won't Start

- Ensure you have enough memory (at least 4GB available)
- Check logs: `docker-compose logs elasticsearch`
- Try increasing Docker memory limit in Docker Desktop settings

### Port Already in Use

If ports 5601, 9200, 5044, 8000, 8500, or 12201 are already in use, modify `docker-compose.yml`:
```yaml
ports:
  - "5602:5601"  # Change host port
```

### Container Keeps Restarting

Check the logs for the specific container:
```bash
docker-compose logs <service-name>
```

## Configuration Files

- `docker-compose.yml` - Service definitions and configuration
- `user_flows.yml` - **User flow definitions** (customize user journeys)
- `logstash/pipeline/logstash.conf` - Logstash pipeline configuration
- `filebeat/filebeat.yml` - Filebeat configuration
- `traffic-generator/` - Traffic generation service
  - `traffic_generator.py` - Core log generation logic
  - `flow_manager.py` - User flow state machine manager
  - `api.py` - FastAPI application for management
  - `Dockerfile` - Traffic generator container image
  - `requirements.txt` - Python dependencies
- `user-database/app.py` - User database Flask application
{{ ... }}
- `user-database/requirements.txt` - User database Python dependencies
- `remove-volumes.sh` - Script to clean up volumes
- `traffic-start.sh` - Script to start traffic generation
- `traffic-stop.sh` - Script to stop traffic generation
- `traffic-status.sh` - Script to check traffic status
- `update-interval.sh` - Script to update log generation interval
- `simulate-ddos.sh` - Script to simulate DDoS attacks

## Documentation

- 📖 `README.md` - This file (main documentation)
- 🚀 `QUICK_REFERENCE.md` - **Quick reference card** (start here!)
- 🔄 `USER_FLOWS.md` - User flow system documentation
- 🎯 `METHOD_MAPPING.md` - HTTP method mapping configuration
- 🎮 `TRAFFIC_CONTROL.md` - Traffic control API guide
- 📊 `IMPLEMENTATION_SUMMARY.md` - Complete implementation overview
- 🗂️ `FLOW_SYSTEM_SUMMARY.md` - Flow system technical details
- 👥 `SETUP_USER_DATABASE.md` - User database setup guide

## Customization

### Modify Log Generation Rate

**Recommended: Use the API** (no restart required):
```bash
./update-interval.sh 0.1 0.5
```

**Alternative: Edit code** (requires rebuild):
Edit `log-generator/log_generator.py` and change the default values in the `LogGeneratorConfig` class:
```python
class LogGeneratorConfig:
    def __init__(self):
        self.min_interval = 0.2  # Change these
        self.max_interval = 1.5  # Change these
```
Then rebuild: `docker-compose up --build -d log-generator`

### Add Custom Fields to Logs

Edit `log-generator/log_generator.py` in the `generate_log_entry()` function to add new fields to the `log_data` dictionary.

### Change Index Pattern

Edit `logstash/pipeline/logstash.conf`:
```ruby
output {
  elasticsearch {
    hosts => ["http://elasticsearch:9200"]
    index => "my-custom-logs-%{+YYYY.MM.dd}"  # Change this
  }
}
```

### Adjust Geographic Distribution

Edit the `ip_ranges` list in `log-generator/generate_logs.py` to add/remove IP ranges for different regions.

## Data Retention

By default, logs are stored indefinitely. To implement retention policies:

1. Use Elasticsearch Index Lifecycle Management (ILM)
2. Or manually delete old indices:
   ```bash
   curl -X DELETE "http://localhost:9200/webapp-logs-2025.10.01"
   ```

## Performance Tuning

### For Production Use

1. **Increase Elasticsearch heap size** in `docker-compose.yml`:
   ```yaml
   environment:
     - ES_JAVA_OPTS=-Xms2g -Xmx2g  # Increase from 1g
   ```

2. **Add Elasticsearch replicas** for high availability

3. **Use persistent volumes** for production data

4. **Enable security** (X-Pack) in Elasticsearch

## Quick Reference

### Essential Commands
```bash
# Start the stack
docker-compose up -d

# Stop the stack
docker-compose down

# View logs
docker-compose logs -f

# Rebuild traffic generator
docker-compose up --build -d traffic-generator

# Remove all data
./remove-volumes.sh
```

### Management Scripts
```bash
# Control traffic generation
./traffic-start.sh      # Start/resume traffic generation
./traffic-stop.sh       # Stop/pause traffic generation
./traffic-status.sh     # Check current status

# Update log generation speed
./update-interval.sh <min> <max>

# Simulate DDoS attack
./simulate-ddos.sh <duration> [region]
```

### API Endpoints
- **Traffic Generator API**: http://localhost:8000/docs
- **User Database API**: http://localhost:8500/health
- **Kibana**: http://localhost:5601
- **Elasticsearch**: http://localhost:9200

### Useful Queries
```bash
# Check Elasticsearch health
curl http://localhost:9200/_cluster/health?pretty

# List indices
curl http://localhost:9200/_cat/indices?v

# Check traffic generator status
curl http://localhost:8000/status

# Check user database
curl http://localhost:8500/users

# Count user database logs
curl http://localhost:9200/user-database-logs-*/_count
```

## License

This project is provided as-is for educational and development purposes.

## Support

For issues or questions, check the logs and ensure all services are running properly using `docker-compose ps` and `docker-compose logs`.
