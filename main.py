import os.path
import sqlite3
import tkinter as tk
from tkinter import messagebox
import re


# клас для роботи з табличкою Users
class Users(object):
    def __init__(self, id, user_name, password, is_admin, password_type_id, created):
        self.id = id
        self.user_name = user_name
        self.password = password
        self.is_admin = is_admin
        self.password_type_id = password_type_id
        self.created = created


# функція для роботи з файлами
def read_file(file_name):
    with open(file_name) as file:
        return file.read().strip()


# сторінка для авторизації
class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        show_users_btn = tk.Button(self, text="Список користувачів", font=("Arial", 12), command=self.show_users)
        show_users_btn.pack(side="top")

        border = tk.LabelFrame(self, text='Вхід', bg='ivory', bd=10, font=("Arial", 20))
        border.pack(fill="both", expand="yes", padx=150, pady=150)

        tk.Label(border, text="Логін", font=("Arial Bold", 15), bg='ivory').place(x=50, y=20)
        self.username_entry = tk.Entry(border, width=30, bd=5)
        self.username_entry.place(x=180, y=20)

        tk.Label(border, text="Пароль", font=("Arial Bold", 15), bg='ivory').place(x=50, y=80)
        self.password_entry = tk.Entry(border, width=30, show='*', bd=5)
        self.password_entry.place(x=180, y=80)

        b1 = tk.Button(border, text="Підтвердити", font=("Arial", 12), command=self.verify)
        b1.place(x=372, y=90)

    def show_users(self):
        with sqlite3.connect("Sqlite.sqlite3") as db:
            cursor = db.cursor()
            select_query = read_file("Resourсe/SelectAllFromUsers.txt")
            cursor.execute(select_query)

            user_list = []
            for row in cursor:
                user = Users(*row)
                user_list.append(user.user_name)

            # Показати список імен користувачів у новому вікні
            user_list_window = tk.Toplevel(self)
            user_list_window.title("Список користувачів")
            user_list_window.geometry("300x300")

            # Створити список для відображення імен користувачів
            user_listbox = tk.Listbox(user_list_window)
            user_listbox.pack(expand=True, fill="both")

            # Додати імена користувачів до списку
            for user in user_list:
                user_listbox.insert("end", user)

    # очищення вікна
    def clear_entries(self):
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)

    # метод для верифікації користувача
    def verify(self):
        with sqlite3.connect("Sqlite.sqlite3") as db:
            cursor = db.cursor()
            select_query = read_file("Resourсe/SelectAllFromUsers.txt")
            cursor.execute(select_query)

            for row in cursor:
                user = Users(*row)
                if user.user_name == self.username_entry.get() and user.password == self.password_entry.get():
                    self.controller.shared_data["username"].set(user.user_name)
                    self.controller.show_frame(AdminMainPage if user.is_admin else MainPage)
                    self.clear_entries()
                    return

            messagebox.showerror("Помилка", "Будь ласка перевірте правильність логіну і паролю!!")
            self.clear_entries()


# сторінка користувача
class MainPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        tk.Label(self, textvariable=self.controller.shared_data["username"], font=('Helvetica', 18, "bold")).pack(
            side="top", fill="x", pady=5)
        button = tk.Button(self, text="Вихід", font=("Arial", 15),
                           command=lambda: [self.controller.shared_data["username"].set(''),
                                            controller.show_frame(LoginPage)])
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
                            command=lambda: controller.show_frame(LoginPage))
        button3.place(x=730, y=450)


