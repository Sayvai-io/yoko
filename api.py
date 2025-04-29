from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from gui.pattern_parser import PatternParser
from typing import Optional
from datetime import datetime
import shutil
from pathlib import Path
import yaml
from assets.garment_programs.meta_garment import MetaGarment
from assets.bodies.body_params import BodyParameters
from pygarment.data_config import Properties
import logging
import uuid

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Pattern Parser API")

# Initialize PatternParser
parser = PatternParser()

# Static body measurements path
BODY_MEASUREMENTS_PATH = './assets/bodies/mean_all.yaml'

# Set the directory for DXF files
DXF_DIR = Path("dxffiles")
DXF_DIR.mkdir(exist_ok=True)

def load_default_yaml(file_path: str) -> dict:
    try:
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Error loading default.yaml: {str(e)}")
        raise Exception(f"Failed to load default.yaml: {str(e)}")

def merge_dicts(default_dict: dict, config_dict: dict) -> dict:
    merged = default_dict.copy()
    
    for key, value in config_dict.items():
        if key not in merged:
            # If key from config_dict is not in default_dict, skip it
            continue
        if isinstance(value, dict) and isinstance(merged[key], dict):
            # Recursively merge nested dictionaries
            merged[key] = merge_dicts(merged[key], value)
        else:
            # Update value from config_dict
            merged[key] = value
            
    return merged

@app.post("/generate-pattern/")
async def generate_pattern(
    text: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None)
):
    try:
        # Process input to get config_dict
        image_data = None
        if image:
            image_bytes = await image.read()
            content_type = image.content_type
            image_data = (image_bytes, content_type)

        config_dict = parser.process_input(text=text, image_data=image_data)
        logger.info("Generated config_dict")

        # Load default.yaml template
        default_yaml_path = './assets/design_params/default.yaml'
        default_dict = load_default_yaml(default_yaml_path)
        
        # Merge config_dict with default_dict
        updated_config_dict = merge_dicts(default_dict['design'], config_dict)
        logger.info("Merged config_dict with default.yaml template")

        # Process garment and get the file ID
        file_id = process_garment(updated_config_dict)
        logger.info(f"Generated DXF file with file_id: {file_id}")

        return {"file_id": file_id}

    except Exception as e:
        logger.error(f"Error in generate_pattern: {str(e)}")
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": str(e)}
        )

def delete_file(file_path: Path):
    try:
        file_path.unlink()  # Delete the file
        logger.info(f"Deleted file: {file_path}")
    except Exception as e:
        logger.error(f"Error deleting file: {file_path}, {e}")

@app.get("/fileserver/{file_id}")
async def fileserver(file_id: str, background_tasks: BackgroundTasks):
    # Construct the full path to the file
    file_path = DXF_DIR / f"{file_id}.dxf"

    # Check if the file exists
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    # Schedule file deletion as a background task
    background_tasks.add_task(delete_file, file_path)

    # Serve the file
    return FileResponse(
        path=str(file_path),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{file_id}.dxf"'}
    )

def process_garment(design_params: dict) -> str:
    """
    Process the garment using the provided design parameters and save the DXF file with a unique file ID.

    Args:
        design_params: Dictionary of design parameters (updated_config_dict)

    Returns:
        str: Unique file ID for the generated DXF file
    """
    print(design_params)
    try:
        # Load body measurements
        body = BodyParameters(BODY_MEASUREMENTS_PATH)
        
        # Determine garment type from design_params
        garment_type = design_params.get('meta', {}).get('upper', {}).get('v', 'generic_garment')
        
        # Create garment using design_params directly
        logger.info(f"Processing garment: {garment_type}")
        garment = [MetaGarment(garment_type, body, design_params)]

        # Generate a unique file ID
        file_id = str(uuid.uuid4())
        dxf_file_path = None

        for piece in garment:
            pattern = piece.assembly()
            
            if piece.is_self_intersecting():
                logger.warning(f'{piece.name} is Self-intersecting')
            
            # Save as json file and generate DXF
            sys_props = Properties('./system.json')
            output_dir = Path(sys_props['output'])  # Ensure output_dir is a Path
            folder = pattern.serialize(
                output_dir,
                tag='_' + datetime.now().strftime("%y%m%d-%H%M%S"),
                to_subfolder=True,
                with_3d=False,
                with_text=False,
                view_ids=False,
                with_printable=True,
                with_dxf=True
            )
            # Ensure folder is a Path object
            if isinstance(folder, str):
                folder = Path(folder)
            logger.info(f"Output folder type: {type(folder)}, path: {folder}")

            # Save body measurements
            body.save(folder)
            
            # Save design_params as YAML file in output folder
            output_yaml_path = folder / f"{piece.name}_design_params.yaml"
            with open(output_yaml_path, 'w') as f:
                yaml.safe_dump({'design': design_params}, f)
            logger.info(f"Saved design_params to {output_yaml_path}")

            logger.info(f'Success! {piece.name} saved to {folder}')

            # Find the DXF file in the output folder
            dxf_files = list(folder.glob('*.dxf'))
            if dxf_files:
                dxf_file_path = dxf_files[0]  # Take the first DXF file
                logger.info(f"DXF file found: {dxf_file_path}")
            else:
                raise Exception(f"No DXF file found in {folder}")

        if not dxf_file_path:
            raise Exception("No DXF file generated for any garment")

        # Move the DXF file to dxffiles directory with file_id
        new_dxf_path = DXF_DIR / f"{file_id}.dxf"
        shutil.move(dxf_file_path, new_dxf_path)
        logger.info(f"Moved DXF file to: {new_dxf_path}")

        return file_id

    except Exception as e:
        logger.error(f"Error processing garment: {str(e)}")
        raise Exception(f"Error processing garment: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)