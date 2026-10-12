
import csv
import json
from datetime import datetime
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).resolve().parent
CSV_FILE = BASE_DIR / "setrise.csv"
JSON_FILE = BASE_DIR / "averages.json"


def time_to_minutes(time_text):
    """Convert HH:MM into minutes after midnight."""
    parsed_time = datetime.strptime(time_text, "%H:%M")
    return parsed_time.hour * 60 + parsed_time.minute


def minutes_to_time(minutes):
    """Convert minutes after midnight into HH:MM."""
    minutes = round(minutes) % (24 * 60)
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours:02d}:{mins:02d}"


def build_averages():
    # Each month-day stores all its observed sunrise and sunset times.
    grouped = {}
    seen_dates = set()
    invalid_rows = []

    with CSV_FILE.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        required_columns = {"Date", "Sunrise", "Sunset"}
        if not required_columns.issubset(reader.fieldnames or []):
            raise ValueError(
                "CSV must contain Date, Sunrise, and Sunset columns."
            )

        for line_number, row in enumerate(reader, start=2):
            try:
                # Interpret YY-MM-DD as a date in 2000-2099.
                date = datetime.strptime(row["Date"], "%y-%m-%d").date()

                sunrise = time_to_minutes(row["Sunrise"])
                sunset = time_to_minutes(row["Sunset"])

                if sunset <= sunrise:
                    raise ValueError("Sunset must be later than sunrise.")

                if date in seen_dates:
                    raise ValueError(f"Duplicate date: {date}")

                seen_dates.add(date)

                # Ignore the year when grouping observations.
                key = date.strftime("%m-%d")

                if key not in grouped:
                    grouped[key] = {
                        "sunrise": [],
                        "sunset": [],
                    }

                grouped[key]["sunrise"].append(sunrise)
                grouped[key]["sunset"].append(sunset)

            except (ValueError, TypeError, KeyError) as error:
                invalid_rows.append(
                    f"Line {line_number}: {error}"
                )

    if invalid_rows:
        print("Invalid CSV rows:")
        for error in invalid_rows:
            print(" -", error)
        raise ValueError(
            f"Found {len(invalid_rows)} invalid row(s)."
        )

    # Calculate averages for each month-day.
    averages = {}

    for key, values in sorted(grouped.items()):
        sunrise_average = sum(values["sunrise"]) / len(values["sunrise"])
        sunset_average = sum(values["sunset"]) / len(values["sunset"])

        averages[key] = {
            "sunrise": minutes_to_time(sunrise_average),
            "sunset": minutes_to_time(sunset_average),
        }

    # Save the JSON file.
    with JSON_FILE.open("w", encoding="utf-8") as file:
        json.dump(averages, file, indent=2)
        file.write("\n")

    print(f"CSV records processed: {len(seen_dates)}")
    print(f"Month-day averages created: {len(averages)}")
    print(f"JSON saved to: {JSON_FILE}")

    expected_days = 366
    if len(averages) != expected_days:
        print(
            f"Note: expected {expected_days} month-day entries, "
            f"but found {len(averages)}."
        )


if __name__ == "__main__":
    build_averages()
