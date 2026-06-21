# Campus Business System Demo

This is a small campus business system used to demonstrate API integration with the AI data query system.

It owns its own SQLite database and exposes HTTP APIs for common school scenarios:

- student population
- library entry traffic
- canteen consumption
- student leave/return status

## Local Run

```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8500
```

Open:

```bash
http://127.0.0.1:8500/docs
```

## Docker Run

```bash
cd /opt/ai-data-query-system/campus-business-system
docker build -t campus-business-system:latest .
docker stop campus-business-system 2>/dev/null || true
docker rm campus-business-system 2>/dev/null || true
docker run -d \
  --name campus-business-system \
  --restart unless-stopped \
  -p 18500:8500 \
  -v /opt/ai-data-query-system/campus-business-system/data:/app/data \
  campus-business-system:latest
```

Check:

```bash
curl http://127.0.0.1:18500/health
curl http://127.0.0.1:18500/api/students/undergraduate-count
```

## AI Data Query System API Datasource

In the AI data query system, create an `API` datasource and paste the JSON from:

```bash
docs/CAMPUS_BUSINESS_API_DATASOURCE.json
```

If the AI data query system container calls this service through host mapping, use:

```text
http://114.213.146.102:18500
```
