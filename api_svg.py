from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import logging
from pygarment.pattern.wrappers import VisPattern
import time
from pathlib import Path
from pydantic import BaseModel

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="File Generation API")

tmp_path = Path.cwd() / 'tmp_gui' / 'display' / "temp_folder"

class PatternRequest(BaseModel):
    pattern_data: dict


def _view_serialize_with_json(pattern_data: dict = None, name: str = "Configured_design"):
    """Save a sewing pattern svg representation to tmp folder be used
    for display"""
    spattern = VisPattern()
    spattern.name = "Test"
    spattern.pattern = pattern_data

    try:
        svg_filename = f'{name}_pattern_{time.time()}.svg'
        dwg = spattern.get_svg(tmp_path / svg_filename,
                                with_text=False,
                                view_ids=False,
                                flat=False,
                                margin=0
        )
        dwg.save()
        return tmp_path / svg_filename

    except Exception as e:
        logger.error(f"Error generating SVG: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate SVG: {str(e)}")


@app.post("/generate/2d")
def generate_2D(request: PatternRequest):

    file_name = _view_serialize_with_json(request.pattern_data)
    file_path = tmp_path / file_name
    return FileResponse(
        path=str(file_path),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{file_name}.svg"'}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api_svg:app", host="0.0.0.0", port=8000, reload=True)
