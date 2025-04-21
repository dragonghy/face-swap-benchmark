"""
FastAPI web application for the face swap benchmark.

This module provides a web interface for running face swap benchmarks, 
viewing results, and generating reports.
"""

import os
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse

from benchmark.web.sockets import ConnectionManager
from benchmark.core.models import load_test_cases, HumanScore
from benchmark.core.runner import start_run, execute_run_async
from benchmark.core.db import SessionLocal
from benchmark.config import RUNS_DIR, DATASETS_DIR
from benchmark.report.report_builder import build_report

# Configure logging
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Face Swap Benchmark",
    description="A web interface for benchmarking face-swapping tools",
    version="0.1.0"
)

# Mount static files and directories
static_dir = os.path.join(os.path.dirname(__file__), 'static')
templates_dir = os.path.join(os.path.dirname(__file__), 'templates')

app.mount('/static', StaticFiles(directory=static_dir), name='static')
app.mount('/runs', StaticFiles(directory=str(RUNS_DIR)), name='runs')
app.mount('/datasets', StaticFiles(directory=str(DATASETS_DIR)), name='datasets')
templates = Jinja2Templates(directory=templates_dir)

# Initialize WebSocket connection manager
manager = ConnectionManager()


@app.get('/', response_class=HTMLResponse)
async def get_index(request: Request) -> HTMLResponse:
    """Render the main application page."""
    return templates.TemplateResponse('index.html', {'request': request})


@app.get('/api/test-cases')
async def get_test_cases() -> List[Dict[str, Any]]:
    """
    Retrieve all test cases with relative URLs for images.
    
    Returns:
        A list of test case dictionaries with added template_url and avatar_urls fields
    """
    cases = load_test_cases()
    case_data = [case.dict() for case in cases]
    
    # Base path for relative URL conversion
    base_path = str(Path(__file__).parent.parent.parent)
    
    for case in case_data:
        # Convert template image path to URL
        if 'template_image' in case and case['template_image']:
            template_path = case['template_image']
            if template_path.startswith('/'):
                if template_path.startswith(base_path):
                    rel_path = template_path[len(base_path):].lstrip('/')
                    case['template_url'] = f"/{rel_path}"
        
        # Convert avatar paths to URLs
        if 'avatars' in case and case['avatars']:
            avatar_urls = []
            for avatar_path in case['avatars']:
                if avatar_path and avatar_path.startswith('/'):
                    if avatar_path.startswith(base_path):
                        rel_path = avatar_path[len(base_path):].lstrip('/')
                        avatar_urls.append(f"/{rel_path}")
                else:
                    avatar_urls.append(avatar_path)
            case['avatar_urls'] = avatar_urls
    
    return case_data


@app.get('/api/tools')
async def get_tools() -> List[str]:
    """
    List available face-swapping tools.
    
    Returns:
        A list of tool IDs available for benchmarking
    """
    return ['baseline_replicate']


@app.post('/api/run')
async def post_run(payload: Dict[str, Any]) -> Dict[str, str]:
    """
    Start a new benchmark run and broadcast progress via WebSocket.
    
    Args:
        payload: A dictionary containing case_ids and tool_ids to run
        
    Returns:
        A dictionary with the run_id of the created run
    """
    case_ids = payload.get('case_ids', []) or []
    tool_ids = payload.get('tool_ids', []) or []
    
    logger.info(f"Starting new benchmark run with {len(case_ids)} cases and {len(tool_ids)} tools")
    
    # Start the run and get the run ID
    run_id = start_run(case_ids, tool_ids)
    
    # Execute run in background
    asyncio.create_task(execute_run_async(run_id, manager))
    
    return {'run_id': run_id}


@app.websocket('/api/run/{run_id}')
async def websocket_run(websocket: WebSocket, run_id: str) -> None:
    """
    WebSocket endpoint for receiving real-time updates on a run.
    
    Args:
        websocket: The WebSocket connection
        run_id: The ID of the run to monitor
    """
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info(f"WebSocket disconnected for run {run_id}")


@app.post('/api/rate')
async def post_rate(payload: Dict[str, Any]) -> Dict[str, str]:
    """
    Save human rating for a run item.
    
    Args:
        payload: A dictionary containing run_item_id and stars rating
        
    Returns:
        A dictionary with status indicator
    """
    run_item_id = payload.get('run_item_id')
    stars = payload.get('stars')
    
    if not run_item_id or not stars:
        return {'status': 'error', 'message': 'Missing required fields'}
    
    session = SessionLocal()
    try:
        # Update or insert human score
        existing = session.query(HumanScore).filter_by(run_item_id=run_item_id).first()
        if existing:
            existing.stars = int(stars)
            logger.info(f"Updated rating for run item {run_item_id}: {stars} stars")
        else:
            hs = HumanScore(run_item_id=run_item_id, stars=int(stars))
            session.add(hs)
            logger.info(f"Created new rating for run item {run_item_id}: {stars} stars")
        
        session.commit()
        return {'status': 'success'}
        
    except Exception as e:
        session.rollback()
        logger.exception(f"Error saving rating: {e}")
        return {'status': 'error', 'message': str(e)}
    finally:
        session.close()


@app.get('/api/run/{run_id}/status')
async def get_run_status(run_id: str) -> List[Dict[str, Any]]:
    """
    Get the current status of a run.
    
    Args:
        run_id: The ID of the run to get status for
        
    Returns:
        A list of dictionaries containing status information for each run item
    """
    from benchmark.core.models import RunItem
    
    session = SessionLocal()
    try:
        # Convert run_id to int
        run_id_int = int(run_id)
        items = session.query(RunItem).filter_by(run_id=run_id_int).all()
        result = []
        
        logger.info(f"Status request for run {run_id}: found {len(items)} items")
        
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
            logger.debug(f"Item status: {item.case_id}/{item.tool_id} = {item.status}")
        
        return result
    except Exception as e:
        logger.exception(f"Error getting run status: {e}")
        return []
    finally:
        session.close()


@app.get('/api/report/{run_id}')
async def get_report(run_id: str) -> FileResponse:
    """
    Generate and return a static HTML report for the run.
    
    Args:
        run_id: The ID of the run to generate a report for
        
    Returns:
        A FileResponse containing the HTML report
    """
    logger.info(f"Generating report for run {run_id}")
    report_path = build_report(run_id)
    return FileResponse(
        report_path, 
        media_type='text/html', 
        filename=f'report_{run_id}.html'
    )