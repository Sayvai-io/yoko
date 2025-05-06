"""Module to handle LLM-based pattern parameter generation from text/image input"""

import base64
from typing import Dict, Union, Tuple, Optional
from datetime import datetime
from pathlib import Path
import json
import base64
from openai import OpenAI
import json
import os
from dotenv import load_dotenv
from gui.utils import system_prompt, template
import logging
from rich.logging import RichHandler
from rich.console import Console
from db.models import Message, MessageTypeEnum


load_dotenv()

# Initialize the rich console and logger
# console = Console()
# logging.basicConfig(level=logging.DEBUG, format="%(message)s",
#                     handlers=[RichHandler(rich_tracebacks=True, console=console)])
# logger = logging.getLogger("rich")


class PatternParser:
    def __init__(self):
        # Initialize any LLM/vision model clients here
        # logger.info("[bold green]PatternParser initialized[/bold green]")
        pass

    def process_input(
            self,
            curr_dict,
            prompts,
            text: Optional[str] = None,
            image_data: Optional[Tuple[bytes, str]] = None
    ) -> Dict:
        """Process text and/or image input to generate pattern parameters

        Args:
            text: Text description of the desired garment
            image_data: Tuple of (image_bytes, content_type)

        Returns:
            Dictionary of pattern parameters
        """
        try:
            self.curr_dict = str(curr_dict)
            # Store inputs for reference
            if text:
                self._save_text_input(text)
            if image_data:
                self._save_image_input(*image_data)

            # Pass inputs to parameter generation
            # logger.info(f"[bold green] type of image data {type(image_data)} [/bold green]")
            params = self._generate_dummy_params(prompts, text, image_data)

            return params

        except Exception as e:
            # logger.error(f"[bold red]Error processing input:[/bold red] {str(e)}")
            raise

    def _save_text_input(self, text: str):
        """Save text input for reference/training"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_dir = Path("./data/pattern_inputs/text")
        save_dir.mkdir(parents=True, exist_ok=True)

        with open(save_dir / f"input_{timestamp}.txt", "w") as f:
            f.write(text)

        # logger.info(f"[bold cyan]Text input saved[/bold cyan] to {save_dir / f'input_{timestamp}.txt'}")

    def _save_image_input(self, image_bytes: bytes, content_type: str):
        """Save image input for reference/training"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_dir = Path("./data/pattern_inputs/images")
        save_dir.mkdir(parents=True, exist_ok=True)

        ext = content_type.split("/")[-1]
        with open(save_dir / f"input_{timestamp}.{ext}", "wb") as f:
            f.write(image_bytes)

        # logger.info(f"[bold cyan]Image input saved[/bold cyan] to {save_dir / f'input_{timestamp}.{ext}'}")

    def _generate_dummy_params(self, prompts: [Message] = None, text: Optional[str] = None, image_data: bytes = None) -> Dict:

        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

        def encode_image(image_data: bytes) -> str:
            return base64.b64encode(image_data[0]).decode("utf-8")
        user_messages = []
        for prompt in prompts:
            if prompt.message_type == MessageTypeEnum.IMAGE:
                default_text = "From the provided image and template, please generate a parameter configuration for the garment."
                user_messages.append({"type": "text", "text": default_text})
                user_messages.append(
                    {
                        "type": "image_url",
                        "image_url": {"url": prompt.message},
                    }
                )
            elif prompt.message_type == MessageTypeEnum.TEXT:
                user_messages.append({"type": "text", "text": prompt.message})

        user_messages.append({
            "type": "text",
            "text": f"Using this template as base:\n{template}\n\nReturn ONLY a modified configuration dictionary based "
                    f"on the following request. Modify just the 'v' values while preserving all structure, ranges, types"
                    f" and default_prob values:"
        })

        if text:
            user_messages.append({"type": "text", "text": text})
        else:
            default_text = "From the provided image and template, please generate a parameter configuration for the garment."
            user_messages.append({"type": "text", "text": default_text})

        if image_data:
            base64_image = encode_image(image_data)
            user_messages.append(
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                }
            )

        if not user_messages:
            raise ValueError("Either text or image_file must be provided.")
        print(user_messages)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": system_prompt}] + [
                {"role": "user", "content": user_messages}
            ],
            response_format={"type": "json_object"}
        )

        config_dict = json.loads(response.choices[0].message.content)
        # print_data(config_dict)

        return config_dict

def print_data(data):
    for key, value in data.items():
        print(f"\n=== {key} ===")
        print_params(value)

def print_params(data, indent=""):
    for key, value in data.items():
        if isinstance(value, dict):
            if 'v' in value and 'range' in value:
                # Print simple parameters with their values
                print(f"{indent}{key} = {value['v']}")
            else:
                # Print nested structure headers
                print(f"{indent}{key}:")
                print_params(value, indent + "  ")
        else:
            print(f"{indent}{key} = {value}")
            # Print non-dictionary values directly
