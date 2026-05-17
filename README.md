# Publication Website Link

https://biogeospatial.github.io/Biodiverse_publication_list/

# Publication List Explained

This repository includes a collection of scripts designed to generate an HTML publication list from data stored in a CSV file.

Biodiverse publication Workflow (Visualisation of CICD, also can be replicated locally if required. Instructions down further below):

![Biodiverse publication workflow](process-flowchart.png)

The pipeline runs three steps:

1. `fetch_bib.py` reads `publication-list.csv`, fetches BibTeX data for each DOI from CrossRef, and writes `publication-list-biodiverse.bib`.
2. `build_qmd.py` splits the bib into per-year chapters, renders them, and updates `_quarto.yml`.
3. Quarto renders the full book to `docs/`, after which `add_pub_headers.py` injects year-group headers into the HTML.

# Important information

### Updating the csv file `publication-list.csv`:

To add new DOIs, just add the doi as a new line entry into the `publication-list.csv` file. It does not matter what order you add the entry to in the file (Quarto uses Pandoc under the hood to handle citations and bibliography ordering), as long as each DOI entry is on its own line.

#### Column Order:

The CSV file must follow this exact column order:
`doi,note`
It is important you follow this order, where each value is separated by a comma (,). The doi field is required, the note field is optional. If there is no note, just end the line with a comma. An api is called that fetches all the information related to the doi. Hence, there is no manual work required to add all the other information in the csv file. Just the doi is necessary.

#### Missing Values (No note):

If a DOI (or any entry) does not have a value for a particular column, leave that column empty. For example:

`10.1234/abc,`

Here, there is no note field for this entry.

#### Handling Commas in Entries:

If a value itself contains a comma, enclose it in double quotation marks. For example:

`10.1234/abc,"Comma, inbetween"`

#### Signifying a DOI as either a "in press" or "preprint" option

The csv file has a column named note. Add either option "in press" or "preprint" to this column.

### Errors in `fetch_bib.py`

`fetch_bib.py` will print warnings and continue if it encounters any of these three problems:

#### 1. Duplicate DOI
The same DOI or bib key appears more than once in the CSV. The first occurrence is kept, subsequent ones are skipped.
```
⚠️ Skipping duplicate DOI: 10.1111/jbi.15066 (CSV line 250)
```

#### 2. Incorrect bib key
A CSV entry doesn't start with `10.` (so it's treated as a bib key) but no matching entry exists in `bib_no_doi.bib`. Fix by either adding the entry to `bib_no_doi.bib` or correcting the key in the CSV.
```
❗ No bib entry found for key: Gonzalez_Orozco_et_al_2026_SysBot (CSV line 278)
```

#### 3. DOI not found
A valid DOI (starting with `10.`) was not found on CrossRef — either the DOI is wrong or the paper hasn't been registered yet. Fix by correcting the DOI or commenting the line out with `#` until it's available.
```
❗ Failed to retrieve BibTeX for 10.22201/20078706e.2026.97 (CSV line 42): 404 Client Error
```

A summary of all failures is printed at the end of the script.

### What happens if CICD Automation fails

There is two options to this:

#### 1. Manually triggering CICD

The `render-publications.yml` workflow has included: `workflow_dispatch: {}`. This allows you to manually trigger the workflow button in the Actions tab anytime you want without commiting anything.

#### 2. Running Locally

Running it locally should always work. Install dependencies:

```
sudo apt install python3-pip pandoc
pip install mistune pandas bibtexparser requests PyYAML
```

Then run the three steps in order:

```
python3 fetch_bib.py
python3 build_qmd.py
quarto render
python3 add_pub_headers.py docs/all_publications.html
```

The rendered book will be in `docs/`.

## Dependencies

- Python 3.8+
- Quarto
- pandoc

This filter was created following [Quarto's documentation](https://quarto.org/docs/extensions/filters.html#filter-extensions).
