# Scrape Goat

A robust Twitter scraping tool that uses Tor for anonymous and distributed data collection. This tool specializes in checking account suspension status and handling rate limits through Tor circuit rotation.

## Features

- Anonymous scraping using Tor network
- Automatic Tor identity rotation
- Rate limit handling
- Support for both requests and browser-based scraping
- MongoDB integration for data storage
- Random header generation for request anonymization

## Prerequisites

- Python 3.x
- Tor service installed
- MongoDB (optional)

## Installation

1. Clone the repository
2. Install Python dependencies:
```bash
pip install -r requirements.txt
```
3. Make sure Tor is installed on your system
4. Create a `.env` file with your MongoDB connection string:
```
PYMONGO_CLI_URI=your_mongodb_connection_string
```

## Components

- `tor_scraper.py`: Core scraping functionality with Tor integration
- `setup_tor.py`: Tor configuration and process management
- `author_id_to_suspension.py`: Twitter account suspension checker
- `utils.py`: Helper functions for data management

## Usage

1. Place Twitter user IDs in `user_ids.txt` (one ID per line)
2. Run the suspension checker:
```bash
python author_id_to_suspension.py
```

## Data Storage

- Suspension data is stored in `suspension_data.json`
- MongoDB integration available for tweet and author data

## Safety Features

- Automatic circuit rotation
- Random user agents and headers
- Request rate limiting
- Multiple retry attempts

## License

MIT License