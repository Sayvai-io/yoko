"""Module to handle LLM-based pattern parameter generation from text/image input"""

import base64
from typing import Dict, Union, Tuple, Optional
from datetime import datetime
from pathlib import Path
import json
import base64
from openai import OpenAI
import json

class PatternParser:
    def __init__(self):
        # Initialize any LLM/vision model clients here
        pass

    async def process_input(
        self, 
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
            # Store inputs for reference
            if text:
                self._save_text_input(text)
            if image_data:
                self._save_image_input(*image_data)

            # Pass inputs to parameter generation
            params = self._generate_dummy_params(text, image_data)

            return params

        except Exception as e:
            print(f"Error processing input: {str(e)}")
            raise

    def _save_text_input(self, text: str):
        """Save text input for reference/training"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_dir = Path("./data/pattern_inputs/text")
        save_dir.mkdir(parents=True, exist_ok=True)
        
        with open(save_dir / f"input_{timestamp}.txt", "w") as f:
            f.write(text)

    def _save_image_input(self, image_bytes: bytes, content_type: str):
        """Save image input for reference/training"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_dir = Path("./data/pattern_inputs/images") 
        save_dir.mkdir(parents=True, exist_ok=True)

        ext = content_type.split("/")[-1]
        with open(save_dir / f"input_{timestamp}.{ext}", "wb") as f:
            f.write(image_bytes)

    def _generate_dummy_params(self, text: Optional[str] = None, image_data: Optional[Tuple[bytes, str]] = None) -> Dict:
        # Ensure you have the necessary client setup for OpenAI
        client = OpenAI(api_key='sk-proj-RmbrB5vG9cCPp9QbZutyT3BlbkFJJOxFlhQxTot7ewzLtuGz')

        print("text:",text)
        print("image:",image_data)

        # Function to encode the image
        def encode_image(image_data: bytes) -> str:
            return base64.b64encode(image_data).decode("utf-8")
        
        template = """
        {
                    'meta': {
                        'upper': {'v': 'FittedShirt', 'range': ['FittedShirt', 'Shirt', None], 'type': 'select_null', 'default_prob': 0.3},
                        'wb': {'v': None, 'range': ['StraightWB', 'FittedWB', None], 'type': 'select_null', 'default_prob': 0.5},
                        'bottom': {'v': None, 'range': ['SkirtCircle', 'AsymmSkirtCircle', 'GodetSkirt', 'Pants', 'Skirt2', 'SkirtManyPanels', 'PencilSkirt', 'SkirtLevels', None], 'type': 'select_null', 'default_prob': 0.3}
                    },
                    'waistband': {
                        'waist': {'v': 1.0, 'range': [1.0, 2], 'type': 'float', 'default_prob': 0.7},
                        'width': {'v': 0.2, 'range': [0.1, 1.0], 'type': 'float', 'default_prob': 0.5}
                    },
                    'shirt': {
                        'strapless': {'v': False, 'range': [True, False], 'type': 'bool', 'default_prob': 0.8},
                        'length': {'v': 1.2, 'range': [0.5, 3.5], 'type': 'float', 'default_prob': 0.7},
                        'width': {'v': 1.05, 'range': [1.0, 1.3], 'type': 'float', 'default_prob': 0.4},
                        'flare': {'v': 1.0, 'range': [0.7, 1.6], 'type': 'float', 'default_prob': 0.4}
                    },
                    'collar': {
                        'f_collar': {'v': 'CircleNeckHalf', 'range': ['CircleNeckHalf', 'CurvyNeckHalf', 'VNeckHalf', 'SquareNeckHalf', 'TrapezoidNeckHalf', 'CircleArcNeckHalf', 'Bezier2NeckHalf'], 'type': 'select', 'default_prob': 0.4},
                        'b_collar': {'v': 'CircleNeckHalf', 'range': ['CircleNeckHalf', 'CurvyNeckHalf', 'VNeckHalf', 'SquareNeckHalf', 'TrapezoidNeckHalf', 'CircleArcNeckHalf', 'Bezier2NeckHalf'], 'type': 'select', 'default_prob': 0.8},
                        'width': {'v': 0.2, 'range': [-0.5, 1], 'type': 'float', 'default_prob': 0.4},
                        'fc_depth': {'v': 0.4, 'range': [0.3, 2], 'type': 'float', 'default_prob': 0.3},
                        'bc_depth': {'v': 0, 'range': [0, 2], 'type': 'float', 'default_prob': 0.4},
                        'fc_angle': {'v': 95, 'range': [70, 110], 'type': 'int'},
                        'bc_angle': {'v': 95, 'range': [70, 110], 'type': 'int'},
                        'f_bezier_x': {'v': 0.3, 'range': [0.05, 0.95], 'type': 'float', 'default_prob': 0.4},
                        'f_bezier_y': {'v': 0.55, 'range': [0.05, 0.95], 'type': 'float', 'default_prob': 0.4},
                        'b_bezier_x': {'v': 0.15, 'range': [0.05, 0.95], 'type': 'float', 'default_prob': 0.4},
                        'b_bezier_y': {'v': 0.1, 'range': [0.05, 0.95], 'type': 'float', 'default_prob': 0.4},
                        'f_flip_curve': {'v': False, 'range': [True, False], 'type': 'bool', 'default_prob': 0.8},
                        'b_flip_curve': {'v': False, 'range': [True, False], 'type': 'bool', 'default_prob': 0.8},
                        'component': {
                            'style': {'v': None, 'range': ['Turtle', 'SimpleLapel', 'Hood2Panels', None], 'type': 'select_null', 'default_prob': 0.6},
                            'depth': {'v': 7, 'range': [2, 8], 'type': 'int'},
                            'lapel_standing': {'v': False, 'range': [True, False], 'type': 'bool'},
                            'hood_depth': {'v': 1, 'range': [1, 2], 'type': 'float', 'default_prob': 0.6},
                            'hood_length': {'v': 1, 'range': [1, 1.5], 'type': 'float', 'default_prob': 0.6}
                        }
                    },
                    'sleeve': {
                        'sleeveless': {'v': True, 'range': [True, False], 'type': 'bool', 'default_prob': 0.7},
                        'armhole_shape': {'v': 'ArmholeCurve', 'range': ['ArmholeSquare', 'ArmholeAngle', 'ArmholeCurve'], 'type': 'select', 'default_prob': 0.7},
                        'length': {'v': 0.3, 'range': [0.1, 1.15], 'type': 'float'},
                        'connecting_width': {'v': 0.2, 'range': [0, 2], 'type': 'float', 'default_prob': 0.6},
                        'end_width': {'v': 1.0, 'range': [0.2, 2], 'type': 'float', 'default_prob': 0.4},
                        'sleeve_angle': {'v': 10, 'range': [10, 50], 'type': 'int'},
                        'opening_dir_mix': {'v': 0.1, 'range': [-0.9, 0.8], 'type': 'float', 'default_prob': 1.0},
                        'standing_shoulder': {'v': False, 'range': [True, False], 'type': 'bool', 'default_prob': 0.8},
                        'standing_shoulder_len': {'v': 5.0, 'range': [4, 10], 'type': 'float'},
                        'connect_ruffle': {'v': 1, 'range': [1, 2], 'type': 'float', 'default_prob': 0.4},
                        'smoothing_coeff': {'v': 0.25, 'range': [0.1, 0.4], 'type': 'float', 'default_prob': 0.8},
                        'cuff': {
                            'type': {'v': None, 'range': ['CuffBand', 'CuffSkirt', 'CuffBandSkirt', None], 'type': 'select_null'},
                            'top_ruffle': {'v': 1, 'range': [1, 3], 'type': 'float'},
                            'cuff_len': {'v': 0.1, 'range': [0.05, 0.9], 'type': 'float', 'default_prob': 0.7},
                            'skirt_fraction': {'v': 0.5, 'range': [0.1, 0.9], 'type': 'float', 'default_prob': 0.5},
                            'skirt_flare': {'v': 1.2, 'range': [1, 2], 'type': 'float'},
                            'skirt_ruffle': {'v': 1.0, 'range': [1, 1.5], 'type': 'float', 'default_prob': 0.3}
                        }
                    },
                    'left': {
                        'enable_asym': {'v': False, 'range': [True, False], 'type': 'bool', 'default_prob': 0.8},
                        'shirt': {
                            'strapless': {'v': False, 'range': [True, False], 'type': 'bool', 'default_prob': 0.8},
                            'width': {'v': 1.05, 'range': [1.0, 1.3], 'type': 'float', 'default_prob': 0.4},
                            'flare': {'v': 1.0, 'range': [0.7, 1.6], 'type': 'float', 'default_prob': 0.4}
                        },
                        'collar': {
                            'f_collar': {'v': 'CircleNeckHalf', 'range': ['CircleNeckHalf', 'CurvyNeckHalf', 'VNeckHalf', 'SquareNeckHalf', 'TrapezoidNeckHalf', 'CircleArcNeckHalf', 'Bezier2NeckHalf'], 'type': 'select', 'default_prob': 0.4},
                            'b_collar': {'v': 'CircleNeckHalf', 'range': ['CircleNeckHalf', 'CurvyNeckHalf', 'VNeckHalf', 'SquareNeckHalf', 'TrapezoidNeckHalf', 'CircleArcNeckHalf', 'Bezier2NeckHalf'], 'type': 'select', 'default_prob': 0.8},
                            'width': {'v': 0.2, 'range': [0, 1], 'type': 'float', 'default_prob': 0.4},
                            'fc_angle': {'v': 95, 'range': [70, 110], 'type': 'int'},
                            'bc_angle': {'v': 95, 'range': [70, 110], 'type': 'int'},
                            'f_bezier_x': {'v': 0.3, 'range': [0.05, 0.95], 'type': 'float', 'default_prob': 0.4},
                            'f_bezier_y': {'v': 0.55, 'range': [0.05, 0.95], 'type': 'float'},
                            'b_bezier_x': {'v': 0.15, 'range': [0.05, 0.95], 'type': 'float', 'default_prob': 0.4},
                            'b_bezier_y': {'v': 0.1, 'range': [0.05, 0.95], 'type': 'float'},
                            'f_flip_curve': {'v': False, 'range': [True, False], 'type': 'bool', 'default_prob': 0.8},
                            'b_flip_curve': {'v': False, 'range': [True, False], 'type': 'bool', 'default_prob': 0.8}
                        },
                        'sleeve': {
                            'sleeveless': {'v': True, 'range': [True, False], 'type': 'bool', 'default_prob': 0.7},
                            'armhole_shape': {'v': 'ArmholeCurve', 'range': ['ArmholeSquare', 'ArmholeAngle', 'ArmholeCurve'], 'type': 'select', 'default_prob': 0.7},
                            'length': {'v': 0.3, 'range': [0.1, 1.15], 'type': 'float'},
                            'connecting_width': {'v': 0.2, 'range': [0, 2], 'type': 'float', 'default_prob': 0.6},
                            'end_width': {'v': 1.0, 'range': [0.2, 2], 'type': 'float', 'default_prob': 0.4},
                            'sleeve_angle': {'v': 10, 'range': [10, 50], 'type': 'int'},
                            'opening_dir_mix': {'v': 0.1, 'range': [-0.9, 0.8], 'type': 'float', 'default_prob': 1.0},
                            'standing_shoulder': {'v': False, 'range': [True, False], 'type': 'bool', 'default_prob': 0.8},
                            'standing_shoulder_len': {'v': 5.0, 'range': [4, 10], 'type': 'float'},
                            'connect_ruffle': {'v': 1, 'range': [1, 2], 'type': 'float', 'default_prob': 0.4},
                            'smoothing_coeff': {'v': 0.25, 'range': [0.1, 0.4], 'type': 'float', 'default_prob': 0.8},
                            'cuff': {
                                'type': {'v': None, 'range': ['CuffBand', 'CuffSkirt', 'CuffBandSkirt', None], 'type': 'select_null'},
                                'top_ruffle': {'v': 1, 'range': [1, 2], 'type': 'float'},
                                'cuff_len': {'v': 0.1, 'range': [0.05, 0.9], 'type': 'float', 'default_prob': 0.7},
                                'skirt_fraction': {'v': 0.5, 'range': [0.1, 0.9], 'type': 'float', 'default_prob': 0.5},
                                'skirt_flare': {'v': 1.2, 'range': [1, 2], 'type': 'float'},
                                'skirt_ruffle': {'v': 1.0, 'range': [1, 1.5], 'type': 'float', 'default_prob': 0.3}
                            }
                        }
                    },
                    'skirt': {
                        'length': {'v': 0.2, 'range': [-0.2, 0.95], 'type': 'float'},
                        'rise': {'v': 1, 'range': [0.5, 1], 'type': 'float', 'default_prob': 0.3},
                        'ruffle': {'v': 1.3, 'range': [1, 2], 'type': 'float', 'default_prob': 0.3},
                        'bottom_cut': {'v': 0, 'range': [0, 0.9], 'type': 'float', 'default_prob': 0.3},
                        'flare': {'v': 0, 'range': [0, 20], 'type': 'int', 'default_prob': 0.5}
                    },
                    'flare-skirt': {
                        'length': {'v': 0.2, 'range': [-0.2, 0.95], 'type': 'float'},
                        'rise': {'v': 1, 'range': [0.5, 1], 'type': 'float', 'default_prob': 0.3},
                        'suns': {'v': 0.75, 'range': [0.1, 1.95], 'type': 'float'},
                        'skirt-many-panels': {
                            'n_panels': {'v': 4, 'range': [4, 15], 'type': 'int'},
                            'panel_curve': {'v': 0, 'range': [-0.35, -0.25, -0.15, 0, 0.15, 0.25, 0.35, 0.45], 'type': 'select'}
                        },
                        'asymm': {'front_length': {'v': 0.5, 'range': [0.1, 0.9], 'type': 'float', 'default_prob': 0.5}},
                        'cut': {
                            'add': {'v': False, 'range': [True, False], 'type': 'bool', 'default_prob': 0.6},
                            'depth': {'v': 0.5, 'range': [0.05, 0.95], 'type': 'float', 'default_prob': 0.6},
                            'width': {'v': 0.1, 'range': [0.05, 0.4], 'type': 'float'},
                            'place': {'v': -0.5, 'range': [-1, 1], 'type': 'float'}
                        }
                    },
                    'godet-skirt': {
                        'base': {'v': 'PencilSkirt', 'range': ['Skirt2', 'PencilSkirt'], 'type': 'select', 'default_prob': 0.7},
                        'insert_w': {'v': 15, 'range': [10, 50], 'type': 'int'},
                        'insert_depth': {'v': 20, 'range': [10, 50], 'type': 'int'},
                        'num_inserts': {'v': 4, 'range': [4, 6, 8, 10, 12], 'type': 'select'},
                        'cuts_distance': {'v': 5, 'range': [0, 10], 'type': 'int'}
                    },
                    'pencil-skirt': {
                        'length': {'v': 0.4, 'range': [0.2, 0.95], 'type': 'float'},
                        'rise': {'v': 1, 'range': [0.5, 1], 'type': 'float', 'default_prob': 0.3},
                        'flare': {'v': 1.0, 'range': [0.6, 1.5], 'type': 'float', 'default_prob': 0.3},
                        'low_angle': {'v': 0, 'range': [-30, 30], 'type': 'int', 'default_prob': 0.7},
                        'front_slit': {'v': 0, 'range': [0, 0.9], 'type': 'float', 'default_prob': 0.4},
                        'back_slit': {'v': 0, 'range': [0, 0.9], 'type': 'float', 'default_prob': 0.4},
                        'left_slit': {'v': 0, 'range': [0, 0.9], 'type': 'float', 'default_prob': 0.6},
                        'right_slit': {'v': 0, 'range': [0, 0.9], 'type': 'float', 'default_prob': 0.6},
                        'style_side_cut': {'v': None, 'range': ['Sun', 'SIGGRAPH_logo'], 'type': 'select_null', 'default_prob': 1.0}
                    },
                    'levels-skirt': {
                        'base': {'v': 'PencilSkirt', 'range': ['Skirt2', 'PencilSkirt', 'SkirtCircle', 'AsymmSkirtCircle'], 'type': 'select'},
                        'level': {'v': 'Skirt2', 'range': ['Skirt2', 'SkirtCircle', 'AsymmSkirtCircle'], 'type': 'select'},
                        'num_levels': {'v': 1, 'range': [1, 5], 'type': 'int'},
                        'level_ruffle': {'v': 1.0, 'range': [1, 1.7], 'type': 'float'},
                        'length': {'v': 0.5, 'range': [0.2, 0.95], 'type': 'float'},
                        'rise': {'v': 1, 'range': [0.5, 1], 'type': 'float', 'default_prob': 0.3},
                        'base_length_frac': {'v': 0.5, 'range': [0.2, 0.8], 'type': 'float'}
                    },
                    'pants': {
                        'length': {'v': 0.3, 'range': [0.2, 0.9], 'type': 'float'},
                        'width': {'v': 1.0, 'range': [1.0, 1.5], 'type': 'float', 'default_prob': 0.5},
                        'flare': {'v': 1.0, 'range': [0.5, 1.2], 'type': 'float', 'default_prob': 0.3},
                        'rise': {'v': 1.0, 'range': [0.5, 1], 'type': 'float', 'default_prob': 0.3},
                        'cuff': {
                            'type': {'v': None, 'range': ['CuffBand', 'CuffSkirt', 'CuffBandSkirt', None], 'type': 'select_null', 'default_prob': 0.5},
                            'top_ruffle': {'v': 1.0, 'range': [1, 2], 'type': 'float'},
                            'cuff_len': {'v': 0.1, 'range': [0.05, 0.9], 'type': 'float', 'default_prob': 0.3},
                            'skirt_fraction': {'v': 0.5, 'range': [0.1, 0.9], 'type': 'float'},
                            'skirt_flare': {'v': 1.2, 'range': [1, 2], 'type': 'float'},
                            'skirt_ruffle': {'v': 1.0, 'range': [1, 1.5], 'type': 'float'}
                        }
                    }
                }
        """

        user_messages = []

        user_messages.append({
                    "type": "text",
                    "text": f"Using this template as base:\n{template}\n\nReturn ONLY a modified configuration dictionary based on the following request. Modify just the 'v' values while preserving all structure, ranges, types and default_prob values:"
                })

        # Add text content if provided
        if text:
            user_messages.append({"type": "text", "text": text})

        # Add image content if provided
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

        # Prepare the API request
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a garment configuration assistant. Generate the response as a JSON object containing only the Python dictionary without explanation. Format the output as a valid JSON object."
                },
                {
                    "role": "user",
                    "content": user_messages
                }
            ],
            response_format={
                    "type": "json_object"
            }
        )

        config_dict = json.loads(response.choices[0].message.content)
        return config_dict
    




