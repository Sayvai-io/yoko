"""Callback functions & State info for Sewing Pattern Configurator """

# NOTE: NiceGUI reference: https://nicegui.io/

import yaml
import traceback
from datetime import datetime, timedelta
from argparse import Namespace
import numpy as np
import shutil
from pathlib import Path
import time
import base64
from pprint import pprint
from collections import OrderedDict
import pprint as pp_module
from .mmua import prompt_enhancer
from db.services import ChatService, MessageService
from nicegui import ui, app, events, background_tasks
from sqlalchemy.orm import Session
# Async execution of regular functions
from concurrent.futures import ThreadPoolExecutor
import asyncio
from db.models import generate_unique_uid, Chat, MessageTypeEnum
import ast
# Customdede
from .gui_pattern import GUIPattern
from .pattern_parser import PatternParser

theme_colors = Namespace(
    primary='cadetblue',
    secondary='#a33e6c',
    accent='#a82c64',
    dark='#4d1f48',
    positive='#22ba38',
    negative='#f50000',
    info='#31CCEC',
    warning='#9333ea'
)

# State of GUI
class GUIState:
    """State of GUI-related objects

        NOTE: "#" is used as a separator in GUI keys to avoid confusion with
            symbols that can be (typically) used in body/design parameter names
            ('_', '-', etc.)

    """
    def __init__(self, user, db:Session) -> None:
        self.user = user
        self.chat_service = ChatService(db, user_id=user.id)
        self.message_service = MessageService(db, user_id=user.id)
        self.chat_uid = generate_unique_uid(model=Chat, field='chat_uid')
        self.window = None
        self.content_type = None
        self.image_bytes = None
        self.last_chat_input = None
        self.temp_session_id= None
        # Pattern
        self.pattern_state = GUIPattern()

        # Pattern display constants
        self.canvas_aspect_ratio = 1500. / 900   # Millimiter paper
        self.w_rel_body_size = 0.5  # Body size as fraction of horisontal canvas axis
        self.h_rel_body_size = 0.95
        self.background_body_scale = 1 / 171.99   # Inverse of the mean_all body height from GGG
        self.background_body_canvas_center = 0.273  # Fraction of the canvas (millimiter paper)
        self.w_canvas_pad, self.h_canvas_pad = 0.011, 0.04
        self.body_outline_classes = ''   # Application of pattern&body scaling when it overflows

        # Paths setup
        # Static images for GUI
        self.path_static_img = '/img'
        app.add_static_files(self.path_static_img, './assets/img')

        # 3D updates
        self.path_static_3d = '/geo'
        self.garm_3d_filename = f'garm_3d_{self.pattern_state.id}.glb'
        self.local_path_3d = Path('./tmp_gui/garm_3d')
        self.local_path_3d.mkdir(parents=True, exist_ok=True)
        app.add_static_files(self.path_static_3d, self.local_path_3d)
        app.add_static_files('/body', './assets/bodies')

        # Elements
        self.ui_design_subtabs = {}
        self.ui_pattern_display = None
        self._async_executor = ThreadPoolExecutor(1)

        self.pattern_state.reload_garment()
        self.stylings()
        self.layout()

        self.pattern_parser = PatternParser()

    def release(self):
        """Clean-up after the sesssion"""
        self.pattern_state.release()
        (self.local_path_3d / self.garm_3d_filename).unlink(missing_ok=True)

    # Initial definitions
    def stylings(self):
        """Theme definition"""
        # Theme
        # Here: https://quasar.dev/style/theme-builder
        ui.colors(
            primary=theme_colors.primary,
            secondary=theme_colors.secondary,
            accent=theme_colors.accent,
            dark=theme_colors.dark,
            positive=theme_colors.positive,
            negative=theme_colors.negative,
            info=theme_colors.info,
            warning=theme_colors.warning
        )

    # SECTION Top level layout
    def layout(self):
        """Overall page layout"""

        # as % of viewport width/height
        self.h_header = 5
        self.h_params_content = 88
        self.h_garment_display = 74
        self.w_garment_display = 65
        self.w_splitter_design = 32
        self.scene_base_resoltion = (1024, 800)
        self.w_chat_sidebar = 20  # Width for chat history sidebar (percentage of viewport width)
        self.sidebar_visible = False  # Initial state: hidden
        self.sidebar_floating = True  # Make sidebar float over content instead of pushing it

        # Helpers
        self.def_pattern_waiting()
        # TODOLOW One dialog for both?
        self.def_design_file_dialog()
        self.def_body_file_dialog()
        # Configurator GUI
        with ui.element('div').classes('w-full'):
            # Floating chat history sidebar (moved to left side)
            self.sidebar_column = ui.column().classes(f'fixed left-0 top-[{self.h_header}vh] h-[90vh] w-[{self.w_chat_sidebar}vw] bg-white shadow-lg z-10 transition-all duration-300 ease-in-out').style('transform: translateX(-100%)')
            with self.sidebar_column:
                with ui.row().classes('w-full justify-between items-center p-2 border-b'):
                    ui.button(icon='chevron_left', on_click=self.toggle_sidebar).props('flat dense').classes('text-gray-600')
                    ui.label("Chat History").classes("text-lg font-semibold")
                self.def_chat_history()

            # Toggle button for sidebar (fixed position - moved to left side)
            self.sidebar_toggle_btn = ui.button(icon='chat', on_click=self.toggle_sidebar).classes(f'fixed top-[{self.h_header + 1}vh] left-2 z-20').props('round color=primary')
            
            with ui.row(wrap=False).classes(f'w-full h-[{self.h_params_content}dvh] p-0 m-0 '):
                self.def_param_tabs_layout()
                self.view_tabs_layout()
            
            # Overall wrapping
            # NOTE: https://nicegui.io/documentation/section_pages_routing#page_layout
        with ui.header(elevated=True, fixed=False).classes(f'h-[{self.h_header}vh] items-center bg-gradient-to-br from-blue-100 to-indigo-100  justify-end py-0 px-4 m-0'):
            ui.label('Yokostyles - GarmentCode design configurator').classes('mr-auto text-black').style('font-size: 150%; font-weight: 400')
            with ui.label(f"User - {self.user.email}").classes('ml-auto text-black').style('font-size: 120%; font-weight: 400'):
                ui.button('Logout', on_click=lambda: ui.navigate.to('/logout')).classes("ml-4")

    def toggle_sidebar(self):
        """Toggle visibility of the sidebar"""
        self.sidebar_visible = not self.sidebar_visible
        if self.sidebar_visible:
            self.sidebar_column.style('transform: translateX(0%)')
        else:
            self.sidebar_column.style('transform: translateX(-100%)')

    def view_tabs_layout(self):
        """2D/3D view tabs"""
        with ui.column(wrap=False).classes(f'h-[{self.h_params_content}vh] w-full items-center'):
            with ui.tabs() as tabs:
                self.ui_2d_tab = ui.tab('Sewing Pattern')
                self.ui_3d_tab = ui.tab('3D view')
            with ui.tab_panels(tabs, value=self.ui_2d_tab, animated=True).classes('w-full h-full items-center'):
                with ui.tab_panel(self.ui_2d_tab).classes('w-full h-full items-center justify-center p-0 m-0'):
                    self.def_pattern_display()
                with ui.tab_panel(self.ui_3d_tab).classes('w-full h-full items-center p-0 m-0'):
                    self.def_3d_scene()
            with ui.row().classes('justify-self-end items-center'):
                file_format = ui.select(
                    ['SVG', 'PNG', 'PDF', 'DXF'],
                    value='SVG',
                    label='Format'
                ).classes('w-32')
                ui.button('Download', on_click=lambda: self.state_download(file_format.value)).classes('justify-self-end')
            # ui.button('Download Current Garment', on_click=lambda: self.state_download()).classes('justify-self-end')

    # !SECTION
    # SECTION -- Parameter menu
    def def_param_tabs_layout(self):
        """Layout of tabs with parameters"""
        with ui.column(wrap=False).classes(f'h-[{self.h_params_content}vh]'):
            with ui.tabs() as self.tabs:
                self.ui_parse_tab = ui.tab('Parse Design')    # Moved to first position
                self.ui_design_tab = ui.tab('Design parameters')
                self.ui_body_tab = ui.tab('Body parameters')
            with ui.tab_panels(self.tabs, value=self.ui_parse_tab, animated=True).classes('w-full h-full items-center'):  # Changed default value to parse tab
                with ui.tab_panel(self.ui_parse_tab).classes('w-full h-full items-center p-0 m-0'):
                    self.def_parse_tab()
                with ui.tab_panel(self.ui_design_tab).classes('w-full h-full items-center p-0 m-0'):
                    self.def_design_tab()
                with ui.tab_panel(self.ui_body_tab).classes('w-full h-full items-center p-0 m-0'):
                    self.def_body_tab()

    def def_body_tab(self):

        # Set of buttons
        with ui.row():
            ui.button('Upload', on_click=self.ui_body_dialog.open)

        self.ui_active_body_refs = {}
        self.ui_passive_body_refs = {}
        with ui.scroll_area().classes('w-full h-full p-0 m-0'): # NOTE: p-0 m-0 gap-0 dont' seem to have effect
            body = self.pattern_state.body_params
            for param in body:
                param_name = param.replace('_', ' ').capitalize()
                elem = ui.number(
                        label=param_name,
                        value=str(body[param]),
                        format='%.2f',
                        precision=2,
                        step=0.5,
                ).classes('text-[0.85rem]')

                if param[0] == '_':  # Info elements for calculatable parameters
                    elem.disable()
                    self.ui_passive_body_refs[param] = elem
                else:   # active elements accepting input
                    # NOTE: e.sender == UI object, e.value == new value
                    elem.on_value_change(lambda e, dic=body, param=param: self.update_pattern_ui_state(
                        dic, param, e.value, body_param=True
                    ))
                    self.ui_active_body_refs[param] = elem

    def def_flat_design_subtab(self, ui_elems, design_params, use_collapsible=False):
        """Group of design parameters"""
        for param in design_params:
            param_name = param.replace('_', ' ').capitalize()
            if 'v' not in design_params[param]:
                ui_elems[param] = {}
                if use_collapsible:
                    with ui.expansion().classes('w-full p-0 m-0') as expansion:
                        with expansion.add_slot('header'):
                            ui.label(f'{param_name}').classes('text-base self-center w-full h-full p-0 m-0')
                        with ui.row().classes('w-full h-full p-0 m-0'):  # Ensures correct application of style classes for children
                            self.def_flat_design_subtab(ui_elems[param], design_params[param])
                else:
                    with ui.card().classes('w-full shadow-md border m-0 rounded-md'):
                        ui.label(f'{param_name}').classes('text-base self-center w-full h-full p-0 m-0')
                        self.def_flat_design_subtab(ui_elems[param], design_params[param])
            else:
                # Leaf value
                p_type = design_params[param]['type']
                val = design_params[param]['v']
                p_range = design_params[param]['range']
                if 'select' in p_type:
                    values = design_params[param]['range']
                    if 'null' in p_type and None not in values:
                        values.append(None)  # NOTE: Displayable value
                    ui.label(param_name).classes('p-0 m-0 mt-2 text-stone-500 text-[0.85rem]')
                    ui_elems[param] = ui.select(
                        values, value=val,
                        on_change=lambda e, dic=design_params, param=param: self.update_pattern_ui_state(dic, param, e.value)
                    ).classes('w-full')
                elif p_type == 'bool':
                    ui_elems[param] = ui.switch(
                        param_name, value=val,
                        on_change=lambda e, dic=design_params, param=param: self.update_pattern_ui_state(dic, param, e.value)
                    ).classes('text-stone-500')
                elif p_type == 'float' or p_type == 'int':
                    ui.label(param_name).classes('p-0 m-0 mt-2 text-stone-500 text-[0.85rem]')
                    ui_elems[param] = ui.slider(
                        value=val,
                        min=p_range[0],
                        max=p_range[1],
                        step=0.025 if p_type == 'float' else 1,
                    ).props('snap label').classes('w-full')  \
                        .on('update:model-value',
                            lambda e, dic=design_params, param=param: self.update_pattern_ui_state(dic, param, e.args),
                            throttle=0.5, leading_events=False)

                    # NOTE Events control: https://nicegui.io/documentation/slider#throttle_events_with_leading_and_trailing-options
                elif 'file' in p_type:
                    print(f'GUI::NotImplementedERROR::{param}::'
                          '"file" parameter type is not yet supported in Web GarmentCode. '
                          'Creation of corresponding UI element skipped'
                    )
                else:
                    print(f'GUI::WARNING::Unknown parameter type: {p_type}')
                    ui_elems[param] = ui.input(label=param_name, value=val, placeholder='Type the value',
                        validation={'Input too long': lambda value: len(value) < 20},
                        on_change=lambda e, dic=design_params, param=param: self.update_pattern_ui_state(dic, param, e.value)
                    ).classes('w-full')

    def def_design_tab(self):
        # Set of buttons
        with ui.row():
            ui.button('Random', on_click=self.random)
            ui.button('Default', on_click=self.default)
            ui.button('Upload', on_click=self.ui_design_dialog.open)

        # Design parameters
        design_params = self.pattern_state.design_params
        self.ui_design_refs = {}
        if self.pattern_state.is_design_sectioned():
            # Use tabs to represent top-level sections
            with ui.splitter(value=self.w_splitter_design).classes('w-full h-full p-0 m-0') as splitter:
                with splitter.before:
                    with ui.tabs().props('vertical').classes('w-full h-full') as tabs:
                        for param in design_params:
                            # Tab
                            self.ui_design_subtabs[param] = ui.tab(param)
                            self.ui_design_refs[param] = {}

                with splitter.after:
                    with ui.tab_panels(tabs, value=self.ui_design_subtabs['meta']).props('vertical').classes('w-full h-full p-0 m-0'):
                        for param, tab_elem in self.ui_design_subtabs.items():
                            with ui.tab_panel(tab_elem).classes('w-full h-full p-0 m-0').style('gap: 0px'):
                                with ui.scroll_area().classes('w-full h-full p-0 m-0').style('gap: 0px'):
                                    self.def_flat_design_subtab(
                                        self.ui_design_refs[param],
                                        design_params[param],
                                        use_collapsible=(param == 'left')
                                    )
        else:
            # Simplified display of designs
            with ui.scroll_area().classes('w-full h-full p-0 m-0'):
                self.def_flat_design_subtab(
                    self.ui_design_refs,
                    design_params,
                    use_collapsible=True
                )

    # !SECTION
    # SECTION -- Pattern visuals
    def def_pattern_display(self):
        """Prepare pattern display area"""
        with ui.column().classes('h-full p-0 m-0'):
            with ui.row().classes('w-full p-0 m-0 justify-between'):
                switch = ui.switch(
                    'Body Silhouette', value=True,
                ).props('dense left-label').classes('text-stone-800')

                self.ui_self_intersect = ui.label(
                    'WARNING: Garment panels are self-intersecting!'
                ).classes('font-semibold text-purple-600 border-purple-600 border py-0 px-1.5 rounded-md') \
                .bind_visibility(self.pattern_state, 'is_self_intersecting')

            with ui.image(
                    f'{self.path_static_img}/millimiter_paper_1500_900.png'
                ).classes(f'aspect-[{self.canvas_aspect_ratio}] h-[95%] p-0 m-0')  as self.ui_pattern_bg:
                # NOTE: Positioning: https://github.com/zauberzeug/nicegui/discussions/957
                with ui.row().classes('w-full h-full p-0 m-0 bg-transparent relative top-[0%] left-[0%]'):
                    self.body_outline_classes = 'bg-transparent h-full absolute top-[0%] left-[0%] p-0 m-0'
                    self.ui_body_outline = ui.image(f'{self.path_static_img}/ggg_outline_mean_all.svg') \
                        .classes(self.body_outline_classes)
                    switch.bind_value(self.ui_body_outline, 'visible')

                # NOTE: ui.row allows for correct classes application (e.g. no padding on svg pattern)
                with ui.row().classes('w-full h-full p-0 m-0 bg-transparent relative'):
                    # Automatically updates from source
                    self.ui_pattern_display = ui.interactive_image(
                        ''
                    ).classes('bg-transparent p-0 m-0')

    # !SECTION
    # SECTION 3D view
    def create_lights(self, scene:ui.scene, intensity=30.0):
        light_positions = np.array([
            [1.60614, 1.23701, 1.5341,],
            [1.31844, -2.52238, 1.92831],
            [-2.80522, 2.34624, 1.2594],
            [0.160261, 3.52215, 1.81789],
            [-2.65752, -1.26328, 1.41194]
        ])
        light_colors = [
            '#ffffff',
            '#ffffff',
            '#ffffff',
            '#ffffff',
            '#ffffff'
        ]
        z_dirs = np.arctan2(light_positions[:, 1], light_positions[:, 0])

        # Add lights to the scene
        for i in range(len(light_positions)):
            scene.spot_light(
                color=light_colors[i], intensity=intensity,
                angle=np.pi,
                ).rotate(0., 0., -z_dirs[i]).move(light_positions[i][0], light_positions[i][1], light_positions[i][2])

    def create_camera(self, cam_location, fov, scale=1.):
        camera = ui.scene.perspective_camera(fov=fov)
        camera.x = cam_location[0] * scale
        camera.y = cam_location[1] * scale
        camera.z = cam_location[2] * scale

        # direction
        camera.look_at_x = 0
        camera.look_at_y = 0
        camera.look_at_z = cam_location[2] * scale * 2/3

        return camera

    def def_3d_scene(self):
        y_fov = 30   # Degrees == np.pi / 6. rad FOV
        camera_location = [0, -4.15, 1.25]
        bg_color='#ffffff'

        def body_visibility(value):
            self.ui_body_3d.visible(value)

        with ui.row().classes('w-full p-0 m-0 justify-between items-center'):
            self.ui_body_3d_switch = ui.switch(
                'Body Silhouette',
                value=True,
                on_change=lambda e: body_visibility(e.value)
            ).props('dense left-label').classes('text-stone-800')

            ui.button('Drape current design', on_click=lambda: self.update_3d_scene())

            ui.label(
                'INFO: it takes a few minutes'
            ).classes(f'font-semibold text-[{theme_colors.primary}] border-[{theme_colors.primary}] '
                    'border py-0 px-1.5 rounded-md')

        camera = self.create_camera(camera_location, y_fov)
        with ui.scene(
            width=self.scene_base_resoltion[0],
            height=self.scene_base_resoltion[1],
            camera=camera,
            grid=False,
            background_color=bg_color
            ).classes(f'w-[{self.w_garment_display}vw] h-[90%] p-0 m-0') as self.ui_3d_scene:
            # Lights setup
            self.create_lights(self.ui_3d_scene, intensity=60.)
            # NOTE: texture is there, just needs a better setup
            self.ui_garment_3d = None
            # TODOLOW Update body model to a correct shape
            self.ui_body_3d = self.ui_3d_scene.stl(
                    '/body/mean_all.stl'
                ).rotate(np.pi / 2, 0., 0.).material(color='#000000')

    # !SECTION
    # SECTION -- Other UI details
    def def_pattern_waiting(self):
        """Define the waiting splashcreen with spinner
            (e.g. waiting for a pattern to update)"""

        # NOTE: the screen darkens because of the shadow
        with ui.dialog(value=False).props(
            'persistent maximized'
        ) as self.spin_dialog, ui.card().classes('bg-transparent'):
            # Styles https://quasar.dev/vue-components/spinners
            ui.spinner('hearts', size='15em').classes('fixed-center')   # NOTE: 'dots' 'ball'

    def def_body_file_dialog(self):
        """ Dialog for loading parameter files (body)
        """
        async def handle_upload(e: events.UploadEventArguments):
            param_dict = yaml.safe_load(e.content.read())['body']

            self.toggle_param_update_events(self.ui_active_body_refs)

            self.pattern_state.set_new_body_params(param_dict)
            self.update_body_params_ui_state(self.ui_active_body_refs)
            await self.update_pattern_ui_state()

            self.toggle_param_update_events(self.ui_active_body_refs)

            ui.notify(f'Successfully applied {e.name}')
            self.ui_body_dialog.close()

        with ui.dialog() as self.ui_body_dialog, ui.card().classes('items-center'):
            # NOTE: https://www.reddit.com/r/nicegui/comments/1393i2f/file_upload_with_restricted_types/
            ui.upload(
                label='Body parameters .yaml or .json',
                on_upload=handle_upload
            ).classes('max-w-full').props('accept=".yaml,.json"')

            ui.button('Close without upload', on_click=self.ui_body_dialog.close)

    def def_design_file_dialog(self):
        """ Dialog for loading parameter files (design)
        """

        async def handle_upload(e: events.UploadEventArguments):
            param_dict = yaml.safe_load(e.content.read())['design']

            self.toggle_param_update_events(self.ui_design_refs)  # Don't react to value updates

            self.pattern_state.set_new_design(param_dict)
            self.update_design_params_ui_state(self.ui_design_refs, self.pattern_state.design_params)
            await self.update_pattern_ui_state()

            self.toggle_param_update_events(self.ui_design_refs)  # Re-enable reaction to value updates

            ui.notify(f'Successfully applied {e.name}')
            self.ui_design_dialog.close()

        with ui.dialog() as self.ui_design_dialog, ui.card().classes('items-center'):
            # NOTE: https://www.reddit.com/r/nicegui/comments/1393i2f/file_upload_with_restricted_types/
            ui.upload(
                label='Design parameters .yaml or .json',
                on_upload=handle_upload
            ).classes('max-w-full').props('accept=".yaml,.json"')

            ui.button('Close without upload', on_click=self.ui_design_dialog.close)

    def start_edit(self, chat):
        """Start editing a chat title"""
        chat.editing = True
        self.refresh_chat_list()

    def save_edit(self, chat, input_box):
        """Save edited chat title and update UI"""
        new_title = input_box.value
        if new_title.strip():
            self.chat_service.update_chat_title(chat_uid=chat.chat_uid, title=new_title)
            chat.title = new_title
        chat.editing = False
        self.refresh_chat_list()
        ui.notify('Chat title updated', type='positive')

    def cancel_edit(self, chat):
        """Cancel editing a chat title"""
        chat.editing = False
        self.refresh_chat_list()

    def def_chat_history(self):
        def start_edit(chat):
            with ui.dialog() as edit_dialog:
                with ui.card():
                    input_box = ui.input(value=chat.title).classes("text-sm w-full")
                    with ui.row().classes("gap-2 mt-1"):
                        ui.button('Save', on_click=lambda: save_edit(chat, input_box, edit_dialog)).props('dense flat color=positive')
                        ui.button('Cancel', on_click=edit_dialog.close).props('dense flat color=negative')
            edit_dialog.open()

        def save_edit(chat, input_box, dialog):
            new_title = input_box.value
            if new_title.strip():
                self.chat_service.update_chat_title(chat_uid=chat.chat_uid, title=new_title)
                chat.title = new_title
            chat.editing = False
            dialog.close()
            ui.update()

        chat_history = self.chat_service.get_user_chats()
        def format_time(dt):
            today = datetime.now().date()
            yesterday = today - timedelta(days=1)
            chat_date = dt.date()

            if chat_date == today:
                return "Today"
            elif chat_date == yesterday:
                return "Yesterday"
            return dt.strftime("%b %d")

        with ui.row().classes("w-full h-screen"):
            # Sidebar
            with ui.column().classes("w-full h-full border-r bg-white shadow-sm"):
                # Header
                with ui.row().classes("w-full p-4 border-b items-center justify-between"):
                    ui.label("Chat History").classes("text-lg font-semibold")
                    with ui.button(icon="add", color=None).classes("text-gray-500 hover:bg-gray-100 rounded-full p-1"):
                        ui.tooltip("New Chat")

                # Search bar
                with ui.row().classes("w-full p-2 border-b"):
                    with ui.input(placeholder="Search chats").classes("w-full rounded-lg bg-gray-100 px-3 py-2 text-sm border-none"):
                        ui.icon("search").classes("text-gray-400")

                # Chat list
                with ui.column().classes("w-full overflow-y-auto") as self.chat_list_container:
                    for chat in chat_history:
                        is_selected = self.chat_uid == chat.chat_uid

                        chat_row = ui.row().classes(f"""w-full p-3 items-center cursor-pointer {"bg-blue-50" if is_selected else "hover:bg-gray-50"}""")
                        chat_row.on('click', lambda e, c=chat: asyncio.create_task(self.open_previous_chat(c.chat_uid)))

                        with chat_row:
                            with ui.row().classes("w-full items-center justify-between gap-3"):
                                with ui.column().classes("flex-1"):
                                    ui.label(chat.title).classes("text-sm font-medium text-gray-900 truncate")
                                    ui.label(format_time(chat.created_at)).classes("text-xs text-gray-500")
                                with ui.row().classes("gap-1"):
                                    edit_btn = ui.button(icon='edit').props('dense flat size="sm"').classes("text-gray-600")
                                    edit_btn.on('click', lambda e, c=chat: self.start_edit(c))
                                    
                                    delete_btn = ui.button(icon='delete').props('dense flat size="sm"').classes("text-red-600")
                                    delete_btn.on('click', lambda e, c=chat: self.delete_chat(c))

                # User section at bottom
                with ui.row().classes("w-full p-3 border-t items-center gap-2 mt-auto"):
                    ui.avatar("U", color="blue").classes("bg-blue-100 text-blue-600")
                    ui.label(self.user.email).classes("text-sm font-medium text-gray-900")

    def handle_chat_deletion(self, chat_uid):
        """Handle the deletion of a chat"""
        try:
            # Delete the chat from the database
            self.chat_service.delete_chat(chat_uid)
            
            # Refresh the chat list
            self.refresh_chat_list()
            
            # If the deleted chat was the current chat, create a new one
            if self.chat_uid == chat_uid:
                self.chat_uid = generate_unique_uid(model=Chat, field='chat_uid')
                self.chat_container.clear()
            
            ui.notify('Chat deleted successfully', type='positive')
        except Exception as e:
            ui.notify(f'Failed to delete chat: {str(e)}', type='negative')

    def refresh_chat_list(self):
        """Refresh the chat list in the sidebar"""
        # Clear the existing chat list
        self.chat_list_container.clear()
        
        # Get updated chat history
        chat_history = self.chat_service.get_user_chats()
        
        # Recreate the chat list
        def format_time(dt):
            today = datetime.now().date()
            yesterday = today - timedelta(days=1)
            chat_date = dt.date()

            if chat_date == today:
                return "Today"
            elif chat_date == yesterday:
                return "Yesterday"
            return dt.strftime("%b %d")
            
        with self.chat_list_container:
            for chat in chat_history:
                is_selected = self.chat_uid == chat.chat_uid

                with ui.row().classes(f"""w-full p-3 items-center cursor-pointer {"bg-blue-50" if is_selected else "hover:bg-gray-50"}""").on('click', lambda e, c=chat: asyncio.create_task(self.open_previous_chat(c.chat_uid))):
                    if hasattr(chat, 'editing') and chat.editing:
                        input_box = ui.input(value=chat.title).classes("text-sm w-full")
                        with ui.row().classes("gap-2 mt-1"):
                            ui.button('Save', on_click=lambda c=chat, i=input_box: self.save_edit(c, i)).props('dense flat color=positive')
                            ui.button('Cancel', on_click=lambda c=chat: self.cancel_edit(c)).props('dense flat color=negative')
                    else:
                        with ui.row().classes("w-full items-center justify-between gap-3"):
                            with ui.column().classes("flex-1"):
                                ui.label(chat.title).classes("text-sm font-medium text-gray-900 truncate")
                                ui.label(format_time(chat.created_at)).classes("text-xs text-gray-500")
                            with ui.row().classes("gap-1"):
                                ui.button(icon='edit', on_click=lambda e, c=chat: self.start_edit(c)).props('dense flat size="sm"').classes("text-gray-600")
                                ui.button(icon='delete', on_click=lambda e, c=chat: self.delete_chat(c)).props('dense flat size="sm"').classes("text-red-600")

    def delete_chat(self, chat):
        print(f"Deleting chat with UID: {chat.chat_uid}")
        # Create a confirmation dialog instead of using ui.confirm
        with ui.dialog().props('persistent') as delete_dialog:
            with ui.card():
                ui.label('Are you sure you want to delete this chat?').classes('text-lg font-medium mb-4')
                with ui.row().classes('justify-end gap-2'):
                    ui.button('Cancel', on_click=delete_dialog.close).props('flat')
                    ui.button('Delete', on_click=lambda: (self.handle_chat_deletion(chat.chat_uid), delete_dialog.close())).props('color=negative')
        delete_dialog.open()
        
    def def_parse_tab(self):
        """Define content for Parse Design tab"""
        # Main container without scroll
        with ui.column().classes('w-full h-full p-0 m-0'):
            # Chat messages container with scroll
            with ui.column().classes('w-full h-[80vh] p-4 gap-4'):
                # Header text
                ui.label('Describe your design or upload reference images').classes('text-lg font-medium text-gray-700')

                # Messages will be added here
                self.chat_container = ui.column().classes('w-full flex-grow overflow-auto gap-4')

            # Input area at the bottom (redesigned)
            with ui.row().classes('w-full items-center gap-3 p-4 bg-white border-t shadow-md'):
                # Attachment icon button
                ui.button(
                    icon='attach_file',
                    on_click=lambda: self.upload_dialog.open()
                ).props('flat round color=primary').classes('min-w-[2.5rem] min-h-[2.5rem]')

                # Chat input field
                self.chat_input = ui.input(
                    placeholder='Describe your design...'
                ).props('outlined rounded-3xl dense').classes('flex-grow text-base')

                # Send button
                ui.button(
                    icon='send',
                    on_click=self.handle_chat_input
                ).props('unelevated round color=primary').classes('min-w-[2.5rem] min-h-[2.5rem]')


            # Add upload dialog
            with ui.dialog() as self.upload_dialog, ui.card():
                ui.upload(
                    label='Upload reference image',
                    on_upload=self.handle_image_upload,
                    max_files=1
                ).props('accept="image/*"')
                ui.button('Close', on_click=self.upload_dialog.close)

    async def open_previous_chat(self,chat_uid:str, isNew:bool = False):
        try:
            self.spin_dialog.open()
            if not chat_uid:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat uid must not be empty")
            chat = self.chat_service.get_chat_by_uid(chat_uid)
            prompt_lists = self.message_service.get_messages_by_chat(chat_uid=chat_uid)
            self.tabs.value = self.ui_parse_tab
            self.chat_uid = chat_uid
            self.chat_container.clear()
            for prompt in prompt_lists:
                self.add_parse_tab_prompt(prompt=prompt.message, isUser=True)
                self.add_parse_tab_prompt(prompt="I've updated the pattern based on your description. You can adjust the parameters further if needed.", isUser=False)
            try:
                raw_response = prompt_lists[-1].response
                params = ast.literal_eval(raw_response)
                self.toggle_param_update_events(self.ui_design_refs)
                self.pattern_state.set_new_design(params)
                self.update_design_params_ui_state(self.ui_design_refs, self.pattern_state.design_params)
                await self.update_pattern_ui_state()
                self.toggle_param_update_events(self.ui_design_refs)
            except (ValueError, SyntaxError) as e:
                print(f"Invalid dict format: {e}")

        except Exception as e:
            print(e)
        finally:
            self.spin_dialog.close()

    def add_parse_tab_prompt(self, prompt:str, isUser:bool, prompt_type: MessageTypeEnum = MessageTypeEnum.TEXT):
        if isUser:
            if prompt_type == MessageTypeEnum.TEXT:
                with self.chat_container:
                    with ui.row().classes('w-full justify-end'):
                        with ui.card().classes('max-w-[70%] p-1 bg-blue-100 rounded-xl shadow-sm'):
                            with ui.column().classes('p-3 gap-1'):
                                ui.label(prompt).classes('text-gray-900 text-base')
                                ui.label(datetime.now().strftime('%H:%M')).classes('text-xs text-gray-500 text-right')
            elif prompt_type == MessageTypeEnum.IMAGE:
                with self.chat_container:
                    with ui.card().classes('w-3/4 ml-auto bg-gray-200 rounded-lg'):
                        ui.label('Reference image:').classes('p-2')
                        ui.image(prompt).classes('w-full rounded-lg')
                        ui.label(datetime.now().strftime('%H:%M')).classes('text-xs text-gray-500 p-2')
        else:
            with self.chat_container:
                with ui.row().classes('w-full justify-start'):
                    with ui.card().classes('max-w-[70%] p-1 bg-gray-100 rounded-xl shadow-sm'):
                        with ui.column().classes('p-3 gap-1'):
                            ui.label(prompt).classes('text-gray-800 text-base')
                            ui.label(datetime.now().strftime('%H:%M')).classes('text-xs text-gray-500 text-left')


    async def handle_chat_input(self):
        """Handle chat input and update pattern"""
        if not self.chat_input.value:
            return

        # Add user message (right-aligned bubble)
        self.add_parse_tab_prompt(prompt=self.chat_input.value, isUser=True)

        try:
            # Show existing spinner dialog
            self.spin_dialog.open()

            # Process input through LLM using ThreadPoolExecutor
            loop = asyncio.get_event_loop()
            try:
                prompts = self.message_service.get_messages_by_chat(chat_uid=self.chat_uid)
                prompts = prompts[len(prompts)-20:] if len(prompts)>20 else prompts
            except Exception as e:
                prompts = []

            params = await loop.run_in_executor(
                self._async_executor,
                lambda: self.pattern_parser.process_input(curr_dict=self.pattern_state.design_params, prompts=prompts, text=self.chat_input.value)
            )

            # Update design parameters
            self.toggle_param_update_events(self.ui_design_refs)
            self.pattern_state.set_new_design(params)
            self.update_design_params_ui_state(self.ui_design_refs, self.pattern_state.design_params)
            await self.update_pattern_ui_state()
            self.toggle_param_update_events(self.ui_design_refs)

            try:
                self.message_service.add_message(chat_uid=self.chat_uid, message=self.chat_input.value, response=str(params))
            except Exception as e:
                print(e)
            # Add system message (left-aligned bubble)
            self.add_parse_tab_prompt(prompt="I've updated the pattern based on your description. You can adjust the parameters further if needed.", isUser=False)

        except TimeoutError:
            ui.notify('Request timed out. Please try again.', type='negative')
            with self.chat_container:
                with ui.card().classes('w-3/4 mr-auto bg-red-100 rounded-lg'):
                    with ui.column().classes('p-3 gap-1'):
                        ui.label("Sorry, the request took too long. Please try again with a simpler description.").classes('text-gray-800')
                        ui.label(datetime.now().strftime('%H:%M')).classes('text-xs text-gray-500')

        except Exception as e:
            ui.notify(f"Failed to process input: {str(e)}", type='negative')
            with self.chat_container:
                with ui.card().classes('w-3/4 mr-auto bg-red-100 rounded-lg'):
                    with ui.column().classes('p-3 gap-1'):
                        ui.label("Sorry, I couldn't process that input. Please try again.").classes('text-gray-800')
                        ui.label(datetime.now().strftime('%H:%M')).classes('text-xs text-gray-500')

        finally:
            # Always close the spinner dialog
            self.spin_dialog.close()
            # Clear input
            # Clear input
            self.last_chat_input = self.chat_input.value
            self.chat_input.value = ''

    async def handle_image_upload(self, e: events.UploadEventArguments):
        """Handle uploaded reference images"""
        try:
            # Read content once and store it
            self.image_bytes = e.content.read()
            self.content_type = e.type or 'image/png'  # fallback to png if type not provided

            # Create data URL using the stored bytes
            data_url = f'data:{self.content_type};base64,{base64.b64encode(self.image_bytes).decode()}'
            self.data_url = data_url
            # Add user message with image
            self.add_parse_tab_prompt(prompt=data_url, isUser=True, prompt_type=MessageTypeEnum.IMAGE)
            # Show spinner while processing
            self.spin_dialog.open()
            try:
                prompts = self.message_service.get_messages_by_chat(chat_uid=self.chat_uid)
                prompts = prompts[len(prompts)-20:] if len(prompts)>20 else prompts
            except Exception as e:
                prompts = []
            # Process through LLM using ThreadPoolExecutor
            loop = asyncio.get_event_loop()
            params = await loop.run_in_executor(
                self._async_executor,
                lambda: self.pattern_parser.process_input(curr_dict=self.pattern_state.design_params, prompts=prompts, image_data=(self.image_bytes, self.content_type))
            )

            # Update design parameters
            self.toggle_param_update_events(self.ui_design_refs)
            self.pattern_state.set_new_design(params)
            self.update_design_params_ui_state(self.ui_design_refs, self.pattern_state.design_params)
            await self.update_pattern_ui_state()
            self.toggle_param_update_events(self.ui_design_refs)
            try:
                self.message_service.add_message(chat_uid=self.chat_uid, message=self.data_url, response=str(params), message_type=MessageTypeEnum.IMAGE)
            except Exception as e:
                print(e)
            # Add system response
            self.add_parse_tab_prompt(prompt="I've updated the pattern based on your description. You can adjust the parameters further if needed.", isUser=False)

            ui.notify(f'Successfully processed {e.name}')
            self.upload_dialog.close()

        except Exception as err:
            ui.notify(f'Failed to process image: {str(err)}', type='negative')
            with self.chat_container:
                with ui.card().classes('w-3/4 mr-auto bg-red-100 rounded-lg'):
                    with ui.column().classes('p-3 gap-1'):
                        ui.label("Sorry, I couldn't process that image. Please try again.").classes('text-gray-800')
                        ui.label(datetime.now().strftime('%H:%M')).classes('text-xs text-gray-500')
        finally:
            self.spin_dialog.close()

    # !SECTION
    # SECTION -- Event callbacks
    async def update_pattern_ui_state(self, param_dict=None, param=None, new_value=None, body_param=False):
        """UI was updated -- update the state of the pattern parameters and visuals"""
        # NOTE: Fixing to the "same value" issue in lambdas
        # https://github.com/zauberzeug/nicegui/wiki/FAQs#why-have-all-my-elements-the-same-value

        print('INFO::Updating pattern...')
        # Update the values
        if param_dict is not None:
            if body_param:
                param_dict[param] = new_value
            else:
                param_dict[param]['v'] = new_value
                self.pattern_state.is_in_3D = False
                  # Design param changes -> 3D model is not synced with the param
        try:
            if not self.pattern_state.is_slow_design():
                # Quick update
                self._sync_update_state()
                return

            # Display waiting spinner untill getting the result
            # NOTE Splashscreen solution to block users from modifying params while updating
            # https://github.com/zauberzeug/nicegui/discussions/1988

            self.spin_dialog.open()
            # NOTE: Using threads for async call
            # https://stackoverflow.com/questions/49822552/python-asyncio-typeerror-object-dict-cant-be-used-in-await-expression
            self.loop = asyncio.get_event_loop()
            await self.loop.run_in_executor(self._async_executor, self._sync_update_state)

            self.spin_dialog.close()

        except KeyboardInterrupt as e:
            raise e
        except BaseException as e:
            traceback.print_exc()
            print(e)
            self.spin_dialog.close()  # If open
            ui.notify(
                'Failed to generate pattern correctly. Try different parameter values',
                type='negative',
                close_button=True,
                position='center'
            )

    def _sync_update_state(self):
        # Update derivative body values (just in case)
        # TODOLOW only do that on body value updates
        self.pattern_state.body_params.eval_dependencies()
        self.update_body_params_ui_state(self.ui_passive_body_refs) # Display evaluated dependencies

        # Update the garment
        # Sync left-right for easier editing
        self.pattern_state.sync_left(with_check=True)

        # NOTE This is the slow part
        self.pattern_state.reload_garment()

        # TODOLOW the pattern is floating around when collars are added..
        # Update display
        if self.ui_pattern_display is not None:

            if self.pattern_state.svg_filename:
                # Re-align the canvas and body with the new pattern
                p_bbox_size = self.pattern_state.svg_bbox_size
                p_bbox = self.pattern_state.svg_bbox

                # Margin calculations w.r.t. canvas size
                # s.t. the pattern scales correctly
                w_shift = abs(p_bbox[0])  # Body feet location in width direction w.r.t top-left corner of the pattern
                m_top = (1. - abs(p_bbox[2]) * self.background_body_scale) * self.h_rel_body_size + (1. - self.h_rel_body_size) / 2
                m_left = self.background_body_canvas_center - w_shift * self.background_body_scale * self.w_rel_body_size
                m_right = 1 - m_left - p_bbox_size[0] * self.background_body_scale * self.w_rel_body_size
                m_bottom = 1 - m_top - p_bbox_size[1] * self.background_body_scale * self.h_rel_body_size

                # Canvas padding adjustment
                m_top -= self.h_canvas_pad
                m_left -= self.w_canvas_pad
                m_right += self.w_canvas_pad  # preserve evaluated width
                m_bottom -= self.h_canvas_pad

                # New placement
                if m_top < 0 or m_bottom < 0 or m_left < 0 or m_right < 0:
                    # Calculate the fraction
                    scale_margin = 1.2
                    y_top_scale = abs(min(m_top * scale_margin, 0.)) + 1.
                    y_bot_scale = 1. + abs(min(m_bottom * scale_margin, 0.))
                    x_left_scale = abs(min(m_left * scale_margin, 0.)) + 1.
                    x_right_scale = abs(min(m_right * scale_margin, 0.)) + 1.
                    scale = min(1. / y_top_scale, 1. / y_bot_scale, 1. / x_left_scale, 1. / x_right_scale)

                    # Rescale the body
                    self.ui_body_outline.classes(
                        replace=self.body_outline_classes + f' origin-center scale-[{scale}]'
                    )

                    # Recalculate positioning & width
                    body_center = 0.5 - self.background_body_canvas_center
                    m_top = (1. - abs(p_bbox[2]) * self.background_body_scale) * self.h_rel_body_size * scale + (1. - self.h_rel_body_size * scale) / 2
                    m_left = (0.5 - body_center * scale) - w_shift * self.background_body_scale * self.w_rel_body_size * scale
                    m_right = 1 - m_left - p_bbox_size[0] * self.background_body_scale * self.w_rel_body_size * scale

                    # Canvas padding adjustment
                    # TODOLOW For some reason top adjustment is not needed here: m_top -= self.h_canvas_pad * scale
                    m_left -= self.w_canvas_pad * scale
                    m_right += self.w_canvas_pad * scale

                else:  # Display normally
                    # Remove body transforms if any were applied
                    self.ui_body_outline.classes(replace=self.body_outline_classes)

                # New pattern image
                self.ui_pattern_display.set_source(
                    str(self.pattern_state.svg_path()) if self.pattern_state.svg_filename else '')
                self.ui_pattern_display.classes(
                        replace=f"""bg-transparent p-0 m-0
                                absolute
                                left-[{m_left * 100}%]
                                top-[{m_top * 100}%]
                                w-[{(1. - m_right - m_left) * 100}%]
                                height-auto
                        """)

            else:
                # Restore default state
                self.ui_pattern_display.set_source('')
                self.ui_body_outline.classes(replace=self.body_outline_classes)

    def update_design_params_ui_state(self, ui_elems, design_params):
        """Sync ui params with the current state of the design params"""
        for param in design_params:
            if 'v' not in design_params[param]:
                self.update_design_params_ui_state(ui_elems[param], design_params[param])
            else:
                ui_elems[param].value = design_params[param]['v']

    def toggle_param_update_events(self, ui_elems):
        """Enable/disable event handling on the ui elements related to GarmentCode parameters"""
        for param in ui_elems:
            if isinstance(ui_elems[param], dict):
                self.toggle_param_update_events(ui_elems[param])
            else:
                if ui_elems[param].is_ignoring_events:  # -> disabled
                    ui_elems[param].enable()
                else:
                    ui_elems[param].disable()

    def update_body_params_ui_state(self, ui_body_refs):
        """Sync ui params with the current state of the body params"""
        for param in ui_body_refs:
            ui_body_refs[param].value = self.pattern_state.body_params[param]

    async def update_3d_scene(self):
        """According the whatever pattern current state"""

        print('INFO::Updating 3D...')

        # Cleanup
        if self.ui_garment_3d is not None:
            self.ui_garment_3d.delete()
            self.ui_garment_3d = None

        if not self.pattern_state.svg_filename:
            print('INFO::Current garment is empty, skipped 3D update')
            ui.notify('Current garment is empty. Chose a design to start simulating!')
            self.ui_body_3d.visible(True)
            self.ui_body_3d_switch.set_value(True)
            return

        try:
            # Display waiting spinner untill getting the result
            # NOTE Splashscreen solution to block users from modifying params while updating
            # https://github.com/zauberzeug/nicegui/discussions/1988

            self.spin_dialog.open()
            # NOTE: Using threads for async call
            # https://stackoverflow.com/questions/49822552/python-asyncio-typeerror-object-dict-cant-be-used-in-await-expression
            self.loop = asyncio.get_event_loop()
            await self.loop.run_in_executor(self._async_executor, self._sync_update_3d)

            # Update ui
            # https://github.com/zauberzeug/nicegui/discussions/1269
            with self.ui_3d_scene:
                # NOTE: material is defined in the glb file
                self.ui_garment_3d = self.ui_3d_scene.gltf(
                            f'geo/{self.garm_3d_filename}',
                        ).scale(0.01).rotate(np.pi / 2, 0., 0.)

            # Show the result! =)
            self.spin_dialog.close()

        except KeyboardInterrupt as e:
            raise e
        except BaseException as e:
            traceback.print_exc()
            print(e)
            self.ui_3d_scene.set_visibility(True)
            self.spin_dialog.close()  # If open
            ui.notify(
                'Failed to generate 3D model correctly. Try different parameter values',
                type='negative',
                close_button=True,
                position='center'
            )

    async def upgrade_prompt(self):

        if self.image_bytes is not None and self.content_type is not None:
            image_path = self.pattern_parser._save_image_input(self.image_bytes, self.content_type)
        else:
            image_path = None

        text = self.last_chat_input


        front_view_path = "tmp_gui/downloads/"+str(self.pattern_state.id) + "/Configured_design_3D/Configured_design_3D_render_front.png"
        back_view_path = "tmp_gui/downloads/"+str(self.pattern_state.id)+"/Configured_design_3D/Configured_design_3D_render_back.png"

        print("\n\nThe text prompt data\n " , text)
        print("\n\nThe image prompt image path\n " , image_path)
        print("\n\nThe 3d front image path\n " , front_view_path)
        print("\n\nThe 3d back image path\n " , back_view_path)
        # all the 3 image will have the path now..
        enhanced_prompt = prompt_enhancer(text, image_path, front_view_path, back_view_path) # new AI integration can be written inside the above funstion

        if enhanced_prompt is not None:
            self.chat_input.value = enhanced_prompt
            await self.handle_chat_input() # this will make a call to gpt and render the 2d again
            await self.update_3d_scene() # this is start draping to 3d which call this same function again..

    def _sync_update_3d(self):
        """Update 3d model"""

        # Run simulation
        path, filename = self.pattern_state.drape_3d()


        # NOTE: The files will be available publically at the static point
        # However, we cannot do much about it, since it won't be available for the interface otherwise

        # Delete previous file
        (self.local_path_3d / self.garm_3d_filename).unlink(missing_ok=True)
        # Put the new one for display
        self.garm_3d_filename = f'garm_3d_{self.pattern_state.id}_{time.time()}.glb'
        shutil.copy2(path / filename, self.local_path_3d / self.garm_3d_filename)

        self.loop.create_task(self.upgrade_prompt())

    # Design buttons updates
    async def design_sample(self):
        """Run design sampling"""
        self.loop = asyncio.get_event_loop()
        await self.loop.run_in_executor(self._async_executor, self.pattern_state.sample_design)

    async def random(self):
        # Sampling could be slow, so add spin always
        self.spin_dialog.open()

    async def default(self):
        self.toggle_param_update_events(self.ui_design_refs)

        self.pattern_state.restore_design(False)
        self.update_design_params_ui_state(self.ui_design_refs, self.pattern_state.design_params)
        await self.update_pattern_ui_state()

        self.toggle_param_update_events(self.ui_design_refs)

    def state_download(self, file_format):
        """Download current state of a garment in the specified file_format with JSON"""
        archive_path = self.pattern_state.save_for_format(file_format=file_format, pack=True)
        filename = f"Configured_design_{datetime.now().strftime('%y%m%d-%H-%M-%S')}.zip"
        ui.download(archive_path, filename)
    
    # def state_download(self):
    #     """Download current state of a garment"""
    #     archive_path = self.pattern_state.save()
    #     ui.download(archive_path, f'Configured_design_{datetime.now().strftime("%y%m%d-%H-%M-%S")}.zip')
