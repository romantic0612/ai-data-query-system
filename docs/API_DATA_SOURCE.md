# API Data Source

This project supports API as a backend datasource type. Users do not choose an "API question answering" mode. They ask questions normally, and the backend decides whether the selected datasource is a database or an API datasource.

## How It Works

1. Admin adds a datasource with type `API`.
2. The datasource configuration stores one or more API endpoints in `api_sources`.
3. During chat, SQLBot selects the most relevant datasource.
4. If the datasource type is `api`, SQLBot skips SQL generation.
5. SQLBot matches the question with API endpoint `name`, `description`, and `keywords`.
6. SQLBot calls the matched HTTP API, or uses `mock_response` when `url` is empty.
7. SQLBot normalizes the API result into `fields` and `data`, then returns a compact answer or table.

## Admin Configuration

Open datasource management, choose `API`, and paste JSON like this:

```json
{
  "api_sources": [
    {
      "id": "undergraduate_count",
      "name": "普通本科生人数",
      "description": "查询学校普通本科生人数统计",
      "keywords": ["普通本科生人数", "普通本科生", "本科生人数", "学生人数"],
      "method": "GET",
      "url": "https://school.example.edu/api/students/undergraduate-count",
      "timeout": 15,
      "headers": {
        "Authorization": "${SCHOOL_API_TOKEN}"
      },
      "params": {
        "campus": "main"
      },
      "result_path": "data",
      "field_mapping": {
        "student_level": "学生类型",
        "metric_name": "指标名称",
        "student_count": "学生人数",
        "unit": "单位"
      },
      "raw_answer": {
        "label_template": "{student_level}{metric_name}",
        "value_field": "student_count",
        "unit_field": "unit"
      }
    }
  ]
}
```

## Environment Variables

Header, param, and body values can reference environment variables:

```json
{
  "headers": {
    "Authorization": "${SCHOOL_API_TOKEN}"
  }
}
```

Then start Docker with:

```bash
-e SCHOOL_API_TOKEN="Bearer xxxxxx"
```

## Mock API

For demos, leave `url` empty and configure `mock_response`:

```json
{
  "url": "",
  "mock_response": {
    "student_level": "普通本科生",
    "metric_name": "人数",
    "student_count": 22634,
    "unit": "人"
  }
}
```

## Result Path

If the API response is:

```json
{
  "code": 0,
  "data": {
    "student_count": 22634,
    "unit": "人"
  }
}
```

Set:

```json
{
  "result_path": "data"
}
```

If the API response directly returns the object or list, leave `result_path` empty.

## Current Version

- API is now a datasource type in backend configuration.
- Chat automatically switches to API execution when the selected datasource type is `api`.
- Endpoint matching is keyword-based.
- Complex natural-language parameter extraction is not yet implemented.
- Multiple endpoints are supported in config, but permission, audit, and parameter forms should be improved later.
