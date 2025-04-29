from nicegui import ui, Client

# Custom
from gui.callbacks import GUIState
import gui.error_pages


icon_image_b64 = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAQAAAAEACAYAAABccqhmAAAACXBIWXMAAAsSAAALEgHS3X78AAAWd0lEQVR4nO2dfYxc1XnGz+587+x49tO7ttf2GK/tpTZ4mlwawF9rbPMRzIeAEGTTUgpSCzSp1EopSImEaNVUVUWTqFFVCQilIk2bokYptKEJASJopXaimoAEIaYYB7telvXudnZ2d762qsd7R6x3Z9c765lz3rnn+Un+gz/Y+5477/vcc9773HOaSqWSIoTYSTN/d0LshQJAiMVQAAixGAoAIRZDASDEYigAhFgMBYAQi6EAEGIxFABCLIYCQIjFUAAIsRgKACEWQwEgxGIoAIRYDAWAEIuhABBiMRQAQiyGAkCIxVAACLEYCgAhFkMBIMRiKACEWAwFgBCLoQAQYjEUAEJsRSn1/wo3KFPhDTaqAAAAAElFTkSuQmCC'

@ui.page('/')
async def index(client: Client):
    # Start the interface!
    gui_st = GUIState()

    # Connection end
    # https://github.com/zauberzeug/nicegui/discussions/1379
    print('Closed connection ', gui_st.pattern_state.id, '. Deleting files...')
    gui_st.release()

if __name__ == '__main__':
    ui.run(
            reload=False,
            favicon=icon_image_b64,
            title='GarmentCode',
            show=False,
            # reconnect_timeout=90
        )
    