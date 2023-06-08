import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import pymongo

# MongoDB connection details
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client['meetapp']
collection = db['tester']
def end_meet():
    confirm = messagebox.askquestion("Confirmation", "Are you sure you want to end the meeting and delete all entries?")
    if confirm == 'yes':
        collection.delete_many({})
        messagebox.showinfo("Meeting Ended", "All entries have been deleted.")
        
def fetch_data():
    # Fetch data from the collection
    data = collection.find()

    # Clear existing data in the table
    table.delete(*table.get_children())

    # Insert fetched data into the table
    for item in data:
        # Extract the fields you want to display
        name = item.get('name')
        status = item.get('status')
        active_time = item.get('active_time')

        # Insert data into the table
        table.insert('', 'end', values=(name, status, active_time))

    root.after(500, fetch_data)

def print_attendance():
    
    num=int(entry.get())

    # Perform the query to retrieve the names
    query = {"active_time": {"$gte": num}}
    projection = {"name": 1}
    results = collection.find(query, projection)

    # Create a list to store the names
    names = []

    # Iterate over the results and extract the names
    for result in results:
        names.append(result['name'])
    with open('attendance.txt', 'w') as file:
        for name in names:
            file.write(name + '\n')
    messagebox.showinfo("Done", "Attendance has been taken.")
root = tk.Tk()
root.title("ActiveMeet: Central")
root.geometry("350x600")

# Create a style for customizing the widget appearance
style = ttk.Style()
style.configure("Custom.TButton", font=("Arial", 12, "bold"), background="light yellow", padding=10)

# Create the table to display the data
table = ttk.Treeview(root)
table['columns'] = ('Name', 'Status', 'Active Time')
table.column('#0', width=0, stretch='no')
table.column('Name', width=100, anchor='center')
table.column('Status', width=100, anchor='center')
table.column('Active Time', width=100, anchor='center')

table.heading('#0', text='')
table.heading('Name', text='Name')
table.heading('Status', text='Status')
table.heading('Active Time', text='Active Time')

# Increase the height of the table
table['height'] = 20

table.pack()

# Fetch and display the data initially
fetch_data()

# Create the entry box and print button
entry = tk.Entry(root, font=("Arial", 12))
entry.pack(pady=10)

print_button = ttk.Button(root, text="Print  Attendance", command=print_attendance, style="Custom.TButton")
print_button.pack()
EndButton = ttk.Button(root, text="End Meet", command=end_meet, style="Custom.TButton")
EndButton.pack()

print_button.configure(width=30)
EndButton.configure(width=30)

# Run the Tkinter event loop
root.mainloop()
