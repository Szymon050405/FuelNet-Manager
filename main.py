
from tkinter import *
from tkinter import ttk
import tkintermapview

from utils import get_city_coordinates

station_markers = []
station_data = []
stations_tab_data = []
stations_tab_markers = []
employees_data = []
customers_data = []
customers_by_station = {}
editing_employee_index = None
editing_customer_index = None

# ----------------- STACJE ------------------

from utils import get_fuel_stations_near_city  # dodaj na górze pliku main, jeśli jeszcze nie masz

def find_stations():
    city = entry_city.get()
    if not city:
        label_info.config(text="❗ Podaj nazwę miejscowości")
        return

    listbox.delete(0, END)
    for m in station_markers:
        m.delete()
    station_markers.clear()
    station_data.clear()

    stations = get_fuel_stations_near_city(city)  # poprawne źródło danych

    if not stations:
        label_info.config(text="⚠️ Nie znaleziono stacji w okolicy.")
        return

    for station in stations:
        try:
            marker = map_widget_mapa.set_marker(station["lat"], station["lon"], text=station["name"])
            station_markers.append(marker)
            station_data.append(station)
            listbox.insert(END, f"{station['name']} – {station['lat']:.5f}, {station['lon']:.5f}")
        except KeyError as e:
            print(f"Błąd w danych stacji: {e}")  # jeśli jakiś wpis nie ma 'lat', 'lon' lub 'name'

    map_widget_mapa.set_position(stations[0]["lat"], stations[0]["lon"])
    map_widget_mapa.set_zoom(13)
    label_info.config(text=f"✅ Znaleziono {len(stations)} stacji")

def on_listbox_click(event):
    try:
        index = listbox.curselection()[0]
        station = station_data[index]
        map_widget_mapa.set_position(station["lat"], station["lon"])
        map_widget_mapa.set_zoom(16)
    except IndexError:
        pass

def move_selected_station_to_tab():
    try:
        index = listbox.curselection()[0]
        station = station_data[index]
        if station not in stations_tab_data:
            stations_tab_data.append(station)
            marker = map_widget_stations.set_marker(station["lat"], station["lon"], text=station["name"])
            stations_tab_markers.append(marker)
            listbox_stations.insert(END, f"{station['name']} – {station['lat']:.5f}, {station['lon']:.5f}")
        notebook.select(frame_stations)
    except IndexError:
        label_info.config(text="❗ Zaznacz stację na liście")

def delete_selected_station():
    try:
        index = listbox_stations.curselection()[0]
        stations_tab_data.pop(index)
        marker = stations_tab_markers.pop(index)
        marker.delete()
        listbox_stations.delete(index)


    except IndexError:
        pass

# ----------------- PRACOWNICY ------------------

def update_employee_table():
    tree_all_employees.delete(*tree_all_employees.get_children())
    for emp in employees_data:
        location = emp.get("location", "")
        tree_all_employees.insert("", END, values=(
            emp['name'], emp['surname'], emp['role'], emp['station'], location
        ))

def add_employee():
    global editing_employee_index
    name = entry_employee_name.get().strip()
    surname = entry_employee_surname.get().strip()
    role = entry_employee_role.get().strip()
    station = entry_station_name.get().strip()
    lat = entry_employee_lat.get().strip()
    lon = entry_employee_lon.get().strip()

    if name and surname and role and station:
        location = f"{lat},{lon}" if lat and lon else ""
        employees_data.append({
            "name": name,
            "surname": surname,
            "role": role,
            "station": station,
            "location": location
        })
        # Reset fields
        entry_employee_name.delete(0, END)
        entry_employee_surname.delete(0, END)
        entry_employee_role.delete(0, END)
        entry_station_name.delete(0, END)
        entry_employee_lat.delete(0, END)
        entry_employee_lon.delete(0, END)
        editing_employee_index = None
        update_employee_table()
        label_employees_info.config(text="✅ Dodano pracownika")
    else:
        label_employees_info.config(text="❗ Uzupełnij wszystkie pola")

