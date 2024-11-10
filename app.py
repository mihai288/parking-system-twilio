import tkinter as tk
from tkinter import messagebox
from datetime import date
import pandas as pd
import random
from twilio.rest import Client

#your twilio data here
TWILIO_ACCOUNT_SID = ''
TWILIO_AUTH_TOKEN = ''
TWILIO_PHONE_NUMBER = '

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
verification_code = ""

def generate_verification_code():
    return str(random.randint(100000, 999999))

def send_verification_code(phone_number, code):
    try:
        message = client.messages.create(
            body=f"Parking code is: {code}",
            from_=TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        print(f"SMS sent successfully! SID: {message.sid}")
    except Exception as e:
        print(f"Failed to send SMS: {e}")

def verify_code(input_code, actual_code):
    return input_code == actual_code

csv_file = "parking_reservations.csv"

parking_spots = {str(i): "free" for i in range(1, 13)}

def initialize_csv():
    try:
        df = pd.read_csv(csv_file)
        if df.empty:
            raise pd.errors.EmptyDataError
    except (FileNotFoundError, pd.errors.EmptyDataError, pd.errors.ParserError):
        columns = ["Date", "License Plate", "Hours", "Cost", "Spot"]
        df = pd.DataFrame(columns=columns)
        df.to_csv(csv_file, index=False)

def load_reservations():
    initialize_csv()
    try:
        df = pd.read_csv(csv_file)
        for _, row in df.iterrows():
            spot = str(row["Spot"])
            if spot in parking_spots:
                parking_spots[spot] = "occupied"
    except Exception as e:
        messagebox.showerror("Error", f"Error loading reservations: {e}")

def update_parking_display():
    for i in range(12):
        spot_num = str(i + 1)
        if parking_spots[spot_num] == "free":
            spot_buttons[i].config(bg="green", fg="white", activebackground="darkgreen")
        else:
            spot_buttons[i].config(bg="red", fg="white", activebackground="darkred")

def reserve_parking(spot):
    global verification_code
    if parking_spots[spot] == "free":
        license_plate = license_plate_entry.get()
        phone_number = phone_entry.get()

        if not phone_number:
            messagebox.showerror("Error", "Phone number invalid")
            return

        verification_code = generate_verification_code()
        send_verification_code(phone_number, verification_code)

        code_window = tk.Toplevel()
        code_window.title("SMS Verification")

        code_label = tk.Label(code_window, text="Code from SMS:")
        code_label.pack(pady=5)

        code_entry = tk.Entry(code_window, width=10)
        code_entry.pack(pady=5)

        def confirm_code():
            input_code = code_entry.get()
            if verify_code(input_code, verification_code):
                try:
                    time_to_stay = int(hours_entry.get())
                    if time_to_stay <= 0:
                        messagebox.showerror("Error", "Time must be a positive number")
                        code_window.destroy()
                        return
                    need_to_pay = 5 * time_to_stay
                    today = date.today()

                    reservation_info = {
                        "Date": today,
                        "License Plate": license_plate,
                        "Hours": time_to_stay,
                        "Cost": need_to_pay,
                        "Spot": spot
                    }

                    try:
                        df = pd.read_csv(csv_file)
                        df = pd.concat([df, pd.DataFrame([reservation_info])], ignore_index=True)
                        df.to_csv(csv_file, index=False)
                    except Exception as e:
                        messagebox.showerror("Error", f"Error saving reservation: {e}")
                        code_window.destroy()
                        return

                    parking_spots[spot] = "occupied"
                    update_parking_display()
                    messagebox.showinfo("Success",
                                        f"Parking {spot} reserved for {license_plate}!\nCost: {need_to_pay} eur")
                except ValueError:
                    messagebox.showerror("Error", "Invalid")
                finally:
                    code_window.destroy()
            else:
                messagebox.showerror("Error", "Incorrect")
                code_window.destroy()

        confirm_button = tk.Button(code_window, text="Confirm", command=confirm_code)
        confirm_button.pack(pady=10)

def create_gui():
    global license_plate_entry, hours_entry, phone_entry, spot_buttons

    window = tk.Tk()
    window.title("Parking system - mihai288")
    window.geometry("400x400")

    entry_frame = tk.Frame(window, padx=10, pady=10)
    entry_frame.grid(row=0, column=0, columnspan=2)

    license_plate_label = tk.Label(entry_frame, text="License Plate:")
    license_plate_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
    license_plate_entry = tk.Entry(entry_frame, width=20)
    license_plate_entry.grid(row=0, column=1, padx=5, pady=5)

    hours_label = tk.Label(entry_frame, text="Hours:")
    hours_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
    hours_entry = tk.Entry(entry_frame, width=20)
    hours_entry.grid(row=1, column=1, padx=5, pady=5)

    phone_label = tk.Label(entry_frame, text="Phone Number:")
    phone_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
    phone_entry = tk.Entry(entry_frame, width=20)
    phone_entry.grid(row=2, column=1, padx=5, pady=5)

    button_frame = tk.Frame(window, padx=10, pady=10)
    button_frame.grid(row=1, column=0, columnspan=2)

    spot_buttons = []
    for i in range(1, 13):
        button_color = "green" if parking_spots[str(i)] == "free" else "red"
        button = tk.Button(button_frame, text=f"{i}", width=5,
                           bg=button_color, fg="white",
                           activebackground="darkgreen" if button_color == "green" else "darkred",
                           command=lambda spot=str(i): reserve_parking(spot))
        if i <= 6:
            button.grid(row=i - 1, column=0, padx=5, pady=5)
        else:
            button.grid(row=i - 7, column=1, padx=5, pady=5)
        spot_buttons.append(button)

    exit_button = tk.Button(window, text="Ieșire", command=window.quit)
    exit_button.grid(row=2, column=1, padx=5, pady=10, sticky="e")

    window.mainloop()

def main():
    load_reservations()
    create_gui()

if __name__ == "__main__":
    main()
