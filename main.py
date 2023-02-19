import os.path
import sqlite3
import tkinter as tk
from tkinter import messagebox
import re


# клас для роботи з табличкою Users
class Users(object):
    def __init__(self, i_d, user_name, password, is_admin, password_type_id, created):
        self.i_d = i_d
        self.user_name = user_name
        self.password = password
        self.is_admin = is_admin
        self.password_type_id = password_type_id
        self.created = created


# функція для роботи з файлами
def parser_files(file_name):
    res = ''
    with open(file_name) as file_text:
        for line in file_text:
            line = line.rstrip('\n')
            res += line
    return res


# сторінка для авторизації
class LogPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        border = tk.LabelFrame(self, text='Вхід', bg='ivory', bd=10, font=("Arial", 20))
        border.pack(fill="both", expand="yes", padx=150, pady=150)

        l1 = tk.Label(border, text="Логін", font=("Arial Bold", 15), bg='ivory')
        l1.place(x=50, y=20)
        t1 = tk.Entry(border, width=30, bd=5)
        t1.place(x=180, y=20)

        l2 = tk.Label(border, text="Пароль", font=("Arial Bold", 15), bg='ivory')
        l2.place(x=50, y=80)
        t2 = tk.Entry(border, width=30, show='*', bd=5)
        t2.place(x=180, y=80)

        # очищення вікна
        def clear_screen():
            t1.delete(0, tk.END)
            t2.delete(0, tk.END)

        # метод для верифікації користувача
        def verify():
            i = 0
            db = sqlite3.connect("Sqlite.sqlite3")
            cursor = db.cursor()
            select_txt = parser_files("Resourсe/SelectAllFromUsers.txt")
            cursor.execute(select_txt)
            for row in cursor:
                all_row = Users(*row)
                if all_row.user_name == t1.get() and all_row.password == t2.get():
                    if all_row.is_admin:
                        controller.shared_data["username"].set(all_row.user_name)
                        controller.show_frame(AdminMainPage)
                        clear_screen()
                    else:
                        controller.shared_data["username"].set(all_row.user_name)
                        controller.show_frame(MainPage)
                        clear_screen()
                    i = 1
                    break
            if i == 0:
                messagebox.showinfo("Помилка", "Будь ласка перевірте правильність логіну і паролю!!")
                clear_screen()
            db.close()

        b1 = tk.Button(border, text="Підтвердити", font=("Arial", 15), command=verify)
        b1.place(x=350, y=115)


# сторінка користувача
class MainPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        tk.Label(self, textvariable=self.controller.shared_data["username"], font=('Helvetica', 18, "bold")).pack(
            side="top", fill="x", pady=5)
        button = tk.Button(self, text="Вихід", font=("Arial", 15),
                           command=lambda: controller.show_frame(LogPage))
        button.place(x=730, y=450)


# сторінка адміна
class AdminMainPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        tk.Label(self, textvariable=self.controller.shared_data["username"], font=('Helvetica', 18, "bold")).pack(
            side="top", fill="x", pady=5)

        button1 = tk.Button(self, text="Створити користувача", font=("Arial", 15),
                            command=lambda: controller.show_frame(CreateUsersPage))
        button1.place(x=100, y=60)

        button2 = tk.Button(self, text="Редагувати користувача", font=("Arial", 15),
                            command=lambda: controller.show_frame(EditUsersPage))
        button2.place(x=450, y=60)

        button3 = tk.Button(self, text="Вихід", font=("Arial", 15),
                            command=lambda: controller.show_frame(LogPage))
        button3.place(x=730, y=450)


