from pathlib import Path
from excel_manager import ExcelDB, REQUIRED_SHEETS

path = Path(__file__).resolve().parent.parent / "My_Captain_English_A1.xlsx"
print("Excel:", path)
print("Exists:", path.exists())

if not path.exists():
    raise SystemExit("ПОМИЛКА: Excel не знайдено.")

db = ExcelDB(path)

for sheet in REQUIRED_SHEETS:
    rows = db.read(sheet)
    print(f"{sheet}: {len(rows)} рядків")

print("OK: структура Excel перевірена.")
