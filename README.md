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

### 1. Initialize Submodules

This project uses a Git submodule for the traffic generator. After cloning the repository, initialize the submodule:

```bash
# Initialize and clone the submodule
git submodule update --init --recursive
```

If you've already cloned the repository without the `--recursive` flag, run the command above to fetch the submodule content.

### 2. Start the Stack

```bash
docker-compose up -d
```

This will start all services:
- **Elasticsearch** on port 9200
- **Logstash** on ports 5044 (Beats) and 12201 (UDP/GELF)
- **Kibana** on port 5601
- **Traffic Generator** on port 8000 (API)
- **Server Assignment** on port 8100 (API)
- **User Database** on port 8500 (API)
- **Filebeat** (collects logs from user database and server assignment)

### 3. Access Kibana

Open your browser and navigate to:
```
http://localhost:5601
```

Wait a few moments for Kibana to initialize (usually 30-60 seconds).

### 4. Create Data Views

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

### 5. View Logs

1. Go to **Analytics** → **Discover**
2. Select the `webapp-logs-*` index pattern
3. You should see logs flowing in real-time

### 6. Control Traffic Generation (Optional)

The traffic generator provides scripts for controlling log generation. For detailed API documentation, see [fake-traffic-generator/README.md](fake-traffic-generator/README.md).

```bash
# Check API status
curl http://localhost:8000/

# Control traffic generation
./fake-traffic-generator/traffic-start.sh
./fake-traffic-generator/traffic-stop.sh
./fake-traffic-generator/traffic-status.sh
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
- **Features**: User flows, geographic distribution, DDoS simulation
- **API Documentation**: http://localhost:8000/docs
- **Full Documentation**: See [fake-traffic-generator/README.md](fake-traffic-generator/README.md)

### User Database
- **Port**: 8500 (API)
- **Purpose**: Manages up to 100 users for log generation
- **Full Documentation**: See [fake-traffic-generator/README.md](fake-traffic-generator/README.md)

### Server Assignment
- **Port**: 8100 (API)
- **Purpose**: Assigns users to geographic servers
- **Full Documentation**: See [fake-traffic-generator/README.md](fake-traffic-generator/README.md)

### Filebeat
- **Purpose**: Collects logs from User Database service
- **Input**: Reads `/data/user_database.log`
- **Output**: Sends to Logstash on port 5044
- **Index**: Logs are stored in `user-database-logs-*`

## Log Structure

Logs are generated in JSON format and sent via GELF to Logstash. After processing, they are enriched with:
- `client.geo.*` - Geographic information (country, city, coordinates)
- `user_agent.parsed.*` - Parsed browser and OS information

For detailed log structure and examples, see [fake-traffic-generator/README.md](fake-traffic-generator/README.md).

## Traffic Generator API

The traffic generator exposes a REST API on port 8000 for runtime configuration and simulation.

For complete API documentation including all endpoints, parameters, and examples, see [fake-traffic-generator/README.md](fake-traffic-generator/README.md).

**Quick Links:**
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

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
- `metricbeat/metricbeat.yml` - Metricbeat configuration
- `fake-traffic-generator/` - Traffic generation system (Git submodule)
  - See [fake-traffic-generator/README.md](fake-traffic-generator/README.md) for details
- `remove-volumes.sh` - Script to clean up volumes

## Documentation

### Main Documentation
- 📖 `README.md` - This file (main documentation)
- 🚀 `QUICK_REFERENCE.md` - **Quick reference card** (start here!)

### Traffic Generator Documentation
- 🚦 [fake-traffic-generator/README.md](fake-traffic-generator/README.md) - **Traffic generator system documentation**
- 🔄 `USER_FLOWS.md` - User flow system documentation
- 🎯 `METHOD_MAPPING.md` - HTTP method mapping configuration
- 🔗 `SESSION_TRACKING.md` - Session ID tracking and analytics
- 🌍 `SERVER_ASSIGNMENT.md` - Server assignment system and geographic distribution
- 🎮 `TRAFFIC_CONTROL.md` - Traffic control API guide
- 📊 `IMPLEMENTATION_SUMMARY.md` - Complete implementation overview
- 🗂️ `FLOW_SYSTEM_SUMMARY.md` - Flow system technical details
- 👥 `SETUP_USER_DATABASE.md` - User database setup guide

## Customization

### Traffic Generator Customization

For customizing log generation rate, user flows, geographic distribution, and other traffic generator settings, see [fake-traffic-generator/README.md](fake-traffic-generator/README.md).

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

### Traffic Control Scripts
```bash
# Control traffic generation (see fake-traffic-generator/README.md for details)
./fake-traffic-generator/traffic-start.sh
./fake-traffic-generator/traffic-stop.sh
./fake-traffic-generator/traffic-status.sh
./fake-traffic-generator/update-interval.sh <min> <max>
./fake-traffic-generator/simulate-ddos.sh <duration> [region]
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
