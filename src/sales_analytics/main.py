import argparse
import logging
from pathlib import Path
from datetime import datetime

from .db import create_in_memory_db
from .loaders import load_all_data
from .analytics import generate_reports
from .config import DEFAULT_REPORTS_DIR


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_REPORTS_DIR
    )
    parser.add_argument(
        "--from-date",
        type=str,
        default=None
    )
    parser.add_argument(
        "--to-date",
        type=str,
        default=None
    )
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO)

    args = parse_args()

    # Create a unique version folder for this execution
    run_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    versioned_output_dir = args.output_dir / run_id

    logging.info(
        "Writing reports to %s",
        versioned_output_dir
    )

    conn = create_in_memory_db()

    load_all_data(conn)

    generate_reports(
        conn,
        output_dir=versioned_output_dir,
        from_date=args.from_date,
        to_date=args.to_date
    )


if __name__ == "__main__":
    main()