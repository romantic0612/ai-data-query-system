# API Data Source

This project supports a first version of API-based question answering.

Use it when a school department does not want to expose database tables directly, but can provide an HTTP API.

## How It Works

When the user selects `API问数`, SQLBot does not generate SQL. Instead, it:

1. Loads API definitions from `backend/templates/api_sources/*.yaml`.
2. Matches the user question with API `name`, `description`, and `keywords`.
3. Calls the matched HTTP API, or uses `mock_response` if no `url` is configured.
4. Normalizes the API result into `fields` and `data`.
5. Returns a compact answer or table in the chat UI.

## API Config Example

```yaml
api_sources:
  - id: undergraduate_count
    name: 普通本科生人数
    description: 查询学校普通本科生人数统计
    keywords:
      - 普通本科生人数
      - 普通本科生
      - 本科生人数
      - 学生人数
    method: GET
    url: https://school.example.edu/api/students/undergraduate-count
    timeout: 15
    headers:
      Authorization: ${SCHOOL_API_TOKEN}
    params:
      campus: main
    result_path: data
    field_mapping:
      student_level: 学生类型
      metric_name: 指标名称
      student_count: 学生人数
      unit: 单位
    raw_answer:
      label_template: "{student_level}{metric_name}"
      value_field: student_count
      unit_field: unit
```

## Environment Variables

Header, param, and body values can reference environment variables:

```yaml
headers:
  Authorization: ${SCHOOL_API_TOKEN}
```

Then start Docker with:

```bash
-e SCHOOL_API_TOKEN="Bearer xxxxxx"
```

## Mock API

For demos, leave `url` empty and configure `mock_response`:

```yaml
url:
mock_response:
  student_level: 普通本科生
  metric_name: 人数
  student_count: 22634
  unit: 人
```

This lets the API data source flow work before the school provides real APIs.

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

```yaml
result_path: data
```

If the API response directly returns the object or list, leave `result_path` empty.

## Current Limitations

- API selection is keyword-based in this first version.
- Complex parameter extraction from natural language is not yet implemented.
- API configuration is file-based YAML, not yet managed from the UI.

Recommended next step: add a visual API data source management page and LLM-based parameter extraction.

