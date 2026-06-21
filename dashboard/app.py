from flask import Flask, render_template, send_from_directory
import pandas as pd
import os

app = Flask(__name__)

CSV_PATH = "../outputs/violations.csv"
EVIDENCE_FOLDER = "../outputs/evidence"


@app.route("/")
def index():

    if not os.path.exists(CSV_PATH):
        return render_template(
            "index.html",
            records=[],
            total_records=0,
            helmet_count=0,
            triple_count=0,
            unique_vehicles=0
        )

    try:
        df = pd.read_csv(CSV_PATH)

    except Exception:
        df = pd.DataFrame()

    if df.empty:

        return render_template(
            "index.html",
            records=[],
            total_records=0,
            helmet_count=0,
            triple_count=0,
            unique_vehicles=0
        )

    def get_violation_type(row):

        if row["helmet_violation"] and row["triple_violation"]:
            return "Helmet + Triple Riding"

        if row["helmet_violation"]:
            return "Helmet"

        if row["triple_violation"]:
            return "Triple Riding"

        return "Unknown"

    df["violation_type"] = df.apply(get_violation_type, axis=1)

    df = df.sort_values(
        by="timestamp",
        ascending=False
    )

    total_records = len(df)

    helmet_count = int(df["helmet_violation"].sum())

    triple_count = int(df["triple_violation"].sum())

    unique_vehicles = df[
        df["plate_number"] != "UNKNOWN"
    ]["plate_number"].nunique()

    records = df.to_dict("records")

    return render_template(
        "index.html",
        records=records,
        total_records=total_records,
        helmet_count=helmet_count,
        triple_count=triple_count,
        unique_vehicles=unique_vehicles
    )


@app.route("/evidence/<path:filename>")
def evidence(filename):

    return send_from_directory(
        EVIDENCE_FOLDER,
        filename
    )


if __name__ == "__main__":
    app.run(
        debug=True
    )