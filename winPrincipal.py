from tkinter import *
from tkinter import ttk
from connection import Database
import re


def buildMainWindow():
    window = Tk()
    window.title("CRUD Application")
    window.geometry("600x500")
    return window


window = buildMainWindow()

database = Database()

firstName = StringVar()
lastName = StringVar()
email = StringVar()
age = StringVar()
address = StringVar()
salary = StringVar()


def createLabel(firstName, lastName, email, age, address, salary, lblMessage):
    frame = LabelFrame(window, text="Form Students")
    frame.place(x=50, y=50, width=510, height=400)

    Label(frame, text="First Name").grid(column=1, row=0)
    txtFirstName = Entry(frame, textvariable=firstName)
    txtFirstName.grid(column=2, row=0)

    Label(frame, text="Last Name").grid(column=1, row=1)
    txtLastName = Entry(frame, textvariable=lastName)
    txtLastName.grid(column=2, row=1)

    Label(frame, text="Email").grid(column=3, row=0)
    txtEmail = Entry(frame, textvariable=email)
    txtEmail.grid(column=4, row=0)

    Label(frame, text="Age").grid(column=3, row=1)
    txtAge = Entry(frame, textvariable=age)
    txtAge.grid(column=4, row=1)

    Label(frame, text="Address").grid(column=1, row=3)
    txtAddress = Entry(frame, textvariable=address)
    txtAddress.grid(column=2, row=3)

    Label(frame, text="Salary").grid(column=3, row=3)
    txtSalary = Entry(frame, textvariable=salary)
    txtSalary.grid(column=4, row=3)

    lblMessage.config(text="Here Message", fg="green")

    return frame


def buildMessage():
    lblMessage = Label()
    lblMessage.config(text="Here message", fg="green")
    lblMessage.grid(column=1, row=4, columnspan=4)

    return lblMessage


lblMessage = buildMessage()

frame = createLabel(firstName, lastName, email, age, address, salary, lblMessage)

treeStudents = ttk.Treeview(frame, selectmode=NONE)


def selected(event):
    select_item = treeStudents.selection()

    if not select_item:
        lblMessage.config(text="No students selected")
        return

    itemSelected = select_item[0]

    if re.match(r'^\d+$', itemSelected):
        int(itemSelected)
    else:
        int(re.sub(r'\D', '', itemSelected))

    itemSelected = treeStudents.selection()[0]

    firstName.set(treeStudents.item(itemSelected, "values")[1])
    lastName.set(treeStudents.item(itemSelected, "values")[2])
    email.set(treeStudents.item(itemSelected, "values")[3])
    age.set(treeStudents.item(itemSelected, "values")[4])
    address.set(treeStudents.item(itemSelected, "values")[5])
    salary.set(treeStudents.item(itemSelected, "values")[6])


# Table of Student List
def buildTreeStudent():
    treeStudents.grid(column=1, row=5, columnspan=4)
    treeStudents["columns"] = ("ID", "FIRSTNAME", "LASTNAME", "EMAIL", "AGE", "ADDRESS", "SALARY")
    treeStudents.column("#0", width=0, stretch=NO)  # ID
    treeStudents.column("ID", width=20, anchor=CENTER)  # FIRSTNAME
    treeStudents.column("FIRSTNAME", width=50, anchor=CENTER)  # LASTNAME
    treeStudents.column("LASTNAME", width=50, anchor=CENTER)  # EMAIL
    treeStudents.column("EMAIL", width=50, anchor=CENTER)  # AGE
    treeStudents.column("AGE", width=50, anchor=CENTER)  # ADDRESS
    treeStudents.column("ADDRESS", width=50, anchor=CENTER)  # SALARY
    treeStudents.column("SALARY", width=50, anchor=CENTER)  # SALARY


# Heading columns
def buildTreeHeader():
    treeStudents.heading("#0", text="")
    treeStudents.heading("ID", text="ID", anchor=CENTER)
    treeStudents.heading("FIRSTNAME", text="FIRSTNAME", anchor=CENTER)
    treeStudents.heading("LASTNAME", text="LASTNAME", anchor=CENTER)
    treeStudents.heading("EMAIL", text="EMAIL", anchor=CENTER)
    treeStudents.heading("AGE", text="AGE", anchor=CENTER)
    treeStudents.heading("ADDRESS", text="ADDRESS", anchor=CENTER)
    treeStudents.heading("SALARY", text="SALARY", anchor=CENTER)

    treeStudents.bind("<<TreeviewSelect>>", selected)


