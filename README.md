# Sunrise/Sunset Calculator

Calculate median sunrise and sunset times for each month of the year.

## Quick Start with Docker

```bash
# Build and run
docker-compose up --build

# Or build manually
docker build -t sunrise-sunset-calculator .
docker run -p 8000:8000 sunrise-sunset-calculator
```

## Usage

Open http://localhost:8000 in your browser and enter a year to see monthly median sunrise/sunset times.
