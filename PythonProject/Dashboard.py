from pathlib import Path
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage
from PIL import Image
# ctk cannot run during school period
import customtkinter as ctk
import hashlib
import socket
import sqlite3
from datetime import datetime
from openai import OpenAI
client = OpenAI(api_key="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")



OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"C:\Users\rkyad\OneDrive\Documents\GitHub\CSIS\PythonProject\assets1\frame0")
CARAPI_TOKEN = "05301f7e-cbf6-4654-a6d1-4f5bb4818a38"

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

def open_user_dashboard(user_id, username):
    window = Tk()
    #window.iconphoto(file='insertPhotoHere')

    window.geometry("1100x700")
    window.configure(bg = "#260356")
    
    # Creation of canvas and contentFrame that displays widgets
    canvas = Canvas(window, bg = "#260356", height = 700, width = 1100, bd = 0, highlightthickness = 0, relief = "ridge")
    content_frame = ctk.CTkFrame(window, fg_color="#260356", corner_radius=0, width=1020, height=620)
    canvas.create_window(80, 80, window=content_frame, anchor="nw")

    home_label = None
    takeme_btn = None
    update_overlay = None
    update_dropdown = None
    projectParts = []

    # placeholder lambda
    def clicked():
        print("clicked")

    def clear_overlays():
        nonlocal update_overlay, update_dropdown
        if update_overlay is not None:
            update_overlay.place_forget()
            update_overlay = None
        if update_dropdown is not None:
            update_dropdown.place_forget()
            update_dropdown = None
        
    def clearLabels():
        nonlocal home_label, home_label_window, takeme_btn, takeme_btn_window
        if takeme_btn is not None:
            canvas.delete(takeme_btn_window)
            takeme_btn = None
        if home_label is not None:
            canvas.delete(home_label_window)
            home_label = None
        for widget in content_frame.winfo_children():
            widget.destroy() 

    def create_overlay():
        nonlocal update_overlay, update_dropdown
        update_overlay = ctk.CTkScrollableFrame(window, width=360, height=250, fg_color="transparent", corner_radius=12,
            scrollbar_button_color="#8749DF", scrollbar_button_hover_color="#CCAEEC"
        )
        update_overlay.place(x=510, y=262)
        updates_data = {
            "All": [
                "CarPartPicker will switch to CarAPI solely.",
                "UI smoothed and fixed for a seamless experience.",
                "Improved backend communication reliability.",
                "Optimized project loading times.",
                "Added hover animations and transitions.",
                "Database patch for project-part relationships.",
                "New theme adjustments and minor bug fixes."
            ],
            "UI": [
                "UI smoothed and fixed for a seamless experience.",
                "Added hover animations and transitions.",
                "New theme adjustments and minor bug fixes."
            ],
            "API": [
                "CarPartPicker will switch to CarAPI solely.",
                "Improved backend communication reliability."
            ],
            "Fixes": [
                "Database patch for project-part relationships.",
                "Minor bug fixes."
            ],
            "Features": [
                "Optimized project loading times.",
                "Hover animations added to several widgets."
            ]
        }

        def populate_updates(category="All"):
            for widget in update_overlay.winfo_children():
                widget.destroy()
            for text in updates_data.get(category, []):
                ctk.CTkLabel(update_overlay, text=f"• {text}", font=("Segoe UI", 20), text_color="white", anchor="w",
                    justify="left", wraplength=400
                ).pack(anchor="w", padx=15, pady=3)

        populate_updates("All")

        def on_update_filter(choice):
            populate_updates(choice)
            
        update_dropdown = ctk.CTkOptionMenu(master=window, values=list(updates_data.keys()), fg_color="#5E329C", button_color="#8749DF",
            button_hover_color="#CCAEEC", text_color="white", width=140, command=on_update_filter
        )
        update_dropdown.set("All")
        update_dropdown.place(x=728, y=526)

    def change_profile_picture(user_id):
        def upload_image():
            from tkinter import filedialog, messagebox
            file_path = filedialog.askopenfilename(
                title="Select Profile Picture",
                filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")]
            )
            if not file_path:
                return

            try:
                with open(file_path, "rb") as f:
                    img_data = f.read()
                conn = sqlite3.connect("userdata.db")
                cur = conn.cursor()
                cur.execute("UPDATE userdata SET profile_picture = ? WHERE id = ?", (img_data, user_id))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Profile picture updated successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update profile picture: {e}")

    def search_part(entry, combobox, content_frame, user_id=1):
        import socket
        part_id = entry.get().strip()
        quantity = combobox.get().strip()

        if not part_id or not quantity.isdigit():
            errorLabel = ctk.CTkLabel(
                content_frame,
                text="Enter valid Part ID and Quantity",
                text_color="red",
            )
            errorLabel.place(relx=0.1, rely=0.4, anchor="nw")
            return

        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(("localhost", 9000))

            message = f"add:{user_id}:{part_id}:{quantity}"
            client.send(message.encode())

            response = client.recv(4096).decode()

            success = "success" in response.lower()
            text = f"Updated cart for user {user_id}" if success else response
            ctk.CTkLabel(content_frame, text=text, text_color="#00FF00" if success else "red").place(relx=0.1, rely=0.5, anchor="nw")


            client.close()
        except Exception as e:
            ctk.CTkLabel(
                content_frame,
                text=f"Error connecting to server: {e}",
                text_color="red",
                font=ctk.CTkFont(size=16, family="Segoe UI")
            ).place(relx=0.1, rely=0.4, anchor="nw")

    def favorites():
        clear_overlays()
        clearLabels()

        base_path = Path(__file__).parent / "Images"
        try:
            fav_frame_image = ctk.CTkImage(Image.open(base_path / "FavoritesUI.png"), size=(873, 548))
        except Exception as e:
            print(f"Error loading favorites frame image: {e}")

        fav_frame_label = ctk.CTkLabel(content_frame, text="", image=fav_frame_image, fg_color="transparent", height=548, width=873)
        fav_frame_label.place(relx=0.5, rely=0.5, anchor="center")

        
    def open_profile_window(user_id):
        profile_win = ctk.CTkToplevel(window)
        profile_win.title("My Profile")
        profile_win.geometry("500x450")
        profile_win.configure(fg_color="#260356")
        profile_win.resizable(False, False)
        profile_win.attributes("-alpha", 0.0)

        profile_win.wm_transient(window)
        profile_win.grab_set()

        close_btn = ctk.CTkButton(
            profile_win,
            text="Close",
            width=30,
            height=30,
            corner_radius=15,
            fg_color="#A564EB",
            hover_color="#C58EFF",
            text_color="white",
            command=profile_win.destroy
        )
        close_btn.place(x=440, y=10)

        ctk.CTkLabel(
            profile_win,
            text="User Profile",
            font=("Segoe UI", 24, "bold"),
            text_color="white"
        ).pack(pady=(40, 20))

        try:
            conn = sqlite3.connect("userdata.db")
            cur = conn.cursor()
            cur.execute("SELECT id, username, registry FROM userdata WHERE id = ?", (user_id,))
            user = cur.fetchone()
        except Exception as e:
            ctk.CTkLabel(profile_win, text=f"Error: {e}", text_color="red").pack(pady=20)
            return
        finally:
            conn.close()

        if not user:
            ctk.CTkLabel(profile_win, text="User not found.", text_color="red").pack(pady=20)
            return

        uid, uname, reg_date = user

        id_label = ctk.CTkLabel(profile_win, text=f"User ID: {uid}", font=("Segoe UI", 16), text_color="white")
        name_label = ctk.CTkLabel(profile_win, text=f"Username: {uname}", font=("Segoe UI", 16), text_color="white")
        reg_label = ctk.CTkLabel(profile_win, text=f"Registered: {reg_date}", font=("Segoe UI", 16), text_color="white")

        id_label.pack(pady=5)
        name_label.pack(pady=5)
        reg_label.pack(pady=10)

        ctk.CTkLabel(profile_win, text="Change Username or Password", font=("Segoe UI", 18, "bold"), text_color="#C58EFF").pack(pady=(15, 10))

        username_entry = ctk.CTkEntry(profile_win, placeholder_text="New Username", font=("Segoe UI", 14), width=250)
        username_entry.pack(pady=5)

        password_entry = ctk.CTkEntry(profile_win, placeholder_text="New Password", font=("Segoe UI", 14), width=250, show="•")
        password_entry.pack(pady=5)

        status_label = ctk.CTkLabel(profile_win, text="", font=("Segoe UI", 14), text_color="white")
        status_label.pack(pady=10)

        def update_user():
            new_username = username_entry.get().strip()
            new_password = password_entry.get().strip()

            if not new_username and not new_password:
                status_label.configure(text="Enter at least one field to update.", text_color="red")
                return

            try:
                conn = sqlite3.connect("userdata.db")
                cur = conn.cursor()

                if new_username:
                    cur.execute("UPDATE userdata SET username = ? WHERE id = ?", (new_username, user_id))
                    name_label.configure(text=f"Username: {new_username}")
                if new_password:
                    import hashlib
                    hashed_pw = hashlib.sha256(new_password.encode()).hexdigest()
                    cur.execute("UPDATE userdata SET password = ? WHERE id = ?", (hashed_pw, user_id))

                conn.commit()
                status_label.configure(text="Profile updated successfully!", text_color="#00FF88")

                username_entry.delete(0, "end")
                password_entry.delete(0, "end")

            except Exception as e:
                status_label.configure(text=f"Error: {e}", text_color="red")
            finally:
                conn.close()

        save_btn = ctk.CTkButton(
            profile_win,
            text="Save Changes",
            width=160,
            height=40,
            fg_color="#5E329C",
            hover_color="#8749DF",
            corner_radius=10,
            font=("Segoe UI", 16, "bold"),
            command=update_user
        )
        save_btn.pack(pady=(10, 20))

        def fade_in(alpha=0.0):
            if alpha < 1.0:
                alpha += 0.05
                profile_win.attributes("-alpha", alpha)
                profile_win.after(20, lambda: fade_in(alpha))
            else:
                profile_win.attributes("-alpha", 1.0)
        fade_in()

        def on_close():
            profile_win.destroy()

        profile_win.protocol("WM_DELETE_WINDOW", on_close)

    def quit_app():
        window.destroy()

    def return_home():
        nonlocal home_label, home_label_window, takeme_btn, takeme_btn_window
        clear_overlays()
        for widget in content_frame.winfo_children():
            widget.destroy()
        if home_label is None:
            home_label = ctk.CTkLabel(window, image=window.home_img, text="", fg_color="transparent", height=619, width=996)
            home_label_window = canvas.create_window(80, 80, anchor="nw", window=home_label)
        if takeme_btn is None:
            takeme_btn = ctk.CTkButton(window, height=39, width=171, image=window.takeme_img, text="", fg_color="transparent", hover_color="#360A64", command=my_projects)
            takeme_btn_window = canvas.create_window(105,550,anchor="nw",window=takeme_btn)

        create_overlay()

    def compatibility(project_id):
        conn = sqlite3.connect("userdata.db")
        cur = conn.cursor()

        cur.execute("""
            SELECT name, manufacturer, description, price, category, quantity
            FROM project_parts
            WHERE project_id = ?
        """, (project_id,))


        parts = cur.fetchall()
        conn.close()

        if not parts:
            formatted_parts = "No parts found for this project."
        else:
            formatted_parts = "\n".join(
                f"- {name} ({category}) x{qty} — {manufacturer or 'Unknown'}, "
                f"{description or 'No description'} (${price})"
                for name, manufacturer, description, price, category, qty in parts
            )

        prompt = f"""
            You are an expert automotive engineer.

            Evaluate the compatibility of the following project components.
            Output must be STRICT FORMAT:

            X.X - Explanation

            Consider:
            - Engine ↔ transmission compatibility
            - Drivetrain consistency
            - Suspension suitability
            - Electrical system load matching
            - Fuel, cooling, and accessory alignment

            Parts list:
            {formatted_parts}
        """

        try:
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": "Reply ONLY with: X.X - Explanation"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.3
            )

            result = response.choices[0].message["content"].strip()

            if " - " not in result:
                return "3.0 - Formatting issue."

            return result

        except Exception as e:
            print("ChatGPT API Error:", e)
            return "3.0 - Error generating compatibility score."


    def switch_to_compatibility():
        clear_overlays()
        clearLabels()

        base_path = Path(__file__).parent / "Images"
        try:
            comp_frame_image = ctk.CTkImage(Image.open(base_path / "CompatibilityUI.png"), size=(873, 548))
        except Exception as e:
            print(f"Error loading compatibility frame image: {e}")

        comp_frame_label = ctk.CTkLabel(
            content_frame, text="", image=comp_frame_image, 
            fg_color="transparent", height=548, width=873
        )
        comp_frame_label.place(relx=0.5, rely=0.5, anchor="center")

        # Rating label (numeric)
        rating = ctk.CTkLabel(
            content_frame, text='-', width=40, height=28, 
            fg_color="#5D3296",
            font=ctk.CTkFont(size=20, family="Segoe UI", weight='bold'),
            text_color="white"
        )
        rating.place(x=770, y=106, anchor="nw")


        # Load star images
        base_path = Path(__file__).parent / "Ratings"
        try:
            R1 = ctk.CTkImage(Image.open(base_path / "R1.png"), size=(33, 34))
            R2 = ctk.CTkImage(Image.open(base_path / "R2.png"), size=(68, 34))
            R3 = ctk.CTkImage(Image.open(base_path / "R3.png"), size=(103, 34))
            R4 = ctk.CTkImage(Image.open(base_path / "R4.png"), size=(138, 34))
            R5 = ctk.CTkImage(Image.open(base_path / "R5.png"), size=(173, 34))
        except Exception as e:
            print(f"Error loading rating images: {e}")

        R1L = ctk.CTkLabel(content_frame, text='', image=R1, fg_color="#5E3497")
        R2L = ctk.CTkLabel(content_frame, text='', image=R2, fg_color="#5E3497")
        R3L = ctk.CTkLabel(content_frame, text='', image=R3, fg_color="#5E3497")
        R4L = ctk.CTkLabel(content_frame, text='', image=R4, fg_color="#5E3497")
        R5L = ctk.CTkLabel(content_frame, text='', image=R5, fg_color="#5E3497")

        star_labels = [R1L, R2L, R3L, R4L, R5L]

        # Hide all stars initially
        for lbl in star_labels:
            lbl.place_forget()


        # Load user's projects
        conn = sqlite3.connect("userdata.db")
        cur = conn.cursor()
        cur.execute("SELECT project_id, project_name, date_created FROM projects WHERE user_id = ?", (user_id,))
        projects = cur.fetchall()
        conn.close()

        project_list = ctk.CTkScrollableFrame(
            content_frame, width=240, height=300, fg_color="#471B82",
            scrollbar_button_color="#9B9797", corner_radius=0,
            scrollbar_button_hover_color="#F0EBEB"
        )
        project_list.place(x=87, y=160, anchor="nw")

        # Right panel
        details_frame = ctk.CTkFrame(content_frame, width=430, height=350, fg_color="#4F228C", corner_radius=0)
        details_frame.place(x=485, y=195, anchor="nw")

        project_details = ctk.CTkLabel(
            details_frame, text="Select a project to view compatibility.",
            text_color="white", font=ctk.CTkFont(size=16), justify="left", wraplength=400
        )
        project_details.place(x=20, y=20)


        # ⭐ Update star graphic to match rating
        def update_star_display(score_float):
            for lbl in star_labels:
                lbl.place_forget()

            if score_float <= 1.0:
                R1L.place(x=505, y=104, anchor="nw")
            elif score_float <= 2.0:
                R2L.place(x=505, y=104, anchor="nw")
            elif score_float <= 3.0:
                R3L.place(x=505, y=104, anchor="nw")
            elif score_float <= 4.0:
                R4L.place(x=505, y=104, anchor="nw")
            else:
                R5L.place(x=505, y=104, anchor="nw")


        # 🔥 When project is clicked → Generate AI compatibility score
        def select_project(pid, pname, pdate):
            project_details.configure(
                text=f"📦 {pname}\nProject ID: {pid}\n📅 Created: {pdate}\n\nGenerating compatibility...",
                text_color="white"
            )
            content_frame.update()

            # Call ChatGPT compatibility
            result = compatibility(pid)  # <-- Your AI call
            score_str, explanation = result.split(" - ", 1)

            # Update numeric rating
            rating.configure(text=score_str)

            # Convert score to float for star display
            try:
                score_float = float(score_str)
                update_star_display(score_float)
            except:
                update_star_display(3.0)

            # Update explanation
            project_details.configure(
                text=(
                    f"📦 {pname}\nProject ID: {pid}\n📅 Created: {pdate}\n\n"
                    f"⭐ Compatibility Score: {score_str}\n\n"
                    f"{explanation}"
                ),
                wraplength=400,
                justify="left"
            )


        # Build project buttons
        if projects:
            for proj_id, proj_name, proj_date in projects:
                btn = ctk.CTkButton(
                    project_list,
                    text=f"{proj_name}\n📅 {proj_date}",
                    width=250, height=50,
                    fg_color="#482D8C", hover_color="#5E3FC2",
                    command=lambda pid=proj_id, pname=proj_name, pdate=proj_date: select_project(pid, pname, pdate)
                )
                btn.pack(pady=5)
        else:
            ctk.CTkLabel(project_list, text="No projects found.", text_color="gray").pack(pady=20)

  
    def switch_to_resell():
        clear_overlays()
        clearLabels()

        base_path = Path(__file__).parent / "Images"
        try:
            resell_ctk_image = ctk.CTkImage(Image.open(base_path / "Resell_Frame.png"), size=(913, 553))
        except Exception as e:
            print(f"Error {e}")

        resell_label = ctk.CTkLabel(content_frame, text="", image=resell_ctk_image,
                                    fg_color="transparent", height=553, width=913)
        resell_label.place(relx=0.5, rely=0.5, anchor="center")

        zip_code_entry = ctk.CTkEntry(content_frame, placeholder_text="e.g. 77777",
                                    font=ctk.CTkFont(size=16, family="Segoe UI"),
                                    width=100, height=40, corner_radius=8,
                                    border_width=0, fg_color="#250356", text_color="white")
        zip_code_entry.place(x=310, y=59, anchor="nw")

        distance_entry = ctk.CTkEntry(content_frame, placeholder_text="e.g. 25 miles",
                                    font=ctk.CTkFont(size=16, family="Segoe UI"),
                                    width=100, height=40, corner_radius=8,
                                    border_width=0, fg_color="#250356", text_color="white")
        distance_entry.place(x=310, y=107, anchor="nw")

        query_btn = ctk.CTkButton(content_frame, text="Query Locations",font=ctk.CTkFont(size=16, family="Segoe UI"),
                                corner_radius=12, fg_color="#5E329C", hover_color="#693FA5", command=lambda: query_locations_osm(zip_code_entry, distance_entry))
        query_btn.place(x=316, y=142, anchor="nw")

        locations = ctk.CTkScrollableFrame(content_frame, width=860, height=250,
                                        fg_color="#3F1874", scrollbar_button_color="#A392BB")
        locations.place(x=70, y=290, anchor="nw")

        queryPart = ctk.CTkButton(content_frame, text="Open Query Window",font=ctk.CTkFont(size=16, family="Segoe UI"), corner_radius=12,
                                  fg_color="#5E329C", hover_color="#7654A5", width=300, height=120, command=lambda: qpart_popup())
        queryPart.place(x=630, y=87, anchor="nw")

        headers = ["Shop Name", "Address", "Contact"]
        header_font = ctk.CTkFont(size=15, weight="bold", family="Segoe UI")
        for col, text in enumerate(headers):
            ctk.CTkLabel(locations, text=text, text_color="white",fg_color="#5E329C", corner_radius=6,font=header_font, width=280, height=35
                        ).grid(row=0, column=col, padx=4, pady=4, sticky="nsew")

        for col in range(len(headers)):
            locations.grid_columnconfigure(col, weight=1)

        def qpart_popup():
            import requests

            popup = ctk.CTkToplevel(window)
            popup.title("Part Query")
            popup.geometry("650x480")
            popup.configure(fg_color="#260356")
            popup.grab_set()

            bg_frame = ctk.CTkFrame(popup, fg_color="#41127E", width=640, height=470, corner_radius=12)
            bg_frame.place(relx=0.5, rely=0.5, anchor="center")

            ctk.CTkLabel(bg_frame, text="🔍 Part Query", font=ctk.CTkFont(size=22, weight="bold", family="Segoe UI"),
                        text_color="white").place(x=25, y=15)
            search_entry = ctk.CTkEntry(bg_frame, placeholder_text="Enter part name or ID...",width=400, height=40, corner_radius=8,
                                        fg_color="#250356", text_color="white",font=ctk.CTkFont(size=15, family="Segoe UI"))
            search_entry.place(x=25, y=60)
            search_btn = ctk.CTkButton(bg_frame, text="Search", width=100, height=40, fg_color="#5E329C", hover_color="#8749DF",
                                    font=ctk.CTkFont(size=15, family="Segoe UI", weight="bold"))
            search_btn.place(x=440, y=60)

            results_frame = ctk.CTkScrollableFrame(bg_frame, width=580, height=280, fg_color="#3F1874", scrollbar_button_color="#A392BB",
                                                   corner_radius=12)
            results_frame.place(x=25, y=120)


            bottom_frame = ctk.CTkFrame(bg_frame, fg_color="#6A42AA",
                                        width=580, height=70, corner_radius=20)
            bottom_frame.place(x=25, y=415, anchor="sw")

            result_label = ctk.CTkLabel(bottom_frame, text="Select a part above to view details.",
                                        font=ctk.CTkFont(size=14, family="Segoe UI"),
                                        text_color="white", justify="left", anchor="w", wraplength=560)
            result_label.place(x=20, y=15)


            def perform_query():
                query = search_entry.get().strip()
                for widget in results_frame.winfo_children():
                    widget.destroy()

                if not query:
                    ctk.CTkLabel(results_frame, text="Please enter a search term.",
                                text_color="red", font=ctk.CTkFont(size=14)).pack(pady=10)
                    return
                mock_parts = [
                    {"name": "Alternator A101", "id": "ALT-001", "desc": "High-output alternator 12V"},
                    {"name": "Brake Pad Set B202", "id": "BRK-002", "desc": "Ceramic pads for improved grip"},
                    {"name": "Oil Filter F303", "id": "OIL-003", "desc": "Long-life synthetic oil filter"},
                    {"name": "Air Intake I404", "id": "AIR-004", "desc": "Cold air intake system for sedans"}
                ]
                filtered = [p for p in mock_parts if query.lower() in p["name"].lower() or query.lower() in p["id"].lower()]

                if not filtered:
                    ctk.CTkLabel(results_frame, text=f"No parts found for '{query}'",
                                text_color="#CCAEEC").pack(pady=10)
                    return
                for part in filtered:
                    def select_part(p=part):
                        result_label.configure(
                            text=f"🧩 {p['name']}\nID: {p['id']}\n{p['desc']}"
                        )
                    ctk.CTkButton(results_frame,
                                text=f"{part['name']}  |  ID: {part['id']}",
                                fg_color="#5A3392", hover_color="#8749DF",
                                text_color="white", corner_radius=8,
                                font=ctk.CTkFont(size=15),
                                command=select_part).pack(pady=5, padx=10, fill="x")

            search_btn.configure(command=perform_query)

        def query_locations_osm(zip_code_entry, distance_entry):
            import requests
            zip_code = zip_code_entry.get().strip()
            distance = distance_entry.get().strip().split()[0]

            for widget in locations.winfo_children()[len(headers):]:
                widget.destroy()

            if not zip_code.isdigit() or not distance.isdigit():
                ctk.CTkLabel(locations, text="Enter valid ZIP and distance.", text_color="red").grid(row=1, column=0, columnspan=3)
                return

            radius_meters = int(distance) * 1609.34

            try:
                geo_resp = requests.get(
                    f"https://nominatim.openstreetmap.org/search?postalcode={zip_code}&countrycodes=us&format=json",
                    headers={"User-Agent": "CarPartPickerApp/1.0"},
                    timeout=10
                )
                geo_data = geo_resp.json()
                if not geo_data:
                    raise ValueError("Invalid ZIP code.")
                
                lat, lon = float(geo_data[0]["lat"]), float(geo_data[0]["lon"])
            except Exception as e:
                ctk.CTkLabel(locations, text=f"Error locating ZIP: {e}", text_color="red").grid(row=1, column=0, columnspan=3)
                return
            try:
                query = f"""
                [out:json];
                node(around:{radius_meters},{lat},{lon})["shop"~"car|car_repair|car_parts|automotive"];
                out;
                """
                resp = requests.post("https://overpass-api.de/api/interpreter", data=query, timeout=20)
                data = resp.json()
                results = data.get("elements", [])
            except Exception as e:
                ctk.CTkLabel(locations, text=f"Overpass error: {e}", text_color="red").grid(row=1, column=0, columnspan=3)
                return

            if not results:
                ctk.CTkLabel(locations, text="No auto part shops found nearby.", text_color="#CCAEEC").grid(row=1, column=0, columnspan=3)
                return

            body_font = ctk.CTkFont(size=14, family="Segoe UI")
            for i, elem in enumerate(results[:10], start=1):
                tags = elem.get("tags", {})
                name = tags.get("name", "Unnamed Shop")
                address_parts = [tags.get("addr:street", ""), tags.get("addr:city", ""), tags.get("addr:state", "")]
                address = ", ".join([p for p in address_parts if p])
                phone = tags.get("phone", "N/A")

                # Each row
                values = [name, address if address else "Address not available", phone]
                for j, value in enumerate(values):
                    ctk.CTkLabel(
                        locations, text=value, text_color="white",
                        fg_color="#4C2389", corner_radius=4,
                        font=body_font, width=280, height=32,
                        wraplength=260, justify="left"
                    ).grid(row=i, column=j, padx=4, pady=3, sticky="nsew")

    def open_suspension_popup(ridx, button_widget, pid, pframe):
        import requests
        popup = ctk.CTkToplevel(window)
        popup.title("Select a Suspension")
        popup.geometry("600x400")
        popup.configure(fg_color="#260356")
        popup.grab_set()

        sL = ctk.CTkLabel(window=popup, text="Fetching Suspensions..", font=ctk.CTkFont("Segoe UI", 18, "Bold"))
        sL.pack(pady=10)

        def fetch_suspension_popup():
            try:
                url = "https://api.carapi.app/suspensions"
                headers = {
                    "accept": "application/json",
                    "authorization": f"Bearer {CARAPI_TOKEN}"
                }
                resp = requests.get(url, headers=headers, timeout=10)

                data = resp.json()

                for widget in frame.winfo_children():
                    widget.destroy()

                engines = data.get("data", [])
                if not engines:
                    ctk.CTkLabel(frame, text="No engines found.", text_color="red").pack(pady=10)
                    return

                for eng in engines[:10]:
                    name = eng.get("name", "Unknown Engine")
                    manufacturer = eng.get("make", "Unknown")
                    displacement = eng.get("displacement", "N/A")

                    def select_engine(e=name, m=manufacturer, d=displacement):
                        popup.destroy()
                        if button_widget and button_widget.winfo_exists():
                            button_widget.destroy()
                        ctk.CTkLabel(parts_frame, text=f"{e}\n{m}\n{d}", text_color="#FFFFFF", fg_color="#5A3392", corner_radius=8,
                            width=190, height=60, font=ctk.CTkFont(size=13), justify="left"
                        ).grid(row=row_index, column=0, pady=3, padx=13)

                        try:
                            conn = sqlite3.connect("userdata.db")
                            cur = conn.cursor()
                            cur.execute("""
                                INSERT INTO project_parts (project_id, part_id, quantity)
                                VALUES (?, ?, 1)
                            """, (project_id, eng.get("id", 0)))
                            conn.commit()
                            conn.close()
                        except Exception as e:
                            print("DB save error:", e)

                    ctk.CTkButton(frame, text=f"{name} | {manufacturer} | {displacement}", fg_color="#5A3392", hover_color="#8749DF",
                        text_color="white", font=ctk.CTkFont(size=13), command=select_engine
                    ).pack(pady=3, padx=10, fill="x")

            except Exception as e:
                for widget in frame.winfo_children():
                    widget.destroy()
                ctk.CTkLabel(frame, text=f"Error fetching engines: {e}", text_color="red").pack(pady=10)

    def open_engine_popup(row_index, button_widget, project_id, parts_frame):
        import requests 
        popup = ctk.CTkToplevel(window)
        popup.title("Select an Engine")
        popup.geometry("600x400")
        popup.configure(fg_color="#260356")
        popup.grab_set()

        eL = ctk.CTkLabel(popup, text="Fetching available engines...", font=ctk.CTkFont(size=18, weight="bold"), text_color="white")
        eL.pack(pady=10)

        frame = ctk.CTkScrollableFrame(popup, fg_color="#3A1A6B", width=560, height=300)
        frame.pack(pady=10)

        def fetch_carapi_engines():
            try:
                url = "https://api.carapi.app/v2/engines"
                headers = {
                    "accept": "application/json",
                    "authorization": f"Bearer {CARAPI_TOKEN}"
                }
                resp = requests.get(url, headers=headers, timeout=10)

                data = resp.json()

                for widget in frame.winfo_children():
                    widget.destroy()

                engines = data.get("data", [])
                if not engines:
                    ctk.CTkLabel(frame, text="No engines found.", text_color="red").pack(pady=10)
                    return

                for eng in engines[:10]:
                    name = eng.get("name", "Unknown Engine")
                    manufacturer = eng.get("make", "Unknown")
                    displacement = eng.get("displacement", "N/A")

                    def select_engine(e=name, m=manufacturer, d=displacement):
                        popup.destroy()
                        if button_widget and button_widget.winfo_exists():
                            button_widget.destroy()
                        ctk.CTkLabel(parts_frame, text=f"{e}\n{m}\n{d}", text_color="#FFFFFF", fg_color="#5A3392", corner_radius=8,
                            width=190, height=60, font=ctk.CTkFont(size=13), justify="left"
                        ).grid(row=row_index, column=0, pady=3, padx=13)

                        try:
                            conn = sqlite3.connect("userdata.db")
                            cur = conn.cursor()
                            cur.execute("""
                                INSERT INTO project_parts (project_id, part_id, quantity)
                                VALUES (?, ?, 1)
                            """, (project_id, eng.get("id", 0)))
                            conn.commit()
                            conn.close()
                        except Exception as e:
                            print("DB save error:", e)

                    ctk.CTkButton(frame, text=f"{name} | {manufacturer} | {displacement}", fg_color="#5A3392", hover_color="#8749DF",
                        text_color="white", font=ctk.CTkFont(size=13), command=select_engine
                    ).pack(pady=3, padx=10, fill="x")

            except Exception as e:
                for widget in frame.winfo_children():
                    widget.destroy()
                ctk.CTkLabel(frame, text=f"Error fetching engines: {e}", text_color="red").pack(pady=10)

        window.after(200, fetch_carapi_engines)
        
    def component_popup(type, project_id):
        import requests
        popup = ctk.CTkToplevel(window)
        popup.title(f"{type.title()} Selection")
        popup.geometry("600x600")
        popup.configure(fg_color="#260356")
        popup.grab_set()

        eL = ctk.CTkLabel(popup, text="Fetching available data...", font=ctk.CTkFont(size=18, weight="bold"), text_color="white")
        eL.pack(pady=10)

        # load unique data (type)
        # issue with api connection (token may have expired)
        if type.title() == "Engine":
            try:
                url = "https://api.carapi.app/v2/engines"
                headers = {
                    "accept": "application/json",
                    "authorization": f"Bearer {CARAPI_TOKEN}"
                }
                resp = requests.get(url, headers=headers, timeout=10)
                data = resp.json()

                engines = data.get("data", [])
                if engines == None:
                    print("No engine data-")
            except Exception as e:
                print(f"API Error - {e}")

        if type.title() == "Transmission":
            try:
                url = "https://api.carapi.app/v2/X"
                headers = {
                    "accept": "application/json",
                    "authorization": f"Bearer {CARAPI_TOKEN}"
                }
                resp = requests.get(url, headers=headers, timeout=10)
                data = resp.json()

                engines = data.get("data", [])
                if engines == None:
                    print("No transmission data-")
            except Exception as e:
                print(f"API Error - {e}")

        if type.title() == "Suspension":
            try:
                url = "https://api.carapi.app/v2/X"
                headers = {
                    "accept": "application/json",
                    "authorization": f"Bearer {CARAPI_TOKEN}"
                }
                resp = requests.get(url, headers=headers, timeout=10)
                data = resp.json()

                engines = data.get("data", [])
                if engines == None:
                    print("No suspension data-")
            except Exception as e:
                print(f"API Error - {e}")

        if type.title() == "Brakes":
            try:
                url = "https://api.carapi.app/v2/X"
                headers = {
                    "accept": "application/json",
                    "authorization": f"Bearer {CARAPI_TOKEN}"
                }
                resp = requests.get(url, headers=headers, timeout=10)
                data = resp.json()

                engines = data.get("data", [])
                if engines == None:
                    print("No brakes data-")
            except Exception as e:
                print(f"API Error - {e}")

        if type.title() == "Chassis":
            try:
                url = "https://api.carapi.app/v2/X"
                headers = {
                    "accept": "application/json",
                    "authorization": f"Bearer {CARAPI_TOKEN}"
                }
                resp = requests.get(url, headers=headers, timeout=10)
                data = resp.json()

                engines = data.get("data", [])
                if engines == None:
                    print("No chassis data-")
            except Exception as e:
                print(f"API Error - {e}")

        if type.title() == "Tires":
            try:
                url = "https://api.carapi.app/v2/X"
                headers = {
                    "accept": "application/json",
                    "authorization": f"Bearer {CARAPI_TOKEN}"
                }
                resp = requests.get(url, headers=headers, timeout=10)
                data = resp.json()

                engines = data.get("data", [])
                if engines == None:
                    print("No tires data-")
            except Exception as e:
                print(f"API Error - {e}")

        if type.title() == "Exhaust":
            try:
                url = "https://api.carapi.app/v2/X"
                headers = {
                    "accept": "application/json",
                    "authorization": f"Bearer {CARAPI_TOKEN}"
                }
                resp = requests.get(url, headers=headers, timeout=10)
                data = resp.json()

                engines = data.get("data", [])
                if engines == None:
                    print("No exhaust data-")
            except Exception as e:
                print(f"API Error - {e}")

        if type.title() == "Air Filter":
            try:
                url = "https://api.carapi.app/v2/X"
                headers = {
                    "accept": "application/json",
                    "authorization": f"Bearer {CARAPI_TOKEN}"
                }
                resp = requests.get(url, headers=headers, timeout=10)
                data = resp.json()

                engines = data.get("data", [])
                if engines == None:
                    print("No air filter data-")
            except Exception as e:
                print(f"API Error - {e}")
    
    def delete_forum_message(message_id):
        conn = sqlite3.connect("userdata.db")
        cur = conn.cursor()

        cur.execute("DELETE FROM forum_messages WHERE id = ?", (message_id,))

        conn.commit()
        conn.close()
        
        save_popup("Message deleted successfully.")

        # Update the forum view
        forum(user_id, username)
        
    def save_forum_message(user_id, username, message):
        conn = sqlite3.connect("userdata.db")
        cur = conn.cursor()
        from datetime import datetime

        def check_limit():
            cur.execute("SELECT COUNT(*) FROM forum_messages WHERE user_id = ? AND timestamp >= datetime('now', '-1 hour')", (user_id,))
            count = cur.fetchone()[0]
            return count < 5
        
        if not check_limit():
            print("Message limit reached.")
            return
        if message.strip() == "":
            print("Empty message, not saved.")
            return
        
        cur.execute("INSERT INTO forum_messages (user_id, username, message, timestamp) VALUES (?, ?, ?, ?)",
                (user_id, username, message, datetime.now().strftime("%m/%d/%Y %I:%M:%S %p")))
        
        save_popup("Message posted successfully!")
        
        conn.commit()
        conn.close()

    def forum(user_id, username):
        base_path = Path(__file__).parent / "Images"
        try:
            forum_bg_img = ctk.CTkImage(Image.open(base_path / "Forum.png"), size=(450, 800))
            postM = ctk.CTkImage(Image.open(base_path / "Post.png"), size=(128, 43))
        except Exception as e:
            print(f"Error loading forum background image: {e}")
            forum_bg_img = None
        print("Opening forum for user:", username)

        forum = ctk.scrollable_frame(content_frame, text="", image=forum_bg_img, fg_color="transparent", height=450, width=800)
        forum.place(relx=0.5, rely=0, anchor="center")

        entry = ctk.entry(forum, fg_color="#7745BD", placeholder_text="Add a message.", font=("Segoe UI", 12, "bold"), width="385", height="40", corner_radius="12")
        entry.place(x=(372-335), y=(732-88), anchor="nw")

        postMessage = ctk.CTkButton(forum, fg_color="#5E329C", text="", width="128", height="43", corner_radius="12", image=postM, command=lambda: save_forum_message(user_id, username, entry.get()))
        postMessage.place(x=(637-335), y=(799-88), anchor="nw")

        #Load existing messages
        conn = sqlite3.connect("userdata.db")
        cur = conn.cursor()
        cur.execute("SELECT id, user_id, username, message, timestamp FROM forum_messages ORDER BY timestamp DESC")
        messages = cur.fetchall()

        conn.close()
        offset_messages = 15
        for msg_id, uid, uname, msg, ts in messages:

            msg_frame = ctk.CTkFrame(forum, fg_color="#5A3392", width=700, height=100, corner_radius=12)
            msg_frame.place(x=50, y=offset_messages, anchor="nw")

            msg_label = ctk.CTkLabel(msg_frame, text=f"{uname} (@{ts}):\n{msg}", font=("Segoe UI", 12), text_color="white", justify="left", wraplength=650)
            msg_label.place(x=10, y=10)

            if uid == user_id:
                delete_btn = ctk.CTkButton(msg_frame, text="Delete", fg_color="#AA3333", hover_color="#FF5555", width=60, height=30,
                                           command=lambda mid=msg_id: delete_forum_message(mid))
                delete_btn.place(x=620, y=60)

            offset_messages += 110
        
        def open_profile(user_id, username):
            uid = user_id
            user = username
            profile_win = ctk.CTkToplevel(window)
            profile_win.title("My Profile")
            profile_win.geometry("500x450")
            profile_win.configure(fg_color="#260356")
            profile_win.resizable(False, False)
            profile_win.attributes("-alpha", 0.0)

            profile_win.wm_transient(window)
            profile_win.grab_set()

            close_btn = ctk.CTkButton(
                profile_win,
                text="Close",
                width=30,
                height=30,
                corner_radius=15,
                fg_color="#A564EB",
                hover_color="#C58EFF",
                text_color="white",
                command=profile_win.destroy
            )
            close_btn.place(x=440, y=10)

            ctk.CTkLabel(
                profile_win,
                text="User Profile",
                font=("Segoe UI", 24, "bold"),
                text_color="white"
            ).pack(pady=(40, 20))

            try:
                conn = sqlite3.connect("userdata.db")
                cur = conn.cursor()
                cur.execute("SELECT id, username, registry FROM userdata WHERE id = ?", (user_id,))
                user = cur.fetchone()
            except Exception as e:
                ctk.CTkLabel(profile_win, text=f"Error: {e}", text_color="red").pack(pady=20)
                return
            finally:
                conn.close()

            clear_overlays()
            clearLabels()
            uid = user_id
            user = username

            forum_window = ctk.CTkToplevel(window)
            forum_window.title("My Profile")
            forum_window.geometry("900x600")
            forum_window.configure(fg_color="#260356")
            forum_window.resizable(False, False)

            message_board = ctk.scrollable_frame(forum_window, width=700, height=400, fg_color="transparent", 
                scrollbar_button_color="#FFFFFF", )
            message_board.place(x=100, y=100, anchor="nw", fill="both")

            forum_hero = ctk.label(img="placeimagehere.png", width=900, height=60)
            forum_hero.place(x=0, y=0, anchor="nw")

            forum_entry = ctk.entry(forum_window, fg_color="transparent", placeholder_text="Add a message.", font=("Segoe UI", 20, "bold"), width="80", height="60", corner_radius="12")
            forum_entry.place(x=720, y=520, anchor="nw")

            forum_post = ctk.CTkButton(forum_window, fg_color="transparent", text="Post Message", width=60, height="40", corner_radius="12")
            forum_post.place(x=720, y=580)

    

    # loads user projects from server db, if none are found there is a creation option
    # TODO: figure out why content_frame is deleted sometimes
    # TODO: tidy up code and minimize redundancy
    def projects_menu(content_frame, user_id, myProjects):
        clearLabels()
        clear_overlays()
        if not content_frame.winfo_exists():
            print("Content frame no longer exists — skipping projects_menu() call.")
            return

        # Safely clear existing widgets
        for widget in content_frame.winfo_children():
            try:
                widget.destroy()
            except:
                pass
        base_path = Path(__file__).parent / "Images"

        try:
            header_img = ctk.CTkImage(Image.open(base_path / "PMenuHeader.png"), size=(800, 70))
            menu_bg_img = ctk.CTkImage(Image.open(base_path / "PMenu_bg.png"), size=(700, 650))
            new_project_img = ctk.CTkImage(Image.open(base_path / "NewProject.png"), size=(486, 76))
            user_project_img = ctk.CTkImage(Image.open(base_path / "ProjectCell.png"), size=(470, 60))
        except Exception as e:
            print(f"Error loading project menu images: {e}")

        header = ctk.CTkLabel(content_frame, text="", image=header_img, fg_color="transparent", height=70, width=800)
        header.place(x=100, y=0, anchor="nw")

        menu = ctk.CTkScrollableFrame(content_frame, fg_color="#350972", corner_radius=0, width=700, height=540, scrollbar_button_color="#A392BB"
                                      , scrollbar_button_hover_color="#FFFFFF")
        menu.place(x=150, y=70, anchor="nw")

        greeting = ctk.CTkLabel(content_frame, text=f"👋 Hello {username}! Choose a project to begin customizing", font=("Segoe UI", 20, "bold"), text_color="white", fg_color="#6522C0")
        greeting.place(x=250, y=20, anchor="nw")

        conn = sqlite3.connect("userdata.db")
        cur = conn.cursor()
        cur.execute("SELECT project_id, project_name, date_created FROM projects WHERE user_id = ?", (user_id,))
        projects = cur.fetchall()
        conn.close()

        # --- Populate projects as buttons ---
        if projects:
            for proj_id, proj_name, proj_date in projects:
                btn = ctk.CTkButton(
                    menu,
                    text=f"{proj_name}\n📅 {proj_date}",
                    width=320,
                    height=60,
                    corner_radius=10,
                    fg_color="#482D8C",
                    hover_color="#5E3FC2",
                    command=lambda pid=proj_id: my_projects(pid)
                )
                btn.pack(pady=8)
        else:
            no_proj_label = ctk.CTkLabel(
                menu,
                text="No projects found.",
                text_color="gray",
                font=("Segoe UI", 16)
            )
            no_proj_label.pack(pady=(20, 10))

        # --- New Project button ---

        new_proj_btn = ctk.CTkButton(
            menu,
            text="➕ New Project",
            width=320,
            height=50,
            corner_radius=8,
            fg_color="#3E1E7A",
            hover_color="#5A2EB0",
            command=lambda: create_new_project_popup(user_id, menu, my_projects)
        )
        new_proj_btn.pack(pady=20)

    def create_new_project_popup(user_id, parent_frame, myProjects):
        popup = ctk.CTkToplevel()
        popup.title("New Project")
        popup.geometry("350x200")
        popup.resizable(False, False)
        popup.grab_set()
        popup.focus_force()

        ctk.CTkLabel(popup, text="Enter new project name:", font=("Segoe UI", 14)).pack(pady=(20, 10))
        entry = ctk.CTkEntry(popup, width=250, placeholder_text="My Project Name")
        entry.pack(pady=10)

        def confirm_create():
            name = entry.get().strip()
            if not name:
                ctk.CTkLabel(popup, text="Name cannot be empty.", text_color="red").pack()
                return

            conn = sqlite3.connect("userdata.db")
            cur = conn.cursor()
            from datetime import datetime
            cur.execute(
                "INSERT INTO projects (user_id, project_name, date_created) VALUES (?, ?, ?)",
                (user_id, name, datetime.now().strftime("%m/%d/%Y %I:%M:%S %p"))
            )
            conn.commit()
            conn.close()
            popup.destroy()
            # Reload menu
            projects_menu(parent_frame.master, user_id, myProjects)

        ctk.CTkButton(popup, text="Create", fg_color="#4B2FB8", command=confirm_create).pack(pady=20)

    # will recieve ID and load project accordingly
    def my_projects(projectId):
        clearLabels()
        clear_overlays()
        for widget in content_frame.winfo_children():
            widget.destroy()
        base_path = Path(__file__).parent / "Images"

        scroll_frame = ctk.CTkScrollableFrame(content_frame, fg_color="#18003A", corner_radius=0,
            width=1000, height=620
        )
        scroll_frame.pack(fill="both", expand=True)
        
        conn = sqlite3.connect("userdata.db")
        cur = conn.cursor()
        cur.execute("SELECT project_name, date_created FROM projects WHERE project_id = ?", (projectId,))
        projects = cur.fetchone()
        conn.close()
        header_text = f"Name: {projects[0]} | Created: {projects[1]}"

        # load project data from db and customize heading label

        try:
            build_img = Image.open(base_path / "Project_Frame.png")
            build_ctk_image = ctk.CTkImage(build_img, size=(build_img.width, build_img.height))
            img_label = ctk.CTkLabel(scroll_frame, text="", image=build_ctk_image)
            img_label.image = build_ctk_image
            img_label.pack(padx=0, pady=0, fill="both", expand=True)
        except Exception as e:
            print(f"Error loading project frame image: {e}")
        
        currDate = datetime.now()
        r_date = currDate.strftime("%m/%d/%Y %I:%M:%S %p")
        date_label = ctk.CTkLabel(scroll_frame, text=f"{r_date}", font=ctk.CTkFont(size=12, family="Segoe UI"), text_color="white", fg_color="#AA95C8")
        date_label.place(x=190, y=74, anchor="nw")

        try:
            engine_img = ctk.CTkImage(Image.open(base_path / "Engine.png"), size=(120, 39))
            transmission_img = ctk.CTkImage(Image.open(base_path / "Transmission.png"), size=(165, 45))
            suspension_img = ctk.CTkImage(Image.open(base_path / "Suspension.png"), size=(150, 39))
            brakes_img = ctk.CTkImage(Image.open(base_path / "Brakes.png"), size=(120, 39))
            chassis_img = ctk.CTkImage(Image.open(base_path / "Chassis.png"), size=(130, 39))
            tires_img = ctk.CTkImage(Image.open(base_path / "Tires.png"), size=(108, 39))
            exhaust_img = ctk.CTkImage(Image.open(base_path / "Exhaust.png"), size=(130, 39))
            airfilter_img = ctk.CTkImage(Image.open(base_path / "AirFilter.png"), size=(125, 39))
            save_img = ctk.CTkImage(Image.open(base_path / "SaveProject.png"), size=(195, 45))
        except Exception as e:
            print(f"Error loading button images: {e}")

        engine_btn = ctk.CTkButton(scroll_frame, image=engine_img, text="", fg_color="transparent", border_width=0, hover_color="#170438", command=clicked)
        engine_btn.place(x=180, y=165, anchor="nw")
        transmission_btn = ctk.CTkButton(scroll_frame, image=transmission_img, text="", fg_color="transparent", border_width=0, hover_color="#170438", command=clicked)
        transmission_btn.place(x=180, y=235, anchor="nw")
        suspension_btn = ctk.CTkButton(scroll_frame, image=suspension_img, text="", fg_color="transparent", border_width=0, hover_color="#170438", command=clicked)
        suspension_btn.place(x=180, y=304, anchor="nw")
        brakes_btn = ctk.CTkButton(scroll_frame, image=brakes_img, text="", fg_color="transparent", border_width=0, hover_color="#170438", command=clicked)
        brakes_btn.place(x=180, y=373, anchor="nw")
        chassis_btn = ctk.CTkButton(scroll_frame, image=chassis_img, text="", fg_color="transparent", border_width=0, hover_color="#170438", command=clicked)
        chassis_btn.place(x=180, y=440, anchor="nw")
        tires_btn = ctk.CTkButton(scroll_frame, image=tires_img, text="", fg_color="transparent", border_width=0, hover_color="#170438", command=clicked)
        tires_btn.place(x=174, y=509, anchor="nw")
        exhaust_btn = ctk.CTkButton(scroll_frame, image=exhaust_img, text="", fg_color="transparent", border_width=0, hover_color="#170438", command=clicked)
        exhaust_btn.place(x=180, y=577, anchor="nw")
        airfilter_btn = ctk.CTkButton(scroll_frame, image=airfilter_img, text="", fg_color="transparent", border_width=0, hover_color="#170438", command=clicked)
        airfilter_btn.place(x=180, y=646, anchor="nw")
        save_btn = ctk.CTkButton(scroll_frame, image=save_img, text="", fg_color="transparent", border_width=0, hover_color="#170438", command=lambda: save_popup("Project saved successfully!"))
        save_btn.place(x=715, y=746, anchor="nw")

        projectParts = []

        header = ctk.CTkLabel(scroll_frame, text=header_text, font=ctk.CTkFont(size=20, weight="bold", family="Segoe UI"), text_color="white", fg_color="#7C39D3")
        header.place(x=255,y=38, anchor="nw")

    def save_project(projectId, name):
        conn = sqlite3.connect("userdata.db")
        cur = conn.cursor()

        cur.execute("SELECT 1 FROM projects WHERE project_id = ?", (projectId,))
        if cur.fetchone():
            cur.execute("UPDATE project_name SET = ?", (name))
            # TODO: Part saving logic
            cur.execute("SELECT * FROM project_parts WHERE project_id = ?", (projectId,))
            if cur.fetchall() is not None:
                for part in projectParts:
                    cur.execute("UPDATE project_parts SET = (link_id, part_id, quantity) VALUES (?, ?, ?)", ())
                    print("Individual part saved for "+{projectId})

                    conn = sqlite3.connect("userdata.db")
                    cur = conn.cursor()

                    cur.execute("SELECT * FROM project_parts WHERE project_id = ?", (proj_id,))
                    """
                    if part_id is in cur.fetchall():
                        print({proj_id} + " Exists, part not added")
                    if cur is None:
                        print({proj_id}+ " ID not found (Project)")
                    else:
                        if cur.execute("INSERT INTO project_parts (project_id, part_id, quantity) VALUES (?, ?, ?)", (proj_id, part_id, qty)):
                            return
                        else:
                            print("Part addition failed")
                        
                        save_popup(content_frame)
                    """

        else:
            print("project_id not found")

    def save_popup(message):
        window.update_idletasks()

        popup_height=60
        popup_width = window.winfo_width()
        app_x = window.winfo_rootx()
        app_y = window.winfo_rooty()

        start_y = app_y-popup_height-8
        target_y = app_y-5

        toast = ctk.CTkToplevel(window)
        toast.overrideredirect(True)
        toast.wm_transient(window)
        toast.lift()
        toast.attributes("-topmost", True)

        toast.geometry(f"{int(popup_width)}x{int(popup_height)}+{int(app_x)}+{int(start_y)}")
        toast.configure(fg_color="#27AE60")

        label = ctk.CTkLabel(
            toast,
            text=f"🗹  {message}",
            text_color="white",
            font=ctk.CTkFont(size=24, weight="bold", family="Segoe UI"),
            anchor="w",
            padx=20
        )
        label.place(relx=0.0, rely=0.0, relwidth=1.0, relheight=1.0)

        step = 6
        fade_step = 0.06
        delay = 12
        alpha = 0.0
        y = start_y

        def animate_in():
            nonlocal y, alpha
            finished_y = False
            if y < target_y:
                y += step
                if y > target_y:
                    y = target_y
                    finished_y = True
            else:
                finished_y = True

            if alpha < 1.0:
                alpha = min(1.0, alpha + fade_step)

            toast.geometry(f"{int(popup_width)}x{int(popup_height)}+{int(app_x)}+{int(y)}")
            try:
                toast.attributes("-alpha", alpha)
            except Exception:
                pass

            if not (finished_y and alpha >= 1.0):
                toast.after(delay, animate_in)
            else:
                toast.after(1700, animate_out)

        def animate_out():
            nonlocal y, alpha
            if alpha > 0.0:
                alpha = max(0.0, alpha - fade_step)
                y -= max(1, step // 2)
                toast.geometry(f"{int(popup_width)}x{int(popup_height)}+{int(app_x)}+{int(y)}")
                try:
                    toast.attributes("-alpha", alpha)
                except Exception:
                    pass
                toast.after(delay, animate_out)
            else:
                try:
                    toast.destroy()
                except Exception:
                    pass

        try:
            toast.attributes("-alpha", 0.0)
        except Exception:
            pass

        animate_in()

    def query_part(entry, combobox, content_frame, user_id=1):
        import socket
        part_id = entry.get().strip()
        quantity = combobox.get().strip()

        if not part_id or not quantity.isdigit():
            errorLabel = ctk.CTkLabel(
                content_frame,
                text="Enter valid Part ID and Quantity",
                text_color="red",
            )
            errorLabel.place(relx=0.1, rely=0.4, anchor="nw")
            return

        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(("localhost", 9000))

            message = f"add:{user_id}:{part_id}:{quantity}"
            client.send(message.encode())

            response = client.recv(4096).decode()

            success = "success" in response.lower()
            text = f"Updated cart for user {user_id}" if success else response
            ctk.CTkLabel(content_frame, text=text, text_color="#00FF00" if success else "red").place(relx=0.1, rely=0.5, anchor="nw")


            client.close()
        except Exception as e:
            ctk.CTkLabel(
                content_frame,
                text=f"Error connecting to server: {e}",
                text_color="red",
                font=ctk.CTkFont(size=16, family="Segoe UI")
            ).place(relx=0.1, rely=0.4, anchor="nw")

    # DASHBOARD UI SETUP BELOW
    try:
        base_path = Path(__file__).parent / "Images"
        print("Loading from:", base_path.resolve())

        window.comp_img = ctk.CTkImage(Image.open(base_path / "Compatibiltiy_btn.png"), size=(254, 40))
        window.quit_img = ctk.CTkImage(Image.open(base_path / "Quit_btn.png"), size=(35, 35))
        window.resell_img = ctk.CTkImage(Image.open(base_path / "Resellers_btn.png"), size=(249, 40))
        window.return_img = ctk.CTkImage(Image.open(base_path / "Return_btn.png"), size=(35, 35))
        window.profile_img = ctk.CTkImage(Image.open(base_path / "Profile_btn.png"), size=(50, 50))
        window.myprojects_img = ctk.CTkImage(Image.open(base_path / "MyProjects_btn.png"), size=(42, 202))
        window.home_img = ctk.CTkImage(Image.open(base_path / "Home.png"), size=(996, 619))
        window.takeme_img = ctk.CTkImage(Image.open(base_path / "TakeMe.png"), size=(171, 39))
        print("Images loaded successfully.")
    except Exception as e:
        import traceback; traceback.print_exc()

    comp_btn = ctk.CTkButton(window, height=40, width=254, image=window.comp_img, text="", fg_color="#632EAD", hover_color="#A564EB", command=switch_to_compatibility)
    canvas.create_window(113,19,anchor="nw",window=comp_btn)
    quit_btn = ctk.CTkButton(window, height=35, width=35, image=window.quit_img, text="", fg_color="#D13E2A", hover_color="#A564EB", command=quit_app)
    canvas.create_window(17,647,anchor="nw",window=quit_btn)
    resell_btn = ctk.CTkButton(window, height=40, width=249, image=window.resell_img, text="", fg_color="#632EAD", hover_color="#A564EB", command=switch_to_resell)
    canvas.create_window(420,19,anchor="nw",window=resell_btn)
    return_btn = ctk.CTkButton(window, height=35, width=35, image=window.return_img, text="", fg_color="#5F378A", hover_color="#A564EB", command=return_home)
    canvas.create_window(17,585,anchor="nw",window=return_btn)
    profile_btn = ctk.CTkButton(window, height=55, width=55, image=window.profile_img, text="", fg_color="#823CE2", hover_color="#A564EB", command=lambda: open_profile_window(user_id))
    canvas.create_window(8,10,anchor="nw",window=profile_btn)
    myprojects_btn = ctk.CTkButton(window, height=260, width=42, image=window.myprojects_img, text="", fg_color="#632EAD", hover_color="#A564EB", command=lambda: projects_menu(content_frame, user_id, myProjects=my_projects))
    canvas.create_window(10,110,anchor="nw",window=myprojects_btn)

    home_label = ctk.CTkLabel(window, image=window.home_img, text="", fg_color="transparent", height=619, width=996)
    home_label_window = canvas.create_window(80, 80, anchor="nw", window=home_label)
    takeme_btn = ctk.CTkButton(window, height=39, width=171, image=window.takeme_img, text="", fg_color="transparent", hover_color="#360A64", command=my_projects)
    takeme_btn_window = canvas.create_window(105,550,anchor="nw",window=takeme_btn)
    create_overlay()

    canvas.place(x = 0, y = 0)
    image_image_1 = PhotoImage(
        file=relative_to_assets("image_1.png"))
    image_1 = canvas.create_image(
        550.0,
        40.0,
        image=image_image_1
    )
    image_image_2 = PhotoImage(
        file=relative_to_assets("image_2.png"))
    image_2 = canvas.create_image(
        40.0,
        350.0,
        image=image_image_2
    )
    canvas.create_text(
        466.0,
        29.0,
        anchor="nw",
        text="Resellers Near Me",
        fill="#FFFFFF",
        font=("InstrumentSans Bold", 24 * -1)
    )
    canvas.create_text(
        156.0,
        29.0,
        anchor="nw",
        text="Part Compatibility",
        fill="#FFFFFF",
        font=("InstrumentSans Bold", 24 * -1)
    )
    image_image_9 = PhotoImage(
        file=relative_to_assets("image_9.png"))
    image_9 = canvas.create_image(
        40.0,
        177.0,
        image=image_image_9
    )
    image_image_10 = PhotoImage(
        file=relative_to_assets("image_10.png"))
    image_10 = canvas.create_image(
        42.0,
        43.0,
        image=image_image_10
    )
    image_image_11 = PhotoImage(
        file=relative_to_assets("image_11.png"))
    image_11 = canvas.create_image(
        40.0,
        283.0,
        image=image_image_11
    )
    canvas.create_text(
        905.0,
        29.0,
        anchor="nw",
        text="CarPartPicker",
        fill="#FFFFFF",
        font=("Inter Bold", 24 * -1)
    )
    image_image_12 = PhotoImage(
        file=relative_to_assets("image_12.png"))
    image_12 = canvas.create_image(
        878.0,
        40.0,
        image=image_image_12
    )
    image_image_13 = PhotoImage(
        file=relative_to_assets("image_13.png"))
    image_13 = canvas.create_image(
        133.0,
        42.0,
        image=image_image_13
    )
    image_image_14 = PhotoImage(
        file=relative_to_assets("image_14.png"))
    image_14 = canvas.create_image(
        440.0,
        42.0,
        image=image_image_14
    )
    image_image_15 = PhotoImage(
        file=relative_to_assets("image_15.png"))
    image_15 = canvas.create_image(
        42.0,
        664.0,
        image=image_image_15
    )
    image_image_16 = PhotoImage(
        file=relative_to_assets("image_16.png"))
    image_16 = canvas.create_image(
        42.0,
        602.0,
        image=image_image_16
    )
    
    window.resizable(False, False)
    window.mainloop()