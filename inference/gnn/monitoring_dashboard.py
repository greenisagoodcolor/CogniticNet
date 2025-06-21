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

    def __init__(self, host: str='127.0.0.1', port: int=5000, update_interval: int=5):
        """
        Initialize monitoring dashboard.

        Args:
            host: Dashboard host address
            port: Dashboard port
            update_interval: Update interval in seconds
        """
        if not FLASK_AVAILABLE:
            raise ImportError('Flask is required for the monitoring dashboard')
        self.host = host
        self.port = port
        self.update_interval = update_interval
        self.app = Flask(__name__)
        CORS(self.app)
        self.monitor = get_monitor()
        self.collector = get_metrics_collector()
        self._setup_routes()
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
            stats = {'performance': self.monitor.get_statistics(), 'metrics': self.collector.get_real_time_stats(), 'timestamp': datetime.utcnow().isoformat()}
            return jsonify(stats)

        @self.app.route('/api/stats/historical')
        def historical_stats():
            """Get historical statistics"""
            hours = int(request.args.get('hours', 24))
            group_by = request.args.get('group_by', 'hour')
            start_time = datetime.utcnow() - timedelta(hours=hours)
            stats = self.collector.db.get_aggregated_stats(start_time=start_time, group_by=group_by)
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
            system_stats = self.monitor.get_statistics('_system')
            return jsonify({'cpu': {'current': system_stats.get('cpu_percent', {}).get('mean', 0), 'max': system_stats.get('cpu_percent', {}).get('max', 0)}, 'memory': {'current': system_stats.get('memory_mb', {}).get('mean', 0), 'max': system_stats.get('memory_mb', {}).get('max', 0)}, 'gpu': {'memory': system_stats.get('gpu_memory_mb', {}).get('mean', 0) if 'gpu_memory_mb' in system_stats else None}})

        @self.app.route('/api/alerts')
        def get_alerts():
            """Get recent alerts"""
            return jsonify([])

    def start(self):
        """Start the dashboard"""
        self._running = True
        import werkzeug.serving

        def run_app():
            werkzeug.serving.run_simple(self.host, self.port, self.app, use_reloader=False, use_debugger=False)
        app_thread = threading.Thread(target=run_app)
        app_thread.daemon = True
        app_thread.start()
        logger.info(f'Monitoring dashboard started at http://{self.host}:{self.port}')

    def stop(self):
        """Stop the dashboard"""
        self._running = False
        logger.info('Monitoring dashboard stopped')