# сторінка для створення коритувачів
class CreateUsersPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        tk.Label(self, text="Створення користувачів", font=('Helvetica', 18, "bold")).pack(side="top", fill="x", pady=5)
        l1 = tk.Label(self, text="Створити логін", font=("Arial Bold", 15), bg='ivory')
        l1.place(x=50, y=50)
        self.user_name_entry = tk.Entry(self, width=30, bd=5)
        self.user_name_entry.place(x=250, y=50)

        l2 = tk.Label(self, text="Створити пароль", font=("Arial Bold", 15), bg='ivory')
        l2.place(x=50, y=100)
        self.user_password_entry = tk.Entry(self, width=30, bd=5)
        self.user_password_entry.place(x=250, y=100)

        self.password_option = tk.IntVar()
        self.password_option.set(1)
        r1 = tk.Radiobutton(self, text="Простий пароль", font=("Arial Bold", 10), variable=self.password_option,
                            value=1)
        r1.place(x=50, y=140)

        r2 = tk.Radiobutton(self, text="Складний пароль", font=("Arial Bold", 10), variable=self.password_option,
                            value=2)
        r2.place(x=200, y=140)

        self.result_label = tk.Label(self)

        button1 = tk.Button(self, text="Підтвердити", font=("Arial", 15),
                            command=self.create_user)
        button1.place(x=160, y=180)

        button2 = tk.Button(self, text="Назад", font=("Arial", 15),
                            command=self.forget_label)
        button2.place(x=722, y=450)

    # метод який створює користувача
    def create_user(self):
        self.result_label.place(x=475, y=75)
        with sqlite3.connect("Sqlite.sqlite3") as db:

            cursor = db.cursor()
            select_txt = "SELECT UserName FROM Users WHERE UserName = ?"
            cursor.execute(select_txt, (self.user_name_entry.get(),))
            if cursor.fetchone() is not None:
                self.password_option.set(1)
                self.result_label.config(text="Користувач з таким логіном вже існує, введіть інший!", fg="red")
                self.clear_entries()

            elif not self.user_name_entry.get() or not self.user_password_entry.get():
                self.result_label.config(text="Будь ласка введіть логін і пароль!", fg="red")

            if self.password_option.get() == 2 and self.user_name_entry != '' and self.user_password_entry != '':
                select_txt1 = f"SELECT ValidationRegex FROM PaswordTypes WHERE Id={self.password_option.get()}"
                cursor.execute(select_txt1)
                pattern = ''.join(pat[0] for pat in cursor)
                # перевірка дотримання умов складного паролю
                if re.match(rf"{pattern}", self.user_password_entry.get()) is None:
                    self.result_label.config(text=f"Пароль має не вірний формат!", fg="red")
                    self.user_password_entry.delete(0, tk.END)

                else:
                    select_txt2 = f"INSERT INTO users(UserName, Password, PasswordTypeId) VALUES('{self.user_name_entry.get()}', '{self.user_password_entry.get()}', {self.password_option.get()})"
                    cursor.execute(select_txt2)
                    db.commit()
                    self.result_label.config(text=f"Користувача {self.user_name_entry.get()} успішно створено!",
                                             fg="green")
                    self.clear_entries()

            if self.password_option.get() == 1 and self.user_name_entry.get() != '' and self.user_password_entry.get() != '':
                select_txt3 = f"INSERT INTO users(UserName, Password, PasswordTypeId) VALUES('{self.user_name_entry.get()}', '{self.user_password_entry.get()}', {self.password_option.get()})"
                cursor.execute(select_txt3)
                db.commit()
                self.result_label.config(text=f"Користувача {self.user_name_entry.get()} успішно створено!", fg="green")
                self.clear_entries()

    # очищення вікна
    def clear_entries(self):
        self.user_name_entry.delete(0, tk.END)
        self.user_password_entry.delete(0, tk.END)

    def forget_label(self):
        self.result_label.place_forget()
        self.clear_entries()
        self.password_option.set(1)
        self.controller.show_frame(AdminMainPage)


