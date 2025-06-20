import json
from pathlib import Path
from flask import Flask, render_template_string, abort

app = Flask(__name__)

# Correctly locate the project root relative to the script's location.
# This script is in scripts/testing/, so the project root is two levels up.
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CI_OUTPUT_DIR = PROJECT_ROOT / '.ci_output'
REPORTS_DIR = CI_OUTPUT_DIR / 'reports'

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; margin: 0; padding: 2rem; background: #f7f7f7; color: #333; }
        .container { max-width: 1200px; margin: auto; background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
        h1, h2 { color: #111; border-bottom: 2px solid #eee; padding-bottom: 10px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem; margin-top: 2rem; }
        .card { background: #fafafa; padding: 1.5rem; border-radius: 6px; box-shadow: 0 2px 6px rgba(0,0,0,0.05); }
        .card h3 { margin-top: 0; color: #333; }
        .status-passed { color: #28a745; }
        .status-failed { color: #dc3545; }
        .status-skipped { color: #ffc107; }
        ul { list-style-type: none; padding: 0; }
        li { background: #fff; padding: 10px; border: 1px solid #ddd; border-radius: 4px; margin-bottom: 8px; }
        .report-link { display: block; margin-top: 1rem; }
    </style>
</head>
<body>
    <div class="container">
        <h1>FreeAgentics Test Dashboard</h1>

        <h2>Overall Summary</h2>
        <div class="grid">
            <div class="card">
                <h3>Total Tests</h3>
                <p>{{ summary.total_tests }}</p>
            </div>
            <div class="card">
                <h3>Pass Rate</h3>
                <p class="status-passed">{{ "%.2f"|format(summary.pass_rate * 100) }}%</p>
            </div>
            <div class="card">
                <h3>Code Coverage</h3>
                <p>{{ "%.2f"|format(summary.overall_coverage) }}%</p>
            </div>
            <div class="card">
                <h3>Quality Score</h3>
                <p>{{ "%.1f"|format(summary.quality_score) }}/100</p>
            </div>
        </div>

        <h2>Test Suites</h2>
        <div class="grid">
            {% for suite, results in detailed_results.items() %}
            <div class="card">
                <h3>{{ suite }}</h3>
                <ul>
                    <li>Passed: <span class="status-passed">{{ results.passed }}</span></li>
                    <li>Failed: <span class="status-failed">{{ results.failed }}</span></li>
                    <li>Skipped: <span class="status-skipped">{{ results.skipped }}</span></li>
                    <li>Duration: {{ "%.2f"|format(results.duration) }}s</li>
                </ul>
            </div>
            {% endfor %}
        </div>

        <div class="grid">
            <div class="card">
                <h2>Tests Over Time</h2>
                <canvas id="testsOverTimeChart"></canvas>
            </div>
            <div class="card">
                <h2>Coverage Over Time</h2>
                <canvas id="coverageOverTimeChart"></canvas>
            </div>
        </div>

        <a href="/report.html" class="report-link" target="_blank">View Full HTML Report</a>
    </div>

    <script>
        const historicalData = {{ historical_data|tojson }};
        const labels = historicalData.map(d => new Date(d.timestamp).toLocaleString());

        // Tests Over Time Chart
        const testsCtx = document.getElementById('testsOverTimeChart').getContext('2d');
        new Chart(testsCtx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Passed',
                        data: historicalData.map(d => d.summary.passed),
                        borderColor: '#28a745',
                        backgroundColor: 'rgba(40, 167, 69, 0.1)',
                        fill: true,
                    },
                    {
                        label: 'Failed',
                        data: historicalData.map(d => d.summary.failed),
                        borderColor: '#dc3545',
                        backgroundColor: 'rgba(220, 53, 69, 0.1)',
                        fill: true,
                    }
                ]
            },
            options: { responsive: true, scales: { y: { beginAtZero: true } } }
        });

        // Coverage Over Time Chart
        const coverageCtx = document.getElementById('coverageOverTimeChart').getContext('2d');
        new Chart(coverageCtx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Coverage (%)',
                    data: historicalData.map(d => d.summary.overall_coverage),
                    borderColor: '#007bff',
                    backgroundColor: 'rgba(0, 123, 255, 0.1)',
                    fill: true,
                }]
            },
            options: { responsive: true, scales: { y: { beginAtZero: true, max: 100 } } }
        });
    </script>
</body>
</html>
"""

def get_historical_data():
    """Loads all JSON reports from the reports directory, sorted by timestamp."""
    history = []
    if not REPORTS_DIR.exists():
        return history

    report_files = sorted(REPORTS_DIR.glob('test_report_*.json'), key=lambda p: p.stat().st_mtime)
    for report_file in report_files:
        try:
            with open(report_file, 'r') as f:
                history.append(json.load(f))
        except (json.JSONDecodeError, IOError):
            # Skip corrupted or unreadable files
            continue
    return history

@app.route('/')
def dashboard():
    """Serves the main dashboard."""
    historical_data = get_historical_data()
    if not historical_data:
        return "No test reports found. Please run the baseline reporting script first.", 404

    latest_report = historical_data[-1]

    return render_template_string(
        HTML_TEMPLATE,
        summary=latest_report['summary'],
        detailed_results=latest_report['detailed_results'],
        historical_data=historical_data
    )

@app.route('/report.html')
def full_report():
    """Serves the latest full HTML report."""
    html_report_path = REPORTS_DIR / 'test_report.html'
    if not html_report_path.exists():
        abort(404, "HTML report not found.")
    return html_report_path.read_text()

if __name__ == '__main__':
    print(f"Serving dashboard. CI Output directory: {CI_OUTPUT_DIR}")
    print(f"Expecting reports in: {REPORTS_DIR}")
    app.run(debug=True, port=5001)
