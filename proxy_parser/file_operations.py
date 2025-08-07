"""
File operations for proxy parsing.
"""

from loguru import logger
from pathlib import Path
from typing import Set, List, Dict


class FileManager:
    """Manages file operations for proxy parsing."""

    def __init__(self, sources_path: Path, proxies_path: Path):
        self.sources_path = sources_path
        self.proxies_path = proxies_path
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Ensure required directories exist."""
        self.sources_path.mkdir(exist_ok=True)
        self.proxies_path.mkdir(exist_ok=True)

    def clear_file(self, file_path: Path) -> None:
        """
        Clear contents of a file.

        Args:
            file_path: Path to the file to clear
        """
        try:
            file_path.write_text("")
            logger.debug(f"Cleared file: {file_path}")
        except Exception as e:
            logger.error(f"Error clearing file {file_path}: {e}")

    def append_to_file(self, file_path: Path, content: str) -> None:
        """
        Append content to a file.

        Args:
            file_path: Path to the file
            content: Content to append
        """
        try:
            with file_path.open("a", encoding="utf-8") as file:
                file.write(f"{content}\n")
            logger.debug(f"Appended to file: {file_path}")
        except Exception as e:
            logger.error(f"Error appending to file {file_path}: {e}")

    def append_iterable_to_file(self, file_path: Path, iterable: Set[str]) -> None:
        """
        Append multiple items to a file.

        Args:
            file_path: Path to the file
            iterable: Set of strings to append
        """
        try:
            with file_path.open("a", encoding="utf-8") as file:
                for item in iterable:
                    file.write(f"{item}\n")
            logger.debug(f"Appended {len(iterable)} items to file: {file_path}")
        except Exception as e:
            logger.error(f"Error appending to file {file_path}: {e}")

    def read_lines(self, file_path: Path) -> List[str]:
        """
        Read all lines from a file.

        Args:
            file_path: Path to the file

        Returns:
            List of lines (without newlines)
        """
        try:
            if not file_path.exists():
                logger.warning(f"File does not exist: {file_path}")
                return []

            with file_path.open("r", encoding="utf-8") as file:
                lines = [line.strip() for line in file.readlines()]
                return [line for line in lines if line]  # Remove empty lines
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return []

    def write_lines(self, file_path: Path, lines: List[str]) -> None:
        """
        Write lines to a file.

        Args:
            file_path: Path to the file
            lines: List of strings to write
        """
        try:
            with file_path.open("w", encoding="utf-8") as file:
                for line in lines:
                    file.write(f"{line}\n")
            logger.debug(f"Wrote {len(lines)} lines to file: {file_path}")
        except Exception as e:
            logger.error(f"Error writing to file {file_path}: {e}")

    def clean_duplicates(self, file_path: Path) -> None:
        """
        Remove duplicate lines from a file.

        Args:
            file_path: Path to the file
        """
        try:
            lines = self.read_lines(file_path)
            unique_lines = list(set(lines))
            self.write_lines(file_path, unique_lines)
            removed_count = len(lines) - len(unique_lines)
            if removed_count > 0:
                logger.info(f"Removed {removed_count} duplicate lines from {file_path}")
        except Exception as e:
            logger.error(f"Error cleaning duplicates from {file_path}: {e}")

    def get_files_from_folder(self, folder_path: Path) -> List[Path]:
        """
        Get all .txt files from a folder.

        Args:
            folder_path: Path to the folder

        Returns:
            List of file paths
        """
        try:
            return [
                f for f in folder_path.iterdir() if f.is_file() and f.suffix == ".txt"
            ]
        except Exception as e:
            logger.error(f"Error getting files from folder {folder_path}: {e}")
            return []

    def get_sources_dict(self, sources_list: List[Path]) -> Dict[str, List[str]]:
        """
        Create a dictionary mapping source names to their URLs.

        Args:
            sources_list: List of source file paths

        Returns:
            Dictionary mapping source names to URL lists
        """
        sources_dict = {}
        for source_file in sources_list:
            try:
                source_name = source_file.stem  # Remove .txt extension
                urls = self.read_lines(source_file)
                sources_dict[source_name] = urls
                logger.debug(f"Loaded {len(urls)} URLs from {source_name}")
            except Exception as e:
                logger.error(f"Error processing source file {source_file}: {e}")

        return sources_dict
