import tkinter as tk 
from tkinter import messagebox 
from datetime import datetime 
import qrcode 
import pandas as pd 
from PIL import Image, ImageTk 
import os 
from fpdf import FPDF 


data_member = {
    'members': {
        '123456': {'plat': 'B 2394 SIW', 'kategori': 'Member'},
        '654321': {'plat': 'B 6430 SQL', 'kategori': 'Member'},
        '111111': {'plat': 'B 3019 DEF', 'kategori': 'Member'}
    }
}


RIWAYAT_FILE = "riwayat_parkir.csv"

def load_riwayat():
    if os.path.exists(RIWAYAT_FILE):
        df = pd.read_csv(RIWAYAT_FILE)
        return df.to_dict(orient="records")
    return []

def save_riwayat():
    df = pd.DataFrame(riwayat_parkir)
    df.to_csv(RIWAYAT_FILE, index=False)


riwayat_parkir = load_riwayat()

def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def generate_qr(text, filename='ticket.png'):
    img = qrcode.make(text)
    img.save(filename)
    return filename

def hitung_tarif(jam_masuk, jam_keluar):  
    return 2000

def simpan_riwayat(kategori, id_card, plat, jam_masuk, jam_keluar, tarif):
    riwayat_parkir.append({
        "kategori": kategori,
        "id_card": id_card,
        "plat": plat,
        "jam_masuk": jam_masuk,
        "jam_keluar": jam_keluar,
        "tarif": tarif
    })
    save_riwayat()


