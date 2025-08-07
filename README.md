# Proxy Parser

A robust, async proxy parser that scrapes free proxies from GitHub repositories and validates them.

## Features

- **Async HTTP Client**: High-performance async HTTP requests using httpx
- **GitHub Integration**: Searches GitHub for proxy files using various queries
- **Proxy Validation**: Checks proxies against ip-api.com for validity
- **Configurable**: Easy configuration via config.ini
- **Logging**: Comprehensive logging for debugging and monitoring
- **Error Handling**: Robust error handling and recovery
- **Modular Design**: Clean separation of concerns with dedicated modules

## Proxy Support

The parser supports the following proxy types:

- **HTTP/HTTPS proxies**: Fully supported
- **SOCKS5 proxies**: Fully supported via httpx[socks]
- **SOCKS4 proxies**: Not supported (httpx limitation)

SOCKS4 proxies will be automatically skipped during validation with a clear warning message.

## Installation

### Using pip

```bash
pip install -r requirements.txt
```

### Using uv (recommended)

```bash
uv sync
```

## Configuration

Edit `config.ini` to customize the behavior:

```ini
[General]
Timeout = 10
MaxConnections = 10000
SavePath = ./proxies
MainTimeout = 600
ParsingDepth = 7
```

### Configuration Options

- **Timeout**: HTTP request timeout in seconds
- **MaxConnections**: Maximum concurrent connections
- **SavePath**: Directory to save proxy files
- **MainTimeout**: Seconds between parsing cycles
- **ParsingDepth**: Number of GitHub pages to search

## Usage

### Run in infinite mode (default)

```bash
python -m proxy_parser
```

This will continuously:
1. Search GitHub for proxy files
2. Parse proxies from found sources
3. Validate proxies for functionality
4. Save working proxies to `parsed.txt`
5. Wait for the configured timeout before repeating

### Run a single cycle

```bash
python -c "import asyncio; from proxy_parser.__main__ import main; asyncio.run(main())"
```

## Project Structure

```
proxyParser/
├── proxy_parser/
│   ├── __init__.py
│   ├── __main__.py          # Entry point
│   ├── config.py            # Configuration management
│   ├── http_client.py       # HTTP client utilities
│   ├── file_operations.py   # File I/O operations
│   ├── parsers.py           # Proxy parsing logic
│   ├── checkers.py          # Proxy validation
│   └── orchestrator.py      # Main workflow orchestration
├── sources/                 # Source files for different proxy types
│   ├── http.txt
│   ├── https.txt
│   ├── socks4.txt
│   └── socks5.txt
├── tests/                   # Test suite
├── config.ini              # Configuration file
└── README.md
```

## Architecture

The project follows a modular architecture with clear separation of concerns:

- **HTTP Client**: Handles all HTTP requests with proper error handling
- **File Manager**: Manages file operations with error recovery
- **Proxy Parser**: Extracts proxies from various sources
- **Proxy Checker**: Validates proxy functionality
- **Orchestrator**: Coordinates the entire workflow

## Development

### Running Tests

```bash
pytest tests/
```

### Code Quality

The codebase follows Python best practices:
- Type hints throughout
- Comprehensive error handling
- Async/await patterns
- Proper logging
- Unit tests

## Output Files

- `unchecked_proxies.txt`: Raw proxies found from sources
- `parsed.txt`: Validated, working proxies

## Warning

The parser runs in infinite mode by default, which means it will continuously collect and check proxies every cycle as specified in the `MainTimeout` configuration. Use Ctrl+C to stop the process.

## Dependencies

- `httpx[socks]`: Async HTTP client with SOCKS5 support
- `requests`: Synchronous HTTP client for GitHub search
- `beautifulsoup4`: HTML parsing
- `loguru`: Enhanced logging
- `pytest`: Testing framework

## License

This project is open source and available under the MIT License.