# сторінка для створення коритувачів
class CreateUsersPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        tk.Label(self, text="Створення користувачів", font=('Helvetica', 18, "bold")).pack(side="top", fill="x", pady=5)
        l1 = tk.Label(self, text="Створити логін", font=("Arial Bold", 15), bg='ivory')
        l1.place(x=50, y=50)
        t1 = tk.Entry(self, width=30, bd=5)
        t1.place(x=250, y=50)

        l2 = tk.Label(self, text="Створити пароль", font=("Arial Bold", 15), bg='ivory')
        l2.place(x=50, y=100)
        t2 = tk.Entry(self, width=30, bd=5)
        t2.place(x=250, y=100)

        password_option = tk.IntVar()
        password_option.set(1)
        r1 = tk.Radiobutton(self, text="Простий пароль", font=("Arial Bold", 10), variable=password_option, value=1)
        r1.place(x=50, y=140)

        r2 = tk.Radiobutton(self, text="Складний пароль", font=("Arial Bold", 10), variable=password_option, value=2)
        r2.place(x=200, y=140)

        # метод який створює користувача
        def create_users():

            if controller.shared_data["del_label"].get() == 1:
                result_label.place(x=475, y=75)

            db = sqlite3.connect("Sqlite.sqlite3")
            cursor = db.cursor()

            user_name = t1.get()
            user_password = t2.get()

            select_txt = "SELECT UserName FROM Users"
            cursor.execute(select_txt)
            for user in cursor:
                if user[0] == user_name:
                    password_option.set(0)
                    t1.delete(0, tk.END)
                    t2.delete(0, tk.END)
                    break

            if password_option.get() == 2 and user_name != '' and user_password != '':
                select_txt1 = parser_files("Resourсe/ValidationRegex.txt")
                cursor.execute(select_txt1)
                pattern = ''
                for pat in cursor:
                    pattern += pat[0]
                # перевірка дотримання умов складного паролю
                if re.match(rf"{pattern}", user_password) is None:
                    result_label.config(text=f"Пароль має не вірний формат!", fg="red")
                    t2.delete(0, tk.END)
                else:
                    select_txt2 = f"INSERT INTO users(UserName, Password, PasswordTypeId) VALUES('{user_name}', '{user_password}', 2)"
                    cursor.execute(select_txt2)
                    db.commit()
                    db.close()
                    result_label.config(text=f"Користувача {t1.get()} успішно створено!", fg="green")
                    t1.delete(0, tk.END)
                    t2.delete(0, tk.END)
            if password_option.get() == 1 and user_name != '' and user_password != '':
                select_txt3 = f"INSERT INTO users(UserName, Password, PasswordTypeId) VALUES('{user_name}', '{user_password}', 1)"
                cursor.execute(select_txt3)
                db.commit()
                db.close()
                result_label.config(text=f"Користувача {t1.get()} успішно створено!", fg="green")
                t1.delete(0, tk.END)
                t2.delete(0, tk.END)
            if password_option.get() == 0:
                result_label.place_forget()
                password_option.set(1)
                messagebox.showinfo("Помилка", "Користувач з таким логіном вже існує, введіть інший!")
            if user_name == '' or user_password == '':
                result_label.place_forget()
                messagebox.showinfo("Помилка", "Будь ласка введіть логін і пароль!")

        def forget_label():
            result_label.place_forget()
            controller.show_frame(AdminMainPage)

        result_label = tk.Label(self)

        button1 = tk.Button(self, text="Підтвердити", font=("Arial", 15),
                            command=create_users)
        button1.place(x=160, y=180)

        button2 = tk.Button(self, text="Назад", font=("Arial", 15),
                            command=forget_label)
        button2.place(x=722, y=450)


