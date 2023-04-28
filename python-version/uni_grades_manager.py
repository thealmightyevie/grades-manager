# Import modules
from tkinter import *
from tkinter.ttk import *
import sqlite3

# Main window setup
main_win = Tk()
main_win.title('Uni Grades Manager')
main_win.geometry('900x650')
main_win.pack_propagate(0) # Children of main_win do not influence pack size
main_win.state('zoomed') # Automatically open full screen

# Access sqlite database
conn = sqlite3.connect('uni_grades_manager.db')
ugm_db = conn.cursor()

# Add unit window setup
def au_win_mgmt():
    global au_win
    au_win = Tk()
    au_win.title('Add Unit')
    au_win.geometry('225x200')

    # Title label
    auw_title = Label(au_win, text = 'Add Unit', font = ('calibri', 15))
    auw_title.pack(padx = 5)

    uc_title = Label(au_win, text = 'Unit Code', font = ('calibri', 10))
    uc_title.pack(anchor = 'w', padx = (25, 0))

    global uc_entry
    uc_entry = Entry(au_win)
    uc_entry.pack(anchor = 'w', padx = 25, pady = 5, fill = 'x')

    un_title = Label(au_win, text = 'Unit Name', font = ('calibri', 10))
    un_title.pack(anchor = 'w', padx = (25, 0))

    global un_entry
    un_entry = Entry(au_win)
    un_entry.pack(anchor = 'w', padx = 25, pady = 5, fill = 'x')

    add_nu = Button(au_win, text = 'Add', command = add_new_unit)
    add_nu.pack(anchor = 'e', padx = (0, 25), pady = 10)

# Add new unit
def add_new_unit():
    if len(uc_entry.get()) == 0 or len(un_entry.get()) == 0:
        uc_entry.delete(0, END)
        un_entry.delete(0, END)
        au_error_msg = Label(au_win, text = 'Error: Please enter name and code.')
        au_error_msg.pack(anchor = 's')
    else:
        try:
            new_uc = uc_entry.get()
            new_un = un_entry.get()

            insert_units_query = f"INSERT INTO units (unitCode, unitName) VALUES ('{new_uc}', '{new_un}')"
            ugm_db.execute(insert_units_query)
            conn.commit()

            global units
            units.insert(END, f'{new_uc}')
        except:
            uc_entry.delete(0, END)
            un_entry.delete(0, END)
            au_error_msg = Label(au_win, text = 'Error: Could not be added, try again.')
            au_error_msg.pack(anchor = 's')

# Add new grade
def add_new_grade():
    try:
        selected_unit = units.get(units.curselection())
        new_at = at_entry.get()
        new_weight = weight_entry.get()
        new_grade = grade_entry.get()

        insert_assignments = f"INSERT INTO assignments (unitCode, assignmentName, weight, grade) VALUES ('{selected_unit}', '{new_at}', '{new_weight}', '{new_grade}')"
        ugm_db.execute(insert_assignments)

        select_all = "SELECT assignments.unitCode, unitName, assignmentName, weight, assignments.grade FROM units INNER JOIN assignments On units.unitCode = assignments.unitCode"
        ugm_db.execute(select_all)
        acquire = ugm_db.fetchall()

        grade_info.delete(*grade_info.get_children())

        for info in acquire:
            tree_info = info
            grade_info.insert('', 'end', values = tree_info)

        conn.commit()
    except:
        print("Error: A variable has been entered incorrectly. Try again.")
# Update grade
def update_grade():
    update_at = at_entry.get()
    update_weight = weight_entry.get()
    update_grade = grade_entry.get()

    if len(update_weight) != 0:
        update_weight = f"UPDATE assignments SET weight = {update_weight} WHERE assignmentName = '{update_at}'"
        ugm_db.execute(update_weight)

    if len(update_grade) != 0:
        update_grade = f"UPDATE assignments SET grade = {update_grade} WHERE assignmentName = '{update_at}'"
        ugm_db.execute(update_grade)

    if (len(update_at) == 0) or (len(update_weight) == 0 and len(update_grade) == 0):
        at_entry.delete(0, END)
        weight_entry.delete(0, END)
        grade_entry.delete(0, END)
        error_msg = Label(assignment_info, text = 'Error: Could not be updated, missing values.')
        error_msg.grid(row = 5, column = 0, padx = 5)
    
    conn.commit()

    #grade_info.update(selected_grade)

# Remove grade
def remove_grade():
    selected_grade = grade_info.selection()

    remove_gr_id = grade_info.item(selected_grade)['values'][2] # Selects the assignment's name

    remove_entry = f"DELETE FROM assignments WHERE assignmentName = '{remove_gr_id}'"
    ugm_db.execute(remove_entry)
    conn.commit()

    grade_info.delete(selected_grade)

# Remove unit
def remove_unit():
    selected_unit_rm = units.get(units.curselection())

    remove_unit = f"DELETE FROM units WHERE unitCode = '{selected_unit_rm}'"
    ugm_db.execute(remove_unit)
    conn.commit()

    units.delete('anchor')

