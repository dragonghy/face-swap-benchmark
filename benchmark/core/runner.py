import json
import asyncio
import os
from pathlib import Path

from benchmark.config import DATASETS_DIR, TEST_CASES_FILE, RUNS_DIR
from benchmark.core.db import init_db, SessionLocal
from benchmark.core.models import Run, RunItem
from benchmark.core.evaluator import evaluate
from benchmark.utils.image_io import save_image

def generate_cases():
    """Automatically generate test case ideas using OpenAI and save to datasets directory."""
    import os
    import openai
    import re

    # Default sizes for generated images (higher resolution improves facial detail)
    DEFAULT_TEMPLATE_SIZE = os.getenv("BENCHMARK_TEMPLATE_SIZE", "1024x1024")
    DEFAULT_AVATAR_SIZE = os.getenv("BENCHMARK_AVATAR_SIZE", "256x256")
    # Ensure datasets directory exists
    DATASETS_DIR.mkdir(parents=True, exist_ok=True)
    # Load API key
    openai.api_key = os.getenv('OPENAI_API_KEY')
    # Attempt to generate test case ideas via OpenAI
    try:
        # Prompt ChatGPT to create test cases
        system_msg = {
            'role': 'system',
            'content': 'You are a helpful assistant that generates JSON test cases for image generation benchmarks.'
        }
        user_msg = {
            'role': 'user',
            'content': (
                'Generate 3 test cases for a face-swap benchmark. Each test case must be a JSON object ' \
                'with these fields: ' \
                '"description": a scene description containing exactly two people (a male and a female), ' \
                '"avatars": an array of two textual prompts [male avatar prompt, female avatar prompt], and ' \
                '"instructions": a clear instruction string telling the tool to replace the male face in the scene with the male avatar and the female face with the female avatar. ' \
                'Respond only with a JSON array of these objects.'
            )
        }
        resp = openai.ChatCompletion.create(
            model='gpt-4',
            messages=[system_msg, user_msg],
            temperature=0.5,
        )
        content = resp.choices[0].message.content.strip()
        # Extract JSON array
        match = re.search(r'\[.*\]', content, re.S)
        json_str = match.group(0) if match else content
        cases = json.loads(json_str)
        # Validate that each case has two avatars and instructions
        valid = all(
            isinstance(c.get('avatars'), list) and len(c.get('avatars', [])) == 2 and isinstance(c.get('instructions'), str)
            for c in cases
        )
        if not valid:
            raise ValueError("Invalid test-case structure, falling back to stub cases")
    except Exception as e:
        print(f"[Runner] Error generating test cases: {e}")
        # Fallback to stub cases with human subjects and avatars
        cases = [
            {
              "id": "tc_01",
              "description": "A dining room scene with a couple seated at a table, using photo-realistic and show the couple's faces clearly",
              "avatars": [
                  "headshot portrait of a smiling man, studio lighting",
                  "headshot portrait of a smiling woman, studio lighting"
              ],
              "instructions": "In the dining scene, replace the male face with the male avatar image and the female face with the female avatar image."
            },
            {
              "id": "tc_02",
              "description": "A park bench scene showing a boyfriend and girlfriend together, using photo-realistic and show the couple's faces clearly",
              "avatars": [
                  "portrait of a young man wearing glasses, sunny outdoor background",
                  "portrait of a young woman with curly hair, sunny outdoor background"
              ],
              "instructions": "In the park scene, replace the male face with the first avatar and the female face with the second avatar."
            },
            {
              "id": "tc_03",
              "description": "A wedding photo with a groom and bride standing side by side, using photo-realistic and show the couple's faces clearly",
              "avatars": [
                  "formal portrait of a man in a tuxedo, studio backdrop",
                  "formal portrait of a woman in a wedding dress, studio backdrop"
              ],
              "instructions": "In the wedding photo, swap the groom's face with the male avatar and the bride's face with the female avatar."
            }
        ]
    # For each case, assign ID, generate input images, and update paths
    import base64
    from io import BytesIO
    from pathlib import Path
    from benchmark.utils.image_io import save_image

    for idx, case in enumerate(cases, start=1):
        # Assign ID
        if not case.get('id'):
            case['id'] = f'tc_{idx:02d}'
        cid = case['id']
        # Prepare directory for this case
        case_dir = DATASETS_DIR / cid
        case_dir.mkdir(parents=True, exist_ok=True)
        # Generate template image from description
        desc = case.get('description', '')
        try:
            print(f"[Runner] Generating template image for case {cid} at size {DEFAULT_TEMPLATE_SIZE}")
            tpl_resp = openai.images.generate(
                model="dall-e-3",
                quality="hd",
                prompt=desc,
                n=1,
                size=DEFAULT_TEMPLATE_SIZE,
                response_format="b64_json"
            )
            tpl_b64 = tpl_resp.data[0].b64_json
            tpl_data = base64.b64decode(tpl_b64)
            tpl_path = case_dir / 'template.png'
            with open(tpl_path, 'wb') as f:
                f.write(tpl_data)
            case['template_image'] = str(tpl_path)
        except Exception as e:
            print(f"[Runner] Error generating template image for {cid}: {e}")
        # Generate avatar images
        avatar_prompts = case.get('avatars', []) or []
        new_avatars = []
        for j, avatar_prompt in enumerate(avatar_prompts, start=1):
            try:
                print(f"[Runner] Generating avatar {j} for case {cid} at size {DEFAULT_AVATAR_SIZE}")
                av_resp = openai.images.generate(
                    prompt=avatar_prompt,
                    n=1,
                    size=DEFAULT_AVATAR_SIZE,
                    response_format="b64_json"
                )
                av_b64 = av_resp.data[0].b64_json
                av_data = base64.b64decode(av_b64)
                av_path = case_dir / f'avatar_{j}.png'
                with open(av_path, 'wb') as f:
                    f.write(av_data)
                new_avatars.append(str(av_path))
            except Exception as e:
                print(f"[Runner] Error generating avatar {j} for {cid}: {e}")
        case['avatars'] = new_avatars
    # Save enriched test cases to file
    with open(TEST_CASES_FILE, 'w') as f:
        json.dump(cases, f, indent=2)

