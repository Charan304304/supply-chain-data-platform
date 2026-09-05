import pandas as pd
from pathlib import Path
from datetime import datetime


METADATA_DIR = Path("data/metadata")

METADATA_DIR.mkdir(
    parents=True,
    exist_ok=True
)

METADATA_FILE = METADATA_DIR / "ingestion_log.csv"


def log_ingestion(
    filename,
    records,
    status,
    error=None
):

    record = {
        "filename": filename,
        "records": records,
        "status": status,
        "error": error,
        "ingestion_time": datetime.now()
    }

    new_data = pd.DataFrame([record])

    if METADATA_FILE.exists():

        existing = pd.read_csv(
            METADATA_FILE
        )

        result = pd.concat(
            [existing, new_data],
            ignore_index=True
        )

    else:

        result = new_data

    result.to_csv(
        METADATA_FILE,
        index=False
    )