import os
import base64
from pathlib import Path

from benchmark.config import RUNS_DIR
from benchmark.core.db import SessionLocal
from benchmark.core.models import RunItem, HumanScore

def build_report(run_id: str) -> str:
    """Build a static HTML report for the given run, embedding images and scores."""
    report_file = f"report_{run_id}.html"
    session = SessionLocal()
    # Query run items
    items = session.query(RunItem).filter_by(run_id=int(run_id)).all()
    # Begin HTML
    html_lines = [
        '<!DOCTYPE html>',
        '<html><head><meta charset="UTF-8">',
        f'<title>Report for run {run_id}</title>',
        '</head><body>',
        f'<h1>Report for run {run_id}</h1>',
        '<table border="1" cellpadding="5" cellspacing="0">',
        '<tr><th>Case ID</th><th>Tool ID</th><th>Machine Score</th><th>Human Rating</th><th>Image</th></tr>'
    ]
    # Populate rows
    for item in items:
        # Human score if exists
        hs = session.query(HumanScore).filter_by(run_item_id=item.id).first()
        stars = hs.stars if hs else ''
        # Image file path
        img_path = Path(RUNS_DIR) / str(run_id) / item.tool_id / f"{item.case_id}.png"
        img_src = ''
        if img_path.exists():
            with open(img_path, 'rb') as imgf:
                data = base64.b64encode(imgf.read()).decode('ascii')
            img_src = f"data:image/png;base64,{data}"
        # Table row
        img_tag = f'<img src="{img_src}" width="200"/>' if img_src else ''
        html_lines.append(
            '<tr>'
            f'<td>{item.case_id}</td>'
            f'<td>{item.tool_id}</td>'
            f'<td>{item.score}</td>'
            f'<td>{stars}</td>'
            f'<td>{img_tag}</td>'
            '</tr>'
        )
    # Close HTML
    html_lines.extend(['</table>', '</body></html>'])
    # Write to file
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(html_lines))
    session.close()
    return os.path.abspath(report_file)