# Calculate unit total
def calculate_total(selected_unit):
    selected_unit = grade_values.get()
    calculated_grade_query = f"SELECT SUM(Grade) FROM assignments WHERE unitCode = '{selected_unit}'"
    ugm_db.execute(calculated_grade_query)
    final_grade = ugm_db.fetchall()

    tg_selected.configure(state = NORMAL)
    tp_selected.configure(state = NORMAL)

    for item in final_grade:
        tg_selected.delete(1.0, END)
        tp_selected.delete(1.0, END)
        try:
            tp_selected.insert(INSERT, item[0])

            if item[0] >= 0 and item[0] < 25:
                tg_selected.insert(INSERT, '1')
            elif item[0] >= 25 and item[0] < 40:
                tg_selected.insert(INSERT, '2')
            elif item[0] >= 40 and item[0] < 50:
                tg_selected.insert(INSERT, '3')
            elif item[0] >= 50 and item[0] < 65:
                tg_selected.insert(INSERT, '4')
            elif item[0] >= 65 and item[0] < 75:
                tg_selected.insert(INSERT, '5')
            elif item[0] >= 75 and item[0] < 85:
                tg_selected.insert(INSERT, '6')
            elif item[0] >= 85 and item[0] < 101:
                tg_selected.insert(INSERT, '7')

        except:
            tp_selected.insert(INSERT, 'N/A')
            tg_selected.insert(INSERT, 'N/A')

    tg_selected.configure(state = DISABLED)
    tp_selected.configure(state = DISABLED)

    selected_unit = grade_values.get()
    final_grade_val = int(tg_selected.get('1.0', 'end-1c'))
    update_db_query = f"UPDATE units SET grade = {final_grade_val} WHERE unitCode = '{selected_unit}'"
    ugm_db.execute(update_db_query)
    conn.commit()

def display_gpa():
    unit_grades = [] # Grades for each unit added to a list
    for unit in units_list:
        select_unit_grade = f"SELECT grade FROM units WHERE unitCode = '{unit}'" # Selecting the grade of each unit
        ugm_db.execute(select_unit_grade) # Executing the select query
        fetch = ugm_db.fetchall() # Fetching results from query
        for grade in fetch:
            unit_grades.append(*grade) # Adding results to grades list

    sum_of_performance = 0
    for grade in unit_grades:
        performance_per_unit = 12 * grade
        sum_of_performance = sum_of_performance + performance_per_unit

    num_units_q = f"SELECT COUNT(*) FROM units"
    ugm_db.execute(num_units_q) # Executing the select query
    fetch = ugm_db.fetchall()
    num_of_units = 0
    for result in fetch:
        num_of_units = int(*result)

    credit_points = 12 * 12
    calculated_gpa = sum_of_performance / credit_points
    current_gpa.configure(state = NORMAL)
    current_gpa.insert(INSERT, calculated_gpa)
    current_gpa.configure(state = DISABLED)

# HEADING
title = Label(main_win, text = 'Uni Grades Manager', font = ('calibri', 28, 'bold'))
title.pack(pady = (5, 0))

# TREEVIEW
treeview_frame = Frame(main_win)
treeview_frame.pack(anchor = 'n', pady = 10)

    # Tree
gi_headers = ['Unit Name', 'Assignment', 'Weight', 'Grade']
grade_info = Treeview(treeview_frame)
grade_info.pack(padx = (30, 0), fill = 'x', side = 'left')
gi_scrollbar = Scrollbar(treeview_frame, orient = 'vertical', command = grade_info.yview)
gi_scrollbar.pack(fill = 'y', side = 'right', anchor = 'w')
grade_info.configure(yscrollcommand = gi_scrollbar.set)

    # Tree columns
grade_info['columns'] = ('Unit Code', 'Unit Name', 'Assignment', 'Weight', 'Grade')
grade_info['height'] = 15
grade_info.column('#0', width = 0, minwidth = 0, stretch = False)
grade_info.column('Unit Code', width = 70, minwidth = 70, stretch = True)
grade_info.column('Unit Name', width = 225, minwidth = 130, stretch = True)
grade_info.column('Assignment', width = 185, minwidth = 130, stretch = True)
grade_info.column('Weight', width = 50, minwidth = 50, stretch = True)
grade_info.column('Grade', width = 50, minwidth = 50, stretch = True)

    # Definition of the headings
grade_info.heading('#0', text = '', anchor = 'w')
grade_info.heading('Unit Code', text = 'Unit Code', anchor = 'w')
grade_info.heading('Unit Name', text = 'Unit Name', anchor = 'w')
grade_info.heading('Assignment', text = 'Assignment', anchor = 'w')
grade_info.heading('Weight', text = 'Weight', anchor = 'w')
grade_info.heading('Grade', text = 'Grade', anchor = 'w')

    # Display current db info in treeview
select_all = "SELECT assignments.unitCode, unitName, assignmentName, weight, assignments.grade FROM units INNER JOIN assignments On units.unitCode = assignments.unitCode"
ugm_db.execute(select_all)
acquire = ugm_db.fetchall()
for info in acquire:
    tree_info = info # Assignment all items from query except last to variable
    grade_info.insert('', 'end', values = tree_info)