def load_selected_employee():
    global editing_employee_index
    selected = tree_all_employees.selection()
    if not selected:
        label_employees_info.config(text="❗ Zaznacz pracownika")
        return
    index = tree_all_employees.index(selected[0])
    emp = employees_data[index]
    entry_employee_name.delete(0, END)
    entry_employee_name.insert(0, emp["name"])
    entry_employee_surname.delete(0, END)
    entry_employee_surname.insert(0, emp["surname"])
    entry_employee_role.delete(0, END)
    entry_employee_role.insert(0, emp["role"])
    entry_station_name.delete(0, END)
    entry_station_name.insert(0, emp["station"])

    if "location" in emp and "," in emp["location"]:
        lat, lon = emp["location"].split(",")
        entry_employee_lat.delete(0, END)
        entry_employee_lat.insert(0, lat)
        entry_employee_lon.delete(0, END)
        entry_employee_lon.insert(0, lon)
    else:
        entry_employee_lat.delete(0, END)
        entry_employee_lon.delete(0, END)

    editing_employee_index = index
    label_employees_info.config(text="✏️ Edytuj dane i kliknij ZAPISZ")

def edit_selected_employee():
    global editing_employee_index
    if editing_employee_index is None:
        label_employees_info.config(text="❗ Wybierz pracownika do edycji")
        return
    name = entry_employee_name.get().strip()
    surname = entry_employee_surname.get().strip()
    role = entry_employee_role.get().strip()
    station = entry_station_name.get().strip()
    lat = entry_employee_lat.get().strip()
    lon = entry_employee_lon.get().strip()

    if name and surname and role and station:
        location = f"{lat},{lon}" if lat and lon else ""
        emp = employees_data[editing_employee_index]
        emp.update({
            "name": name,
            "surname": surname,
            "role": role,
            "station": station,
            "location": location
        })
        update_employee_table()
        editing_employee_index = None
        label_employees_info.config(text="✅ Zapisano zmiany")
    else:
        label_employees_info.config(text="❗ Uzupełnij wszystkie pola")

def delete_selected_employee():
    global editing_employee_index
    selected = tree_all_employees.selection()
    if not selected:
        label_employees_info.config(text="❗ Zaznacz pracownika")
        return
    index = tree_all_employees.index(selected[0])
    del employees_data[index]
    update_employee_table()
    editing_employee_index = None
    label_employees_info.config(text="🗑️ Usunięto pracownika")

# ----------------- KLIENCI ------------------

def create_customer_table_for_station(station_name):
    label = Label(frame_customers_right, text=f"📍 Klienci stacji: {station_name}", font=("Arial", 12, "bold"))
    label.pack(pady=(10, 0))
    tree = ttk.Treeview(frame_customers_right, columns=("Imię", "Nazwisko", "Email", "Telefon"), show='headings')
    for col in ("Imię", "Nazwisko", "Email", "Telefon"):
        tree.heading(col, text=col)
        tree.column(col, width=130)
    tree.pack(pady=5, fill=X)
    customers_by_station[station_name] = tree

def update_customer_tables():
    for tree in customers_by_station.values():
        tree.delete(*tree.get_children())
    for customer in customers_data:
        station = customer["station"]
        if station not in customers_by_station:
            create_customer_table_for_station(station)
        customers_by_station[station].insert("", END, values=(customer["name"], customer["surname"], customer["email"], customer["phone"]))

def add_customer():
    def add_customer():
        global editing_customer_index
        name = entry_customer_name.get().strip()
        surname = entry_customer_surname.get().strip()
        email = entry_customer_email.get().strip()
        phone = entry_customer_phone.get().strip()
        station = entry_customer_station.get().strip()
        lat = entry_customer_lat.get().strip()
        lon = entry_customer_lon.get().strip()

        if name and surname and email and phone and station:
            location = f"{lat},{lon}" if lat and lon else ""
            customers_data.append({
                "name": name,
                "surname": surname,
                "email": email,
                "phone": phone,
                "station": station,
                "location": location
            })
            update_customer_tables()
            for entry in [entry_customer_name, entry_customer_surname, entry_customer_email,
                          entry_customer_phone, entry_customer_station, entry_customer_lat, entry_customer_lon]:
                entry.delete(0, END)
            editing_customer_index = None
            label_customers_info.config(text=f"✅ Dodano klienta do stacji: {station}")
        else:
            label_customers_info.config(text="❗ Uzupełnij wszystkie pola")

