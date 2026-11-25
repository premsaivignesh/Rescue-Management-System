from pathlib import Path
import webbrowser
import pandas as pd
import plotly.express as px
from database.incident_db import IncidentDB

BASE_DIR = Path(__file__).resolve().parents[2]
OUTPUT_DIR = BASE_DIR / 'ai_ml' / 'analytics' / 'reports'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def create_dashboard(open_browser=True):
    db = IncidentDB()
    db.cursor.execute('SELECT incident_id,user_id,incident_type,description,address,image_path,video_path,latitude,longitude,severity,status,people_estimated,ambulance_required,police_required,fire_engine_required,department_assigned,priority_score,ai_status,report_time FROM incidents ORDER BY report_time DESC')
    rows = db.cursor.fetchall()
    columns = [
        'incident_id','user_id','incident_type','description','address','image_path','video_path',
        'latitude','longitude','severity','status','people_estimated','ambulance_required',
        'police_required','fire_engine_required','department_assigned','priority_score','ai_status','report_time'
    ]
    df = pd.DataFrame(rows, columns=columns) if rows else pd.DataFrame(columns=columns)
    if df.empty:
        df = pd.DataFrame([{'incident_type':'No Data','severity':'No Data','priority_score':0,'report_time':pd.Timestamp.now()}])
    df['report_time'] = pd.to_datetime(df['report_time'], errors='coerce')

    fig_type = px.histogram(df, x='incident_type', title='Incidents by Type')
    fig_severity = px.histogram(df, x='severity', title='Severity Distribution')
    fig_priority = px.scatter(df, x='report_time', y='priority_score', color='severity', hover_data=['incident_type','status'], title='Incident Priority Over Time')
    fig_resources = px.bar(df, x='incident_id', y=['ambulance_required','police_required','fire_engine_required'], title='Resources Requested per Incident')

    html = f'''<!doctype html><html><head><meta charset="utf-8"><title>Rescue Management Analytics</title><style>body{{font-family:Arial;margin:25px}}h1{{margin-bottom:5px}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:25px}}</style></head><body><h1>Rescue Management System — Analytics</h1><p>Interactive operational analytics generated from the local SQLite database.</p><div class="grid">{fig_type.to_html(full_html=False, include_plotlyjs=True)}{fig_severity.to_html(full_html=False, include_plotlyjs=False)}{fig_priority.to_html(full_html=False, include_plotlyjs=False)}{fig_resources.to_html(full_html=False, include_plotlyjs=False)}</div></body></html>'''
    output = OUTPUT_DIR / 'rescue_analytics.html'
    output.write_text(html, encoding='utf-8')
    if open_browser:
        webbrowser.open(output.as_uri())
    return str(output)


if __name__ == '__main__':
    print(create_dashboard())
