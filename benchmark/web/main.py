import os
import asyncio
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse
from benchmark.web.sockets import ConnectionManager
from benchmark.core.models import load_test_cases
from benchmark.core.runner import start_run, execute_run_async
from benchmark.config import RUNS_DIR, DATASETS_DIR
from benchmark.report.report_builder import build_report

app = FastAPI()
# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), 'static')
app.mount('/static', StaticFiles(directory=static_dir), name='static')
app.mount('/runs', StaticFiles(directory=str(RUNS_DIR)), name='runs')
app.mount('/datasets', StaticFiles(directory=str(DATASETS_DIR)), name='datasets')
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), 'templates'))

manager = ConnectionManager()

@app.get('/', response_class=HTMLResponse)
async def get_index(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})

@app.get('/api/test-cases')
async def get_test_cases():
    cases = load_test_cases()
    case_data = [case.dict() for case in cases]
    
    # Convert absolute paths to relative URLs
    for case in case_data:
        # Make template image path relative
        if 'template_image' in case and case['template_image']:
            template_path = case['template_image']
            if template_path.startswith('/'):
                # Create a URL path from the absolute path
                base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
                if template_path.startswith(base_path):
                    rel_path = template_path[len(base_path):].lstrip('/')
                    case['template_url'] = f"/{rel_path}"
        
        # Make avatar paths relative
        if 'avatars' in case and case['avatars']:
            avatar_urls = []
            for avatar_path in case['avatars']:
                if avatar_path and avatar_path.startswith('/'):
                    # Create a URL path from the absolute path
                    base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
                    if avatar_path.startswith(base_path):
                        rel_path = avatar_path[len(base_path):].lstrip('/')
                        avatar_urls.append(f"/{rel_path}")
                else:
                    avatar_urls.append(avatar_path)
            case['avatar_urls'] = avatar_urls
    
    return case_data

@app.get('/api/tools')
async def get_tools():
    # List available tools
    return ['baseline_replicate']

@app.post('/api/run')
async def post_run(payload: dict):
    """Start a new benchmark run and broadcast progress via WebSocket."""
    case_ids = payload.get('case_ids', []) or []
    tool_ids = payload.get('tool_ids', []) or []
    run_id = start_run(case_ids, tool_ids)
    # Execute run in background
    asyncio.create_task(execute_run_async(run_id, manager))
    return {'run_id': run_id}

@app.websocket('/api/run/{run_id}')
async def websocket_run(websocket: WebSocket, run_id: str):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post('/api/rate')
async def post_rate(payload: dict):
    """Save human rating for a run item."""
    from benchmark.core.db import SessionLocal
    from benchmark.core.models import HumanScore
    run_item_id = payload.get('run_item_id')
    stars = payload.get('stars')
    session = SessionLocal()
    # Update or insert human score
    existing = session.query(HumanScore).filter_by(run_item_id=run_item_id).first()
    if existing:
        existing.stars = int(stars)
    else:
        hs = HumanScore(run_item_id=run_item_id, stars=int(stars))
        session.add(hs)
    session.commit()
    session.close()
    return {'status': 'success'}
 
@app.get('/api/run/{run_id}/status')
async def get_run_status(run_id: str):
    """Get the current status of a run."""
    from benchmark.core.db import SessionLocal
    from benchmark.core.models import RunItem
    session = SessionLocal()
    
    try:
        # Convert run_id to int
        run_id_int = int(run_id)
        items = session.query(RunItem).filter_by(run_id=run_id_int).all()
        result = []
        
        print(f"[Web] Status request for run {run_id}: found {len(items)} items")
        
        for item in items:
            result.append({
                'run_id': run_id,
                'run_item_id': item.id,
                'case_id': item.case_id,
                'tool_id': item.tool_id,
                'status': item.status,
                'image_url': item.image_url,
                'score': item.score
            })
            print(f"[Web] Item status: {item.case_id}/{item.tool_id} = {item.status}")
        
        return result
    except Exception as e:
        import traceback
        print(f"[Web] Error getting run status: {e}")
        traceback.print_exc()
        return []
    finally:
        session.close()

@app.get('/api/report/{run_id}')
async def get_report(run_id: str):
    """Generate and return a static HTML report for the run."""
    report_path = build_report(run_id)
    return FileResponse(report_path, media_type='text/html', filename=f'report_{run_id}.html')