def load_selected_customer():
    global editing_customer_index
    for station, tree in customers_by_station.items():
        selected = tree.selection()
        if selected:
            index = tree.index(selected[0])
            customer = [c for c in customers_data if c["station"] == station][index]

            entry_customer_name.delete(0, END)
            entry_customer_name.insert(0, customer["name"])
            entry_customer_surname.delete(0, END)
            entry_customer_surname.insert(0, customer["surname"])
            entry_customer_email.delete(0, END)
            entry_customer_email.insert(0, customer["email"])
            entry_customer_phone.delete(0, END)
            entry_customer_phone.insert(0, customer["phone"])
            entry_customer_station.delete(0, END)
            entry_customer_station.insert(0, customer["station"])

            location = customer.get("location", "")
            if "," in location:
                lat, lon = location.split(",")
                entry_customer_lat.delete(0, END)
                entry_customer_lat.insert(0, lat)
                entry_customer_lon.delete(0, END)
                entry_customer_lon.insert(0, lon)
            else:
                entry_customer_lat.delete(0, END)
                entry_customer_lon.delete(0, END)

            editing_customer_index = customers_data.index(customer)
            label_customers_info.config(text="✏️ Edytuj dane i kliknij ZAPISZ")
            break
            break

def edit_selected_customer():
    global editing_customer_index
    if editing_customer_index is None:
        label_customers_info.config(text="❗ Wybierz klienta do edycji")
        return

    name = entry_customer_name.get().strip()
    surname = entry_customer_surname.get().strip()
    email = entry_customer_email.get().strip()
    phone = entry_customer_phone.get().strip()
    station = entry_customer_station.get().strip()
    lat = entry_customer_lat.get().strip()
    lon = entry_customer_lon.get().strip()

    if name and surname and email and phone and station:
        location = f"{lat},{lon}" if lat and lon else ""
        customer = customers_data[editing_customer_index]
        customer.update({
            "name": name,
            "surname": surname,
            "email": email,
            "phone": phone,
            "station": station,
            "location": location
        })
        update_customer_tables()
        editing_customer_index = None
        label_customers_info.config(text="✅ Zapisano zmiany")
    else:
        label_customers_info.config(text="❗ Uzupełnij wszystkie pola")

def delete_selected_customer():
    global editing_customer_index
    for station, tree in customers_by_station.items():
        selected = tree.selection()
        if selected:
            index = tree.index(selected[0])
            customer = [c for c in customers_data if c["station"] == station][index]
            customers_data.remove(customer)
            update_customer_tables()
            editing_customer_index = None
            label_customers_info.config(text="🗑️ Usunięto klienta")
            break

# -------------------------- GUI --------------------------

root = Tk()
root.title("Zarządzanie siecią stacji paliw")
root.geometry("1200x750")
notebook = ttk.Notebook(root)
notebook.pack(fill=BOTH, expand=True)

# --- Mapa ---
frame_map = Frame(notebook)
notebook.add(frame_map, text="Mapa")
frame_left = Frame(frame_map)
frame_left.pack(side=LEFT, fill=Y, padx=10, pady=10)
frame_right = Frame(frame_map)
frame_right.pack(side=RIGHT, fill=BOTH, expand=True, padx=10, pady=10)

Label(frame_left, text="Miejscowość:").pack(pady=5)
entry_city = Entry(frame_left, width=30)
entry_city.pack(pady=5)
Button(frame_left, text="Szukaj stacji", command=find_stations).pack(pady=10)
Button(frame_left, text="➡️ Przenieś zaznaczoną stację do zakładki: STACJE", command=move_selected_station_to_tab).pack(pady=2, fill=X)
Button(frame_left, text="➡️ Przejdź do zakładki: PRACOWNICY", command=lambda: notebook.select(frame_employees)).pack(pady=2, fill=X)
Button(frame_left, text="➡️ Przejdź do zakładki: KLIENCI", command=lambda: notebook.select(frame_customers)).pack(pady=2, fill=X)



label_info = Label(frame_left, text="", fg="blue")
label_info.pack(pady=5)
listbox = Listbox(frame_left, width=50)
listbox.pack(pady=10, fill=BOTH, expand=True)
listbox.bind("<<ListboxSelect>>", on_listbox_click)

