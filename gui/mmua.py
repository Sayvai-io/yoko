import base64
import os
import google.genai as genai  
from google.genai import types

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")  # Now it loads from .env

call_count = 0  # Global variable to count function calls

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def prompt_enhancer(text_prompt=None, image_prompt=None, front_view=None, back_view=None):

    global call_count
    if call_count >= 10:
        print("Function has been called 10 times. No further calls will be processed.")
        return None
    
    call_count += 1

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
- Treat all garment types with equal importance and consideration

Garment Terminology and Types (all equally important and DISTINCT):
- Regular shirts: Basic shirts with connected front panels
- Fitted shirts: More tailored shirts with connected front panels, generally closer to the body
- Open-front garments: Items with separated front panels (Shacket)
- Bottoms: Pants, skirts, shorts of various styles
- Outerwear: Jackets, coats, vests
- Other garments: Dresses, jumpsuits, specialty wear

Goal:
- Evaluate only major differences in clothing type and structure in 3D
- Ignore minor details, measurements, and color
- If upper garment changes are requested, only check upper portion changes
- Report only significant mismatches that affect the overall 3D appearance
- If no major structural differences exist, respond with "None"
- Treat all garment categories with equal importance

3D Visualization Understanding:
- Recognize that garments are shown in 3D space with front and back views
- Understand that different garment types have different expected structures
- Natural fabric draping and slight gaps are expected in 3D rendering
- Minor fit variations are normal and should not be flagged

Major Elements to Check:
- Garment Type: Is it the correct type of clothing in 3D?
  • Regular Shirt = standard shirt with connected front panels
  • Fitted Shirt = more tailored shirt with connected front panels
  • Open-front garment = shirt with deliberately separated front
  • Other types: jacket, pants, skirt, etc.
- Basic Structure: Is the fundamental 3D form correct?
  • For both regular and fitted shirts: Front panels should be connected
  • For open-front garments: Front panels are separated
  • The back should always be connected regardless of front style
- Length Category: Is it in the right length category in 3D space? (short/medium/long)
  • For skirts: "Long skirt" or "full skirt" means a skirt that covers the entire leg or reaches the ankle
  • "Full-length skirt" must extend to near ankle length in the 3D model
  • Midi skirts should reach below the knee but above the ankle
  • Short/mini skirts should be well above the knee
- Major Components: Are key 3D structural elements present? (e.g., collar if specified, sleeves if required)

Ignore in 3D View:
- Minor design variations that don't change the fundamental garment type
- Exact measurements and proportions (except for skirt length categories)
- Minor fit variations
- Small styling elements
- Precise draping patterns
- Slight asymmetries due to 3D rendering

Crucial decision rules:
- Regular shirts and fitted shirts are DIFFERENT garment types but BOTH have connected front panels
- When the user requests just "shirt", default to checking for a regular shirt with connected front
- When the user requests "fitted shirt", check for a more tailored shirt with connected front
- NEVER suggest converting a regular shirt or fitted shirt to an open-front garment unless explicitly requested
- Only suggest converting to an open-front design if the original reference explicitly asked for it
- If the 3D model shows connected front panels and the reference requests a shirt, respond with "None"
- If the prompt mentions "long skirt" or "full skirt" same goes for sleeves and pants check the length against the expected value (0.95). If it does not match, report this as a discrepancy.
- If no specific length is mentioned (e.g., just "skirt"), do not flag the output as incorrect; accept whatever is shown as correct.

Output Format:
- If major 3D structural differences exist: Describe only the significant changes needed in one simple sentence
- If no major differences: respond with "None" (this is crucial to prevent unnecessary iterations)
- Use clear, concise language focused on 3D structure
- Focus only on changes that affect the garment's fundamental 3D form
- "None" (if only minor differences exist or the model is already correct)"""
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

