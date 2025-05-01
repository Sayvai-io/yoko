from nicegui import ui, app, Client
import jwt
from datetime import datetime, timedelta
from typing import Optional
from db.models import User  # Import your models
from db.services import UserService, MessageService
from db.db_config import Base, engine, get_db
from gui.callbacks import GUIState
import os

icon_image_b64 = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAQAAAAEACAYAAABccqhmAAAACXBIWXMAAAsSAAALEgHS3X78AAAWd0lEQVR4nO2dfYxc1XnGz+587+x49tO7ttf2GK/tpTZ4mlwawF9rbPMRzIeAEGTTUgpSCzSp1EopSImEaNVUVUWTqFFVCQilIk2bokYptKEJASJopXaimoAEIaYYB7telvXudnZ2d762qsd7R6x3Z9c765lz3rnn+Un+gz/Y+5477/vcc9773HOaSqWSIoTYSTN/d0LshQJAiMVQAAixGAoAIRZDASDEYigAhFgMBYAQi6EAEGIxFABCLIYCQIjFUAAIsRgKACEWQwEgxGIoAIRYDAWAEIuhABBiMRQAQiyGAkCIxVAACLEYCgAhFkMBIMRiKACEWAwFgBCLoQAQYjEUAEJsRSn1/wo3KFPhDTaqAAAAAElFTkSuQmCC'

# Initialize databasecall
Base.metadata.create_all(bind=engine)

# Remove the mock users list since we're using the database now

# JWT Configuration (same as before)
JWT_SECRET = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = "HS256"
TOKEN_EXPIRY_DAYS = 30

db = next(get_db())
user_service = UserService(db)

if not user_service.find_user_by_email("admin@yokostyles.com"):
    user_service.add_user(email="admin@yokostyles.com", password="admin123")

def create_jwt_token(user_uid: str) -> str:
    """Generate JWT token with user ID payload"""
    expiry = datetime.utcnow() + timedelta(days=TOKEN_EXPIRY_DAYS)
    payload = {
        "user_uid": user_uid,
        "exp": expiry.timestamp()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_jwt_token(token: str) -> Optional[dict]:
    """Decode and verify JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload['exp'] < datetime.utcnow().timestamp():
            return None
        return payload
    except jwt.PyJWTError:
        return None

@ui.page('/')
async def main_page(client: Client):
    """Protected main page - checks JWT"""
    if 'jwt_token' not in app.storage.user:
        app.storage.user['jwt_token'] = None

    token = app.storage.user['jwt_token']
    if not token:
        ui.navigate.to('/login')
        return

    decoded = decode_jwt_token(token)
    if not decoded:
        app.storage.user['jwt_token'] = None
        ui.navigate.to('/login')
        return

    # Get user from database
    user_uid = decoded["user_uid"]
    user = user_service.find_user_by_uid(user_uid)
    if not user:
        app.storage.user['jwt_token'] = None
        ui.navigate.to('/login')
        return

    # Rest of your main page code...
    gui_st = GUIState(user=user, db=db)
    await client.disconnected()
    print('Closed connection ', gui_st.pattern_state.id, '. Deleting files...')
    gui_st.release()

@ui.page('/login')
def login_page():
    """Login page with JWT token generation"""
    if 'jwt_token' not in app.storage.user:
        app.storage.user['jwt_token'] = None

    token = app.storage.user['jwt_token']
    if token and decode_jwt_token(token):
        ui.navigate.to('/')
        return

    def authenticate():
        email = email_input.value
        password = password_input.value


        user = user_service.find_user_by_email(email)
        if not user or user.password != password:
            ui.notify("Invalid credentials", color='negative')
            return

        token = create_jwt_token(user.user_uid)
        app.storage.user['jwt_token'] = token

        ui.notify("Login successful!", color='positive')
        ui.navigate.to('/')

    with ui.card().classes('absolute-center w-96'):
        email_input = ui.input('Email').classes('w-full')
        password_input = ui.input('Password', password=True).classes('w-full')
        ui.button('Login', on_click=authenticate).classes('w-full')

@ui.page('/signup')
def login_page():
    """Signup page"""
    if 'jwt_token' not in app.storage.user:
        app.storage.user['jwt_token'] = None

    token = app.storage.user['jwt_token']
    if token and decode_jwt_token(token):
        ui.navigate.to('/')
        return

    def signup():
        email = email_input.value
        password = password_input.value
        conf_password = conf_password_input.value


        user = user_service.find_user_by_email(email)
        if user:
            ui.notify("Email already exists", color='negative')
            return
        if password!=conf_password:
            ui.notify("Passwords do not match", color='negative')
            return
        user_service.add_user(email=email, password=password)
        ui.notify("Signup successful!", color='positive')
        ui.navigate.to('/login')

    with ui.card().classes('absolute-center w-96'):
        email_input = ui.input('Email').classes('w-full')
        password_input = ui.input('Password', password=True).classes('w-full')
        conf_password_input = ui.input('Confirm password', password=True).classes('w-full')
        ui.button('Signup', on_click=signup).classes('w-full')

def logout():
    """Clear JWT token from storage"""
    app.storage.user['jwt_token'] = None
    ui.navigate.to('/login')

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        title="JWT Auth App",
        storage_secret=os.getenv("UI_STORAGE_KEY"),
        favicon=icon_image_b64,
        port=3000,
        show=True
    )
