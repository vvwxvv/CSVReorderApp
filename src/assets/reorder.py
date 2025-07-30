"""
CSV Reorder Utility - Production Level Implementation

A robust, class-based CSV reordering utility with comprehensive error handling,
logging, type hints, and production-ready features.
"""

import csv
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, field


@dataclass
class SortColumn:
    """Data class representing a column to sort by."""

    name: str
    is_date: bool = False

    def __post_init__(self):
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("Column name must be a non-empty string")
        self.name = self.name.strip()


@dataclass
class CSVReorderConfig:
    """Configuration class for CSV reordering operations."""

    sort_columns: List[SortColumn]
    reverse: bool = False
    use_language_sorting: bool = False
    language_column: str = "language"
    language_order: List[str] = field(default_factory=lambda: ["EN", "CN"])
    output_prefix: str = "sorted_"
    encoding: str = "utf-8"

    def __post_init__(self):
        if not self.sort_columns:
            raise ValueError("At least one sort column must be specified")

        if self.use_language_sorting and not self.language_column.strip():
            raise ValueError(
                "Language column name cannot be empty when language sorting is enabled"
            )

        if self.use_language_sorting and not self.language_order:
            raise ValueError(
                "Language order cannot be empty when language sorting is enabled"
            )


class CSVReorderError(Exception):
    """Custom exception for CSV reordering errors."""

    pass


