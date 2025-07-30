# CSV Reorder App

A modern desktop application for reordering and sorting CSV files with advanced features including multi-column sorting, language-based sorting, and date parsing.

## 🚀 Features

- **Multi-Column Sorting**: Sort by multiple columns simultaneously
- **Date Parsing**: Automatic detection of various date formats
- **Language-Based Sorting**: Prioritize rows by language (EN before CN)
- **Reverse Sorting**: Option to sort in descending order
- **Modern UI**: Drag & drop interface with frameless window design
- **Auto-Detection**: Automatic delimiter and encoding detection

## 📋 Requirements

- Windows 10/11
- Python 3.7+ (for source installation)
- 100MB RAM
- 50MB free space

## 🛠️ Installation

### Option 1: Executable (Recommended)

1. Download the latest release
2. Extract and run `CSVReorderApp.exe`

### Option 2: From Source

```bash
git clone https://github.com/vvwxvv/CSVReorderApp.git
cd CSVReorderApp
python -m venv appenv
appenv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## 🎯 How to Use

1. **Launch** the application
2. **Select CSV File** - Choose your input file
3. **Select Output Directory** - Choose where to save
4. **Enter Sort Columns** - Comma-separated column names (e.g., `name, age, date`)
5. **Set Options**:
   - ✓ Use Language Sorting (prioritize EN over CN)
   - ✓ Reverse Sorting (descending order)
6. **Click "Start Cooking"** to process

## 📁 Supported Formats

- **Delimiters**: Comma, semicolon, tab, pipe
- **Encoding**: UTF-8 with auto-detection
- **Date Formats**: YYYY-MM-DD, DD/MM/YYYY, YYYY, etc.
- **Headers**: Required (first row as column names)

## 🔧 Examples

### Basic Sorting

```
Sort Columns: name, age
Result: Sorted by name, then by age
```

### Date + Language Sorting
```
Sort Columns: date, title
Use Language Sorting: ✓
Result: Sorted by date, then language priority, then title
```

### Reverse Sorting

```
Sort Columns: year, category
Reverse Sorting: ✓
Result: Descending order by year, then category
```

## 🐛 Troubleshooting

- **"No header row"**: Ensure first row contains column names
- **"Missing columns"**: Check column names match exactly (case-sensitive)
- **"Encoding error"**: Save CSV as UTF-8 encoding
- **"Language column missing"**: Add language column when using language sorting

## 📄 License

MIT License - see LICENSE file for details.

---

**Made with ❤️ for efficient CSV data management** 