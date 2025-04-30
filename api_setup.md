
# Pattern Parser API Documentation
## Description of Functionalities

The Pattern Parser API is a FastAPI-based service that generates garment patterns from text or image inputs, producing downloadable DXF files. Key functionalities include:

- Input Processing: Accepts text descriptions (e.g., "FittedShirt") or images to generate garment design parameters.
- Pattern Generation: Merges input parameters with a default configuration (default.yaml), creates a garment pattern, and outputs a DXF file.
- File Serving: Stores DXF files temporarily in a dxffiles directory with unique IDs, serves them for download.


## API Endpoints and Results
### POST /generate-pattern/
- Function: Processes text or image input to generate a garment pattern and returns a unique file ID for the DXF file.
- Request: multipart/form-data with text (string, optional) or image (file, optional, e.g., JPEG, PNG).
#### Example:
```bash
  curl -X POST -F "text=FittedShirt" http://localhost:8000/generate-pattern/
```
```bash
- curl -X POST -F "image=@garment_image.jpg" http://localhost:8000/generate-pattern/ 
```
#### Result:
 - Success (200): JSON with a UUID file ID, e.g., {"file_id": "8b1d99cc-f446-4338-9fb0-ffe1da00b60a"}.
 - Error (400): JSON with error message, e.g., {"status": "error", "message": "Error processing input"}.

### GET /fileserver/{file_id}
 - Function: Serves the DXF file for download.
 - Request: Path parameter file_id (UUID string).
#### Example:
```bash
curl -O http://localhost:8000/fileserver/8b1d99cc-f446-4338-9fb0-ffe1da00b60a
```
#### Result:
 - Success (200): Downloads the DXF file named <file_id>.dxf (e.g., 8b1d99cc-f446-4338-9fb0-ffe1da00b60a.dxf).
 - Error (404): JSON with {"detail": "File not found"} if the file doesn’t exist.
## File Server Mechanism
 - DXF files are stored in dxffiles/ with UUID names from where they are fetched for every request. After serving, a background task deletes the file to free up space, ensuring temporary storage.
## Dependencies
 - The API requires Python packages listed in requirements.txt, located in the project root. Install dependencies using:
  ```bash
  pip install -r requirements.txt
  ```
## Run the API
 #### Execute:
 - uvicorn api:app --host 0.0.0.0 --port 8000
Access: The API will be available at http://localhost:8000.