# Functions
def cleanTable():
    # Return all rows
    rows = treeStudents.get_children()

    # Delete row by row index
    for row in rows:
        treeStudents.delete(row)


def fillTable():
    # I perform a cleanup of the tree students
    cleanTable()

    # I query the database
    sql = "SELECT * FROM students"
    database.cursor.execute(sql)

    # I store all the records returned to me by the database
    rows = database.cursor.fetchall()

    # Insert row by row in the student tree
    for row in rows:
        treeStudents.insert("", END, values=row)


def delete():
    # I get the selected item from the tree
    select_item = treeStudents.selection()

    # Evaluate if any record was selected or not
    if not select_item:
        lblMessage.config(text="No students selected")
        return

    # I store in itemSelected the selected record
    itemSelected = select_item[0]

    # I check if itemSelected is a string containing only numbers
    if re.match(r'^\d+$', itemSelected):
        int(itemSelected)
    else:
        # Remove non-numeric characters from string
        itemSelected = int(re.sub(r'\D', '', itemSelected))

    # I perform the query and execute the deletion of the row
    sql = "DELETE FROM students WHERE ID={}".format(itemSelected)
    database.cursor.execute(sql)
    database.connection.commit()

    # Delete the row from the student tree
    treeStudents.delete(select_item[0])

    lblMessage.config(text="Success deleted")


def update():
    global itemSelected

    if len(treeStudents.selection()) > 0:

        itemSelected = treeStudents.selection()[0]

        if re.match(r'^\d+$', itemSelected):
            itemSelected = int(itemSelected)
        else:
            itemSelected = int(re.sub(r'\D', '', itemSelected))

        updateStudent(firstName.get(), lastName.get(), email.get(), int(age.get()), address.get(),
                      float(salary.get()), itemSelected)
        cleanFields()
        lblMessage.config(text="Success updated", fg="green")
        fillTable()


def validateStudent():
    if not age.get().isdigit():
        lblMessage.config(text="Age must be a number", fg="red")

    if not salary.get().isdigit():
        lblMessage.config(text="Salary must be a number")

    if len(firstName.get()) <= 0 and len(lastName.get()) <= 0 and len(email.get()) <= 0 and len(age.get()) <= 0 and len(
            address.get()) <= 0 and len(salary.get()) <= 0:
        lblMessage.config(text="Fields cannot be empty")


def updateStudent(firstNameValue, lastNameValue, emailValue, ageValue, addressValue, salaryValue, itemSelected):
    try:
        database.cursor.execute(
            "UPDATE students SET firstName=%s, lastName=%s, email=%s, age=%s, address=%s, salary=%s WHERE ID=%s",
            (firstNameValue, lastNameValue, emailValue, ageValue, addressValue, salaryValue, itemSelected))
        database.connection.commit()
    except Exception as e:
        print(f"Error to create student {e}")


def addStudent(firstNameValue, lastNameValue, emailValue, ageValue, addressValue, salaryValue):
    try:
        database.cursor.execute("INSERT INTO students (firstName, lastName, email, age, address, salary) VALUES (%s, "
                                "%s, %s, %s, %s, %s)",
                                (firstNameValue, lastNameValue, emailValue, ageValue, addressValue, salaryValue))
        database.connection.commit()
    except Exception as e:
        print(f"Error to create student {e}")


def cleanFields():
    firstName.set("")
    lastName.set("")
    email.set("")
    age.set("")
    address.set("")
    salary.set("")


def create():
    validateStudent()
    addStudent(firstName.get(), lastName.get(), email.get(), int(age.get()), address.get(),
               float(salary.get()))
    cleanFields()
    lblMessage.config(text="Success created", fg="green")
    fillTable()


# Buttons Actions
def buildBtnAction():
    btnDelete = Button(frame, text="Delete", command=delete)
    btnDelete.grid(column=2, row=6)

    btnAdd = Button(frame, text="Save", command=create)
    btnAdd.grid(column=3, row=6)

    btnUpdate = Button(frame, text="Select", command=update)
    btnUpdate.grid(column=4, row=6)


fillTable()
buildTreeStudent()
buildTreeHeader()
buildBtnAction()
window.mainloop()
