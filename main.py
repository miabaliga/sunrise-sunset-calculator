from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from datetime import date
from typing import List
import statistics
from astral import LocationInfo
from astral.sun import sun
import pytz

app = FastAPI(title="Sunrise/Sunset Calculator")


class YearRequest(BaseModel):
    year: int
    latitude: float = 40.7128
    longitude: float = -74.0060
    timezone: str = "America/New_York"


class MonthlyMedian(BaseModel):
    month: str
    median_sunrise: str
    median_sunset: str


def calculate_monthly_medians(year: int, lat: float, lon: float, tz_str: str) -> List[MonthlyMedian]:
    location = LocationInfo(latitude=lat, longitude=lon, timezone=tz_str)
    timezone = pytz.timezone(tz_str)

    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    results = []

    for month_num, month_name in enumerate(months, start=1):
        sunrise_times = []
        sunset_times = []

        for day in range(1, 32):
            try:
                day_date = date(year, month_num, day)
                s = sun(location.observer, date=day_date, tz=timezone)
                sunrise_times.append(s["sunrise"])
                sunset_times.append(s["sunset"])
            except ValueError:
                break

        if sunrise_times and sunset_times:
            median_sunrise = statistics.median(sunrise_times)
            median_sunset = statistics.median(sunset_times)

            results.append(MonthlyMedian(
                month=month_name,
                median_sunrise=median_sunrise.strftime("%H:%M:%S"),
                median_sunset=median_sunset.strftime("%H:%M:%S")
            ))

    return results


@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sunrise/Sunset Calculator</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            h1 { color: #333; }
            .form-group { margin: 15px 0; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input { padding: 10px; width: 200px; border: 1px solid #ddd; border-radius: 4px; }
            button { background: #007bff; color: white; padding: 12px 30px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
            button:hover { background: #0056b3; }
            .results { margin-top: 30px; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
            th { background: #f4f4f4; }
            tr:hover { background: #f9f9f9; }
            .error { color: red; margin-top: 10px; }
        </style>
    </head>
    <body>
        <h1>🌅 Sunrise/Sunset Calculator</h1>
        <p>Calculate median sunrise and sunset times for each month of the year.</p>

        <div class="form-group">
            <label for="year">Year:</label>
            <input type="number" id="year" min="1900" max="2100" value="2024">
        </div>

        <div class="form-group">
            <label for="latitude">Latitude (default: New York City):</label>
            <input type="number" id="latitude" step="any" value="40.7128">
        </div>

        <div class="form-group">
            <label for="longitude">Longitude:</label>
            <input type="number" id="longitude" step="any" value="-74.0060">
        </div>

        <div class="form-group">
            <label for="timezone">Timezone:</label>
            <input type="text" id="timezone" value="America/New_York" placeholder="e.g., America/New_York">
        </div>

        <button onclick="calculate()">Calculate</button>

        <div id="error" class="error"></div>
        <div id="results" class="results"></div>

        <script>
            async function calculate() {
                const year = parseInt(document.getElementById('year').value);
                const latitude = parseFloat(document.getElementById('latitude').value);
                const longitude = parseFloat(document.getElementById('longitude').value);
                const timezone = document.getElementById('timezone').value;

                document.getElementById('error').textContent = '';
                document.getElementById('results').innerHTML = 'Loading...';

                try {
                    const response = await fetch('/api/calculate', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ year, latitude, longitude, timezone })
                    });

                    if (!response.ok) {
                        const error = await response.json();
                        throw new Error(error.detail);
                    }

                    const data = await response.json();

                    let html = '<h2>Results for ' + year + '</h2>';
                    html += '<table><thead><tr><th>Month</th><th>Median Sunrise</th><th>Median Sunset</th></tr></thead><tbody>';

                    data.forEach(item => {
                        html += '<tr><td>' + item.month + '</td><td>' + item.median_sunrise + '</td><td>' + item.median_sunset + '</td></tr>';
                    });

                    html += '</tbody></table>';
                    document.getElementById('results').innerHTML = html;
                } catch (error) {
                    document.getElementById('error').textContent = error.message;
                    document.getElementById('results').innerHTML = '';
                }
            }
        </script>
    </body>
    </html>
    """


@app.post("/api/calculate")
async def calculate(request: YearRequest) -> List[MonthlyMedian]:
    try:
        results = calculate_monthly_medians(
            request.year,
            request.latitude,
            request.longitude,
            request.timezone
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
