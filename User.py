# Варіант 15.
# Розробити класи Житлове приміщення, Орендатор, Орендодавець, Договір
# оренди. Реалізувати логіку роботи процесу оренди житла. У одного
# орендодавця може бути декілька житлових приміщень, готових до оренди.
# В договорі фіксується дата старту та закінчення оренди. Одночасно можуть
# створювати заявки декілька орендаторів. Забезпечити блокування
# приміщення при оформленні договору. Пояснити доцільність такого
# підходу.
# GUI
from tkinter import *
from tkinter import ttk
from Classes import *
import csv
from Window import Default
from dateutil.relativedelta import relativedelta
import threading

class UserWindow:
    def __init__(self, title= str):
        self.root = Default(title)
        self.root.geometry('400x200+300+300')
        self.root.minsize(400, 160)

        self.name = StringVar()
        self.surname = StringVar()
        self.client_type = StringVar()
        self.password = StringVar()
        self.id = StringVar()

        self.mainframe = ttk.Frame(self.root, padding='0 0 0 0')
        self.mainframe.grid(column=0, row=0, sticky='NSEW')
        self.mainframe.pack(expand=True)

        self.Log_Screen()

    def pretty(func):
        def wrapper(self: 'UserWindow'):
            func(self)
            for child in self.mainframe.winfo_children(): 
                child.grid_configure(padx=20, pady=15, sticky='NW')
                if type(child) == ttk.Scrollbar:
                    child.grid_configure(padx=0, sticky='NSW')
        return wrapper


    def Login(self):
        with open('userinfo.csv', newline= '') as file:
            reader = csv.DictReader(file)
            for row in reader:
                entry_found = False
                if self.name.get() == row['name'] and self.surname.get() == row['surname']:
                    entry_found = True
                if entry_found == True:
                    if self.password.get() != row['password']:
                        self.login_status.set('Wrong password!')
                        return
                    self.client_type.set(row['type'])
                    self.id.set(row['id'])
                    self.Main_Screen()
                else:
                    self.login_status.set('Wrong name/surname!')


    @pretty
    def Log_Screen(self):
        for widget in self.mainframe.winfo_children():
            widget.destroy()

        self.root.title('Login screen')

        self.name = StringVar()
        self.surname = StringVar()
        self.client_type = StringVar()
        self.password = StringVar()
        self.id = StringVar()

        name_entry = ttk.Entry(self.mainframe, textvariable= self.name)
        name_entry.grid(column=2, row=1)
        surname_entry = ttk.Entry(self.mainframe, textvariable= self.surname)
        surname_entry.grid(column=2, row=2)
        name_entry = ttk.Entry(self.mainframe, textvariable= self.password)
        name_entry.grid(column=2, row=3)
        
        ttk.Label(self.mainframe, text='Name:').grid(column=1, row=1)
        ttk.Label(self.mainframe, text='Surname:').grid(column=1, row=2)
        ttk.Label(self.mainframe, text='Password:').grid(column=1, row=3)

        self.login_status = StringVar(value='Waiting for login attempt...')
        login_status_label = ttk.Label(self.mainframe, textvariable=self.login_status)
        login_status_label.grid(column=1, columnspan=2, row=4, sticky='W')

        ttk.Button(self.mainframe, text='Log in', command=self.Login).grid(column=3, row= 3)


    @pretty
    def Main_Screen(self):
        for widget in self.mainframe.winfo_children():
            widget.destroy()
        
        self.root.title(f'Leasing manager ({self.client_type.get()})')

        ttk.Label(self.mainframe, text=f'Name: {self.name.get()} {self.surname.get()} [{self.id.get()}]\n{self.client_type.get()}').grid(column=1, row=1)
        ttk.Button(self.mainframe, text='Log out', command=self.Log_Screen).grid(column=1, row=2)

        if self.client_type.get() == 'Landlord':
            self.Landlord_Mode()
        elif self.client_type.get() == 'Tenant':
            self.Tenant_Mode()
        else:
            ttk.Label(self.mainframe, text='Test mode. No functionality available!').grid(column=2, row=1)
            ttk.Button(self.mainframe, text='Exit',command=self.root.quit).grid(column=2, row=2)

    
    def Landlord_Mode(self):
        def show_selection_options(*args):
            index = listbox.curselection()[0]
            info_text.set(f'Area: {user._property[index].area}')

        self.root.geometry('700x200+300+300')
        user = Landlord(self.name.get(), self.surname.get())

        with open('propertyinfo.csv') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['ownerid'] == self.id.get():
                    user._property.append(Housing(float(row['area']), row['address']))
        
        self.mainframe.rowconfigure(1, minsize=30, weight=1)
        self.mainframe.rowconfigure(2, minsize=30, weight=1)

        list_options = StringVar(value=[p.address for p in user._property])
        listbox = Listbox(self.mainframe, listvariable=list_options)
        listbox.grid(column=2, row=1, rowspan=2)

        listbox_scrollbar = ttk.Scrollbar(self.mainframe, orient=VERTICAL, command=listbox.yview)
        listbox_scrollbar.grid(column=3, row=1, rowspan=2, sticky=(N, S))
        listbox.configure(yscrollcommand=listbox_scrollbar.set, selectmode=SINGLE)

        info_text = StringVar()
        info_label = ttk.Label(self.mainframe, textvariable=info_text)
        info_text.set('Select one of your properties to continue')
        info_label.grid(column=4, row=1)

        
        listbox.bind('<<ListboxSelect>>', show_selection_options)
            

    def Tenant_Mode(self):
        self.current_lease: Lease
        index = lambda: listbox.curselection()[0]
        def show_selection_options(*args):
            self.current_lease = user.leases[index()]
            if not self.current_lease.is_signed:
                lease_button.configure(state=NORMAL)
            info_text.set(f'Area: {self.current_lease.subject.area}\nOwner: {self.current_lease.landlord.name} {self.current_lease.landlord.surname}\n\
Duration: {self.current_lease.length_months} seconds')

        def start_lease(*args):
           lease_button.configure(state=DISABLED)
           leasing_thread = threading.Thread(target=user.leases[index()].sign, args=())
           leasing_thread.daemon = True
           leasing_thread.start()
           

        def lease_status():

            if not self.current_lease.is_signed:
                self.status_text.set('Lease is not signed.')
            elif self.current_lease.is_signed and not hasattr(self.current_lease, 'termination'):
                self.status_text.set('Lease is being signed...')
            elif self.current_lease.termination < datetime.datetime.now():
                self.current_lease.terminate()
                self.status_text('Lease terminated.')
                lease_button.configure(state=NORMAL)
            else:
                self.status_text.set(f'Lease is signed. Time left: {self.current_lease.termination - datetime.datetime.now()}')

            self.root.after(100, lease_status)
                

        self.root.geometry('700x200+300+300')
        user = Tenant(self.name.get(), self.surname.get())

        with open('leaseinfo.csv') as leases:
            lreader = csv.DictReader(leases)
            for lrow in lreader:
                if lrow['tenantid'] == self.id.get():
                    id = lrow['id']
                    tenantid = lrow['tenantid']
                    ownerid = lrow['ownerid']
                    length = int(lrow['length'])
        with open('userinfo.csv') as users:
            ureader = csv.DictReader(users)
            for urow in ureader:
                if urow['id'] == tenantid:
                    tenant = Tenant(urow['name'], urow['surname'])
                if urow['id'] == ownerid:
                    owner = Landlord(urow['name'], urow['surname'])
        with open('propertyinfo.csv') as properties:
            preader = csv.DictReader(properties)
            for prow in preader:
                if id == prow['id'] and ownerid == prow['ownerid']:
                    housing = Housing(prow['area'], prow['address'])
                    owner._property.append(housing)
                    lease = Lease(owner, tenant, housing, length)
                    tenant.leases.append(lease)       
        
        self.mainframe.rowconfigure(1, minsize=30, weight=1)
        self.mainframe.rowconfigure(2, minsize=30, weight=1)

        list_options = StringVar(value=[p.subject.address for p in user.leases])
        listbox = Listbox(self.mainframe, listvariable=list_options)
        listbox.grid(column=2, row=1, rowspan=2)

        info_text = StringVar()
        info_label = ttk.Label(self.mainframe, textvariable=info_text)
        info_text.set('Select one of your leases to continue')
        info_label.grid(column=4, row=1)
        
        self.status_text = StringVar(value='Waiting for lease selection...')
        status_label = ttk.Label(self.mainframe, textvariable=self.status_text)
        status_label.grid(column=1, columnspan=3, row=3)

        lease_button = ttk.Button(self.mainframe, text='Lease', command=start_lease)
        if len(listbox.curselection()) == 0:
            lease_button.configure(state=DISABLED)
        lease_button.grid(column=4, row=2, sticky='SE')

        listbox_scrollbar = ttk.Scrollbar(self.mainframe, orient=VERTICAL, command=listbox.yview)
        listbox_scrollbar.grid(column=3, row=1, rowspan=2, sticky=(N, S))
        listbox.configure(yscrollcommand=listbox_scrollbar.set, selectmode=SINGLE)

        listbox.bind('<<ListboxSelect>>', show_selection_options)
        listbox.select_set(0)
        listbox.event_generate('<<ListboxSelect>>')

        lease_status()


        

if __name__ == '__main__':
    w = UserWindow('BaseWindow')
    w.root.mainloop()