class CSVReorder:
    """
    Production-level CSV reordering utility.

    This class provides robust CSV file reordering capabilities with support for:
    - Multiple column sorting with date parsing
    - Language-based sorting
    - Comprehensive error handling and logging
    - Configurable output options
    """

    # Standard date formats to try when parsing dates
    DATE_FORMATS = [
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%Y",
        "%Y-%m",
        "%m-%Y",
        "%m/%d/%Y",
        "%d.%m.%Y",
        "%Y.%m.%d",
    ]

    def __init__(
        self, config: CSVReorderConfig, logger: Optional[logging.Logger] = None
    ):
        """
        Initialize the CSV reorder utility.

        Args:
            config: Configuration object containing reordering parameters
            logger: Optional logger instance. If None, a default logger will be created
        """
        self.config = config
        self.logger = logger or self._setup_default_logger()
        self._validate_config()

    def _setup_default_logger(self) -> logging.Logger:
        """Set up a default logger with appropriate formatting."""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def _validate_config(self) -> None:
        """Validate the configuration object."""
        try:
            # Validate sort columns
            for col in self.config.sort_columns:
                if not isinstance(col, SortColumn):
                    raise ValueError(f"Invalid sort column type: {type(col)}")

            # Validate encoding
            try:
                "test".encode(self.config.encoding)
            except LookupError:
                raise ValueError(f"Invalid encoding: {self.config.encoding}")

        except Exception as e:
            raise CSVReorderError(f"Configuration validation failed: {e}")

    def parse_date(self, date_string: str) -> Union[datetime, str]:
        """
        Attempt to parse a date string using multiple formats.

        Args:
            date_string: String representation of a date

        Returns:
            Parsed datetime object or original string if parsing fails
        """
        if not isinstance(date_string, str) or not date_string.strip():
            return date_string

        date_string = date_string.strip()

        for fmt in self.DATE_FORMATS:
            try:
                return datetime.strptime(date_string, fmt)
            except ValueError:
                continue

        self.logger.warning(f"Could not parse date: '{date_string}'")
        return date_string

    def _validate_csv_columns(self, fieldnames: List[str]) -> None:
        """
        Validate that all required columns exist in the CSV.

        Args:
            fieldnames: List of column names from the CSV file

        Raises:
            CSVReorderError: If required columns are missing
        """
        if not fieldnames:
            raise CSVReorderError("CSV file has no columns")

        # Check sort columns
        sort_column_names = {col.name for col in self.config.sort_columns}
        missing_sort_columns = sort_column_names - set(fieldnames)

        if missing_sort_columns:
            raise CSVReorderError(
                f"Sort columns missing from CSV: {', '.join(missing_sort_columns)}"
            )

        # Check language column if language sorting is enabled
        if (
            self.config.use_language_sorting
            and self.config.language_column not in fieldnames
        ):
            raise CSVReorderError(
                f"Language column '{self.config.language_column}' missing from CSV"
            )

    def _create_sort_key(self, row: Dict[str, Any]) -> Tuple:
        """
        Create a sort key for a CSV row.

        Args:
            row: Dictionary representing a CSV row

        Returns:
            Tuple to be used as sort key
        """
        try:
            key_parts = []

            # Add language sorting if enabled
            if self.config.use_language_sorting:
                lang_value = row.get(self.config.language_column, "").strip()
                try:
                    lang_index = self.config.language_order.index(lang_value)
                except ValueError:
                    lang_index = len(
                        self.config.language_order
                    )  # Unknown languages go last
                key_parts.append(lang_index)

            # Add sort columns
            for sort_col in self.config.sort_columns:
                value = row.get(sort_col.name, "")

                if sort_col.is_date and value:
                    parsed_value = self.parse_date(str(value))
                    key_parts.append(parsed_value)
                else:
                    # For string sorting, convert to lowercase for case-insensitive comparison
                    string_value = str(value).lower() if value else ""
                    key_parts.append(string_value)

            return tuple(key_parts)

        except KeyError as e:
            raise CSVReorderError(f"Column not found in CSV row: {e}")
        except Exception as e:
            raise CSVReorderError(f"Error creating sort key: {e}")

    def _read_csv_file(self, file_path: Path) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        Read and parse the CSV file.

        Args:
            file_path: Path to the CSV file

        Returns:
            Tuple of (fieldnames, data_rows)
        """
        try:
            with open(
                file_path, "r", newline="", encoding=self.config.encoding
            ) as csvfile:
                # Detect delimiter
                sample = csvfile.read(1024)
                csvfile.seek(0)
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter

                reader = csv.DictReader(csvfile, delimiter=delimiter)
                fieldnames = reader.fieldnames

                if not fieldnames:
                    raise CSVReorderError("CSV file has no header row")

                data = list(reader)

            self.logger.info(f"Successfully read {len(data)} rows from {file_path}")
            return fieldnames, data

        except UnicodeDecodeError as e:
            raise CSVReorderError(f"Encoding error reading CSV file: {e}")
        except csv.Error as e:
            raise CSVReorderError(f"CSV parsing error: {e}")
        except Exception as e:
            raise CSVReorderError(f"Error reading CSV file: {e}")

    def _write_csv_file(
        self, file_path: Path, fieldnames: List[str], data: List[Dict[str, Any]]
    ) -> None:
        """
        Write sorted data to a CSV file.

        Args:
            file_path: Output file path
            fieldnames: Column names
            data: Sorted data rows
        """
        try:
            # Ensure output directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(
                file_path, "w", newline="", encoding=self.config.encoding
            ) as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)

            self.logger.info(f"Successfully wrote {len(data)} rows to {file_path}")

        except Exception as e:
            raise CSVReorderError(f"Error writing CSV file: {e}")

    def reorder_csv(
        self, input_file: Union[str, Path], output_directory: Union[str, Path]
    ) -> Optional[Path]:
        """
        Reorder a CSV file based on the configured parameters.

        Args:
            input_file: Path to the input CSV file
            output_directory: Directory to save the sorted CSV file

        Returns:
            Path to the sorted CSV file, or None if an error occurred
        """
        try:
            # Convert to Path objects
            input_path = Path(input_file)
            output_dir = Path(output_directory)

            self.logger.info(f"Starting CSV reordering: {input_path}")

            # Validate input file
            if not input_path.exists():
                raise CSVReorderError(f"Input file not found: {input_path}")

            if not input_path.is_file():
                raise CSVReorderError(f"Input path is not a file: {input_path}")

            # Read CSV file
            fieldnames, data = self._read_csv_file(input_path)

            if not data:
                raise CSVReorderError("The input CSV file contains no data rows")

            # Validate columns
            self._validate_csv_columns(fieldnames)

            # Sort the data
            self.logger.info("Sorting CSV data...")
            sorted_data = sorted(
                data, key=self._create_sort_key, reverse=self.config.reverse
            )

            # Generate output file path
            output_filename = f"{self.config.output_prefix}{input_path.name}"
            output_path = output_dir / output_filename

            # Write sorted data
            self._write_csv_file(output_path, fieldnames, sorted_data)

            self.logger.info(f"CSV reordering completed successfully: {output_path}")
            return output_path

        except CSVReorderError:
            raise
        except Exception as e:
            error_msg = f"Unexpected error during CSV reordering: {e}"
            self.logger.error(error_msg)
            raise CSVReorderError(error_msg)

    def reorder_csv_safe(
        self, input_file: Union[str, Path], output_directory: Union[str, Path]
    ) -> Optional[Path]:
        """
        Safe version of reorder_csv that catches and logs exceptions.

        Args:
            input_file: Path to the input CSV file
            output_directory: Directory to save the sorted CSV file

        Returns:
            Path to the sorted CSV file, or None if an error occurred
        """
        try:
            return self.reorder_csv(input_file, output_directory)
        except CSVReorderError as e:
            self.logger.error(f"CSV reordering failed: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            return None


def create_reorder_config(
    sort_columns: List[Tuple[str, bool]], **kwargs
) -> CSVReorderConfig:
    """
    Convenience function to create a CSVReorderConfig from a list of tuples.

    Args:
        sort_columns: List of (column_name, is_date) tuples
        **kwargs: Additional configuration parameters

    Returns:
        CSVReorderConfig object
    """
    sort_column_objects = [
        SortColumn(name=name, is_date=is_date) for name, is_date in sort_columns
    ]
    return CSVReorderConfig(sort_columns=sort_column_objects, **kwargs)


# Example usage and factory function
def main():
    """Example usage of the CSV reorder utility."""

    # Set up logging
    logging.basicConfig(level=logging.INFO)

    try:
        # Create configuration
        config = create_reorder_config(
            sort_columns=[("year", True), ("title", False)],
            use_language_sorting=True,
            reverse=False,
            output_prefix="reordered_",
        )

        # Create reorder instance
        reorder_util = CSVReorder(config)

        # Perform reordering
        input_file = "Artworks.csv"
        output_directory = "sorted_output"

        result = reorder_util.reorder_csv_safe(input_file, output_directory)

        if result:
            print(f"✅ CSV reordering completed successfully: {result}")
        else:
            print("❌ CSV reordering failed. Check logs for details.")

    except Exception as e:
        print(f"❌ Failed to initialize CSV reorder utility: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