map_widget_mapa = tkintermapview.TkinterMapView(frame_right, width=800, height=450)
map_widget_mapa.pack(fill=BOTH, expand=True)
map_widget_mapa.set_position(52.0, 19.0)
map_widget_mapa.set_zoom(6)

# --- Stacje ---
frame_stations = Frame(notebook)
notebook.add(frame_stations, text="Stacje")
frame_stations_left = Frame(frame_stations)
frame_stations_left.pack(side=LEFT, fill=Y, padx=10, pady=10)
frame_stations_right = Frame(frame_stations)
frame_stations_right.pack(side=RIGHT, fill=BOTH, expand=True, padx=10, pady=10)

listbox_stations = Listbox(frame_stations_left, width=45, height=25)
listbox_stations.pack(pady=10, fill=Y)
Button(frame_stations_left, text="🗑️ Usuń zaznaczoną stację", command=delete_selected_station).pack(pady=2, fill=X)


map_widget_stations = tkintermapview.TkinterMapView(frame_stations_right, width=800, height=450)
map_widget_stations.pack(fill=BOTH, expand=True)
map_widget_stations.set_position(52.0, 19.0)
map_widget_stations.set_zoom(6)

# --- Pracownicy ---
frame_employees = Frame(notebook)
notebook.add(frame_employees, text="Pracownicy")
frame_employees_left = Frame(frame_employees)
frame_employees_left.pack(side=LEFT, fill=Y, padx=10, pady=10)
frame_employees_right = Frame(frame_employees)
frame_employees_right.pack(side=RIGHT, fill=BOTH, expand=True, padx=10, pady=10)

Label(frame_employees_left, text="Imię:").pack()
entry_employee_name = Entry(frame_employees_left, width=30)
entry_employee_name.pack()
Label(frame_employees_left, text="Nazwisko:").pack()
entry_employee_surname = Entry(frame_employees_left, width=30)
entry_employee_surname.pack()
Label(frame_employees_left, text="Stanowisko:").pack()
entry_employee_role = Entry(frame_employees_left, width=30)
entry_employee_role.pack()
Label(frame_employees_left, text="Stacja:").pack()
entry_station_name = Entry(frame_employees_left, width=30)
entry_station_name.pack()

Label(frame_employees_left, text="Szerokość (lat):").pack()
entry_employee_lat = Entry(frame_employees_left, width=30)
entry_employee_lat.pack(pady=2)
Label(frame_employees_left, text="Długość (lon):").pack()
entry_employee_lon = Entry(frame_employees_left, width=30)
entry_employee_lon.pack(pady=2)

Button(frame_employees_left, text="Dodaj pracownika", command=add_employee).pack(pady=5)
Button(frame_employees_left, text="✏️ Wczytaj do edycji", command=load_selected_employee).pack(pady=2)
Button(frame_employees_left, text="💾 Zapisz zmiany", command=edit_selected_employee).pack(pady=2)
Button(frame_employees_left, text="🗑️ Usuń zaznaczonego", command=delete_selected_employee).pack(pady=2)

label_employees_info = Label(frame_employees_left, text="Brak akcji", fg="blue")
label_employees_info.pack(pady=5)

tree_all_employees = ttk.Treeview(
    frame_employees_right,
    columns=("Imię", "Nazwisko", "Stanowisko", "Stacja", "Lokalizacja"),
    show='headings'
)
for col in ("Imię", "Nazwisko", "Stanowisko", "Stacja", "Lokalizacja"):
    tree_all_employees.heading(col, text=col)
    tree_all_employees.column(col, width=130)
tree_all_employees.pack(fill=BOTH, expand=True)
# --- Klienci ---
frame_customers = Frame(notebook)
notebook.add(frame_customers, text="Klienci")
frame_customers_left = Frame(frame_customers)
frame_customers_left.pack(side=LEFT, fill=Y, padx=10, pady=10)
frame_customers_right = Frame(frame_customers)
frame_customers_right.pack(side=RIGHT, fill=BOTH, expand=True, padx=10, pady=10)

