# API Data Source

API is a backend datasource type. Users do not choose an API mode. They ask questions normally, and the backend routes the question.

The routing strategy is:

1. Match API capabilities first.
2. If an API capability matches, call the API directly.
3. If no API capability matches, fall back to the original datasource selection and SQL query flow.
4. If neither API nor database can answer, the system should later produce a data demand document.

## Capability Catalog

Each API endpoint is treated as one capability. A capability can include both natural language text and structured fields:

```json
{
  "id": "library_entry_trend",
  "name": "图书馆进馆趋势",
  "description": "查询最近 N 天图书馆进馆人数趋势",
  "domain": "library",
  "intent": "trend_query",
  "metrics": ["entry_count", "library_entry_count"],
  "dimensions": ["date"],
  "output": "trend",
  "keywords": ["图书馆进馆趋势", "图书馆近七天", "进馆趋势"],
  "method": "GET",
  "url": "http://114.213.146.102:18500/api/library/entry-trend",
  "params": {
    "days": 7
  },
  "parameters": [
    {
      "name": "days",
      "type": "integer",
      "default": 7,
      "description": "查询最近多少天"
    }
  ],
  "result_path": "data"
}
```

The current implementation uses the system default model to parse the user question into structured intent JSON, then combines that result with rule scoring. If model parsing fails, it falls back to rule/keyword matching.

## Natural Language Parameters

The first version supports model-driven parameter extraction plus a rule fallback for `days`:

- `近7天图书馆进馆趋势`
- `最近30天图书馆进馆人数`
- `近七天图书馆情况`

If the matched API capability has `params.days` or a parameter named `days`, the backend fills `days` from the question or from the model's structured JSON.

## Admin Configuration

Open datasource management, choose `API`, and paste JSON like this:

```json
{
  "api_sources": [
    {
      "id": "undergraduate_count",
      "name": "普通本科生人数",
      "description": "查询学校普通本科生人数统计",
      "domain": "student",
      "intent": "single_metric_query",
      "metrics": ["undergraduate_count", "student_count"],
      "dimensions": ["student_level"],
      "output": "single_value",
      "keywords": ["普通本科生人数", "普通本科生", "本科生人数", "学生人数"],
      "method": "GET",
      "url": "https://school.example.edu/api/students/undergraduate-count",
      "timeout": 15,
      "headers": {
        "Authorization": "${SCHOOL_API_TOKEN}"
      },
      "params": {},
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

## Current Version

- API is now a datasource type in backend configuration.
- API capabilities are matched before database datasource selection.
- Database and Excel datasources remain compatible fallback paths.
- Endpoint matching uses model-parsed intent plus rule/keyword fallback.
- Basic `days` parameter extraction is supported by model output and rule fallback.
- Full vector RAG, permission audit, and complex parameter extraction are future work.
