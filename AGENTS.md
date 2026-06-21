# AGENTS.md

## Project

Repository: `https://github.com/romantic0612/ai-data-query-system.git`

This project is based on SQLBot and is deployed as a Docker image on the server.

## Server Deployment Notes

The server already has other services using ports such as `8001`, so this project uses:

- Web: host `18000` -> container `8000`
- MCP/images: host `18001` -> container `8001`

Browser URL:

```bash
http://114.213.146.102:18000
```

## First-Time Clone And Build

```bash
cd /opt
git clone https://github.com/romantic0612/ai-data-query-system.git
cd /opt/ai-data-query-system
docker build -t ai-data-query-system:latest .
```

## Start Container

This command reuses the old SQLBot data directory so model config, datasource config, and PostgreSQL data are kept.

```bash
docker run -d \
  --name ai-data-query-system \
  --restart unless-stopped \
  -p 18000:8000 \
  -p 18001:8001 \
  -e SERVER_IMAGE_HOST=http://114.213.146.102:18001/images/ \
  -v /opt/SQLBot-main/data/sqlbot/excel:/opt/sqlbot/data/excel \
  -v /opt/SQLBot-main/data/sqlbot/file:/opt/sqlbot/data/file \
  -v /opt/SQLBot-main/data/sqlbot/images:/opt/sqlbot/images \
  -v /opt/SQLBot-main/data/sqlbot/logs:/opt/sqlbot/app/logs \
  -v /opt/SQLBot-main/data/postgresql:/var/lib/postgresql/data \
  --privileged=true \
  ai-data-query-system:latest
```

## Check Status

```bash
docker ps | grep ai-data-query-system
docker logs -f ai-data-query-system
```

If the container is not running:

```bash
docker ps -a | grep -E 'ai-data-query-system|sqlbot'
docker logs ai-data-query-system --tail=100
```

If the image is missing:

```bash
docker images | grep ai-data-query-system
```

If no image appears, rebuild:

```bash
cd /opt/ai-data-query-system
git pull
docker build -t ai-data-query-system:latest .
```

## Full Update

Use this when frontend files, Dockerfile, dependencies, or backend files changed.

```bash
cd /opt/ai-data-query-system
git pull
docker build -t ai-data-query-system:latest .
docker stop ai-data-query-system 2>/dev/null || true
docker rm ai-data-query-system 2>/dev/null || true

docker run -d \
  --name ai-data-query-system \
  --restart unless-stopped \
  -p 18000:8000 \
  -p 18001:8001 \
  -e SERVER_IMAGE_HOST=http://114.213.146.102:18001/images/ \
  -v /opt/SQLBot-main/data/sqlbot/excel:/opt/sqlbot/data/excel \
  -v /opt/SQLBot-main/data/sqlbot/file:/opt/sqlbot/data/file \
  -v /opt/SQLBot-main/data/sqlbot/images:/opt/sqlbot/images \
  -v /opt/SQLBot-main/data/sqlbot/logs:/opt/sqlbot/app/logs \
  -v /opt/SQLBot-main/data/postgresql:/var/lib/postgresql/data \
  --privileged=true \
  ai-data-query-system:latest
```

## Backend-Only Fast Update

Only use this when the change is Python backend code and no frontend or dependency changes are needed.

```bash
cd /opt/ai-data-query-system
git pull

docker cp backend/apps/chat/task/llm.py ai-data-query-system:/opt/sqlbot/app/apps/chat/task/llm.py
docker cp backend/apps/chat/models/chat_model.py ai-data-query-system:/opt/sqlbot/app/apps/chat/models/chat_model.py
docker cp backend/apps/chat/api/chat.py ai-data-query-system:/opt/sqlbot/app/apps/chat/api/chat.py

docker restart ai-data-query-system
docker logs -f ai-data-query-system
```

Frontend `.vue` or `.ts` changes require a full Docker build because the running container serves compiled frontend assets from `frontend/dist`.

## API Data Source

API is a backend datasource type, not a chat mode. Users should not need to know whether data comes from MySQL or HTTP API.

In the admin datasource page, add a datasource with type `API`, then paste JSON configuration with an `api_sources` array. During chat, API capabilities are matched before database datasources:

1. The backend first matches the question against API `name`, `description`, `keywords`, `domain`, `intent`, `metrics`, and `dimensions`.
2. If an API capability matches, the backend calls the API and skips SQL generation.
3. If no API capability matches, the backend falls back to the normal datasource selector and SQL flow.
4. Basic natural language parameter extraction is supported for `days`, such as `近7天`.

Documentation:

```bash
docs/API_DATA_SOURCE.md
```

For real school APIs, configure `url`, `method`, `headers`, `params`, and `result_path` in datasource JSON. Secrets can be passed through environment variables, for example:

```yaml
headers:
  Authorization: ${SCHOOL_API_TOKEN}
```

Docker run should then include:

```bash
-e SCHOOL_API_TOKEN="Bearer xxxxxx"
```

## Campus Business System Demo

This repository also contains a small demo business system:

```bash
campus-business-system/
```

It exposes campus APIs for student population, library entries, canteen consumption, and student leave/return data. Run it as a separate container:

```bash
cd /opt/ai-data-query-system
git pull
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

Check it:

```bash
docker ps | grep campus-business-system
curl http://127.0.0.1:18500/health
curl http://127.0.0.1:18500/api/students/undergraduate-count
```

In the AI data query system, add an `API` datasource and paste:

```bash
docs/CAMPUS_BUSINESS_API_DATASOURCE.json
```

Then ask:

```text
普通本科生人数是多少
今日图书馆进馆人数是多少
今日食堂消费金额是多少
学生离返校情况
```

## Common Issues

### Login Redirect After Rebuild

If the app redirects to login and logs show:

```text
Token validation error: Signature verification failed
```

The browser still has an old token. Clear browser storage or log in again:

```js
localStorage.clear()
sessionStorage.clear()
location.reload()
```

### Port Conflict

Check ports:

```bash
ss -tulpen | grep -E ':18000|:18001|:8001'
```

The server has an nginx container using host port `8001`, so do not map SQLBot to host `8001`.

### No Container Or No Image

If `docker ps` shows no `ai-data-query-system` and `docker images` shows no image, rebuild from `/opt/ai-data-query-system` and then run the start command above.
