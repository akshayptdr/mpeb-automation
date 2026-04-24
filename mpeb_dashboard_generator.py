#!/usr/bin/env python3
"""
MPEB Dashboard Generator
Reads mpeb_status.txt and generates an interactive HTML dashboard
"""
import sys
import re
import json
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

def parse_log_file():
    """Parse mpeb_status.txt and extract data"""
    log_file = Path("mpeb_status.txt")

    if not log_file.exists():
        return []

    entries = []
    with open(log_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            # Parse: [2026-04-24 08:32:58] SUCCESS: Form Submitted Successfully - Details Page Reached
            match = re.match(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] (SUCCESS|FAILURE): (.*)', line)
            if match:
                timestamp, status, message = match.groups()
                entries.append({
                    'timestamp': timestamp,
                    'status': status,
                    'message': message
                })

    return entries

def generate_dashboard(entries):
    """Generate HTML dashboard"""

    # Calculate statistics
    total = len(entries)
    success = sum(1 for e in entries if e['status'] == 'SUCCESS')
    failure = sum(1 for e in entries if e['status'] == 'FAILURE')
    success_rate = (success / total * 100) if total > 0 else 0

    # Get last entry
    last_status = entries[-1]['status'] if entries else 'UNKNOWN'
    last_message = entries[-1]['message'] if entries else 'No data'
    last_time = entries[-1]['timestamp'] if entries else 'N/A'

    # Count successes and failures by hour (for chart)
    hourly_stats = {}
    for entry in entries:
        try:
            dt = datetime.strptime(entry['timestamp'], "%Y-%m-%d %H:%M:%S")
            hour_key = dt.strftime("%Y-%m-%d %H:00")
            if hour_key not in hourly_stats:
                hourly_stats[hour_key] = {'success': 0, 'failure': 0}
            if entry['status'] == 'SUCCESS':
                hourly_stats[hour_key]['success'] += 1
            else:
                hourly_stats[hour_key]['failure'] += 1
        except:
            pass

    # Sort by hour
    hourly_sorted = sorted(hourly_stats.items())
    hours = [h[0] for h in hourly_sorted]
    successes = [h[1]['success'] for h in hourly_sorted]
    failures = [h[1]['failure'] for h in hourly_sorted]

    # Prepare JSON data for chart BEFORE building HTML
    hours_json = json.dumps(hours)
    successes_json = json.dumps(successes)
    failures_json = json.dumps(failures)

    # Generate HTML
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MPEB Solar Application Monitor</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}

        header {{
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }}

        h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}

        .subtitle {{
            font-size: 1.1em;
            opacity: 0.9;
        }}

        .dashboard {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .stat-card {{
            background: white;
            border-radius: 10px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            text-align: center;
        }}

        .stat-card h3 {{
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }}

        .stat-value {{
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 5px;
        }}

        .stat-card.success .stat-value {{
            color: #27ae60;
        }}

        .stat-card.failure .stat-value {{
            color: #e74c3c;
        }}

        .stat-card.total .stat-value {{
            color: #3498db;
        }}

        .stat-card.rate .stat-value {{
            color: #f39c12;
        }}

        .status-indicator {{
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }}

        .status-indicator.success {{
            background-color: #27ae60;
        }}

        .status-indicator.failure {{
            background-color: #e74c3c;
        }}

        .chart-container {{
            background: white;
            border-radius: 10px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 30px;
        }}

        .chart-container h2 {{
            margin-bottom: 20px;
            color: #333;
        }}

        .last-status {{
            background: white;
            border-radius: 10px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 30px;
        }}

        .last-status h2 {{
            margin-bottom: 20px;
            color: #333;
        }}

        .status-box {{
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
        }}

        .status-box.success {{
            background-color: #d5f4e6;
            border-left: 4px solid #27ae60;
        }}

        .status-box.failure {{
            background-color: #fadbd8;
            border-left: 4px solid #e74c3c;
        }}

        .status-box-time {{
            font-size: 0.9em;
            color: #666;
            margin-bottom: 5px;
        }}

        .status-box-message {{
            font-weight: 500;
            color: #333;
        }}

        .logs-container {{
            background: white;
            border-radius: 10px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            max-height: 600px;
            overflow-y: auto;
        }}

        .logs-container h2 {{
            margin-bottom: 20px;
            color: #333;
        }}

        .log-entry {{
            padding: 12px;
            border-bottom: 1px solid #eee;
            font-size: 0.95em;
            font-family: 'Courier New', monospace;
        }}

        .log-entry:last-child {{
            border-bottom: none;
        }}

        .log-time {{
            color: #3498db;
            font-weight: bold;
        }}

        .log-status {{
            font-weight: bold;
            margin: 0 10px;
        }}

        .log-status.success {{
            color: #27ae60;
        }}

        .log-status.failure {{
            color: #e74c3c;
        }}

        .log-message {{
            color: #555;
            margin-left: 10px;
        }}

        .refresh-time {{
            text-align: center;
            color: white;
            margin-top: 20px;
            font-size: 0.9em;
            opacity: 0.8;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>☀️ MPEB Solar Application Monitor</h1>
            <p class="subtitle">Automated Rooftop Solar Panel Application Tracker</p>
        </header>

        <div class="dashboard">
            <div class="stat-card total">
                <h3>Total Runs</h3>
                <div class="stat-value">{total}</div>
            </div>
            <div class="stat-card success">
                <h3>Successes</h3>
                <div class="stat-value">{success}</div>
            </div>
            <div class="stat-card failure">
                <h3>Failures</h3>
                <div class="stat-value">{failure}</div>
            </div>
            <div class="stat-card rate">
                <h3>Success Rate</h3>
                <div class="stat-value">{success_rate:.1f}%</div>
            </div>
        </div>

        <div class="last-status">
            <h2>Last Run Status</h2>
            <div class="status-box {last_status.lower()}">
                <div class="status-box-time">
                    <span class="status-indicator {last_status.lower()}"></span>
                    {last_time}
                </div>
                <div class="status-box-message">{last_status}: {last_message}</div>
            </div>
        </div>

        {f'''
        <div class="chart-container">
            <h2>Hourly Success/Failure Trend</h2>
            <canvas id="trendChart"></canvas>
        </div>
        ''' if hourly_sorted else ''}

        <div class="logs-container">
            <h2>Recent Activity Log ({total} entries)</h2>
            {generate_log_entries_html(entries)}
        </div>

        <div class="refresh-time">
            Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            <br>
            <em>Dashboard auto-refreshes in browser. Refresh page to update from log file.</em>
        </div>
    </div>

    {f'''
    <script>
        const ctx = document.getElementById('trendChart').getContext('2d');
        const chart = new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: {hours_json},
                datasets: [
                    {{
                        label: 'Successes',
                        data: {successes_json},
                        borderColor: '#27ae60',
                        backgroundColor: 'rgba(39, 174, 96, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4,
                        pointRadius: 5,
                        pointBackgroundColor: '#27ae60'
                    }},
                    {{
                        label: 'Failures',
                        data: {failures_json},
                        borderColor: '#e74c3c',
                        backgroundColor: 'rgba(231, 76, 60, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4,
                        pointRadius: 5,
                        pointBackgroundColor: '#e74c3c'
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: true,
                plugins: {{
                    legend: {{
                        position: 'top',
                    }},
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        title: {{
                            display: true,
                            text: 'Number of Runs'
                        }}
                    }}
                }}
            }}
        }});
    </script>
    ''' if hourly_sorted else ''}
</body>
</html>
"""

    return html

def generate_log_entries_html(entries):
    """Generate HTML for log entries (show most recent first)"""
    html = ""
    # Show last 50 entries, most recent first
    for entry in reversed(entries[-50:]):
        html += f"""
        <div class="log-entry">
            <span class="log-time">[{entry['timestamp']}]</span>
            <span class="log-status {entry['status'].lower()}">{entry['status']}</span>
            <span class="log-message">{entry['message']}</span>
        </div>
        """
    return html

def push_to_github():
    """Commit and push changes to GitHub"""
    import subprocess

    try:
        # Check if there are changes
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if not result.stdout.strip():
            print("  No changes to push")
            return

        # Add changes
        subprocess.run(
            ["git", "add", "mpeb_status.txt", "mpeb_dashboard.html"],
            capture_output=True,
            timeout=10
        )

        # Commit
        subprocess.run(
            ["git", "commit", "-m", f"Update dashboard and logs - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"],
            capture_output=True,
            timeout=10
        )

        # Push
        result = subprocess.run(
            ["git", "push", "origin", "master"],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            print("  ✓ Pushed to GitHub successfully")
        else:
            print(f"  ⚠ Git push failed: {result.stderr[:100]}")
    except Exception as e:
        print(f"  ⚠ GitHub push error: {str(e)[:100]}")

def main():
    print("Generating MPEB Dashboard...")

    # Parse log file
    entries = parse_log_file()

    if not entries:
        print("ERROR: No entries found in mpeb_status.txt")
        print("Make sure the automation has run at least once.")
        return

    print(f"Found {len(entries)} log entries")

    # Generate dashboard
    dashboard_html = generate_dashboard(entries)

    # Write to file
    output_file = Path("mpeb_dashboard.html")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(dashboard_html)

    print(f"✓ Dashboard generated: {output_file}")
    print(f"\nOpen this file in your browser to view the dashboard:")
    print(f"  {output_file.absolute()}")

    # Push to GitHub
    print("\nPushing to GitHub...")
    push_to_github()

if __name__ == "__main__":
    main()