DASHBOARD_HTML = '\n<!DOCTYPE html>\n<html lang="en">\n<head>\n    <meta charset="UTF-8">\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n    <title>GNN Processing Monitor</title>\n    <script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>\n    <style>\n        * {\n            margin: 0;\n            padding: 0;\n            box-sizing: border-box;\n        }\n\n        body {\n            font-family: -apple-system, BlinkMacSystemFont, \'Segoe UI\', Roboto, sans-serif;\n            background-color: #f5f5f5;\n            color: #333;\n        }\n\n        .header {\n            background-color: #2c3e50;\n            color: white;\n            padding: 1rem 2rem;\n            box-shadow: 0 2px 4px rgba(0,0,0,0.1);\n        }\n\n        .container {\n            max-width: 1400px;\n            margin: 0 auto;\n            padding: 2rem;\n        }\n\n        .metrics-grid {\n            display: grid;\n            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));\n            gap: 1.5rem;\n            margin-bottom: 2rem;\n        }\n\n        .metric-card {\n            background: white;\n            border-radius: 8px;\n            padding: 1.5rem;\n            box-shadow: 0 2px 4px rgba(0,0,0,0.1);\n        }\n\n        .metric-card h3 {\n            font-size: 0.875rem;\n            color: #666;\n            margin-bottom: 0.5rem;\n            text-transform: uppercase;\n            letter-spacing: 0.05em;\n        }\n\n        .metric-value {\n            font-size: 2rem;\n            font-weight: 600;\n            color: #2c3e50;\n        }\n\n        .metric-unit {\n            font-size: 0.875rem;\n            color: #666;\n            margin-left: 0.25rem;\n        }\n\n        .chart-container {\n            background: white;\n            border-radius: 8px;\n            padding: 1.5rem;\n            box-shadow: 0 2px 4px rgba(0,0,0,0.1);\n            margin-bottom: 1.5rem;\n        }\n\n        .chart-container h3 {\n            font-size: 1.125rem;\n            margin-bottom: 1rem;\n            color: #2c3e50;\n        }\n\n        .status-indicator {\n            display: inline-block;\n            width: 12px;\n            height: 12px;\n            border-radius: 50%;\n            margin-right: 0.5rem;\n        }\n\n        .status-healthy { background-color: #27ae60; }\n        .status-warning { background-color: #f39c12; }\n        .status-error { background-color: #e74c3c; }\n\n        .table-container {\n            background: white;\n            border-radius: 8px;\n            padding: 1.5rem;\n            box-shadow: 0 2px 4px rgba(0,0,0,0.1);\n            overflow-x: auto;\n        }\n\n        table {\n            width: 100%;\n            border-collapse: collapse;\n        }\n\n        th, td {\n            text-align: left;\n            padding: 0.75rem;\n            border-bottom: 1px solid #eee;\n        }\n\n        th {\n            font-weight: 600;\n            color: #666;\n            font-size: 0.875rem;\n            text-transform: uppercase;\n            letter-spacing: 0.05em;\n        }\n\n        tr:hover {\n            background-color: #f8f9fa;\n        }\n\n        .refresh-indicator {\n            position: fixed;\n            top: 1rem;\n            right: 1rem;\n            background: #27ae60;\n            color: white;\n            padding: 0.5rem 1rem;\n            border-radius: 4px;\n            font-size: 0.875rem;\n            opacity: 0;\n            transition: opacity 0.3s;\n        }\n\n        .refresh-indicator.active {\n            opacity: 1;\n        }\n    </style>\n</head>\n<body>\n    <div class="header">\n        <h1>GNN Processing Monitor</h1>\n    </div>\n\n    <div class="container">\n        <!-- Real-time Metrics -->\n        <div class="metrics-grid">\n            <div class="metric-card">\n                <h3>Total Graphs Processed</h3>\n                <div class="metric-value" id="total-graphs">0</div>\n            </div>\n\n            <div class="metric-card">\n                <h3>Success Rate</h3>\n                <div class="metric-value">\n                    <span id="success-rate">0</span><span class="metric-unit">%</span>\n                </div>\n            </div>\n\n            <div class="metric-card">\n                <h3>Avg Processing Time</h3>\n                <div class="metric-value">\n                    <span id="avg-time">0</span><span class="metric-unit">ms</span>\n                </div>\n            </div>\n\n            <div class="metric-card">\n                <h3>System Status</h3>\n                <div class="metric-value">\n                    <span class="status-indicator status-healthy"></span>\n                    <span style="font-size: 1.25rem;">Healthy</span>\n                </div>\n            </div>\n        </div>\n\n        <!-- Performance Chart -->\n        <div class="chart-container">\n            <h3>Processing Performance (Last 24 Hours)</h3>\n            <canvas id="performance-chart" height="80"></canvas>\n        </div>\n\n        <!-- Resource Usage Charts -->\n        <div class="metrics-grid">\n            <div class="chart-container">\n                <h3>CPU Usage</h3>\n                <canvas id="cpu-chart" height="100"></canvas>\n            </div>\n\n            <div class="chart-container">\n                <h3>Memory Usage</h3>\n                <canvas id="memory-chart" height="100"></canvas>\n            </div>\n        </div>\n\n        <!-- Recent Operations Table -->\n        <div class="table-container">\n            <h3>Recent Operations</h3>\n            <table id="operations-table">\n                <thead>\n                    <tr>\n                        <th>Time</th>\n                        <th>Graph ID</th>\n                        <th>Nodes</th>\n                        <th>Edges</th>\n                        <th>Model</th>\n                        <th>Duration</th>\n                        <th>Status</th>\n                    </tr>\n                </thead>\n                <tbody id="operations-tbody">\n                    <!-- Populated by JavaScript -->\n                </tbody>\n            </table>\n        </div>\n    </div>\n\n    <div class="refresh-indicator" id="refresh-indicator">\n        Updating...\n    </div>\n\n    <script>\n        // Chart configurations\n        const chartOptions = {\n            responsive: true,\n            maintainAspectRatio: false,\n            plugins: {\n                legend: {\n                    display: false\n                }\n            },\n            scales: {\n                y: {\n                    beginAtZero: true\n                }\n            }\n        };\n\n        // Initialize charts\n        const performanceChart = new Chart(\n            document.getElementById(\'performance-chart\').getContext(\'2d\'),\n            {\n                type: \'line\',\n                data: {\n                    labels: [],\n                    datasets: [{\n                        label: \'Processing Time\',\n                        data: [],\n                        borderColor: \'#3498db\',\n                        backgroundColor: \'rgba(52, 152, 219, 0.1)\',\n                        tension: 0.4\n                    }]\n                },\n                options: chartOptions\n            }\n        );\n\n        const cpuChart = new Chart(\n            document.getElementById(\'cpu-chart\').getContext(\'2d\'),\n            {\n                type: \'line\',\n                data: {\n                    labels: [],\n                    datasets: [{\n                        label: \'CPU %\',\n                        data: [],\n                        borderColor: \'#e74c3c\',\n                        backgroundColor: \'rgba(231, 76, 60, 0.1)\',\n                        tension: 0.4\n                    }]\n                },\n                options: {\n                    ...chartOptions,\n                    scales: {\n                        y: {\n                            beginAtZero: true,\n                            max: 100\n                        }\n                    }\n                }\n            }\n        );\n\n        const memoryChart = new Chart(\n            document.getElementById(\'memory-chart\').getContext(\'2d\'),\n            {\n                type: \'line\',\n                data: {\n                    labels: [],\n                    datasets: [{\n                        label: \'Memory MB\',\n                        data: [],\n                        borderColor: \'#27ae60\',\n                        backgroundColor: \'rgba(39, 174, 96, 0.1)\',\n                        tension: 0.4\n                    }]\n                },\n                options: chartOptions\n            }\n        );\n\n        // Update functions\n        async function updateRealTimeStats() {\n            try {\n                const response = await fetch(\'/api/stats/realtime\');\n                const data = await response.json();\n\n                // Update metric cards\n                const metrics = data.metrics;\n                if (metrics && metrics.counters) {\n                    document.getElementById(\'total-graphs\').textContent =\n                        metrics.counters.total_graphs || 0;\n\n                    const successRate = metrics.counters.successful_operations /\n                        (metrics.counters.successful_operations + metrics.counters.failed_operations) * 100;\n                    document.getElementById(\'success-rate\').textContent =\n                        isNaN(successRate) ? 0 : successRate.toFixed(1);\n                }\n\n                if (metrics && metrics.timers && metrics.timers.processing_times) {\n                    const avgTime = metrics.timers.processing_times.mean * 1000; // Convert to ms\n                    document.getElementById(\'avg-time\').textContent = avgTime.toFixed(0);\n                }\n\n                // Show refresh indicator\n                const indicator = document.getElementById(\'refresh-indicator\');\n                indicator.classList.add(\'active\');\n                setTimeout(() => indicator.classList.remove(\'active\'), 500);\n\n            } catch (error) {\n                console.error(\'Error updating real-time stats:\', error);\n            }\n        }\n\n        async function updateHistoricalData() {\n            try {\n                const response = await fetch(\'/api/stats/historical?hours=24&group_by=hour\');\n                const data = await response.json();\n\n                if (data && data.length > 0) {\n                    // Update performance chart\n                    const labels = data.map(d => {\n                        const date = new Date(d.period);\n                        return date.toLocaleTimeString([], { hour: \'2-digit\' });\n                    }).reverse();\n\n                    const avgTimes = data.map(d => d.avg_processing_time * 1000).reverse();\n\n                    performanceChart.data.labels = labels;\n                    performanceChart.data.datasets[0].data = avgTimes;\n                    performanceChart.update();\n                }\n            } catch (error) {\n                console.error(\'Error updating historical data:\', error);\n            }\n        }\n\n        async function updateSystemResources() {\n            try {\n                const response = await fetch(\'/api/system/resources\');\n                const data = await response.json();\n\n                // Update CPU chart\n                const cpuData = cpuChart.data.datasets[0].data;\n                cpuData.push(data.cpu.current);\n                if (cpuData.length > 20) cpuData.shift();\n\n                const timeLabel = new Date().toLocaleTimeString();\n                const cpuLabels = cpuChart.data.labels;\n                cpuLabels.push(timeLabel);\n                if (cpuLabels.length > 20) cpuLabels.shift();\n\n                cpuChart.update();\n\n                // Update Memory chart\n                const memData = memoryChart.data.datasets[0].data;\n                memData.push(data.memory.current);\n                if (memData.length > 20) memData.shift();\n\n                const memLabels = memoryChart.data.labels;\n                memLabels.push(timeLabel);\n                if (memLabels.length > 20) memLabels.shift();\n\n                memoryChart.update();\n\n            } catch (error) {\n                console.error(\'Error updating system resources:\', error);\n            }\n        }\n\n        async function updateOperationsTable() {\n            try {\n                const response = await fetch(\'/api/metrics/graphs?limit=10\');\n                const data = await response.json();\n\n                const tbody = document.getElementById(\'operations-tbody\');\n                tbody.innerHTML = \'\';\n\n                data.forEach(op => {\n                    const row = tbody.insertRow();\n\n                    const time = new Date(op.timestamp);\n                    row.insertCell(0).textContent = time.toLocaleTimeString();\n                    row.insertCell(1).textContent = op.graph_id;\n                    row.insertCell(2).textContent = op.num_nodes;\n                    row.insertCell(3).textContent = op.num_edges;\n                    row.insertCell(4).textContent = op.model_architecture;\n                    row.insertCell(5).textContent = (op.processing_time * 1000).toFixed(0) + \' ms\';\n\n                    const statusCell = row.insertCell(6);\n                    const statusSpan = document.createElement(\'span\');\n                    statusSpan.className = `status-indicator status-${op.success ? \'healthy\' : \'error\'}`;\n                    statusCell.appendChild(statusSpan);\n                    statusCell.appendChild(document.createTextNode(op.success ? \'Success\' : \'Failed\'));\n                });\n\n            } catch (error) {\n                console.error(\'Error updating operations table:\', error);\n            }\n        }\n\n        // Initial load\n        updateRealTimeStats();\n        updateHistoricalData();\n        updateSystemResources();\n        updateOperationsTable();\n\n        // Set up periodic updates\n        setInterval(updateRealTimeStats, 5000);\n        setInterval(updateSystemResources, 5000);\n        setInterval(updateOperationsTable, 10000);\n        setInterval(updateHistoricalData, 60000);\n    </script>\n</body>\n</html>\n'

def create_dashboard(host: str='127.0.0.1', port: int=5000) -> Optional[MonitoringDashboard]:
    """
    Create and return a monitoring dashboard instance.

    Args:
        host: Dashboard host address
        port: Dashboard port

    Returns:
        MonitoringDashboard instance or None if Flask is not available
    """
    if not FLASK_AVAILABLE:
        logger.warning('Flask is not installed. Install with: pip install flask flask-cors')
        return None
    try:
        dashboard = MonitoringDashboard(host=host, port=port)
        return dashboard
    except Exception as e:
        logger.error(f'Failed to create dashboard: {e}')
        return None
if __name__ == '__main__':
    dashboard = create_dashboard()
    if dashboard:
        dashboard.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            dashboard.stop()