# Remove grade button
remove_grade_btn = Button(main_win, text = 'Remove Grade', command = remove_grade)
remove_grade_btn.pack(pady = (0, 10))

separator = Separator(main_win, orient = 'horizontal')
separator.pack(fill = X)

# ADD INFORAMTION TITLE
add_info = Label(main_win, text = 'Add Information', font = ('calibri', 15, 'bold'))
add_info.pack()

# Add info frame
add_info_frame = Frame(main_win)
add_info_frame.pack(anchor = 's')

# Adding unit info LF
add_unit_inf = LabelFrame(add_info_frame, text = 'Unit Info')
add_unit_inf.grid(row = 0, column = 0, padx = (15, 30), sticky = 'we')

    # Unit Selection label
unit_selection = Label(add_unit_inf, text = 'Unit')
unit_selection.grid(row = 0)

    # Units listbox
units = Listbox(add_unit_inf)
units.grid(row = 1, padx = 20, pady = 5)
units_list = ['']

    # Display all items from units in listbox
select_frm_u_q = "SELECT * FROM units"
ugm_db.execute(select_frm_u_q)
fetch = ugm_db.fetchall()
for item in fetch:
    units.insert(END, item[0])
    units_list.append(item[0])

    # Add unit button
add_unit = Button(add_unit_inf, text = 'Add Unit', command = au_win_mgmt)
add_unit.grid(row = 2, padx = 5, pady = 5, sticky ='w')

remove_unit_btn = Button(add_unit_inf, text = 'Remove Unit', command = remove_unit)
remove_unit_btn.grid(row = 2, padx = 5, pady = 5, sticky = 'e')

# ADDING ASSIGNMENT INFO LF
assignment_info = LabelFrame(add_info_frame, text = 'Assignment Info')
assignment_info.grid(row = 0, column = 1, padx = (30, 15), sticky = 'we')

asgnmnt_title = Label(assignment_info, text = 'Assignment Title')
asgnmnt_title.grid(row = 0, column = 0, padx = 15, pady = (5, 0), sticky = 'w')

at_entry = Entry(assignment_info)
at_entry.grid(row = 1, column = 0, padx = 15, pady = 5)

weight_title = Label(assignment_info, text = 'Weight')
weight_title.grid(row = 2, column = 0, padx = 15, sticky = 'w')

weight_entry = Entry(assignment_info)
weight_entry.grid(row = 3, column = 0, padx = (15, 10), pady = 5)

grade_title = Label(assignment_info, text = 'Grade')
grade_title.grid(row = 2, column = 1, padx = 15, sticky = 'w')

grade_entry = Entry(assignment_info)
grade_entry.grid(row = 3, column = 1, padx = (10, 15), pady = 5)

# Buttons frame
buttons = Frame(assignment_info)
buttons.grid(row = 4, column = 0)

# Update grade button
update_grade_btn = Button(buttons, text = 'Update Grade', command = update_grade)
update_grade_btn.grid(row = 4, column = 0, padx = (10, 15))

# Add grade button
add_grade = Button(buttons, text = 'Add Grade', command = add_new_grade)
add_grade.grid(row = 4, column = 1, sticky = 'e', padx = 15, pady = 5)


# TOTAL GRADE LF
total_grade_info = LabelFrame(add_info_frame, text = 'Total Grade')
total_grade_info.grid(row = 5, column = 1, columnspan = 2)

# Labels
percentage_label = Label(total_grade_info, text = '%')
percentage_label.grid(row = 0, column = 1, pady = (5, 0))

grade_label = Label(total_grade_info, text = 'Grade')
grade_label.grid(row = 0, column = 2, padx = (0, 10), pady = (5, 0))

# Total grades menu variable
grade_values = StringVar()
grade_values.set('Select a Unit')

# Option Menu
total_grade = OptionMenu(total_grade_info, grade_values, *units_list, command = calculate_total)
total_grade.grid(row = 1, column = 0, padx = 20, pady = (0, 10))

# Text box
tp_selected = Text(total_grade_info, height = 1, width = 5, state = DISABLED)
tp_selected.grid(row = 1, column = 1, padx = (0, 5), pady = (0, 10))

# Text box 2
tg_selected = Text(total_grade_info, height = 1, width = 5, state = DISABLED)
tg_selected.grid(row = 1, column = 2, padx = (5, 20), pady = (0, 10))

# GPA LF
gpa = LabelFrame(add_info_frame, text = 'GPA')
gpa.grid(row = 5, column = 0)

# Label
current_gpa_label = Label(gpa, text = 'Current GPA')
current_gpa_label.grid(row = 0, column = 0, padx = 20)

# Text box
current_gpa = Text(gpa, height = 1, width = 5, state = DISABLED)
current_gpa.grid(row = 0, column = 1, padx = 20, pady = 10)

display_gpa()

# Loops main window
main_win.mainloop()
