import re
import os
from pathlib import Path
import pandas as pd
import bibtexparser  #  !!!! v1 API needed at the moment
import requests

INPUT_CSV = "publication-list.csv"
OUTPUT_BIB = "publication-list-biodiverse.bib"

current_directory = os.getcwd()
print("Current Working Directory:", current_directory)

if not os.path.exists(INPUT_CSV):
    print(f"CSV file not found: {INPUT_CSV}")
    exit(1)

df = pd.read_csv(INPUT_CSV)
if "doi" not in df.columns:
    print("The CSV file must have a 'doi' column.")
    exit(1)

df = df[~df['doi'].str.startswith('#')]

with open("bib_no_doi.bib") as bibtex_file:
    bib_database = bibtexparser.load(bibtex_file)
bib_dict = bib_database.entries_dict

with open(OUTPUT_BIB) as bibtex_file:
    bib_database = bibtexparser.load(bibtex_file)
bib_dict2 = bib_database.entries_dict
bib_dict = bib_dict2 | bib_dict

bib_dict_doi = {}
for k, v in bib_dict.items():
    if "doi" in v:
        bib_dict_doi[v["doi"]] = v

has_notes = "note" in df.columns
dois = df["doi"].dropna().astype(str).tolist()
print(f"----- Found {len(dois)} DOIs in {INPUT_CSV} -----")

doi_url_base = "https://doi.org/"
bibtex_entries = []
entry_ids = []
curr_progress_count = 0

for index, row in df.iterrows():
    doi = str(row["doi"]).strip()
    note_value = (
        str(row["note"]).strip() if has_notes and not pd.isna(row["note"]) else ""
    )

    if not doi:
        continue

    if doi.startswith("#"):
        curr_progress_count += 1
        continue

    if note_value.startswith("#"):
        note_value = ""

    fields = {}

    try:
        if doi in bib_dict_doi:
            fields = bib_dict_doi[doi]
        elif doi.startswith("10."):
            response = requests.get(
                doi_url_base + doi,
                headers={"Accept": "application/x-bibtex"},
                timeout=15,
            )
            response.raise_for_status()
            raw_entry = response.content.decode("utf-8").strip()

            m = re.search(r"month=(\w+)", raw_entry)
            if m:
                s = m.group(1)
                raw_entry = raw_entry.replace("month=" + s, "month={" + s + "}")
            b = bibtexparser.loads(raw_entry)
            fields = b.entries[0]
        else:
            fields = bib_dict[doi]

        entry_type = fields["ENTRYTYPE"]
        entry_id = fields["ID"]

        if entry_id in entry_ids:
            entry_id = entry_id + "_" + str(entry_ids.count(entry_id))
            fields["ID"] = entry_id

        clean_fields = {"ENTRYTYPE": entry_type, "ID": entry_id}
        existing_keys = set()
        for key, value in fields.items():
            key = key.lower().strip()
            if key in existing_keys or key in ("entrytype", "id"):
                continue
            value = value.strip().replace("\n", " ")
            existing_keys.add(key)
            if key == "pages":
                pages = re.findall(r"(\d+)", value)
                value = "--".join(pages)
            if key == "title":
                if value[:1] != "{":
                    value = "{" + value + "}"
                #  clean off too many parentheses - assumes balanced
                while value[:2] == "{{":
                    value = value.removeprefix("{").removesuffix("}")

            clean_fields[key] = value

        if note_value and "note" not in existing_keys:
            clean_fields["note"] = note_value

        db = bibtexparser.bibdatabase.BibDatabase()
        db.entries = [clean_fields]
        formatted_entry = bibtexparser.dumps(db).strip()
        entry_ids.append(entry_id)

        bibtex_entries.append(formatted_entry)

        curr_progress_count += 1
        print(f"✅ Processed DOI {doi} [{curr_progress_count}/{len(dois)}]")

    except requests.exceptions.RequestException as e:
        print(f"⚠️ Failed to retrieve BibTeX for {doi}: {e}")

with open(OUTPUT_BIB, "w", encoding="utf-8") as bibfile:
    for entry in bibtex_entries:
        bibfile.write(entry + "\n\n")

print(f"All BibTeX entries saved to '{OUTPUT_BIB}'")

with open(OUTPUT_BIB, "r", encoding="utf-8") as bibfile:
    bib_database = bibtexparser.load(bibfile)

num_entries = len(bib_database.entries)
print(f"The number of entries in {OUTPUT_BIB}: {num_entries}")
print(f"The number of DOIs processed: {len(dois)}")
