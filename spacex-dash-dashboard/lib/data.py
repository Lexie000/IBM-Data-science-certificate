from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]  # repo root
DATA_PATH = BASE_DIR / "data" / "dash_dataset.csv"

REQUIRED_COLUMNS = [
    "FlightNumber", "Date", "BoosterVersion", "PayloadMass", "Orbit", "LaunchSite",
    "Outcome", "Flights", "GridFins", "Reused", "Legs", "LandingPad", "Block",
    "ReusedCount", "Serial", "Longitude", "Latitude", "Class"
]

def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)

    missing = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns in CSV: {sorted(missing)}")

    # Clean types
    df["PayloadMass"] = pd.to_numeric(df["PayloadMass"], errors="coerce")
    df["Class"] = pd.to_numeric(df["Class"], errors="coerce")
    df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")
    df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    # Drop rows that break charts
    df = df.dropna(subset=["PayloadMass", "Class", "LaunchSite"])

    # Make sure Class is 0/1 int
    df["Class"] = df["Class"].astype(int)

    return df