def cetak_struk_pdf(data, filename="struk_parkir.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "STRUK PARKIR", ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.ln(10)
    for key, value in data.items():
        pdf.cell(0, 10, f"{key}: {value}", ln=True)
    pdf.output(filename)
    messagebox.showinfo("Struk PDF", f"Struk berhasil dicetak ke file: {filename}")

def cetak_struk_member():
    if not member_masuk_var.get() or not member_keluar_var.get():
        messagebox.showwarning("Info", "Data belum lengkap untuk cetak struk!")
        return
    data = {
        "Kategori": "Member",
        "ID": member_id_var.get(),
        "Plat Nomor": member_plat_var.get(),
        "Jam Masuk": member_masuk_var.get(),
        "Jam Keluar": member_keluar_var.get(),
        "Tarif": member_tarif_var.get()
    }
    cetak_struk_pdf(data, filename="struk_member.pdf")

def cetak_struk_nonmember():
    if not nonmember_masuk_var.get() or not nonmember_keluar_var.get():
        messagebox.showwarning("Info", "Data belum lengkap untuk cetak struk!")
        return
    data = {
        "Kategori": "Non-Member",
        "Plat Nomor": nonmember_plat_var.get(),
        "Jam Masuk": nonmember_masuk_var.get(),
        "Jam Keluar": nonmember_keluar_var.get(),
        "Tarif": nonmember_tarif_var.get()
    }
    cetak_struk_pdf(data, filename="struk_nonmember.pdf")


def tap_in_member():
    id_card = member_id_var.get().strip()
    if id_card and id_card in data_member['members']:
        member_plat_var.set(data_member['members'][id_card]['plat'])
        member_masuk_var.set(now())
        member_keluar_var.set("")
        member_tarif_var.set("")
        update_member_display()
    else:
        messagebox.showerror("Error", "ID SmartCard tidak ditemukan!")

def checkout_member():
    if not member_masuk_var.get():
        messagebox.showwarning("Info", "Silakan Tap In dahulu.")
        return
    jam_keluar = now()
    member_keluar_var.set(jam_keluar)
    member_tarif_var.set(f"Gratis (Member)")
    update_member_display()
    simpan_riwayat(
        "Member",
        member_id_var.get(),
        member_plat_var.get(),
        member_masuk_var.get(),
        jam_keluar,
        "Gratis (Member)"
    )

def update_member_display():
    info = (
        f"ID         : {member_id_var.get()}\n"
        f"Plat Nomor : {member_plat_var.get()}\n"
        f"Jam Masuk  : {member_masuk_var.get()}\n"
        f"Kategori   : Member\n"
        f"Jam Keluar : {member_keluar_var.get()}\n"
        f"Tarif      : {member_tarif_var.get()}"
    )
    display_member.config(text=info)

def tap_in_nonmember():
    plat = simple_input("Plat Nomor")
    if not plat:
        return
    nonmember_plat_var.set(plat)
    nonmember_masuk_var.set(now())
    nonmember_keluar_var.set("")
    nonmember_tarif_var.set("")
    update_nonmember_display()
    qr_data = f"{plat}|{nonmember_masuk_var.get()}"
    qr_file = generate_qr(qr_data)
    img = Image.open(qr_file).resize((100, 100))
    global qr_img
    qr_img = ImageTk.PhotoImage(img)
    qr_label.config(image=qr_img)

def checkout_nonmember():
    if not nonmember_masuk_var.get():
        messagebox.showwarning("Info", "Silakan Tap In dahulu.")
        return
    jam_keluar = now()
    tarif = hitung_tarif(nonmember_masuk_var.get(), jam_keluar)
    nonmember_keluar_var.set(jam_keluar)
    nonmember_tarif_var.set(f"Rp {tarif:,}")
    update_nonmember_display()
    simpan_riwayat(
        "Non-Member",
        "",
        nonmember_plat_var.get(),
        nonmember_masuk_var.get(),
        jam_keluar,
        f"Rp {tarif:,}"
    )

def update_nonmember_display():
    info = (
        f"Kategori   : Non-Member\n"
        f"Plat Nomor : {nonmember_plat_var.get()}\n"
        f"Jam Masuk  : {nonmember_masuk_var.get()}\n"
        f"Jam Keluar : {nonmember_keluar_var.get()}\n"
        f"Tarif      : {nonmember_tarif_var.get()}"
    )
    display_nonmember.config(text=info)

def reset_all():
    member_id_var.set("")
    member_plat_var.set("")
    member_masuk_var.set("")
    member_keluar_var.set("")
    member_tarif_var.set("")
    display_member.config(text="")

    nonmember_plat_var.set("")
    nonmember_masuk_var.set("")
    nonmember_keluar_var.set("")
    nonmember_tarif_var.set("")
    display_nonmember.config(text="")
    qr_label.config(image="")

def tampilkan_riwayat():
    if not riwayat_parkir:
        messagebox.showinfo("Riwayat Parkir", "Belum ada data riwayat parkir.")
        return
    df = pd.DataFrame(riwayat_parkir)
    info = df.to_string(index=False)
    top = tk.Toplevel(window)
    top.title("Riwayat Parkir")
    text = tk.Text(top, width=120, height=25)
    text.insert(tk.END, info)
    text.pack()

    def reset_riwayat():
        if messagebox.askyesno("Konfirmasi", "Yakin ingin menghapus semua riwayat parkir?"):
            riwayat_parkir.clear()
            if os.path.exists(RIWAYAT_FILE):
                os.remove(RIWAYAT_FILE)
            text.delete(1.0, tk.END)
            text.insert(tk.END, "Semua data riwayat parkir telah dihapus.")

    tk.Button(top, text="Riset", command=reset_riwayat).pack(pady=10)

def simple_input(prompt):
    popup = tk.Toplevel()
    popup.title(prompt)
    tk.Label(popup, text=prompt).pack()
    entry = tk.Entry(popup)
    entry.pack()
    result = {'value': None}
    def on_ok():
        result['value'] = entry.get()
        popup.destroy()
    tk.Button(popup, text="OK", command=on_ok).pack()
    popup.grab_set()
    popup.wait_window()
    return result['value']


window = tk.Tk()
window.title("Smart Parking System")
window.geometry("800x600")

frame = tk.Frame(window, padx=20, pady=20)
frame.grid(row=0, column=0, sticky="nsew")

member_frame = tk.LabelFrame(frame, text="SmartCard (Member)", padx=10, pady=10)
member_frame.grid(row=0, column=0, sticky="nw", padx=10, pady=10)

member_id_var = tk.StringVar()
member_plat_var = tk.StringVar()
member_masuk_var = tk.StringVar()
member_keluar_var = tk.StringVar()
member_tarif_var = tk.StringVar()

tk.Button(member_frame, text="Tap In SmartCard", command=tap_in_member).grid(row=0, column=0, pady=3)
tk.Button(member_frame, text="Checkout SmartCard", command=checkout_member).grid(row=1, column=0, pady=3)
tk.Label(member_frame, text="Input SmartCard ID").grid(row=2, column=0, pady=3)
tk.Entry(member_frame, textvariable=member_id_var).grid(row=3, column=0, pady=3)
tk.Button(member_frame, text="Cetak Struk", command=cetak_struk_member).grid(row=4, column=0, pady=3)


nonmember_frame = tk.LabelFrame(frame, text="Tiket QR (Non-Member)", padx=10, pady=10)
nonmember_frame.grid(row=1, column=0, sticky="nw", padx=10, pady=10)

nonmember_plat_var = tk.StringVar()
nonmember_masuk_var = tk.StringVar()
nonmember_keluar_var = tk.StringVar()
nonmember_tarif_var = tk.StringVar()

tk.Button(nonmember_frame, text="Tap In Tiket", command=tap_in_nonmember).grid(row=0, column=0, pady=3)
tk.Button(nonmember_frame, text="Checkout Tiket", command=checkout_nonmember).grid(row=1, column=0, pady=3)
tk.Button(nonmember_frame, text="Reset", command=reset_all).grid(row=2, column=0, pady=3)
tk.Button(nonmember_frame, text="Cetak Struk", command=cetak_struk_nonmember).grid(row=3, column=0, pady=3)

display_member = tk.Label(frame, text="", anchor="w", justify="left", bg="#eaffea", width=40, height=8, font=("Consolas", 10))
display_member.grid(row=0, column=1, padx=20, pady=20)

display_nonmember = tk.Label(frame, text="", anchor="w", justify="left", bg="#eaffea", width=40, height=8, font=("Consolas", 10))
display_nonmember.grid(row=1, column=1, padx=10, pady=10)


qr_label = tk.Label(frame)
qr_label.grid(row=1, column=2, padx=10)


tk.Button(frame, text="Lihat Riwayat Parkir", command=tampilkan_riwayat).grid(row=2, column=1, pady=20)

window.mainloop()