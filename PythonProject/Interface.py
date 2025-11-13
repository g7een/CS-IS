import customtkinter as ctk
from pathlib import Path
from Authenticate import open_auth_window
from Dashboard import open_user_dashboard

CARAPI_TOKEN = "05301f7e-cbf6-4654-a6d1-4f5bb4818a38"
"""All App connections and functions have been moved to Dashboard/Authentication frames. This class will load/connect
both when run."""

def start_app():
    open_auth_window(on_success_callback=lambda user_id, username: open_user_dashboard(user_id, username))

if __name__ == "__main__":
    start_app()