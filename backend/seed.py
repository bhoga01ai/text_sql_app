"""Create data/company.db with 100 synthetic rows in the `dept` table."""

import random
import sqlite3

from app.db import DB_PATH, SCHEMA

random.seed(42)

AREAS = [
    "Engineering", "Finance", "Marketing", "Sales", "Human Resources", "Legal",
    "Operations", "Customer Support", "Research", "Product", "Procurement",
    "Logistics", "Security", "Data Science", "Quality Assurance", "Facilities",
    "Compliance", "Communications", "Design", "IT Infrastructure",
]
QUALIFIERS = [
    "Global", "Regional", "North America", "EMEA", "APAC", "LATAM", "Enterprise",
    "Consumer", "Platform", "Strategic", "Corporate", "Digital",
]
FOCUS = {
    "Engineering": "builds and maintains core software systems",
    "Finance": "manages budgeting, forecasting and financial reporting",
    "Marketing": "drives brand awareness and demand generation",
    "Sales": "owns revenue targets and customer acquisition",
    "Human Resources": "handles hiring, onboarding and employee relations",
    "Legal": "oversees contracts, litigation and regulatory matters",
    "Operations": "keeps day-to-day business processes running smoothly",
    "Customer Support": "resolves customer issues and support tickets",
    "Research": "explores new technologies and long-term innovation",
    "Product": "defines product strategy and roadmaps",
    "Procurement": "sources vendors and negotiates purchasing",
    "Logistics": "coordinates shipping, warehousing and distribution",
    "Security": "protects company assets, data and infrastructure",
    "Data Science": "builds analytics, models and data-driven insights",
    "Quality Assurance": "tests products and enforces quality standards",
    "Facilities": "manages offices, workplace services and real estate",
    "Compliance": "ensures adherence to policies and regulations",
    "Communications": "handles internal and external communications",
    "Design": "creates user experience and visual design",
    "IT Infrastructure": "runs networks, devices and internal IT services",
}
SUFFIX = [
    "for {q} markets.", "across the {q} business.", "with a focus on {q} customers.",
    "supporting {q} initiatives.",
]


def build_rows(n: int = 100) -> list[tuple[str, str, str]]:
    combos = [(q, a) for a in AREAS for q in QUALIFIERS]
    random.shuffle(combos)
    rows = []
    for i, (q, a) in enumerate(combos[:n], start=1):
        name = f"{q} {a}"
        desc = f"The {name} department {FOCUS[a]} " + random.choice(SUFFIX).format(q=q)
        rows.append((f"{i:03d}", name, desc))
    return rows


def main() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    DB_PATH.unlink(missing_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(SCHEMA)
    conn.executemany("INSERT INTO dept (id, name, description) VALUES (?, ?, ?)", build_rows())
    conn.commit()
    count = conn.execute("SELECT COUNT(*) FROM dept").fetchone()[0]
    conn.close()
    print(f"Seeded {count} rows into {DB_PATH}")


if __name__ == "__main__":
    main()