MAX_CONCURRENT_TASKS = 3

def start_run(case_ids=None, tool_ids=None):
    """Initialize a benchmark run record and items; return run_id."""
    # Initialize DB and load session
    init_db()
    session = SessionLocal()
    # Load test cases
    if TEST_CASES_FILE.exists():
        with open(TEST_CASES_FILE, 'r') as f:
            test_cases = json.load(f)
    else:
        test_cases = []
    # Filter cases
    if case_ids:
        test_cases = [tc for tc in test_cases if tc.get('id') in case_ids]
    # Determine tools
    available_tools = ["baseline_replicate"]
    tools = list(tool_ids) if tool_ids else available_tools
    # Create run record
    run = Run()
    session.add(run)
    session.commit()
    run_id = run.id
    # Create run directory
    run_dir = RUNS_DIR / str(run_id)
    run_dir.mkdir(parents=True, exist_ok=True)
    # Create run items for each case-tool pair
    for tc in test_cases:
        case_id = tc.get('id')
        for tool in tools:
            item = RunItem(
                run_id=run.id,
                case_id=case_id,
                tool_id=tool,
                status='queued',
                image_url='',
                score=None
            )
            session.add(item)
    session.commit()
    session.close()
    return str(run_id)

async def execute_run_async(run_id: str, manager=None):
    """Execute an existing run: generate and evaluate images asynchronously."""
    init_db()
    print(f"[Runner] execute_run_async started for run {{run_id}}")
    session = SessionLocal()
    # Load run items
    items = session.query(RunItem).filter_by(run_id=int(run_id)).all()
    print(f"[Runner] Loaded {{len(items)}} run items for run {{run_id}}")
    # Load test cases for metadata
    if TEST_CASES_FILE.exists():
        with open(TEST_CASES_FILE, 'r') as f:
            test_cases = json.load(f)
    else:
        test_cases = []
    # Semaphore for concurrency
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_TASKS)

    async def _process(item: RunItem):
        async with semaphore:
            # Update status to generating
            item.status = 'generating'
            session.commit()
            if manager:
                await manager.broadcast({
                    'type': 'update',
                    'run_id': run_id,
                    'run_item_id': item.id,
                    'case_id': item.case_id,
                    'tool_id': item.tool_id,
                    'status': item.status,
                    'image_url': None,
                    'score': None
                })
            # Attempt to generate image via plugin
            try:
                module = __import__(f'benchmark.core.plugins.{item.tool_id}', fromlist=['generate'])
                # Load full test-case metadata
                with open(TEST_CASES_FILE, 'r') as f:
                    all_cases = json.load(f)
                case_dict = next((c for c in all_cases if c.get('id') == item.case_id), {'id': item.case_id})
                img = module.generate(case_dict)
                if img is None:
                    raise Exception(f"Plugin {item.tool_id} returned None instead of an image")
            except Exception as e:
                from PIL import Image, ImageDraw
                import traceback
                print(f"[Runner] Error in plugin {item.tool_id} for case {item.case_id}: {str(e)}")
                traceback.print_exc()
                img = Image.new('RGB', (512, 512), color=(200, 200, 200))
                # Add error text to the image
                draw = ImageDraw.Draw(img)
                draw.text((10, 10), f"Error in {item.tool_id}:", fill=(255, 0, 0))
                draw.text((10, 30), f"{str(e)[:100]}...", fill=(0, 0, 0))
            # Save image to disk
            run_dir = Path(RUNS_DIR) / run_id
            tool_dir = run_dir / item.tool_id
            tool_dir.mkdir(parents=True, exist_ok=True)
            img_path = tool_dir / f"{item.case_id}.png"
            save_image(img, str(img_path))
            item.image_url = f"/runs/{run_id}/{item.tool_id}/{item.case_id}.png"
            # Update status to evaluating
            item.status = 'evaluating'
            session.commit()
            if manager:
                await manager.broadcast({
                    'type': 'update',
                    'run_id': run_id,
                    'run_item_id': item.id,
                    'case_id': item.case_id,
                    'tool_id': item.tool_id,
                    'status': item.status,
                    'image_url': item.image_url,
                    'score': None
                })
            # Evaluate image
            score = evaluate(str(img_path))
            item.score = str(score)
            item.status = 'scored'
            session.commit()
            if manager:
                await manager.broadcast({
                    'type': 'update',
                    'run_id': run_id,
                    'run_item_id': item.id,
                    'case_id': item.case_id,
                    'tool_id': item.tool_id,
                    'status': item.status,
                    'image_url': item.image_url,
                    'score': score
                })

    # Launch tasks for all items
    tasks = [asyncio.create_task(_process(item)) for item in items]
    print(f"[Runner] Launched {{len(tasks)}} tasks for run {{run_id}}")
    await asyncio.gather(*tasks)
    print(f"[Runner] All tasks completed for run {{run_id}}")
    session.close()

def run_benchmark(case_ids=None, tool_ids=None):
    """Synchronous wrapper: start run and execute tasks to completion."""
    run_id = start_run(case_ids, tool_ids)
    asyncio.run(execute_run_async(run_id))
    return run_id