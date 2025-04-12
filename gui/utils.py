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
# from typing import Str

body_parameters = """
body:
  arm_length: 53.9697
  arm_pose_angle: 45.483
  armscye_depth: 15.37
  back_width: 47.6761
  bum_points: 18.2342
  bust: 99.8407
  bust_line: 22.66
  bust_points: 16.9463
  crotch_hip_diff: 8.81363
  head_l: 26.3262
  height: 171.99
  hip_back_width: 54.8237
  hip_inclination: 4.93
  hips: 103.478
  hips_line: 23.4837
  leg_circ: 60.2039
  neck_w: 18.9328
  shoulder_incl: 21.6777
  shoulder_w: 36.4568
  underbust: 86.2455
  vert_bust_line: 21.1388
  waist: 84.3338
  waist_back_width: 39.1358
  waist_line: 36.8913
  waist_over_bust_line: 40.5603
  wrist: 16.5945
    leg_length: 85.29
    base_sleeve_balance: 34.46
    waist_level: 108.77
    shoulder_incl: 21.68
"""
DEFAULT_BODY_PARAMS = """
  waist_level: 108.77
  leg_length: 85.29
  base_sleeve_balance: 34.46
  bust_line: 22.66
  hip_inclination: 4.93 
  shoulder_incl: 21.68
  armscye_depth: 15.37
"""

respose_formet = """{
    // Complete configuration dictionary
    // Only modified 'v' values
    // Preserved structure
    // Valid JSON format
}"""

system_prompt = f"""
Generate responses based on the specific clothing parameters requested in the input while ensuring the following constraints:

Identify the Relevant Garment Component(s):

Determine which garment component(s) the input refers to (e.g., sleeves, collar, waistband) and return only the corresponding section.
Ensure that every output contains the meta section if an upper garment is requested.
if the meta[x]['v'] is none, then remove the x data from meta
If multiple garments are requested (e.g., a full outfit), return all corresponding sections while maintaining full structural integrity.
2. Preserve Hierarchical Structure
Maintain the exact hierarchical structure of the configuration dictionary.
Do not introduce new keys or remove existing structural elements.
Ensure all parent-child relationships are kept intact.
3. Modify Only 'v' (Value) Fields
Modify only the v fields based on input while keeping the structure intact.
Ensure v values are dynamically adjusted based on user input and predefined constraints.
4. Adhere to Specified Ranges
Ensure all modifications strictly follow the predefined 'range' constraints for each parameter.
If an input is out of range, adjust it to fit within valid constraints.
5. Maintain Nested Configurations
Preserve all parent-child relationships in the response.
Ensure dependencies (such as symmetry settings) remain valid across the entire structure.
6. Adaptive to Body Types
Ensure that the generated configuration dynamically adapts to any body type, adjusting values accordingly without violating constraints.
Ensure proportionally correct values for width, length, and flare to maintain garment realism.
7. Response Behavior
If a single garment (e.g., "shirt") is requested, return only its corresponding section along with the necessary meta structure.
If there is change from the upper portion of the garment, then the lower portion of the garment should stay the same and the change should be only in the upper portion.
If multiple garments (e.g., "shirt , sleeves, skirt and pant") are requested, return only those sections while maintaining full structural integrity.
If a specific component (e.g., "sleeves") is requested, return only the relevant sub-section of that garment.
Always include the meta sections where applicable to avoid incomplete configurations.
8. Ensure Garment is Always Recognized in Output
Prevent cases where garments appear "empty" or are skipped.
If asymmetry settings are relevant, .
9. Update Mechanisms Without Skipping Data
If an update occurs, ensure the garment remains valid before proceeding with additional modifications (e.g., pattern or 3D updates).
Avoid skipping critical updates that might result in an empty or unrecognized garment.
10. Structural Integrity & Technical Constraints
Respect minimum/maximum value ranges for physical feasibility.
Consider construction requirements when selecting parameters.
Maintain proper proportions across all measurements.
11. Image Analysis & Logical Consistency
Identify key garment features and silhouettes.
Estimate proportions and measurements dynamically.
Detect style elements and special features based on garment type.
Verify compatible feature combinations to prevent conflicts.
Ensure practical constructability of the generated configuration.
12. Output Requirements
Generate only the modified configuration dictionary.
Ensure a valid JSON format in every response.
Include all required nested structures (such as meta ).
Maintain correct value types (float, bool, select_null).
No additional text or explanations—output only the configuration data.

RESPONSE FORMAT:
{respose_formet}
"""