Label(frame_customers_left, text="Imię: ").pack()
entry_customer_name = Entry(frame_customers_left, width=30)
entry_customer_name.pack(pady=2)
Label(frame_customers_left, text="Nazwisko: ").pack()
entry_customer_surname = Entry(frame_customers_left, width=30)
entry_customer_surname.pack(pady=2)
Label(frame_customers_left, text="Email: ").pack()
entry_customer_email = Entry(frame_customers_left, width=30)
entry_customer_email.pack(pady=2)
Label(frame_customers_left, text="Telefon: ").pack()
entry_customer_phone = Entry(frame_customers_left, width=30)
entry_customer_phone.pack(pady=2)
Label(frame_customers_left, text="Stacja: ").pack()
entry_customer_station = Entry(frame_customers_left, width=30)
entry_customer_station.pack(pady=2)
Label(frame_customers_left, text="Szerokość (lat): ").pack()
entry_customer_lat = Entry(frame_customers_left, width=30)
entry_customer_lat.pack(pady=2)
Label(frame_customers_left, text="Długość (lon): ").pack()
entry_customer_lon = Entry(frame_customers_left, width=30)
entry_customer_lon.pack(pady=2)

Button(frame_customers_left, text="Dodaj klienta", command=add_customer).pack(pady=5)
Button(frame_customers_left, text="✏️ Wczytaj do edycji", command=load_selected_customer).pack(pady=2)
Button(frame_customers_left, text="💾 Zapisz zmiany", command=edit_selected_customer).pack(pady=2)
Button(frame_customers_left, text="🗑️ Usuń zaznaczonego", command=delete_selected_customer).pack(pady=2)

label_customers_info = Label(frame_customers_left, text="Brak akcji", fg="blue")
label_customers_info.pack(pady=5)

# --- Mapa Pracownicy i Klienci ---
frame_map_people = Frame(notebook)
notebook.add(frame_map_people, text="Mapa Pracownicy i Klienci")

map_widget_people = tkintermapview.TkinterMapView(frame_map_people, width=1150, height=700)
map_widget_people.pack(fill=BOTH, expand=True)
map_widget_people.set_position(52.0, 19.0)
map_widget_people.set_zoom(6)

def show_people_on_map():
    map_widget_people.delete_all_marker()

    # Pracownicy
    for emp in employees_data:
        loc = emp.get("location", "")
        if loc:
            try:
                lat, lon = map(float, loc.split(","))
                map_widget_people.set_marker(lat, lon, text=f"👷 {emp['name']} {emp['surname']} ({emp['role']})")
            except Exception as e:
                print(f"Błąd lokalizacji pracownika: {e}")

    # Klienci
    for cust in customers_data:
        loc = cust.get("location", "")
        if loc:
            try:
                lat, lon = map(float, loc.split(","))
                map_widget_people.set_marker(lat, lon, text=f"🧑‍💼 {cust['name']} {cust['surname']}")
            except Exception as e:
                print(f"Błąd lokalizacji klienta: {e}")
        else:
            # Fallback – spróbuj znaleźć lokalizację na podstawie stacji
            station_name = cust.get("station", "")
            station = next((s for s in station_data if s["name"] == station_name), None)
            if station:
                try:
                    map_widget_people.set_marker(station["lat"], station["lon"], text=f"🧑‍💼 {cust['name']} {cust['surname']}")
                except Exception as e:
                    print(f"Błąd lokalizacji klienta przez stację: {e}")

    # Pracownicy
    for emp in employees_data:
        loc = emp.get("location", "")
        if loc:
            try:
                lat, lon = map(float, loc.split(","))
                map_widget_people.set_marker(lat, lon, text=f"👷 {emp['name']} {emp['surname']} ({emp['role']})")
            except Exception as e:
                print(f"Błąd lokalizacji pracownika: {e}")

    # Klienci
    for cust in customers_data:
        station_name = cust.get("station", "")
        station = next((s for s in station_data if s["name"] == station_name), None)
        if station:
            try:
                lat = station["lat"]
                lon = station["lon"]
                map_widget_people.set_marker(lat, lon, text=f"🧑‍💼 {cust['name']} {cust['surname']}")
            except Exception as e:
                print(f"Błąd lokalizacji klienta: {e}")

Button(frame_map_people, text="🔄 Odśwież dane na mapie", command=show_people_on_map).pack(pady=10)


root.mainloop()
