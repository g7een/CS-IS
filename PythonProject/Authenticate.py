from pathlib import Path
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage
import customtkinter as ctk
import hashlib
import socket


OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"C:\Users\rkyad\OneDrive\Documents\GitHub\CSIS\PythonProject\assets\frame0")


def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

def open_auth_window(on_success_callback):
    window = Tk()
    window.configure(bg = "#FFFFFF")
    
    w_width=700
    w_height=450
    screen_width=window.winfo_screenwidth()
    screen_height=window.winfo_screenheight()
    x_cordinate=int((screen_width/2)-(w_width/2))
    y_cordinate=int((screen_height/2)-(w_height/2)-50)
    window.geometry(f"{w_width}x{w_height}+{x_cordinate}+{y_cordinate}")


    canvas = Canvas(
        window,
        bg = "#FFFFFF",
        height = 450,
        width = 700,
        bd = 0,
        highlightthickness = 0,
        relief = "ridge"
    )

    username_entry = ctk.CTkEntry(window, placeholder_text="Username", width=210, fg_color="#421E73", text_color="#FFFFFF", border_width=0, corner_radius=0,
                                  font=ctk.CTkFont(size=16, family="Segoe UI"))
    password_entry = ctk.CTkEntry(window, placeholder_text="Password", show="*", width=210, fg_color="#421E73", text_color="#FFFFFF", border_width=0, corner_radius=0,
                                  font=ctk.CTkFont(size=16, family="Segoe UI"))

    canvas.create_window(480, 172, window=username_entry)
    canvas.create_window(480, 262, window=password_entry)




    canvas.place(x = 0, y = 0)
    canvas.create_rectangle(
        0.0,
        0.0,
        700.0,
        450.0,
        fill="#260355",
        outline="")

    canvas.create_text(
        508.0,
        24.0,
        anchor="nw",
        text="CarPartPicker",
        fill="#FFFFFF",
        font=("Inter Bold", 24 * -1)
    )

    image_image_1 = PhotoImage(
        file=relative_to_assets("image_1.png"))
    image_1 = canvas.create_image(
        480.0,
        39.0,
        image=image_image_1
    )

    image_image_2 = PhotoImage(
        file=relative_to_assets("image_2.png"))
    image_2 = canvas.create_image(
        479.0,
        263.0,
        image=image_image_2
    )

    image_image_3 = PhotoImage(
        file=relative_to_assets("image_3.png"))
    image_3 = canvas.create_image(
        479.0,
        172.0,
        image=image_image_3
    )

    image_image_4 = PhotoImage(
        file=relative_to_assets("image_4.png"))
    image_4 = canvas.create_image(
        327.0,
        262.0,
        image=image_image_4
    )

    image_image_5 = PhotoImage(
        file=relative_to_assets("image_5.png"))
    image_5 = canvas.create_image(
        327.0,
        172.0,
        image=image_image_5
    )

    image_image_6 = PhotoImage(
        file=relative_to_assets("image_6.png"))
    image_6 = canvas.create_image(
        131.0,
        225.0,
        image=image_image_6
    )

    image_image_7 = PhotoImage(
        file=relative_to_assets("image_7.png"))
    image_7 = canvas.create_image(
        520.0,
        360.0,
        image=image_image_7
    )

    canvas.create_text(
        473.0,
        349.0,
        anchor="nw",
        text="Log In",
        fill="#FFFFFF",
        font=("Inter Bold", 18 * -1)
    )

    canvas.create_text(
        413.0,
        388.0,
        anchor="nw",
        text="Dont have an account? Sign Up",
        fill="#A09B9B",
        font=("Inter Bold", 12 * -1)
    )

    image_image_8 = PhotoImage(
        file=relative_to_assets("image_8.png"))
    image_8 = canvas.create_image(
        550.0,
        360.0,
        image=image_image_8
    )

    def login():
        user = username_entry.get()
        password = password_entry.get()

        if not user or not password:
            print("Username and password cannot be empty.")
            return

        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(("localhost", 9000))

            client.sendall(f"l:{user}:{password}".encode())

            
            response1 = client.recv(1024).decode()  
            if "login failed" in response1.lower():
                print("Login failed")
                username_entry.delete(0, "end")
                password_entry.delete(0, "end")
                return

            response2 = client.recv(1024).decode()  
            response3 = client.recv(1024).decode()  

            user_id = int(response3.split(":")[1]) if ":" in response3 else int(response3)
            print(f"Logged in as user {user} with ID {user_id}")

            window.destroy()
            on_success_callback(user_id, user)  

        except Exception as e:
            print(f"Login error: {e}")
        finally:
            client.close()
    
    def signup():
        user = username_entry.get()
        password = password_entry.get()
        
        if not user or not password:
            print("Username and password cannot be empty. (this will be a popup)")
            return

        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(("localhost", 9000))

            client.sendall(f"r:{user}:{password}".encode())

            response = client.recv(1024).decode()
            print("Server response:", response)

            if "registration successful" in response.lower():
                print("Signup successful")
                username_entry.delete(0, "end")
                password_entry.delete(0, "end")
            else:
                print("Signup failed:", response)
                username_entry.delete(0, "end")
                password_entry.delete(0, "end")

        except Exception as e:
            print(f"Error: {e}")
        finally:
            client.close()
    
    login_btn = ctk.CTkButton(window, text="Log In", command=login,
                              fg_color="#421E73", text_color="white", font=ctk.CTkFont(size=16, weight="bold", family="Segoe UI"), hover_color="#421E73")
    canvas.create_window(485, 360, window=login_btn)
    login_btn.configure(width=100, height=40, corner_radius=0)
    signup_btn = ctk.CTkButton(window, text="Sign Up", command=signup, text_color="blue",  fg_color="#260355", hover_color="#260355",
                               border_width=0, font=ctk.CTkFont(size=11, weight="bold", family="Segoe UI"))
    signup_btn.configure(width=50, height=26, corner_radius=0)
    canvas.create_window(565, 395, window=signup_btn)


    window.resizable(False, False)
    window.mainloop()

    