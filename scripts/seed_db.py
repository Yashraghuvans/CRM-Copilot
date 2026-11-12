"""Builds backend/data/demo.db from scratch. Run: python scripts/seed_db.py"""
import sqlite3
from pathlib import Path

path = Path(__file__).parent.parent / "backend" / "data" / "demo.db"
path.parent.mkdir(parents=True, exist_ok=True)
db = sqlite3.connect(path)
db.executescript("""
DROP TABLE IF EXISTS tickets; DROP TABLE IF EXISTS users; DROP TABLE IF EXISTS equipment;
CREATE TABLE users(id INTEGER PRIMARY KEY, name TEXT NOT NULL, role TEXT NOT NULL);
CREATE TABLE equipment(id INTEGER PRIMARY KEY, name TEXT NOT NULL, location TEXT NOT NULL, last_service TEXT NOT NULL);
CREATE TABLE tickets(id INTEGER PRIMARY KEY, assigned_to INTEGER REFERENCES users(id),
  status TEXT NOT NULL, equipment_id INTEGER REFERENCES equipment(id), notes TEXT NOT NULL);
""")
db.executemany("INSERT INTO users VALUES(?,?,?)", [
    (1, "Priya Planner", "planner"), (2, "Sam Supervisor", "supervisor"), (3, "Sara Supervisor", "supervisor"),
    (4, "Tom Tech", "technician"), (5, "Tina Tech", "technician"), (6, "Raj Tech", "technician")])
db.executemany("INSERT INTO equipment VALUES(?,?,?,?)", [
    (1, "X200 router", "Acme HQ", "2025-08-14"), (2, "Y10 switch", "Build Co warehouse", "2025-10-02"),
    (3, "Z5 firewall", "Acme HQ", "2025-03-21"), (4, "AP-300 access point", "Globex lobby", "2025-09-30"),
    (5, "UPS-1500", "Initech server room", "2024-12-11"), (6, "X200 router", "Globex annex", "2025-06-05")])
db.executemany("INSERT INTO tickets VALUES(?,?,?,?,?)", [
    (1, 4, "open", 1, "Router offline since morning, customer Acme escalating"),
    (2, 2, "pending", 2, "Switch port 4 flapping, awaiting customer logs"),
    (3, 5, "open", 3, "Firewall firmware overdue for update"),
    (4, 3, "closed", 4, "Access point replaced, wifi restored"),
    (5, 4, "in_progress", 5, "UPS battery failing self-test, replacement on order"),
    (6, 6, "open", 6, "Router rebooting randomly, suspect power supply"),
    (7, 2, "closed", 1, "Reset router and reconfigured WAN"),
    (8, 3, "pending", 2, "Customer requested on-site visit next Tuesday")])
db.commit()
print({t: db.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in ("users", "equipment", "tickets")})
