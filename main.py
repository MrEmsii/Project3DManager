import os, shutil
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, PhotoImage, Listbox
from tkinterdnd2 import DND_FILES, TkinterDnD
from dbControler import SQLconnect, Projekt, Element, Filament, Firma, projekt_relacja

class FolderApp:
    def __init__(self, master):
  
        self.dsc = os.path.dirname(__file__)
        self.master = master
        master.title("Projekt Manager")
        master.iconbitmap(os.path.join(self.dsc, "image", "icon.ico"))

        # Wskazanie miejsca gdzie znaduje sie folder "Projekty"
        self.base_directory = os.path.join(self.dsc, "Projekty")

        # Połączenie z bazą danych
        self.db_session = SQLconnect(self.dsc)

        # Tworzenie okienka dla listy folderów
        self.buttom_frame = ttk.Frame(master)

        self.folder_frame = ttk.Frame(master)
        self.content_frame = ttk.Frame(master)
        self.details_frame = ttk.Frame(master)

        self.buttom_frame.pack(side='left', fill='both', pady=(50,20), padx=(5,0))
        self.buttons()

        # Tworzenie drzewa widoków dla wyświetlenia folderów z projektami
        self.folder_frame.pack(side='left', fill='both', padx=5, pady=20, ipadx=20)
        self.folder_tree = self.create_project_tree(self.folder_frame, 'Projekty')        
        

        # Załadowanie folderami widok
        self.load_folders()

        # Po 2x naciśnięciu załaduj zawartość
        self.folder_tree.bind("<Double-1>", self.on_double_click)

        # Tworzenie ramki dla widoku zawartości
        self.content_frame.pack(side='right', fill='both', padx=5, pady=20, ipadx=5 )

        # Tworzenie widoki drzewa dla zawartości folderów
        self.stl_tree = self.create_content_tree(self.content_frame, 'STL')
        self.prusa_tree = self.create_content_tree(self.content_frame, 'Prusa')
        self.gcode_tree = self.create_content_tree(self.content_frame, 'G-Code')

        #  Po 2x naciśnięciu otwórz zawartość
        self.stl_tree.bind("<Double-1>", self.on_file_double_click)
        self.prusa_tree.bind("<Double-1>", self.on_file_double_click)
        self.gcode_tree.bind("<Double-1>", self.on_file_double_click)


        # Tworzenie ramki dla szczegółów projektu
        self.details_frame.pack(side='top', expand=True, fill='both', padx=5, pady=20)
        self.details_tree = self.create_details_tree(self.details_frame, 'Project Details')
        self.elements_tree = self.create_all_elements_details_tree(self.details_frame, 'Elements Details')
        self.details_project_tree = self.create_details_project_tree(self.details_frame, 'Inforamcje')

        self.details_tree.bind("<Double-1>", self.on_element_double_click)
        self.elements_tree.bind("<Double-1>", self.on_element_detiles_double_click)

        # Tworzenie Drag-and-Drop
        self.dnd_frame = tk.Label(self.content_frame, text="Przeciągnij i upuść pliki tutaj", relief="solid", padx=85, pady=20)
        self.dnd_frame.pack(pady=10)

        self.dnd_frame.drop_target_register(DND_FILES)
        self.dnd_frame.dnd_bind('<<Drop>>', self.on_drop)

    def add_project(self):
        project_name = simpledialog.askstring("Dodaj Projekt", "Podaj nazwę PROJEKTU: \t\t\t")
        firma1_name = simpledialog.askstring("Dodaj Firme", "Podaj nazwę FIRMY: \t\t\t")

        dsc2 = os.path.join(self.base_directory, project_name)

        if not os.path.isdir(dsc2):
            dscs = ["\\STL", "\\G-code", "\\Prusa"]
            os.mkdir(dsc2)
            for dict in dscs:
                os.mkdir(dsc2 + dict)

        # Tworzenie przykładowej firmy

        if firma1_name == None:
            firma1_name = 0

        firma1 = self.db_session.query(Firma).filter_by(nazwa=firma1_name).first()
        if not firma1:
            firma1 = Firma(nazwa=firma1_name)
            self.db_session.add(firma1)

        # Tworzenie przykładowych elementów
        new_element = Element(nazwa="ABSTRACT", waga=0, filament_id=0, czas_druku = 0)
        self.db_session.add_all([new_element])
        
        # Tworzenie przykładowego projektu z przypisaną firmą
        projekt1 = Projekt(nazwa=project_name, firma=firma1, elementy=[new_element])
        self.db_session.add(projekt1)

        # Zatwierdzanie zmian w bazie danych
        print(f"Dodano testowy projekt: {projekt1.nazwa}, firma: {firma1.nazwa}")
        self.db_session.commit()
        self.load_folders()
        
    def delete_project(self):
        dialog = simpledialog.askstring("Usuń folder", "Czy jesteś pewien usunięcia projektu:\n\nCzynność NIE odwracalna\n\nNapisz YES lub TAK \t\t\t")
        if dialog == "YES" or dialog == "TAK":
            project_name = self.folder_tree.item(self.folder_tree.selection()[0], 'text')
            obj = self.db_session.query(Projekt).filter_by(nazwa=project_name).first()
            self.db_session.delete(obj)
            self.db_session.commit()
            self.load_folders()
            remov = os.path.join(self.base_directory, project_name)
            shutil.rmtree(remov)

    def mod_project(self):
        pass

    def add_element(self):
        element_name = simpledialog.askstring("Add Element", "Enter name for the new element:")

        if element_name is not None:
            project_name = self.folder_tree.item(self.folder_tree.selection()[0], 'text')
            project = self.db_session.query(Projekt).filter_by(nazwa=project_name).first()

            new_element = Element(nazwa=element_name, waga=0, filament_id=0, czas_druku = 0)
            project.elementy.append(new_element)
            self.db_session.commit()
            self.load_project_details(project_name)  # Reload details

    def buttons(self):
        #tworzenie przycisków w głównym menu
        self.add_project_icon = PhotoImage(file=os.path.join(self.dsc, "image", "edit_project_icon.png")).subsample(10, 10)
        self.edit_project_icon = PhotoImage(file=os.path.join(self.dsc, "image", "edit_project_icon.png")).subsample(10, 10)
        self.delete_project_icon = PhotoImage(file=os.path.join(self.dsc, "image", "delete_project_icon.png")).subsample(10, 10)

        self.add_element_icon = PhotoImage(file=os.path.join(self.dsc, "image", "add_element_icon.png")).subsample(10, 10)
        self.delete_element_icon = PhotoImage(file=os.path.join(self.dsc, "image", "delete_element_icon.png")).subsample(10, 10)


        self.add_element_button = ttk.Button(self.buttom_frame, text="Dodaj \nprojekt", command=self.add_project, width = 12, image=self.add_project_icon, compound="left")
        self.add_element_button.pack(side='top', pady=3, fill='x')
        self.add_element_button = ttk.Button(self.buttom_frame, text="Edytuj \nprojekt", command=self.mod_project, width = 12, image=self.edit_project_icon, compound="left")
        self.add_element_button.pack(side='top', pady=3, fill='x')
        self.add_element_button = ttk.Button(self.buttom_frame, text="Usuń \nprojekt", command=self.delete_project, width = 12, image=self.delete_project_icon, compound="left")
        self.add_element_button.pack(side='top', pady=3, fill='x')

        self.add_element_button = ttk.Button(self.buttom_frame, text="Dodaj \nelement", command=self.add_element, width = 12, image=self.add_element_icon, compound="left")
        self.add_element_button.pack(side='top', pady=(30,3), fill='x')
        self.add_element_button = ttk.Button(self.buttom_frame, text="Usuń \nelement", command=self.add_element, width = 12, image=self.delete_element_icon, compound="left")
        self.add_element_button.pack(side='top', pady=(3, 30), fill='x')

        self.add_element_button = ttk.Button(self.buttom_frame, text="Odśwież", command=self.refresh, width = 12, image=self.delete_element_icon, compound="left")
        self.add_element_button.pack(side='bottom', pady=(3,0), fill='x')


    def refresh(self):
        self.load_folders
        project_name = self.folder_tree.item(self.folder_tree.selection()[0], 'text')
        self.load_project_details(project_name)

    def on_drop(self, event):
        files = self.master.tk.splitlist(event.data)
        selected_item = self.folder_tree.selection()

        if not selected_item:
            messagebox.showwarning("Warning", "Wybierz pierwsze projekt.")
            return

        project_folder = self.folder_tree.item(selected_item[0], 'text')
        project_path = os.path.join(self.base_directory, project_folder)

        for file in files:
            file_ext = file.lower()
            if file_ext.endswith('.stl'):
                dest_folder = "STL"
            elif file_ext.endswith('.3mf'):
                dest_folder = "Prusa"
            elif file_ext.endswith('.gcode'):
                dest_folder = "G-Code"
            else:
                dest_folder = "Wzorzec"

            dest_path = os.path.join(project_path, dest_folder, os.path.basename(file))
            if not os.path.exists(dest_path):
                os.rename(file, dest_path)

        self.load_folder_contents(project_path)

    def create_content_tree(self, parent_frame, folder_name):
        tree = ttk.Treeview(parent_frame, show='headings')
        tree['columns'] = (folder_name)
        tree.column(folder_name, width=300)
        tree.heading(folder_name, text=folder_name, anchor='w')
        tree.pack(expand=True, fill='both')
        return tree

    def create_filament_tree(self, parent_frame, label_text):
        label = ttk.Label(parent_frame, text=label_text, font=("Arial", 12))
        label.pack(pady=5)

        tree = ttk.Treeview(parent_frame, columns=("ID", 'Name', "Typ", "Cena"), show='headings')

        tree.column('ID', width=20, anchor='e')
        tree.heading('ID', text='ID' + 3*" ", anchor='e')

        tree.column('Name', width=180, anchor='w')
        tree.heading('Name', text='Nazwa', anchor='w')


        tree.column('Typ', width=150, anchor='e')
        tree.heading('Typ', text='Typ' + 3*" ", anchor='e')

        tree.column('Cena', width=150, anchor='e')
        tree.heading('Cena', text='Cena za kg' + 3*" ", anchor='e')

        tree.pack(expand=True, fill='both')

        return tree    

    def create_project_tree(self, parent_frame, label_text):
        label = ttk.Label(parent_frame, text=label_text, font=("Arial", 12))
        label.pack(pady=5)

        tree = ttk.Treeview(parent_frame, columns=( "Company", 'Name', "ID"), show='headings')

        tree.column('Company', width=80, anchor='e')
        tree.heading('Company', text='Firma' + 3*" ", anchor='e')

        tree.column('Name', width=180, anchor='w')
        tree.heading('Name', text='Nazwa', anchor='w')

        tree.column('ID', width=15, anchor='e')
        tree.heading('ID', text='ID' + 3*" ", anchor='e')

        tree.pack(expand=True, fill='both')

        return tree        

    def create_details_project_tree(self, parent_frame, label_text):
        label = ttk.Label(parent_frame, text=label_text, font=("Arial", 12))
        label.pack(pady=5)

        tree = ttk.Treeview(parent_frame, columns=('Name', "Value"), show='headings')

        tree.column('#0', width=200)  # Kolumna z nazwą projektu
        tree.column('Name', width=80, anchor='e')
        tree.column('Value', width=50, anchor='e')

        tree.heading('#0', text='Projekty', anchor='center')
        tree.heading('Name', text='Inforamcja', anchor='center')
        tree.heading('Value', text='Wartość', anchor='center')

        tree.pack(expand=True, fill='both')

        return tree

    def create_details_tree(self, parent_frame, label_text):
        label = ttk.Label(parent_frame, text=label_text, font=("Arial", 12))
        label.pack(pady=5)

        tree = ttk.Treeview(parent_frame, columns=("Element", "Waga", "Filament", "Cena filament", "Koszt", "Czas druku"), show='headings')

        tree.column("Element", width=100)
        tree.column("Waga", width=80, anchor='e')
        tree.column("Filament", width=80)
        tree.column("Cena filament", width=120, anchor='e')
        tree.column("Koszt", width=120, anchor='e')
        tree.column("Czas druku", width=100, anchor='e')

        tree.heading("Element", text="Element")
        tree.heading("Waga", text="Waga")
        tree.heading("Filament", text="Filament")
        tree.heading("Cena filament", text="Cena filament")
        tree.heading("Koszt", text="Koszt")
        tree.heading("Czas druku", text="Czas druku")

        tree.pack(expand=True, fill='both')

        return tree

    def create_all_elements_details_tree(self, parent_frame, label_text):
        label = ttk.Label(parent_frame, text=label_text, font=("Arial", 12))
        label.pack(pady=5)

        tree = ttk.Treeview(parent_frame, columns=("Element", "Ilosc", "Waga", "Koszt", "Czas druku"), show='headings')

        tree.column("Element", width=100)
        tree.column("Ilosc", width=50, anchor='e')
        tree.column("Waga", width=80, anchor='e')
        tree.column("Koszt", width=120, anchor='e')
        tree.column("Czas druku", width=100, anchor='e')

        tree.heading("Element", text="Element")
        tree.heading("Ilosc", text="Ilosc")
        tree.heading("Waga", text="Waga")
        tree.heading("Koszt", text="Koszt")
        tree.heading("Czas druku", text="Czas druku")

        tree.pack(expand=True, fill='both')

        return tree


    def load_folders(self):
        """Load project folders into the treeview sorted by company name."""
        if os.path.exists(self.base_directory):
            projects = self.db_session.query(Projekt).all()
            project_data = []

            for project in projects:
                folder_name = project.nazwa
                folder_path = os.path.join(self.base_directory, folder_name)
                if os.path.isdir(folder_path):
                    projekt_company = project.firma.nazwa if project.firma else 'N/A'
                    project_id = project.id
                    project_data.append((projekt_company, folder_name, project_id))

            project_data.sort(key=lambda x: x[0])
            self.folder_tree.delete(*self.folder_tree.get_children())

            for company, name, proj_id in project_data:
                self.folder_tree.insert('', 'end', text=name, values=(company, name, proj_id))


    def filament_change_window(self):
        # Tworzenie drzewa widoków dla wyświetlenia listy filamentów
        self.window = tk.Toplevel(self.master)
        self.filament_frame = ttk.Frame(self.window)
        self.filament_frame.pack(side='left', expand=True, fill='both', padx=10, pady=20)
        self.filament_tree = self.create_filament_tree(self.filament_frame, 'Filamenty')

        # Wczytanie listy filamentów do drzewa 
        self.load_filaments_contents()
        

    def on_filament_click(self, event):
        selected_item = self.filament_tree.selection()
        if not selected_item:
            return

        region = self.filament_tree.identify('region', event.x, event.y)
        column = self.filament_tree.identify_column(event.x)

        print(region, column)
        if region == 'cell':
            element_value = self.filament_tree.item(selected_item[0], 'values')
            new_value = element_value[0]

            if new_value:
                self.selected_filament = new_value
                self.window.destroy()

    def on_element_detiles_double_click(self, event):
        selected_item = self.elements_tree.selection()
        if not selected_item:
            return

        region = self.elements_tree.identify('region', event.x, event.y)
        column = self.elements_tree.identify_column(event.x)

        if region == 'cell':
            element_value = self.elements_tree.item(selected_item[0], 'values')
            column_index = int(column[1:])-1
            if column_index == 1:
                new_value = simpledialog.askfloat("Edit",'Nowa wartość\t\t\t', initialvalue=float(element_value[column_index].split()[0]))
                column_index = 101
               
            else:
                return
            if new_value:
                self.update_element_value(selected_item[0], column_index, new_value)

    def on_element_double_click(self, event):
        selected_item = self.details_tree.selection()
        if not selected_item:
            return

        region = self.details_tree.identify('region', event.x, event.y)
        column = self.details_tree.identify_column(event.x)

        if region == 'cell':
            element_value = self.details_tree.item(selected_item[0], 'values')
            column_index = int(column[1:])-1
            if column_index == 0:
                new_value = simpledialog.askstring("Edit",'Nowa wartość\t\t\t', initialvalue=element_value[column_index])
            elif column_index == 1 or column_index == 5:
                new_value = simpledialog.askfloat("Edit",'Nowa wartość\t\t\t', initialvalue=float(element_value[column_index].split()[0]))

            elif column_index == 2:

                self.selected_filament = None

                self.filament_change_window()
                self.filament_tree.bind("<Button-1>", self.on_filament_click)
                self.window.wait_window()
                
                new_value = self.selected_filament
                print(new_value)
            
            else:
                return

            if new_value:
                print(selected_item[0], column_index, new_value)
                self.update_element_value(selected_item[0], column_index, new_value)

    def load_filaments_contents(self):
        filamenty = self.db_session.query(Filament).all()
        for element in filamenty:
            filament_id = element.id if element.id else 0
            filament = element.nazwa if element.nazwa else 'N/A'
            filament_type = element.typ if element.typ else 'N/A'
            filament_cena = element.cena if element.cena else 'N/A'

            self.filament_tree.insert('', 'end', values=(filament_id, filament, filament_type, filament_cena))

    def update_element_value(self, item_id, column_index, new_value):
        project_name = self.folder_tree.item(self.folder_tree.selection()[0], 'text')
        project = self.db_session.query(Projekt).filter_by(nazwa=project_name).first()

        element_name = self.details_tree.item(item_id, 'values')[0]
        element = next((e for e in project.elementy if e.nazwa == element_name), None)

        if not element:
            messagebox.showerror("Error", "Brak elementu")
            return

        if column_index == 0:
            element.nazwa = new_value
        elif column_index == 1:
            element.waga = float(new_value)
        elif column_index == 2:
            element.filament_id = new_value
        elif column_index == 5:
            if isinstance(new_value, float):
                values = str(new_value).split('.')
                solid = int(values[0])
                relic = int(values[1][0:2]) / 60
                element.czas_druku = float(solid + relic)
            else:
                element.czas_druku = float(new_value)
        elif column_index == 101:
            ilosc = int(new_value)
            project.update_ilosc_elem(self.db_session, project, element, ilosc)
        elif column_index == 102:
            pass

        # Zatwierdzenie zmian do bazy danych
        self.db_session.commit()

        # Przeładowanie szczegółów projektu
        self.load_project_details(project_name)

    def on_double_click(self, event):
        """Handle double-click event on a project folder."""
        selected_item = self.folder_tree.selection()

        if selected_item:
            folder_name = self.folder_tree.item(selected_item[0], 'text')
            folder_path = os.path.join(self.base_directory, folder_name)

            self.load_folder_contents(folder_path)
            self.load_project_details(folder_name)

    def on_file_double_click(self, event):
        """Handle double-click event on files in the content Treeviews."""
        widget = event.widget
        selected_item = widget.selection()

        if selected_item:
            file_name = widget.item(selected_item[0], 'values')[0]
            folder_name = self.folder_tree.item(self.folder_tree.selection()[0], 'text')
            folder_path = os.path.join(self.base_directory, folder_name)

            if widget == self.stl_tree:
                folder_type = 'STL'
            elif widget == self.prusa_tree:
                folder_type = 'Prusa'
            elif widget == self.gcode_tree:
                folder_type = 'G-Code'
            else:
                return

            file_path = os.path.join(folder_path, folder_type, file_name)

            try:
                os.startfile(file_path)
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {e}")

    def load_folder_contents(self, folder_path):
        """Load contents of the selected folder into the content Treeviews."""
        self.stl_tree.delete(*self.stl_tree.get_children())
        self.prusa_tree.delete(*self.prusa_tree.get_children())
        self.gcode_tree.delete(*self.gcode_tree.get_children())

        subfolders = ['STL', 'Prusa', 'G-Code']
        file_dict = {folder: [] for folder in subfolders}

        for folder in subfolders:
            folder_full_path = os.path.join(folder_path, folder)
            if os.path.exists(folder_full_path) and os.path.isdir(folder_full_path):
                for file_name in os.listdir(folder_full_path):
                    if not file_name.endswith('.ini'):
                        file_dict[folder].append(file_name)

        for stl_file in file_dict['STL']:
            self.stl_tree.insert('', 'end', values=(stl_file,))
        for prusa_file in file_dict['Prusa']:
            self.prusa_tree.insert('', 'end', values=(prusa_file,))
        for gcode_file in file_dict['G-Code']:
            self.gcode_tree.insert('', 'end', values=(gcode_file,))


    def load_project_details(self, project_name):
        """Load details of the selected project and update total cost."""
        self.details_tree.delete(*self.details_tree.get_children())
        self.details_project_tree.delete(*self.details_project_tree.get_children())
        self.elements_tree.delete(*self.elements_tree.get_children())

        project = self.db_session.query(Projekt).filter_by(nazwa=project_name).first()
        total_cost = 0.0  # Initialize total cost
        total_time = 0.0

        for element in project.elementy:
            ilosc = project.get_ilosc_elementu(element, self.db_session)

            czas = element.czas_druku
            czasXilosc = czas *ilosc
            czas_str = f"{int(czas)} h {(czas-int(czas))*60:.0f} min"
            czas_strXilosc = f"{int(czasXilosc)} h {(czasXilosc-int(czasXilosc))*60:.0f} min"

            filament = element.filament.nazwa if element.filament else 'N/A'
            filament_cena = element.filament.cena if element.filament else 'N/A'
            cost = element.oblicz_cene()
            total_cost += cost*ilosc  # Sum up costs
            total_time += czas*ilosc

            self.details_tree.insert('', 'end', values=(element.nazwa, f"{element.waga:} g", filament, f"{filament_cena:} PLN/kg", f"{cost:.2f} PLN", czas_str + 3*" "))
            self.elements_tree.insert('', 'end', values=(element.nazwa, ilosc, f"{element.waga *ilosc:} g", f"{cost * ilosc:.2f} PLN", czas_strXilosc + 3*" "))

        # Reload the selected item in the main tree view (project list) with updated total cost and keep the date
        selected_item = self.folder_tree.selection()[0]
        current_values = self.folder_tree.item(selected_item, 'values')

        # Update the tree item with the new total cost
        project_id = current_values[2]
        projekt_company = project.firma.nazwa if project.firma else 'N/A'
        self.folder_tree.item(selected_item, values=(projekt_company, project_name, project_id))

        all_time = f"{int(total_time)} h {(total_time-int(total_time))*60:.0f} min"

        dictionary = [("Koszt całkowity:", f"{total_cost:.2f} PLN"),
                      ("Czas całkowity:", all_time),
                      ("Data utworzenia:", project.data)]

        for value in dictionary:
            self.details_project_tree.insert('', 'end', values=(value[0], str(value[1]) + 3*" "))


if __name__ == "__main__":
    root = TkinterDnD.Tk()  # Use TkinterDnD for DnD
    root.geometry("1080x580")
    app = FolderApp(root)
    root.mainloop()
