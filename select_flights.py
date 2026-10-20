import pyarrow.parquet as pq
from pathlib import Path

keep_cols = [
    "YEAR", "MONTH", "DAY", "DAY_OF_WEEK", "AIRLINE",
    "ORIGIN_AIRPORT", "DESTINATION_AIRPORT", "DISTANCE",
    "SCHEDULED_DEPARTURE", "SCHEDULED_ARRIVAL",
    "DEPARTURE_DELAY", "ARRIVAL_DELAY",
    "AIR_SYSTEM_DELAY", "SECURITY_DELAY", "AIRLINE_DELAY",
    "LATE_AIRCRAFT_DELAY", "WEATHER_DELAY",
    "CANCELLED", "CANCELLATION_REASON", "DIVERTED",
    "TAXI_OUT", "TAXI_IN", "AIR_TIME",
]

src = Path("data/Flight/flights.parquet")
dst = Path("data/Flight/flights_selected.parquet")

pf = pq.ParquetFile(src)
schema = pf.schema_arrow.empty_table().select(keep_cols).schema

rows = 0
with pq.ParquetWriter(dst, schema, compression="snappy") as writer:
    for i, batch in enumerate(pf.iter_batches(batch_size=50_000, columns=keep_cols)):
        writer.write_batch(batch)
        rows += batch.num_rows
        if i % 10 == 0:
            print(f"batch {i}: {rows:,} sətir")

print("Hazırdır:", dst, f"{dst.stat().st_size / 1e6:.1f} MB | cəmi {rows:,} sətir")