# сторінка для редагування пароля в конкретного користувача
class EditUsersPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        tk.Label(self, text="Редагування паролю для користувача", font=('Helvetica', 18, "bold")).pack(side="top",
                                                                                                       fill="x", pady=5)

        l1 = tk.Label(self, text="Введіть ім'я користувача", font=("Arial Bold", 15), bg='ivory')
        l1.place(x=50, y=50)
        self.t1 = tk.Entry(self, width=30, bd=5)
        self.t1.place(x=350, y=50)

        l2 = tk.Label(self, text="Введіть новий пароль", font=("Arial Bold", 15), bg='ivory')
        l2.place(x=50, y=100)
        self.t2 = tk.Entry(self, width=30, bd=5)
        self.t2.place(x=350, y=100)

        self.password_option = tk.IntVar()
        self.password_option.set(0)
        r1 = tk.Radiobutton(self, text="Простий пароль", font=("Arial Bold", 10), variable=self.password_option, value=1)
        r1.place(x=50, y=140)

        r2 = tk.Radiobutton(self, text="Складний пароль", font=("Arial Bold", 10), variable=self.password_option, value=2)
        r2.place(x=200, y=140)

        button1 = tk.Button(self, text="Підтвердити", font=("Arial", 15),
                            command=self.change_users_parameters)
        button1.place(x=160, y=180)

        button = tk.Button(self, text="Назад", font=("Arial", 15), command=lambda: controller.show_frame(AdminMainPage))
        button.place(x=722, y=450)

    # метод для зміни паролю
    def change_users_parameters(self):
        with sqlite3.connect("Sqlite.sqlite3") as db:
            cursor = db.cursor()

            user_name_entry = self.t1.get()
            new_user_password = self.t2.get()
            select_txt1 = "SELECT UserName FROM users"
            cursor.execute(select_txt1)
            i = 1
            for name in cursor:
                if name[0] == user_name_entry:
                    i = 0
                    select_txt2 = f'UPDATE users SET Password = "{new_user_password}", PasswordTypeId = {self.password_option.get()} WHERE UserName = "{user_name_entry}"'
                    if self.password_option.get() == 1:
                        cursor.execute(select_txt2)
                        db.commit()
                        messagebox.showinfo('Готово', f'Встановлено новий пароль для користувача - {user_name_entry}')
                        self.t1.delete(0, tk.END)
                        self.t2.delete(0, tk.END)
                    elif self.password_option.get() == 2:
                        select_txt = f"SELECT ValidationRegex FROM PaswordTypes WHERE Id={self.password_option.get()}"
                        cursor.execute(select_txt)
                        pattern = ''.join(pat[0] for pat in cursor)
                        if re.match(rf"{pattern}", new_user_password) is None:
                            messagebox.showerror('Помилка', 'Пароль має не вірний формат!')
                            self.t2.delete(0, tk.END)
                        else:
                            cursor.execute(select_txt2)
                            db.commit()
                            messagebox.showinfo('Готово', f'Встановлено новий пароль для користувача - {user_name_entry}')
                            self.t1.delete(0, tk.END)
                            self.t2.delete(0, tk.END)
                    else:
                        messagebox.showinfo('Нагадування', 'Виберіть один з режимів складності для паролю!')
            if i:
                messagebox.showerror('Помилка', 'Такого користувача не існує!')
                self.t1.delete(0, tk.END)
                self.t2.delete(0, tk.END)


# головний клас додатку
class Application(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        # зберігання змінних
        self.shared_data = {
            "username": tk.StringVar(),
        }

        # створення вікна
        window = tk.Frame(self)
        window.pack()

        window.grid_rowconfigure(0, minsize=500)
        window.grid_columnconfigure(0, minsize=800)
        # загрузка фреймів
        self.frames = {}
        for F in (LoginPage, MainPage, AdminMainPage, CreateUsersPage, EditUsersPage):
            frame = F(window, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame(LoginPage)

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
        db.executescript(read_file("Resourсe/CreateTabels.txt"))
        db.close()
    app.mainloop()


# точка входу в програму
if __name__ == '__main__':
    main()
