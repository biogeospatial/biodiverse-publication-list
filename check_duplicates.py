INPUT_CSV = "publication-list.csv"

seen = set()
duplicate_dois = set()
rows = []

with open(INPUT_CSV, "r") as f:
    for i, line in enumerate(f):
        parts = line.strip().split(",", 1)
        doi = parts[0]
        note = parts[1] if len(parts) > 1 and parts[1] else "NaN"

        if not doi or doi == "doi" or doi.startswith("#"):
            continue

        rows.append((i, doi, note))

        if doi in seen:
            duplicate_dois.add(doi)
        else:
            seen.add(doi)

dup_rows = [(i, doi, note) for i, doi, note in rows if doi in duplicate_dois]

if dup_rows:
    print(f"Found {len(dup_rows)} rows with duplicate DOIs:\n")
    print(f"{'':>6}  {'doi':<30} {'note'}")
    print(f"{'':>6}  {'-'*30} {'-'*10}")
    for i, doi, note in dup_rows:
        print(f"{i:<6}  {doi:<30} {note}")
else:
    print("No duplicate DOIs found.")