# сторінка для редагування пароля в конкретного користувача
class EditUsersPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        tk.Label(self, text="Редагування паролю для користувача", font=('Helvetica', 18, "bold")).pack(side="top",
                                                                                                       fill="x", pady=5)

        l1 = tk.Label(self, text="Введіть ім'я користувача", font=("Arial Bold", 15), bg='ivory')
        l1.place(x=50, y=50)
        t1 = tk.Entry(self, width=30, bd=5)
        t1.place(x=350, y=50)

        l2 = tk.Label(self, text="Введіть новий пароль", font=("Arial Bold", 15), bg='ivory')
        l2.place(x=50, y=100)
        t2 = tk.Entry(self, width=30, bd=5)
        t2.place(x=350, y=100)

        password_option = tk.IntVar()
        password_option.set(0)
        r1 = tk.Radiobutton(self, text="Простий пароль", font=("Arial Bold", 10), variable=password_option, value=1)
        r1.place(x=50, y=140)

        r2 = tk.Radiobutton(self, text="Складний пароль", font=("Arial Bold", 10), variable=password_option, value=2)
        r2.place(x=200, y=140)

        # метод для зміни паролю
        def change_users_parameters():
            db = sqlite3.connect("Sqlite.sqlite3")
            cursor = db.cursor()

            user_name = t1.get()
            new_user_password = t2.get()
            select_txt1 = "SELECT UserName FROM users"
            cursor.execute(select_txt1)
            i = 1
            for name in cursor:
                if name[0] == user_name:
                    i = 0
                    select_txt2 = f'UPDATE users SET Password = "{new_user_password}", PasswordTypeId = {password_option.get()} WHERE UserName = "{user_name}"'
                    if password_option.get() == 1:
                        cursor.execute(select_txt2)
                        db.commit()
                        messagebox.showinfo('Готово', f'Встановлено новий пароль для користувача - {user_name}')
                        t1.delete(0, tk.END)
                        t2.delete(0, tk.END)
                    elif password_option.get() == 2:
                        select_txt = parser_files("Resourсe/ValidationRegex.txt")
                        cursor.execute(select_txt)
                        pattern = ''
                        for pat in cursor:
                            pattern += pat[0]
                        if re.match(rf"{pattern}", new_user_password) is None:
                            messagebox.showinfo('Помилка', 'Пароль має не вірний формат!')
                            t2.delete(0, tk.END)
                        else:
                            cursor.execute(select_txt2)
                            db.commit()
                            messagebox.showinfo('Готово', f'Встановлено новий пароль для користувача - {user_name}')
                            t1.delete(0, tk.END)
                            t2.delete(0, tk.END)
                    else:
                        messagebox.showinfo('Нагадування', 'Виберіть один з режимів складності для паролю!')
            if i:
                messagebox.showinfo('Помилка', 'Такого користувача не існує!')
            db.close()

        button1 = tk.Button(self, text="Підтвердити", font=("Arial", 15),
                            command=change_users_parameters)
        button1.place(x=160, y=180)

        button = tk.Button(self, text="Назад", font=("Arial", 15), command=lambda: controller.show_frame(AdminMainPage))
        button.place(x=722, y=450)


# головний клас додатку
class Application(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        # зберігання змінних
        self.shared_data = {
            "username": tk.StringVar(),
            "del_label": tk.IntVar(),
        }

        # створення вікна
        window = tk.Frame(self)
        window.pack()

        self.shared_data["del_label"].set(1)

        window.grid_rowconfigure(0, minsize=500)
        window.grid_columnconfigure(0, minsize=800)
        # загрузка фреймів
        self.frames = {}
        for F in (LogPage, MainPage, AdminMainPage, CreateUsersPage, EditUsersPage):
            frame = F(window, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame(LogPage)

    # метод зміни фреймів
    def show_frame(self, page):
        frame = self.frames[page]
        frame.tkraise()


def main():
    app = Application()
    app.title('ТБД_Білецький')
    app.geometry("800x500")
    app.resizable(width=False, height=False)
    main_menu = tk.Menu(app)
    app.config(menu=main_menu)
    file_menu = tk.Menu(main_menu)
    main_menu.add_cascade(label="Про автора", menu=file_menu)
    file_menu.add_command(label="БІ-442, Білецький Дмитро")
    # перевірка на існування БД
    if os.path.isfile('Sqlite.sqlite3'):
        pass
    else:
        db = sqlite3.connect("Sqlite.sqlite3")
        db.executescript(parser_files("Resourсe/CreateTabels.txt"))
        db.close()
    app.mainloop()


# точка входу в програму
if __name__ == '__main__':
    main()