#  test = {
#             'meta': {
#                 'upper': {'v': 'FittedShirt', 'range': ['FittedShirt', 'Shirt', None], 'type': 'select_null', 'default_prob': 0.3},
#                 'wb': {'v': None, 'range': ['StraightWB', 'FittedWB', None], 'type': 'select_null', 'default_prob': 0.5},
#                 'bottom': {'v': None, 'range': ['SkirtCircle', 'AsymmSkirtCircle', 'GodetSkirt', 'Pants', 'Skirt2', 'SkirtManyPanels', 'PencilSkirt', 'SkirtLevels', None], 'type': 'select_null', 'default_prob': 0.3}
#             },
#             'waistband': {
#                 'waist': {'v': 1.0, 'range': [1.0, 2], 'type': 'float', 'default_prob': 0.7},
#                 'width': {'v': 0.2, 'range': [0.1, 1.0], 'type': 'float', 'default_prob': 0.5}
#             },
#             'shirt': {
#                 'strapless': {'v': False, 'range': [True, False], 'type': 'bool', 'default_prob': 0.8},
#                 'length': {'v': 1.2, 'range': [0.5, 3.5], 'type': 'float', 'default_prob': 0.7},
#                 'width': {'v': 1.05, 'range': [1.0, 1.3], 'type': 'float', 'default_prob': 0.4},
#                 'flare': {'v': 1.0, 'range': [0.7, 1.6], 'type': 'float', 'default_prob': 0.4}
#             },
#             'collar': {
#                 'f_collar': {'v': 'CircleNeckHalf', 'range': ['CircleNeckHalf', 'CurvyNeckHalf', 'VNeckHalf', 'SquareNeckHalf', 'TrapezoidNeckHalf', 'CircleArcNeckHalf', 'Bezier2NeckHalf'], 'type': 'select', 'default_prob': 0.4},
#                 'b_collar': {'v': 'CircleNeckHalf', 'range': ['CircleNeckHalf', 'CurvyNeckHalf', 'VNeckHalf', 'SquareNeckHalf', 'TrapezoidNeckHalf', 'CircleArcNeckHalf', 'Bezier2NeckHalf'], 'type': 'select', 'default_prob': 0.8},
#                 'width': {'v': 0.2, 'range': [-0.5, 1], 'type': 'float', 'default_prob': 0.4},
#                 'fc_depth': {'v': 0.4, 'range': [0.3, 2], 'type': 'float', 'default_prob': 0.3},
#                 'bc_depth': {'v': 0, 'range': [0, 2], 'type': 'float', 'default_prob': 0.4},
#                 'fc_angle': {'v': 95, 'range': [70, 110], 'type': 'int'},
#                 'bc_angle': {'v': 95, 'range': [70, 110], 'type': 'int'},
#                 'f_bezier_x': {'v': 0.3, 'range': [0.05, 0.95], 'type': 'float', 'default_prob': 0.4},
#                 'f_bezier_y': {'v': 0.55, 'range': [0.05, 0.95], 'type': 'float', 'default_prob': 0.4},
#                 'b_bezier_x': {'v': 0.15, 'range': [0.05, 0.95], 'type': 'float', 'default_prob': 0.4},
#                 'b_bezier_y': {'v': 0.1, 'range': [0.05, 0.95], 'type': 'float', 'default_prob': 0.4},
#                 'f_flip_curve': {'v': False, 'range': [True, False], 'type': 'bool', 'default_prob': 0.8},
#                 'b_flip_curve': {'v': False, 'range': [True, False], 'type': 'bool', 'default_prob': 0.8},
#                 'component': {
#                     'style': {'v': None, 'range': ['Turtle', 'SimpleLapel', 'Hood2Panels', None], 'type': 'select_null', 'default_prob': 0.6},
#                     'depth': {'v': 7, 'range': [2, 8], 'type': 'int'},
#                     'lapel_standing': {'v': False, 'range': [True, False], 'type': 'bool'},
#                     'hood_depth': {'v': 1, 'range': [1, 2], 'type': 'float', 'default_prob': 0.6},
#                     'hood_length': {'v': 1, 'range': [1, 1.5], 'type': 'float', 'default_prob': 0.6}
#                 }
#             },
#             'sleeve': {
#                 'sleeveless': {'v': True, 'range': [True, False], 'type': 'bool', 'default_prob': 0.7},
#                 'armhole_shape': {'v': 'ArmholeCurve', 'range': ['ArmholeSquare', 'ArmholeAngle', 'ArmholeCurve'], 'type': 'select', 'default_prob': 0.7},
#                 'length': {'v': 0.3, 'range': [0.1, 1.15], 'type': 'float'},
#                 'connecting_width': {'v': 0.2, 'range': [0, 2], 'type': 'float', 'default_prob': 0.6},
#                 'end_width': {'v': 1.0, 'range': [0.2, 2], 'type': 'float', 'default_prob': 0.4},
#                 'sleeve_angle': {'v': 10, 'range': [10, 50], 'type': 'int'},
#                 'opening_dir_mix': {'v': 0.1, 'range': [-0.9, 0.8], 'type': 'float', 'default_prob': 1.0},
#                 'standing_shoulder': {'v': False, 'range': [True, False], 'type': 'bool', 'default_prob': 0.8},
#                 'standing_shoulder_len': {'v': 5.0, 'range': [4, 10], 'type': 'float'},
#                 'connect_ruffle': {'v': 1, 'range': [1, 2], 'type': 'float', 'default_prob': 0.4},
#                 'smoothing_coeff': {'v': 0.25, 'range': [0.1, 0.4], 'type': 'float', 'default_prob': 0.8},
#                 'cuff': {
#                     'type': {'v': None, 'range': ['CuffBand', 'CuffSkirt', 'CuffBandSkirt', None], 'type': 'select_null'},
#                     'top_ruffle': {'v': 1, 'range': [1, 3], 'type': 'float'},
#                     'cuff_len': {'v': 0.1, 'range': [0.05, 0.9], 'type': 'float', 'default_prob': 0.7},
#                     'skirt_fraction': {'v': 0.5, 'range': [0.1, 0.9], 'type': 'float', 'default_prob': 0.5},
#                     'skirt_flare': {'v': 1.2, 'range': [1, 2], 'type': 'float'},
#                     'skirt_ruffle': {'v': 1.0, 'range': [1, 1.5], 'type': 'float', 'default_prob': 0.3}
#                 }
#             },
#             'left': {
#                 'enable_asym': {'v': False, 'range': [True, False], 'type': 'bool', 'default_prob': 0.8},
#                 'shirt': {
#                     'strapless': {'v': False, 'range': [True, False], 'type': 'bool', 'default_prob': 0.8},
#                     'width': {'v': 1.05, 'range': [1.0, 1.3], 'type': 'float', 'default_prob': 0.4},
#                     'flare': {'v': 1.0, 'range': [0.7, 1.6], 'type': 'float', 'default_prob': 0.4}
#                 },
#                 'collar': {
#                     'f_collar': {'v': 'CircleNeckHalf', 'range': ['CircleNeckHalf', 'CurvyNeckHalf', 'VNeckHalf', 'SquareNeckHalf', 'TrapezoidNeckHalf', 'CircleArcNeckHalf', 'Bezier2NeckHalf'], 'type': 'select', 'default_prob': 0.4},
#                     'b_collar': {'v': 'CircleNeckHalf', 'range': ['CircleNeckHalf', 'CurvyNeckHalf', 'VNeckHalf', 'SquareNeckHalf', 'TrapezoidNeckHalf', 'CircleArcNeckHalf', 'Bezier2NeckHalf'], 'type': 'select', 'default_prob': 0.8},
#                     'width': {'v': 0.2, 'range': [0, 1], 'type': 'float', 'default_prob': 0.4},
#                     'fc_angle': {'v': 95, 'range': [70, 110], 'type': 'int'},
#                     'bc_angle': {'v': 95, 'range': [70, 110], 'type': 'int'},
#                     'f_bezier_x': {'v': 0.3, 'range': [0.05, 0.95], 'type': 'float', 'default_prob': 0.4},
#                     'f_bezier_y': {'v': 0.55, 'range': [0.05, 0.95], 'type': 'float'},
#                     'b_bezier_x': {'v': 0.15, 'range': [0.05, 0.95], 'type': 'float', 'default_prob': 0.4},
#                     'b_bezier_y': {'v': 0.1, 'range': [0.05, 0.95], 'type': 'float'},
#                     'f_flip_curve': {'v': False, 'range': [True, False], 'type': 'bool', 'default_prob': 0.8},
#                     'b_flip_curve': {'v': False, 'range': [True, False], 'type': 'bool', 'default_prob': 0.8}
#                 },
#                 'sleeve': {
#                     'sleeveless': {'v': True, 'range': [True, False], 'type': 'bool', 'default_prob': 0.7},
#                     'armhole_shape': {'v': 'ArmholeCurve', 'range': ['ArmholeSquare', 'ArmholeAngle', 'ArmholeCurve'], 'type': 'select', 'default_prob': 0.7},
#                     'length': {'v': 0.3, 'range': [0.1, 1.15], 'type': 'float'},
#                     'connecting_width': {'v': 0.2, 'range': [0, 2], 'type': 'float', 'default_prob': 0.6},
#                     'end_width': {'v': 1.0, 'range': [0.2, 2], 'type': 'float', 'default_prob': 0.4},
#                     'sleeve_angle': {'v': 10, 'range': [10, 50], 'type': 'int'},
#                     'opening_dir_mix': {'v': 0.1, 'range': [-0.9, 0.8], 'type': 'float', 'default_prob': 1.0},
#                     'standing_shoulder': {'v': False, 'range': [True, False], 'type': 'bool', 'default_prob': 0.8},
#                     'standing_shoulder_len': {'v': 5.0, 'range': [4, 10], 'type': 'float'},
#                     'connect_ruffle': {'v': 1, 'range': [1, 2], 'type': 'float', 'default_prob': 0.4},
#                     'smoothing_coeff': {'v': 0.25, 'range': [0.1, 0.4], 'type': 'float', 'default_prob': 0.8},
#                     'cuff': {
#                         'type': {'v': None, 'range': ['CuffBand', 'CuffSkirt', 'CuffBandSkirt', None], 'type': 'select_null'},
#                         'top_ruffle': {'v': 1, 'range': [1, 2], 'type': 'float'},
#                         'cuff_len': {'v': 0.1, 'range': [0.05, 0.9], 'type': 'float', 'default_prob': 0.7},
#                         'skirt_fraction': {'v': 0.5, 'range': [0.1, 0.9], 'type': 'float', 'default_prob': 0.5},
#                         'skirt_flare': {'v': 1.2, 'range': [1, 2], 'type': 'float'},
#                         'skirt_ruffle': {'v': 1.0, 'range': [1, 1.5], 'type': 'float', 'default_prob': 0.3}
#                     }
#                 }
#             },
#             'skirt': {
#                 'length': {'v': 0.2, 'range': [-0.2, 0.95], 'type': 'float'},
#                 'rise': {'v': 1, 'range': [0.5, 1], 'type': 'float', 'default_prob': 0.3},
#                 'ruffle': {'v': 1.3, 'range': [1, 2], 'type': 'float', 'default_prob': 0.3},
#                 'bottom_cut': {'v': 0, 'range': [0, 0.9], 'type': 'float', 'default_prob': 0.3},
#                 'flare': {'v': 0, 'range': [0, 20], 'type': 'int', 'default_prob': 0.5}
#             },
#             'flare-skirt': {
#                 'length': {'v': 0.2, 'range': [-0.2, 0.95], 'type': 'float'},
#                 'rise': {'v': 1, 'range': [0.5, 1], 'type': 'float', 'default_prob': 0.3},
#                 'suns': {'v': 0.75, 'range': [0.1, 1.95], 'type': 'float'},
#                 'skirt-many-panels': {
#                     'n_panels': {'v': 4, 'range': [4, 15], 'type': 'int'},
#                     'panel_curve': {'v': 0, 'range': [-0.35, -0.25, -0.15, 0, 0.15, 0.25, 0.35, 0.45], 'type': 'select'}
#                 },
#                 'asymm': {'front_length': {'v': 0.5, 'range': [0.1, 0.9], 'type': 'float', 'default_prob': 0.5}},
#                 'cut': {
#                     'add': {'v': False, 'range': [True, False], 'type': 'bool', 'default_prob': 0.6},
#                     'depth': {'v': 0.5, 'range': [0.05, 0.95], 'type': 'float', 'default_prob': 0.6},
#                     'width': {'v': 0.1, 'range': [0.05, 0.4], 'type': 'float'},
#                     'place': {'v': -0.5, 'range': [-1, 1], 'type': 'float'}
#                 }
#             },
#             'godet-skirt': {
#                 'base': {'v': 'PencilSkirt', 'range': ['Skirt2', 'PencilSkirt'], 'type': 'select', 'default_prob': 0.7},
#                 'insert_w': {'v': 15, 'range': [10, 50], 'type': 'int'},
#                 'insert_depth': {'v': 20, 'range': [10, 50], 'type': 'int'},
#                 'num_inserts': {'v': 4, 'range': [4, 6, 8, 10, 12], 'type': 'select'},
#                 'cuts_distance': {'v': 5, 'range': [0, 10], 'type': 'int'}
#             },
#             'pencil-skirt': {
#                 'length': {'v': 0.4, 'range': [0.2, 0.95], 'type': 'float'},
#                 'rise': {'v': 1, 'range': [0.5, 1], 'type': 'float', 'default_prob': 0.3},
#                 'flare': {'v': 1.0, 'range': [0.6, 1.5], 'type': 'float', 'default_prob': 0.3},
#                 'low_angle': {'v': 0, 'range': [-30, 30], 'type': 'int', 'default_prob': 0.7},
#                 'front_slit': {'v': 0, 'range': [0, 0.9], 'type': 'float', 'default_prob': 0.4},
#                 'back_slit': {'v': 0, 'range': [0, 0.9], 'type': 'float', 'default_prob': 0.4},
#                 'left_slit': {'v': 0, 'range': [0, 0.9], 'type': 'float', 'default_prob': 0.6},
#                 'right_slit': {'v': 0, 'range': [0, 0.9], 'type': 'float', 'default_prob': 0.6},
#                 'style_side_cut': {'v': None, 'range': ['Sun', 'SIGGRAPH_logo'], 'type': 'select_null', 'default_prob': 1.0}
#             },
#             'levels-skirt': {
#                 'base': {'v': 'PencilSkirt', 'range': ['Skirt2', 'PencilSkirt', 'SkirtCircle', 'AsymmSkirtCircle'], 'type': 'select'},
#                 'level': {'v': 'Skirt2', 'range': ['Skirt2', 'SkirtCircle', 'AsymmSkirtCircle'], 'type': 'select'},
#                 'num_levels': {'v': 1, 'range': [1, 5], 'type': 'int'},
#                 'level_ruffle': {'v': 1.0, 'range': [1, 1.7], 'type': 'float'},
#                 'length': {'v': 0.5, 'range': [0.2, 0.95], 'type': 'float'},
#                 'rise': {'v': 1, 'range': [0.5, 1], 'type': 'float', 'default_prob': 0.3},
#                 'base_length_frac': {'v': 0.5, 'range': [0.2, 0.8], 'type': 'float'}
#             },
#             'pants': {
#                 'length': {'v': 0.3, 'range': [0.2, 0.9], 'type': 'float'},
#                 'width': {'v': 1.0, 'range': [1.0, 1.5], 'type': 'float', 'default_prob': 0.5},
#                 'flare': {'v': 1.0, 'range': [0.5, 1.2], 'type': 'float', 'default_prob': 0.3},
#                 'rise': {'v': 1.0, 'range': [0.5, 1], 'type': 'float', 'default_prob': 0.3},
#                 'cuff': {
#                     'type': {'v': None, 'range': ['CuffBand', 'CuffSkirt', 'CuffBandSkirt', None], 'type': 'select_null', 'default_prob': 0.5},
#                     'top_ruffle': {'v': 1.0, 'range': [1, 2], 'type': 'float'},
#                     'cuff_len': {'v': 0.1, 'range': [0.05, 0.9], 'type': 'float', 'default_prob': 0.3},
#                     'skirt_fraction': {'v': 0.5, 'range': [0.1, 0.9], 'type': 'float'},
#                     'skirt_flare': {'v': 1.2, 'range': [1, 2], 'type': 'float'},
#                     'skirt_ruffle': {'v': 1.0, 'range': [1, 1.5], 'type': 'float'}
#                 }
#             }
#         }