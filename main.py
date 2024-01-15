from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QGridLayout, \
     QLineEdit, QPushButton, QMainWindow, QTableWidget, QTableWidgetItem, QDialog, \
     QVBoxLayout, QComboBox,QToolBar,QStatusBar,QMessageBox
from PyQt6.QtGui import QAction,QIcon
import sys
import sqlite3


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")
        self.setMinimumSize(500,500)

        file_menu_item = self.menuBar().addMenu("&File")
        help_menu_item = self.menuBar().addMenu("&Help")
        edit_menu_item = self.menuBar().addMenu("&Edit")

        add_student_action = QAction(QIcon("add.png"),"Add Student", self)
        add_student_action.triggered.connect(self.insert)
        file_menu_item.addAction(add_student_action)

        about_action = QAction("About", self)
        help_menu_item.addAction(about_action)
        about_action.triggered.connect(self.about)

        search_action = QAction(QIcon("search.png"),"Search", self)
        edit_menu_item.addAction(search_action)
        search_action.triggered.connect(self.search)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("Id", "Name", "Course", "Mobile"))
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)

        #Create toolbar
        toolbar=QToolBar()
        toolbar.setMovable(True)
        self.addToolBar(toolbar)
        toolbar.addAction(add_student_action)
        toolbar.addAction(search_action)

        #Create status bar
        self.status_bar=QStatusBar()
        self.setStatusBar(self.status_bar)

        #Detect cell clicked
        self.table.cellClicked.connect(self.cell_clicked)


    def cell_clicked(self):
        edit_btn=QPushButton("Edit Record")
        edit_btn.clicked.connect(self.edit)
        delete_btn=QPushButton("Delete Record")
        delete_btn.clicked.connect(self.delete)
        children=self.findChildren(QPushButton)
        if children:
            for child in children:
                self.status_bar.removeWidget(child)

        self.status_bar.addWidget(edit_btn)
        self.status_bar.addWidget(delete_btn)

    def load_data(self):
        connection = sqlite3.connect("database.db")
        result = connection.execute("SELECT * FROM students")
        self.table.setRowCount(0)
        for row_number, row_data in enumerate(result):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))
        connection.close()

    def insert(self):
        dialog = InsertDialog()
        dialog.exec()

    def search(self):
        dialog = SearchDialog()
        dialog.exec()

    def edit(self):
        dialog=EditDialog()
        dialog.exec()

    def delete(self):
        dialog=DeleteDialog()
        dialog.exec()

    def about(self):
        dialog=AboutDialog()
        dialog.exec()


class AboutDialog(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")
        content="""This app was created to store Data of students using SQL database.This app is user friendly"""
        self.setText(content)



class EditDialog(QDialog):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Update Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()
        index=main_window.table.currentRow()

        # Update student id widget
        student_id=main_window.table.item(index,0).text()
        self.student_id = QLineEdit()
        self.student_id.setText(student_id)

        # Update student name widget
        student_name = main_window.table.item(index, 1).text()
        self.student_name = QLineEdit()
        self.student_name.setText(student_name)
        layout.addWidget(self.student_name)

        # Update combo box of courses
        course_name=main_window.table.item(index,2).text()
        self.course_name = QComboBox()
        courses = ["CSE", "COE", "ENC", "ECE","CHE","MEC"]
        self.course_name.addItems(courses)
        self.course_name.setCurrentText(course_name)
        layout.addWidget(self.course_name)

        # Update mobile widget
        mobile_no=main_window.table.item(index,3).text()
        self.mobile = QLineEdit()
        self.mobile.setText(mobile_no)
        layout.addWidget(self.mobile)

        # Add a Update button
        button = QPushButton("Update")
        button.clicked.connect(self.update_student)
        layout.addWidget(button)
        self.setLayout(layout)

    def update_student(self):
        connection=sqlite3.connect("database.db")
        cursor=connection.cursor()
        cursor.execute("UPDATE students SET name=?,course=?,mobile=? WHERE Id=?",
                       (self.student_name.text(),
                        self.course_name.itemText(self.course_name.currentIndex()),self.mobile.text(),
                        self.student_id.text()))
        connection.commit()
        cursor.close()
        connection.close()
        # Refresh the table
        main_window.load_data()


class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Delete Student Data")

        layout=QGridLayout()
        confirmation=QLabel("Are you sure you want to delete?")
        yes=QPushButton("Yes")
        no=QPushButton("No")

        layout.addWidget(confirmation,0,0,1,2)
        layout.addWidget(yes,1,0)
        layout.addWidget(no,1,1)
        self.setLayout(layout)
        yes.clicked.connect(self.delete_student)

    def delete_student(self):
        index=main_window.table.currentRow()
        student_id=main_window.table.item(index,0).text()

        connection=sqlite3.connect("database.db")
        cursor=connection.cursor()
        cursor.execute("DELETE FROM students WHERE Id=?",(student_id,))
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()
        self.close()
        confirmation_widget=QMessageBox()
        confirmation_widget.setWindowTitle("Success")
        confirmation_widget.setText("Record deleted Successfully!!")
        confirmation_widget.exec()


class InsertDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Insert Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Add student id widget
        self.student_id = QLineEdit()
        self.student_id.setPlaceholderText("ID")
        layout.addWidget(self.student_id)

        # Add student name widget
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Add combo box of courses
        self.course_name = QComboBox()
        courses = ["CSE", "COE", "ENC", "ECE","CHE","MEC"]
        self.course_name.addItems(courses)
        layout.addWidget(self.course_name)

        # Add mobile widget
        self.mobile = QLineEdit()
        self.mobile.setPlaceholderText("Mobile")
        layout.addWidget(self.mobile)

        # Add a submit button
        button = QPushButton("Register")
        button.clicked.connect(self.add_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def add_student(self):
        ID=self.student_id.text()
        name = self.student_name.text()
        course = self.course_name.itemText(self.course_name.currentIndex())
        mobile = self.mobile.text()
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("INSERT INTO students (Id,name, course, mobile) VALUES (?,?, ?, ?)",
                       (ID,name, course, mobile))
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()


class SearchDialog(QDialog):
    def __init__(self):
        super().__init__()
        # Set window title and size
        self.setWindowTitle("Search Student")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        # Create layout and input widget
        layout = QVBoxLayout()
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Create button
        button = QPushButton("Search")
        button.clicked.connect(self.search)
        layout.addWidget(button)

        self.setLayout(layout)

    def search(self):
        name = self.student_name.text()
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        result = cursor.execute("SELECT * FROM students WHERE name = ?", (name,))
        row = list(result)[0]
        print(row)
        items = main_window.table.findItems(name, Qt.MatchFlag.MatchFixedString)
        for item in items:
            print(item)
            main_window.table.item(item.row(), 1).setSelected(True)

        cursor.close()
        connection.close()


app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
main_window.load_data()
sys.exit(app.exec())