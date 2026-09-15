# RAG

Retrieval-Augmented Generation project for loading, processing, and indexing
technical documentation.

## Requirements

- Python 3.11

Create and activate a virtual environment, then install the dependencies:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Data layout

Place source files under the relevant product folder in `data/raw/`:

```text
data/
└── raw/
	├── impresora/
	└── vpn/
```

Every file stored in `data/` must follow this naming template:

```text
BRAND-MODEL-FILECATEGORYTYPE
```

Use uppercase letters, separate each component with a hyphen, and do not add
spaces. Include the original file extension after the template when required
by the file format.

Examples:

```text
HP-LASERJET-M404-USERMANUAL.pdf
CISCO-ANYCONNECT-VPNCONFIGURATION.json
TP-LINK-ARCHER-C6-SETUPGUIDE.docx
```

Where:

- `BRAND` is the manufacturer or vendor.
- `MODEL` is the product model or product name.
- `FILECATEGORYTYPE` describes the document content, such as `USERMANUAL`,
  `SETUPGUIDE`, `DATASHEET`, or `VPNCONFIGURATION`.

## Project structure

```text
.
├── data/
│   └── raw/
├── src/
│   ├── core/
│   └── ingestion/
├── main.py
├── requirements.txt
└── README.md
```

## API

Start the Flask server from the project root:

```powershell
python app.py
```

Query the RAG chain with `GET /query`. The `question` parameter is required,
and at least one of `category`, `brand`, or `model` must be provided:

```text
http://127.0.0.1:5000/query?category=impresora&brand=EPSON&model=L355&question=%C2%BFC%C3%B3mo%20puedo%20saber%20si%20el%20nivel%20de%20tinta%20es%20bajo%3F
```

The endpoint returns the generated answer as JSON in the `response` property.
