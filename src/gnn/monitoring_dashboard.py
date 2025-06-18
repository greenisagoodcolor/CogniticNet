"""
Monitoring Dashboard for GNN Processing

This module provides a web-based dashboard for real-time monitoring
and visualization of GNN processing statistics.
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import threading
from pathlib import Path

try:
    from flask import Flask, render_template_string, jsonify, request
    from flask_cors import CORS
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

from .monitoring import get_monitor, get_logger
from .metrics_collector import get_metrics_collector

# Configure logger
logger = get_logger().logger


class MonitoringDashboard:
    """
    Web-based monitoring dashboard for GNN processing.

    Provides real-time visualization of:
    - Processing statistics
    - Performance metrics
    - System resource usage
    - Error tracking
    """

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 5000,
        update_interval: int = 5
    ):
        """
        Initialize monitoring dashboard.

        Args:
            host: Dashboard host address
            port: Dashboard port
            update_interval: Update interval in seconds
        """
        if not FLASK_AVAILABLE:
            raise ImportError("Flask is required for the monitoring dashboard")

        self.host = host
        self.port = port
        self.update_interval = update_interval

        # Initialize Flask app
        self.app = Flask(__name__)
        CORS(self.app)

        # Get monitoring instances
        self.monitor = get_monitor()
        self.collector = get_metrics_collector()

        # Setup routes
        self._setup_routes()

        # Background update thread
        self._running = False
        self._update_thread = None

    def _setup_routes(self):
        """Setup Flask routes"""

        @self.app.route('/')
        def index():
            """Dashboard homepage"""
            return render_template_string(DASHBOARD_HTML)

        @self.app.route('/api/stats/realtime')
        def realtime_stats():
            """Get real-time statistics"""
            stats = {
                'performance': self.monitor.get_statistics(),
                'metrics': self.collector.get_real_time_stats(),
                'timestamp': datetime.utcnow().isoformat()
            }
            return jsonify(stats)

        @self.app.route('/api/stats/historical')
        def historical_stats():
            """Get historical statistics"""
            # Get query parameters
            hours = int(request.args.get('hours', 24))
            group_by = request.args.get('group_by', 'hour')

            start_time = datetime.utcnow() - timedelta(hours=hours)

            stats = self.collector.db.get_aggregated_stats(
                start_time=start_time,
                group_by=group_by
            )

            return jsonify(stats)

        @self.app.route('/api/metrics/graphs')
        def graph_metrics():
            """Get recent graph processing metrics"""
            limit = int(request.args.get('limit', 100))

            metrics = self.collector.db.query_graph_metrics(limit=limit)
            return jsonify(metrics)

        @self.app.route('/api/system/resources')
        def system_resources():
            """Get system resource usage"""
            # Get system metrics from monitor
            system_stats = self.monitor.get_statistics('_system')

            return jsonify({
                'cpu': {
                    'current': system_stats.get('cpu_percent', {}).get('mean', 0),
                    'max': system_stats.get('cpu_percent', {}).get('max', 0)
                },
                'memory': {
                    'current': system_stats.get('memory_mb', {}).get('mean', 0),
                    'max': system_stats.get('memory_mb', {}).get('max', 0)
                },
                'gpu': {
                    'memory': system_stats.get('gpu_memory_mb', {}).get('mean', 0) if 'gpu_memory_mb' in system_stats else None
                }
            })

        @self.app.route('/api/alerts')
        def get_alerts():
            """Get recent alerts"""
            # This would be enhanced with actual alert storage
            return jsonify([])

    def start(self):
        """Start the dashboard"""
        self._running = True

        # Start Flask app in a separate thread
        import werkzeug.serving

        def run_app():
            werkzeug.serving.run_simple(
                self.host,
                self.port,
                self.app,
                use_reloader=False,
                use_debugger=False
            )

        app_thread = threading.Thread(target=run_app)
        app_thread.daemon = True
        app_thread.start()

        logger.info(f"Monitoring dashboard started at http://{self.host}:{self.port}")

    def stop(self):
        """Stop the dashboard"""
        self._running = False
        logger.info("Monitoring dashboard stopped")


# HTML template for the dashboard
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GNN Processing Monitor</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: #f5f5f5;
            color: #333;
        }

        .header {
            background-color: #2c3e50;
            color: white;
            padding: 1rem 2rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }

        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }

        .metric-card {
            background: white;
            border-radius: 8px;
            padding: 1.5rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .metric-card h3 {
            font-size: 0.875rem;
            color: #666;
            margin-bottom: 0.5rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        .metric-value {
            font-size: 2rem;
            font-weight: 600;
            color: #2c3e50;
        }

        .metric-unit {
            font-size: 0.875rem;
            color: #666;
            margin-left: 0.25rem;
        }

        .chart-container {
            background: white;
            border-radius: 8px;
            padding: 1.5rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 1.5rem;
        }

        .chart-container h3 {
            font-size: 1.125rem;
            margin-bottom: 1rem;
            color: #2c3e50;
        }

        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 0.5rem;
        }

        .status-healthy { background-color: #27ae60; }
        .status-warning { background-color: #f39c12; }
        .status-error { background-color: #e74c3c; }

        .table-container {
            background: white;
            border-radius: 8px;
            padding: 1.5rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            overflow-x: auto;
        }

        table {
            width: 100%;
            border-collapse: collapse;
        }

        th, td {
            text-align: left;
            padding: 0.75rem;
            border-bottom: 1px solid #eee;
        }

        th {
            font-weight: 600;
            color: #666;
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        tr:hover {
            background-color: #f8f9fa;
        }

        .refresh-indicator {
            position: fixed;
            top: 1rem;
            right: 1rem;
            background: #27ae60;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 4px;
            font-size: 0.875rem;
            opacity: 0;
            transition: opacity 0.3s;
        }

        .refresh-indicator.active {
            opacity: 1;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>GNN Processing Monitor</h1>
    </div>

    <div class="container">
        <!-- Real-time Metrics -->
        <div class="metrics-grid">
            <div class="metric-card">
                <h3>Total Graphs Processed</h3>
                <div class="metric-value" id="total-graphs">0</div>
            </div>

            <div class="metric-card">
                <h3>Success Rate</h3>
                <div class="metric-value">
                    <span id="success-rate">0</span><span class="metric-unit">%</span>
                </div>
            </div>

            <div class="metric-card">
                <h3>Avg Processing Time</h3>
                <div class="metric-value">
                    <span id="avg-time">0</span><span class="metric-unit">ms</span>
                </div>
            </div>

            <div class="metric-card">
                <h3>System Status</h3>
                <div class="metric-value">
                    <span class="status-indicator status-healthy"></span>
                    <span style="font-size: 1.25rem;">Healthy</span>
                </div>
            </div>
        </div>

        <!-- Performance Chart -->
        <div class="chart-container">
            <h3>Processing Performance (Last 24 Hours)</h3>
            <canvas id="performance-chart" height="80"></canvas>
        </div>

        <!-- Resource Usage Charts -->
        <div class="metrics-grid">
            <div class="chart-container">
                <h3>CPU Usage</h3>
                <canvas id="cpu-chart" height="100"></canvas>
            </div>

            <div class="chart-container">
                <h3>Memory Usage</h3>
                <canvas id="memory-chart" height="100"></canvas>
            </div>
        </div>

        <!-- Recent Operations Table -->
        <div class="table-container">
            <h3>Recent Operations</h3>
            <table id="operations-table">
                <thead>
                    <tr>
                        <th>Time</th>
                        <th>Graph ID</th>
                        <th>Nodes</th>
                        <th>Edges</th>
                        <th>Model</th>
                        <th>Duration</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody id="operations-tbody">
                    <!-- Populated by JavaScript -->
                </tbody>
            </table>
        </div>
    </div>

    <div class="refresh-indicator" id="refresh-indicator">
        Updating...
    </div>

    <script>
        // Chart configurations
        const chartOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        };

        // Initialize charts
        const performanceChart = new Chart(
            document.getElementById('performance-chart').getContext('2d'),
            {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Processing Time',
                        data: [],
                        borderColor: '#3498db',
                        backgroundColor: 'rgba(52, 152, 219, 0.1)',
                        tension: 0.4
                    }]
                },
                options: chartOptions
            }
        );

        const cpuChart = new Chart(
            document.getElementById('cpu-chart').getContext('2d'),
            {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'CPU %',
                        data: [],
                        borderColor: '#e74c3c',
                        backgroundColor: 'rgba(231, 76, 60, 0.1)',
                        tension: 0.4
                    }]
                },
                options: {
                    ...chartOptions,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100
                        }
                    }
                }
            }
        );

        const memoryChart = new Chart(
            document.getElementById('memory-chart').getContext('2d'),
            {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Memory MB',
                        data: [],
                        borderColor: '#27ae60',
                        backgroundColor: 'rgba(39, 174, 96, 0.1)',
                        tension: 0.4
                    }]
                },
                options: chartOptions
            }
        );

        // Update functions
        async function updateRealTimeStats() {
            try {
                const response = await fetch('/api/stats/realtime');
                const data = await response.json();

                // Update metric cards
                const metrics = data.metrics;
                if (metrics && metrics.counters) {
                    document.getElementById('total-graphs').textContent =
                        metrics.counters.total_graphs || 0;

                    const successRate = metrics.counters.successful_operations /
                        (metrics.counters.successful_operations + metrics.counters.failed_operations) * 100;
                    document.getElementById('success-rate').textContent =
                        isNaN(successRate) ? 0 : successRate.toFixed(1);
                }

                if (metrics && metrics.timers && metrics.timers.processing_times) {
                    const avgTime = metrics.timers.processing_times.mean * 1000; // Convert to ms
                    document.getElementById('avg-time').textContent = avgTime.toFixed(0);
                }

                // Show refresh indicator
                const indicator = document.getElementById('refresh-indicator');
                indicator.classList.add('active');
                setTimeout(() => indicator.classList.remove('active'), 500);

            } catch (error) {
                console.error('Error updating real-time stats:', error);
            }
        }

        async function updateHistoricalData() {
            try {
                const response = await fetch('/api/stats/historical?hours=24&group_by=hour');
                const data = await response.json();

                if (data && data.length > 0) {
                    // Update performance chart
                    const labels = data.map(d => {
                        const date = new Date(d.period);
                        return date.toLocaleTimeString([], { hour: '2-digit' });
                    }).reverse();

                    const avgTimes = data.map(d => d.avg_processing_time * 1000).reverse();

                    performanceChart.data.labels = labels;
                    performanceChart.data.datasets[0].data = avgTimes;
                    performanceChart.update();
                }
            } catch (error) {
                console.error('Error updating historical data:', error);
            }
        }

        async function updateSystemResources() {
            try {
                const response = await fetch('/api/system/resources');
                const data = await response.json();

                // Update CPU chart
                const cpuData = cpuChart.data.datasets[0].data;
                cpuData.push(data.cpu.current);
                if (cpuData.length > 20) cpuData.shift();

                const timeLabel = new Date().toLocaleTimeString();
                const cpuLabels = cpuChart.data.labels;
                cpuLabels.push(timeLabel);
                if (cpuLabels.length > 20) cpuLabels.shift();

                cpuChart.update();

                // Update Memory chart
                const memData = memoryChart.data.datasets[0].data;
                memData.push(data.memory.current);
                if (memData.length > 20) memData.shift();

                const memLabels = memoryChart.data.labels;
                memLabels.push(timeLabel);
                if (memLabels.length > 20) memLabels.shift();

                memoryChart.update();

            } catch (error) {
                console.error('Error updating system resources:', error);
            }
        }

        async function updateOperationsTable() {
            try {
                const response = await fetch('/api/metrics/graphs?limit=10');
                const data = await response.json();

                const tbody = document.getElementById('operations-tbody');
                tbody.innerHTML = '';

                data.forEach(op => {
                    const row = tbody.insertRow();

                    const time = new Date(op.timestamp);
                    row.insertCell(0).textContent = time.toLocaleTimeString();
                    row.insertCell(1).textContent = op.graph_id;
                    row.insertCell(2).textContent = op.num_nodes;
                    row.insertCell(3).textContent = op.num_edges;
                    row.insertCell(4).textContent = op.model_architecture;
                    row.insertCell(5).textContent = (op.processing_time * 1000).toFixed(0) + ' ms';

                    const statusCell = row.insertCell(6);
                    const statusSpan = document.createElement('span');
                    statusSpan.className = `status-indicator status-${op.success ? 'healthy' : 'error'}`;
                    statusCell.appendChild(statusSpan);
                    statusCell.appendChild(document.createTextNode(op.success ? 'Success' : 'Failed'));
                });

            } catch (error) {
                console.error('Error updating operations table:', error);
            }
        }

        // Initial load
        updateRealTimeStats();
        updateHistoricalData();
        updateSystemResources();
        updateOperationsTable();

        // Set up periodic updates
        setInterval(updateRealTimeStats, 5000);
        setInterval(updateSystemResources, 5000);
        setInterval(updateOperationsTable, 10000);
        setInterval(updateHistoricalData, 60000);
    </script>
</body>
</html>
"""


def create_dashboard(host: str = "127.0.0.1", port: int = 5000) -> Optional[MonitoringDashboard]:
    """
    Create and return a monitoring dashboard instance.

    Args:
        host: Dashboard host address
        port: Dashboard port

    Returns:
        MonitoringDashboard instance or None if Flask is not available
    """
    if not FLASK_AVAILABLE:
        logger.warning("Flask is not installed. Install with: pip install flask flask-cors")
        return None

    try:
        dashboard = MonitoringDashboard(host=host, port=port)
        return dashboard
    except Exception as e:
        logger.error(f"Failed to create dashboard: {e}")
        return None


# Example usage
if __name__ == "__main__":
    dashboard = create_dashboard()
    if dashboard:
        dashboard.start()

        try:
            # Keep the dashboard running
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            dashboard.stop()
