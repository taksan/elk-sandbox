# ELK Stack with Log Generator

A complete ELK (Elasticsearch, Logstash, Kibana) stack setup with a custom log generator that produces geographically distributed web application logs.

## Overview

This project provides a ready-to-use logging infrastructure that:
- Collects logs using GELF (Graylog Extended Log Format)
- Processes and enriches logs with GeoIP and User-Agent parsing
- Stores logs in Elasticsearch with daily indices
- Visualizes data through Kibana dashboards
- Generates realistic web traffic logs from multiple geographic regions

## Architecture

```
┌─────────────────┐
│  Log Generator  │ ──(GELF/UDP)──┐
└─────────────────┘                │
                                   ▼
┌─────────────────┐         ┌──────────┐         ┌────────────────┐
│     Kibana      │ ◄────── │ Logstash │ ──────► │ Elasticsearch  │
│   (Port 5601)   │         │(Port 5000│         │  (Port 9200)   │
└─────────────────┘         │Port 12201)│        └────────────────┘
                            └──────────┘
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
- **Logstash** on ports 5000 (TCP) and 12201 (UDP/GELF)
- **Kibana** on port 5601
- **Log Generator** (automatically starts generating logs)

### 2. Access Kibana

Open your browser and navigate to:
```
http://localhost:5601
```

Wait a few moments for Kibana to initialize (usually 30-60 seconds).

### 3. Create Index Pattern

1. In Kibana, go to **Management** → **Stack Management** → **Index Patterns**
2. Click **Create index pattern**
3. Enter the pattern: `webapp-logs-*`
4. Click **Next step**
5. Select `@timestamp` as the time field
6. Click **Create index pattern**

### 4. View Logs

1. Go to **Analytics** → **Discover**
2. Select the `webapp-logs-*` index pattern
3. You should see logs flowing in real-time

## Services

### Elasticsearch
- **Port**: 9200
- **Purpose**: Stores and indexes all log data
- **Data Persistence**: Volume `es_data` (persists data between restarts)
- **Health Check**: `http://localhost:9200/_cluster/health`

### Logstash
- **TCP Port**: 5000 (JSON lines input)
- **UDP Port**: 12201 (GELF input)
- **Purpose**: Processes, enriches, and routes logs
- **Features**:
  - GeoIP enrichment for geographic data
  - User-Agent parsing
  - Timestamp normalization
  - JSON parsing for structured logs

### Kibana
- **Port**: 5601
- **Purpose**: Visualization and exploration interface
- **URL**: http://localhost:5601

### Log Generator
- **Purpose**: Generates realistic web application logs
- **Log Format**: JSON with structured fields
- **Geographic Distribution**: 
  - Europe: 20%
  - Asia: 20%
  - South America: 20%
  - Africa: 20%
  - Australia/Oceania: 10%
  - North America: 10%
- **Log Rate**: ~1-5 logs per second (randomized)

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
docker-compose restart log-generator
```

### Rebuild Log Generator
If you modify the log generator code:
```bash
docker-compose up --build -d log-generator
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

If ports 5601, 9200, or 12201 are already in use, modify `docker-compose.yml`:
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
- `logstash/pipeline/logstash.conf` - Logstash pipeline configuration
- `log-generator/generate_logs.py` - Log generation script
- `log-generator/Dockerfile` - Log generator container image
- `remove-volumes.sh` - Script to clean up volumes

## Customization

### Modify Log Generation Rate

Edit `log-generator/generate_logs.py`:
```python
# Change the sleep interval (line ~120)
time.sleep(random.uniform(0.2, 1.5))  # Adjust these values
```

### Add Custom Fields to Logs

Edit `log-generator/generate_logs.py` in the `generate_log_entry()` function to add new fields to the `log_data` dictionary.

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

## License

This project is provided as-is for educational and development purposes.

## Support

For issues or questions, check the logs and ensure all services are running properly using `docker-compose ps` and `docker-compose logs`.
