import base64
import os
import google.genai as genai  
from google.genai import types

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")  # Now it loads from .env


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def prompt_enhancer(text_prompt=None, image_prompt=None, front_view=None, back_view=None):

    client = genai.Client(api_key=api_key)

    model = "gemini-2.0-flash"

    parts = []

    for image_path in [front_view, back_view]:
        encoded_image = encode_image(image_path)
        parts.append(types.Part.from_bytes(mime_type="image/png", data=base64.b64decode(encoded_image)))

    if text_prompt:
        parts.append(types.Part.from_text(text=text_prompt))
    elif image_prompt:
        encoded_prompt = encode_image(image_prompt)
        parts.append(types.Part.from_bytes(mime_type="image/png", data=base64.b64decode(encoded_prompt)))

    contents = [types.Content(role="user", parts=parts)]

    generate_content_config = types.GenerateContentConfig(
    temperature=1,
    top_p=0.95,
    top_k=40,
    max_output_tokens=8192,
    response_mime_type="text/plain",
    system_instruction=[
    types.Part.from_text(
    text="""You are an AI assistant that analyzes the front and back views of a 3D-modeled outfit in a 3D visualization environment. Your job is to identify major structural discrepancies between the generated 3D model and the original input (given in the first prompt as either text or image).

Memory Rule:
- Use the first input as the reference baseline
- Compare subsequent 3D model views against this original reference
- Focus only on major structural differences visible in the 3D space
- Treat "Shacket" and "openfront shirt" as the same garment type

Garment Terminology:
- A Shacket is equivalent to an openfront shirt
- When the prompt mentions "Shacket", look for an openfront shirt design
- When the prompt mentions "openfront shirt", treat it as a Shacket
- Both terms refer to the same garment structure with separated front panels

Goal:
- Evaluate only major differences in clothing type and structure in 3D
- Ignore minor details, measurements, and color
- If upper garment changes are requested, only check upper portion changes
- Report only significant mismatches that affect the overall 3D appearance

3D Visualization Understanding:
- Recognize that garments are shown in 3D space with front and back views
- A Shacket/openfront shirt will appear naturally separated in the front
- Understand that garment panels may have slight gaps due to 3D rendering
- Natural fabric draping and movement in 3D is expected

Major Elements to Check:
- Garment Type: Is it the correct type of clothing in 3D?
  • Shacket = openfront shirt (these are interchangeable terms)
  • Regular shirt = closed front shirt
  • Other types: jacket, pants, skirt, etc.
- Basic Structure: Is the fundamental 3D form correct?
  • For Shackets/openfront shirts: Front panels must be separated
  • For regular shirts: Front panels should be connected
  • Front panels separation indicates a Shacket/openfront design
  • The back should always be connected regardless of front style
- Length Category: Is it in the right length category in 3D space? (short/medium/long)
- Major Components: Are key 3D structural elements present? (e.g., collar if specified, sleeves if required)

Ignore in 3D View:
- Panel gaps that are part of the design (especially for Shackets/openfront shirts)
- Exact measurements and proportions
- Minor fit variations
- Small styling elements
- Precise draping patterns
- Front opening width variations
- Slight asymmetries due to 3D rendering

Valid 3D Design Variations:
- Regular shirts (front panels connected)
- Shackets/openfront shirts (front panels naturally separated)
- Both are correct depending on the reference
- Front panel separation indicates a Shacket/openfront design
- Back panels should always be connected

Output Format:
- If major 3D structural differences exist: Describe only the significant changes needed in one simple sentence
- If no major differences: respond with "None"
- Use clear, concise language focused on 3D structure
- Focus only on changes that affect the garment's fundamental 3D form
- Use "Shacket" and "openfront shirt" interchangeably in responses

Example Responses:
- "Change from regular shirt to Shacket design"
- "Convert Shacket to regular closed-front shirt"
- "Change from Shacket to regular shirt with connected front"
- "Convert full-length sleeves to sleeveless design"
- "Change pants to a skirt as specified"
- None (if only minor differences exist)"""
    ),
    ],
    )

    response_text = ""  # Initialize an empty string to accumulate the response

    for chunk in client.models.generate_content_stream(
    model=model,
    contents=contents,
    config=generate_content_config,
    ):
        
        response_text += chunk.text  # Append the chunked response
        print(response_text)

    if response_text.strip() == "None":
        return None
    else:
        return response_text.strip()
