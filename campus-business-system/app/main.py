import sqlite3
from contextlib import contextmanager
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Query

APP_DIR = Path(__file__).resolve().parent
DATA_DIR = APP_DIR.parent / "data"
DB_PATH = DATA_DIR / "campus_business.db"

app = FastAPI(title="Campus Business System", version="0.1.0")


@contextmanager
def db_conn():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def rows_to_dicts(rows: list[sqlite3.Row]) -> list[dict[str, Any]]:
    return [dict(row) for row in rows]


def response(data: Any, message: str = "success") -> dict[str, Any]:
    return {"code": 0, "message": message, "data": data}


def init_db() -> None:
    with db_conn() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS student_summary (
              student_level TEXT PRIMARY KEY,
              metric_name TEXT NOT NULL,
              student_count INTEGER NOT NULL,
              unit TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS library_entry_daily (
              stat_date TEXT PRIMARY KEY,
              entry_count INTEGER NOT NULL,
              peak_hour TEXT NOT NULL,
              unit TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS canteen_consume_daily (
              stat_date TEXT PRIMARY KEY,
              consume_amount REAL NOT NULL,
              consume_count INTEGER NOT NULL,
              busiest_canteen TEXT NOT NULL,
              unit TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS student_leave_return_daily (
              stat_date TEXT PRIMARY KEY,
              leave_count INTEGER NOT NULL,
              return_count INTEGER NOT NULL,
              not_return_count INTEGER NOT NULL,
              unit TEXT NOT NULL
            );
            """
        )

        exists = conn.execute("SELECT COUNT(*) AS count FROM student_summary").fetchone()["count"]
        if exists:
            return

        conn.executemany(
            """
            INSERT INTO student_summary(student_level, metric_name, student_count, unit)
            VALUES (?, ?, ?, ?)
            """,
            [
                ("普通本科生", "人数", 22634, "人"),
                ("硕士研究生", "人数", 5486, "人"),
                ("博士研究生", "人数", 1382, "人"),
            ],
        )

        today = date.today()
        library_rows = []
        canteen_rows = []
        leave_rows = []
        for index in range(30):
            day = today - timedelta(days=29 - index)
            weekday_factor = 0.82 if day.weekday() >= 5 else 1.0
            library_count = int((2800 + index * 31 + (index % 5) * 180) * weekday_factor)
            consume_count = int((18500 + index * 93 + (index % 6) * 420) * weekday_factor)
            consume_amount = round(consume_count * (13.5 + (index % 4) * 0.8), 2)
            leave_count = int((320 + (index % 7) * 58) * (1.5 if day.weekday() == 4 else 1.0))
            return_count = int((300 + (index % 6) * 62) * (1.4 if day.weekday() == 6 else 1.0))
            not_return_count = max(0, leave_count - return_count // 2)
            library_rows.append((day.isoformat(), library_count, "19:00-20:00", "人次"))
            canteen_rows.append((day.isoformat(), consume_amount, consume_count, "一食堂", "元"))
            leave_rows.append((day.isoformat(), leave_count, return_count, not_return_count, "人"))

        conn.executemany(
            """
            INSERT INTO library_entry_daily(stat_date, entry_count, peak_hour, unit)
            VALUES (?, ?, ?, ?)
            """,
            library_rows,
        )
        conn.executemany(
            """
            INSERT INTO canteen_consume_daily(stat_date, consume_amount, consume_count, busiest_canteen, unit)
            VALUES (?, ?, ?, ?, ?)
            """,
            canteen_rows,
        )
        conn.executemany(
            """
            INSERT INTO student_leave_return_daily(stat_date, leave_count, return_count, not_return_count, unit)
            VALUES (?, ?, ?, ?, ?)
            """,
            leave_rows,
        )


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict[str, Any]:
    return response({"status": "ok", "time": datetime.now().isoformat(timespec="seconds")})


@app.get("/api/students/undergraduate-count")
def undergraduate_count() -> dict[str, Any]:
    with db_conn() as conn:
        row = conn.execute(
            """
            SELECT student_level, metric_name, student_count, unit
            FROM student_summary
            WHERE student_level = ?
            """,
            ("普通本科生",),
        ).fetchone()
    return response(dict(row))


@app.get("/api/students/summary")
def student_summary() -> dict[str, Any]:
    with db_conn() as conn:
        rows = conn.execute(
            """
            SELECT student_level, metric_name, student_count, unit
            FROM student_summary
            ORDER BY student_count DESC
            """
        ).fetchall()
    return response(rows_to_dicts(rows))


@app.get("/api/library/entry-today")
def library_entry_today() -> dict[str, Any]:
    with db_conn() as conn:
        row = conn.execute(
            """
            SELECT stat_date, '今日图书馆进馆人数' AS metric_name, entry_count, peak_hour, unit
            FROM library_entry_daily
            ORDER BY stat_date DESC
            LIMIT 1
            """
        ).fetchone()
    return response(dict(row))


@app.get("/api/library/entry-trend")
def library_entry_trend(days: int = Query(default=7, ge=1, le=30)) -> dict[str, Any]:
    with db_conn() as conn:
        rows = conn.execute(
            """
            SELECT stat_date, entry_count, peak_hour, unit
            FROM library_entry_daily
            ORDER BY stat_date DESC
            LIMIT ?
            """,
            (days,),
        ).fetchall()
    return response(list(reversed(rows_to_dicts(rows))))


@app.get("/api/canteen/consume-today")
def canteen_consume_today() -> dict[str, Any]:
    with db_conn() as conn:
        row = conn.execute(
            """
            SELECT stat_date, '今日食堂消费金额' AS metric_name, consume_amount,
                   consume_count, busiest_canteen, unit
            FROM canteen_consume_daily
            ORDER BY stat_date DESC
            LIMIT 1
            """
        ).fetchone()
    return response(dict(row))


@app.get("/api/canteen/consume-trend")
def canteen_consume_trend(days: int = Query(default=7, ge=1, le=30)) -> dict[str, Any]:
    with db_conn() as conn:
        rows = conn.execute(
            """
            SELECT stat_date, consume_amount, consume_count, busiest_canteen, unit
            FROM canteen_consume_daily
            ORDER BY stat_date DESC
            LIMIT ?
            """,
            (days,),
        ).fetchall()
    return response(list(reversed(rows_to_dicts(rows))))


@app.get("/api/students/leave-return-summary")
def leave_return_summary() -> dict[str, Any]:
    with db_conn() as conn:
        row = conn.execute(
            """
            SELECT stat_date, '学生离返校概况' AS metric_name,
                   leave_count, return_count, not_return_count, unit
            FROM student_leave_return_daily
            ORDER BY stat_date DESC
            LIMIT 1
            """
        ).fetchone()
    return response(dict(row))


@app.get("/api/students/leave-return-trend")
def leave_return_trend(days: int = Query(default=7, ge=1, le=30)) -> dict[str, Any]:
    with db_conn() as conn:
        rows = conn.execute(
            """
            SELECT stat_date, leave_count, return_count, not_return_count, unit
            FROM student_leave_return_daily
            ORDER BY stat_date DESC
            LIMIT ?
            """,
            (days,),
        ).fetchall()
    return response(list(reversed(rows_to_dicts(rows))))
