# Secrets - Delinea Secret Server Client

A Python client library for retrieving credentials from Delinea Secret Server.

## Overview

This project provides a simple interface to interact with the Delinea Secret Server API, allowing you to retrieve secrets, credentials, and TOTP codes programmatically.

#### Delinea Swagger Documentation
Additional information about other APIs not used in this module can be found at:
   - [Full Rest API Docs](https://thycapp.ynhh.org/SecretServer/RestApiDocs.ashx?doc=token-help)
   - [OAuth API Docs](https://thycapp.ynhh.org/SecretServer/RestApiDocs.ashx?doc=oauth-help)

## Requirements

- Python >= 3.10
- [uv](https://docs.astral.sh/uv/) - Fast Python package installer and resolver
- Delinea Secret Server instance with API access

## Installation

1. Clone or download this repository
2. Install uv (if not already installed):
   ```sh
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
3. Install dependencies:
   ```sh
   uv sync
   ```

**Note:** This project includes a [.python-version](.python-version) file, so `uv` will automatically use Python 3.14.

## Configuration

Create a `.env` file in the project root with the following variables:

```env
SSAPP_USERNAME=your_username
SSAPP_PASSWORD=your_password
SSAPP_BASEURL=https://your-delinea-instance.com/
```

**Note:** The `.env` file is gitignored for security.

## Usage

### Basic Example

```python
from secrets import SSCreds

# Retrieve a secret by ID
cred = SSCreds(secret_id=12345)

# Access credential fields
print(f"Username: {cred.ident}")
print(f"Password: {cred.secret}")
print(f"OTP Code: {cred.otp}")
```

### Custom Field Slugs

By default, `SSCreds` looks for `username` and `password` fields. You can specify custom field slugs:

```python
cred = SSCreds(
    secret_id=12345,
    slug_ident="email",
    slug_secret="api_key"
)
```

### Running the Example

Run the interactive example from [main.py](main.py):

```sh
uv run python main.py
```

## Features

- ✅ OAuth2 authentication with token caching
- ✅ Automatic token refresh
- ✅ TOTP/OTP code generation
- ✅ Support for service account secrets
- ✅ Custom field mapping
- ✅ Type hints with Pydantic models

## API Reference

### `SSCreds`

Main class for retrieving secrets from Delinea Secret Server.

**Parameters:**
- `secret_id` (int, required): The ID of the secret to retrieve
- `slug_ident` (str, optional): Field slug for identity/username (default: "username")
- `slug_secret` (str, optional): Field slug for secret/password (default: "password")

**Properties:**
- `ident`: Returns the identity/username value
- `secret`: Returns the secret/password value
- `otp`: Returns the current TOTP code (if configured)

## Dependencies

This project uses `uv` for fast, reliable dependency management. See [pyproject.toml](pyproject.toml) for the full dependency list:
- `httpx` - HTTP client for API requests
- `pydantic` - Data validation and settings management
- `python-dotenv` - Environment variable management

## Development

This project uses `uv` for dependency management. Common commands:

```sh
# Add a new dependency
uv add package-name

# Add a development dependency
uv add --dev package-name

# Update dependencies
uv lock --upgrade

# Run Python scripts
uv run python script.py
```

## License

No specific license has been applied for this repository. It can be used internally and shared with others without restriction.

## Author

John Avitable
Created 03 February 2026
YNHHS Automation Architect