import json
from datetime import date
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
JSON_FILE = BASE_DIR / "averages.json"


def main():
    try:
        year = int(input("year: "))
        month = int(input("month: "))
        day = int(input("day: "))

        # Validate the calendar date.
        selected_date = date(year, month, day)

        # Convert the date to a month-day key, such as 01-02.
        key = selected_date.strftime("%m-%d")

        # Read the precomputed averages.
        with JSON_FILE.open("r", encoding="utf-8") as file:
            averages = json.load(file)

        if key not in averages:
            print("No average data available for this date.")
            return

        result = averages[key]

        print()
        print("=" * 32)
        print("       SUNRISE & SUNSET")
        print("=" * 32)
        print(f"Sunrise: {result['sunrise']}")
        print(f"Sunset:  {result['sunset']}")
        print("=" * 32)

    except ValueError:
        print("Invalid date. Please enter a valid year, month, and day.")
    except FileNotFoundError:
        print("averages.json not found. Run build_data.py first.")
    except json.JSONDecodeError:
        print("averages.json is not valid JSON.")


if __name__ == "__main__":
    main()

