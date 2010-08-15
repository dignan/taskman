#! /usr/bin/python

import sys
import os
from xml.dom import minidom

try:  
    import pygtk  
    pygtk.require("2.0")  
except:  
    pass  
try:  
    import gtk 
except:  
    print("GTK Not Availible")
    sys.exit(1)
    
class taskstore:
    
    liststore = None
    default_file = "~/.taskman/tasks.xml"
    
    def __init__(self):
        self.liststore = gtk.ListStore(int, str, str)
        self.load()
        
    def add_row(self, row_data):
        self.liststore.append(row_data)
        
    def delete_row(self, row_ref):
        row_iter = self.liststore.get_iter(row_ref.get_path())
        self.liststore.remove(row_iter)
        
    def load(self, file_name=None):
        if file_name == None:
            file_name = os.path.expanduser(self.default_file)
        
        if not os.path.exists(file_name):
            return
        
        doc = minidom.parse(file_name)
        
        for task in doc.getElementsByTagName("task"):
            priority = None
            contents = None
            due_date = None
            
            for child in task.childNodes:
                if child.localName == "priority":
                    priority = child.firstChild.nodeValue.strip()
                elif child.localName == "contents":
                    contents = child.firstChild.nodeValue.strip()
                elif child.localName == "due_date":
                    due_date = child.firstChild.nodeValue.strip()
            
            self.liststore.append([int(priority), contents, due_date])                            

    def save(self, file_name=None):
        if file_name == None:
            file_name = os.path.expanduser(self.default_file)
        
        if not os.path.exists(os.path.dirname(file_name)):
            try:
                os.makedirs(os.path.dirname(file_name))
            except OSError as e:
                if e.errno == errno.EEXIST:
                    pass
                else: 
                    raise
        
        doc = minidom.Document()
        root = doc.createElement("tasks")
        doc.appendChild(root)
        
        row_iter = self.liststore.get_iter_first()
        while not row_iter == None:
            task_el = doc.createElement("task")
            priority_el = doc.createElement("priority")
            contents_el = doc.createElement("contents")
            due_date_el = doc.createElement("due_date")
            
            priority_val = doc.createTextNode(str(self.liststore.get_value(row_iter, 0)))
            contents_val = doc.createTextNode(self.liststore.get_value(row_iter, 1))
            due_date_val = doc.createTextNode(self.liststore.get_value(row_iter, 2))
            
            priority_el.appendChild(priority_val)
            contents_el.appendChild(contents_val)
            due_date_el.appendChild(due_date_val)
            
            task_el.appendChild(priority_el)
            task_el.appendChild(contents_el)
            task_el.appendChild(due_date_el)
            
            root.appendChild(task_el)
            row_iter = self.liststore.iter_next(row_iter)
        
        fd = open(file_name, 'w')
        doc.writexml(fd, "", "    ", "\n", "UTF-8")
                
    def get_model(self):
        return self.liststore

class taskman:

    months = {
        0 : 'January',
        1 : 'February',
        2 : 'March',
        3 : 'April',
        4 : 'May',
        5 : 'June',
        6 : 'July',
        7 : 'August',
        8 : 'September',
        9 : 'October',
        10 : 'November', 
        11 : 'December'
    }

    columns = [
        "Priority",
        "Task",
        "Due Date"
    ]
    
    store = None

    def __init__(self):
        settings = gtk.settings_get_default()
        settings.props.gtk_button_images = True

        self.builder = gtk.Builder()
        self.builder.add_from_file("taskman.ui")
        self.builder.connect_signals(self)
        
        self.store = taskstore()
        self.construct_table()
        
        main_window = self.builder.get_object("main_window")
        main_window.show()
        
        gtk.main()
        
    def construct_table(self):
        table = self.builder.get_object("tasks")
        table.set_model(self.store.get_model())
        table.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        
        self.priority_renderer = gtk.CellRendererText()
        table.get_column(0).pack_start(self.priority_renderer, False)
        table.get_column(0).add_attribute(self.priority_renderer, 'text', 0)
    
        self.task_renderer = gtk.CellRendererText()
        table.get_column(1).pack_start(self.task_renderer, True)
        table.get_column(1).add_attribute(self.task_renderer, 'text', 1)
        
        self.due_date_renderer = gtk.CellRendererText()
        table.get_column(2).pack_start(self.due_date_renderer, False)
        table.get_column(2).add_attribute(self.due_date_renderer, 'text', 2)
    
    def add_row(self, row_data):
        self.store.add_row(row_data)
        
    def delete_row (self, row_ref):
        self.store.delete_row(row_ref)
    
    def on_add_task_button_released(self, widget, data=None):
        self.dialog_builder = gtk.Builder()
        self.dialog_builder.add_from_file("taskman_dialog.ui")
        self.dialog_builder.connect_signals(self)
        
        self.dialog = self.dialog_builder.get_object("add_task_dialog")
        self.dialog.show()
        
    def on_quit_menuitem_activate_item(self, widget, data=None):
        self.quit(widget, data)
    
    def on_main_window_delete_event(self, widget, data=None):
        self.quit(widget, data)
        
    def on_main_window_destroy_event(self, widget, data=None):
        self.quit(widget, data)
        
    def on_task_dialog_cancel_button_released(self, widget, data=None):
        self.dialog.destroy()
        
    def on_task_dialog_ok_button_released(self, widget, data=None):
        text_entry = self.dialog_builder.get_object("task_text_entry")
        priority_spinner = self.dialog_builder.get_object("task_priority_spinner")
        calendar = self.dialog_builder.get_object("task_due_date_calendar")
        
        task = text_entry.get_text()
        priority = priority_spinner.get_value()
        due_date = calendar.get_date()
        
        due_date_str = self.months[due_date[1]] + " " + str(due_date[2]) + ", " + str(due_date[0])
        row_data = [priority, task, due_date_str]
        self.add_row(row_data)
        dialog = self.dialog_builder.get_object("add_task_dialog")
        dialog.destroy()    
        
    def on_about_menuitem_activate(self, widget, data=None):
        self.about_builder = gtk.Builder()
        self.about_builder.add_from_file("taskman_about.ui")
        self.about_builder.connect_signals(self)  
        
        self.about = self.about_builder.get_object("about_dialog")
        self.about.run() 
        self.about.destroy()
    
    def on_delete_task_button_released(self, widget, data=None):
        table = self.builder.get_object("tasks")
        selection = table.get_selection()
        
        if not selection.count_selected_rows() <= 0:
            model, rows = selection.get_selected_rows()
            row_refs = []
            
            for row in rows:
                row_refs.append(gtk.TreeRowReference(model, row))
            
            for row in row_refs:
                self.delete_row(row)
    
    def on_save_menuitem_activate(self, widget, data=None):
        self.store.save()
    
    def quit(self, widget, data=None):
        gtk.main_quit()
        
if __name__ == "__main__":
    prog = taskman()
