import os.path
import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import re
from PIL import Image, ImageTk
import subprocess


# клас для роботи з табличкою Users
class Users(object):
    def __init__(self, id, user_name, password, is_admin, password_type_id, user_access_level_id, mod, created):
        self.id = id
        self.user_name = user_name
        self.password = password
        self.is_admin = is_admin
        self.password_type_id = password_type_id
        self.user_access_level_id = user_access_level_id
        self.mod = mod
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

        top_frame = tk.Frame(self)
        top_frame.pack(side="top", fill="x")

        tk.Label(top_frame, text="Користувач:", font=('Helvetica', 12)).pack(side="left", padx=10)
        tk.Label(top_frame, textvariable=self.controller.shared_data["username"], font=('Helvetica', 12, "bold")).pack(
            side="left")

        open_button = tk.Button(self, text="Вибрати файл", font=("Arial", 12), command=self.open_file)
        open_button.place(x=10, y=30)

        self.file_name = tk.Label(self, text="Виберіть файл!", font=("Arial", 12))
        self.file_name.place(x=130, y=35)

        self.save_txt_button = tk.Button(self, text='Зберегти текстовий файл', font=("Arial", 12),
                                         command=self.save_file)

        self.save_img_button = tk.Button(self, text='Зберегти зображення', font=("Arial", 12), command=self.save_image)

        self.run_button = tk.Button(self, text="Запустити програму", font=("Arial", 12), command=self.run_exe,
                                    bg='green')

        self.rotate_button = tk.Button(self, text="Перевернути зображення", command=self.rotate_image)

        self.text = tk.Text(self, width=55, height=20)

        self.canvas = tk.Canvas(self, width=450, height=350, bd=1, relief='solid', highlightthickness=1,
                                highlightbackground='black')

        self.file_path = None
        self.image = None
        self.canvas_image = None

        button = tk.Button(self, text="Вихід", font=("Arial", 15),
                           command=lambda: [self.controller.shared_data["username"].set(''), self.forget_elements(),
                                            self.run_button.place_forget(),
                                            self.file_name.config(text="Файл не вибрано!", fg="black"),
                                            controller.show_frame(LoginPage)])
        button.place(x=730, y=450)

    def forget_elements(self):
        self.canvas.place_forget()
        self.text.place_forget()
        self.save_txt_button.place_forget()
        self.save_img_button.place_forget()
        self.rotate_button.place_forget()

    def open_file(self):
        with sqlite3.connect("Sqlite.sqlite3") as db:
            cursor = db.cursor()
            self.file_path = filedialog.askopenfilename(
                initialdir="D:\IV-курс\ІІ-семестр\Технології безпечного доступу\TBD_Biletskyi\Data")
            file_path1 = self.file_path.split("/")
            select_txt = f"SELECT UserAccessLevelId, Mod FROM Users WHERE UserName = '{self.controller.shared_data['username'].get()}';"
            cursor.execute(select_txt)
            row = cursor.fetchone()
            if row is not None:
                user_access_level_id = row
            if user_access_level_id[0] < 2:
                self.file_name.config(text="Вас заблоковано!", fg='red')
                return
            select_txt2 = f"SELECT FileAccessLevelId FROM Files WHERE FileName = '{file_path1[-1]}'"
            cursor.execute(select_txt2)
            row = cursor.fetchone()
            if row is not None:
                file_access_level_id = row
            else:
                self.file_name.config(text="Файл не вибрано!", fg='red')
                messagebox.showerror("Помилка", "Невідомий файл!")
                return
            if user_access_level_id[0] < file_access_level_id[0]:
                messagebox.showerror("Помилка", "Ви не маєте доступу до цього файлу!")
                return
            else:
                self.file_name.config(
                    text=f"Вибрано файл - {file_path1[-1]} ({', '.join(user_access_level_id[1].split(', '))})",
                    fg='black')
                if file_path1[-1].split(".")[-1] == "txt":
                    self.canvas.place_forget()
                    self.rotate_button.place_forget()
                    self.save_img_button.place_forget()
                    self.text.place(x=200, y=100)
                    if "w" in user_access_level_id[1].split(", "):
                        self.save_txt_button.place(x=370, y=440)
                    else:
                        if "e" in user_access_level_id[1].split(", "):
                            self.forget_elements()
                            messagebox.showerror("Помилка",
                                                 "Ви не маєте право на читання чи редагування даного файлу! Ви лише можете запускати виконуванні файли!")
                            return
                        else:
                            self.save_txt_button.place_forget()

                    with open(self.file_path, 'r', encoding='utf-8') as file:
                        file_contents = file.read()
                        self.text.delete(1.0, tk.END)
                        self.text.insert(tk.END, file_contents)
                elif file_path1[-1].split(".")[-1] == "jpg":
                    self.save_txt_button.place_forget()
                    self.text.place_forget()
                    self.canvas.place(x=200, y=80)
                    if "w" in user_access_level_id[1].split(", "):
                        self.rotate_button.place(x=650, y=250)
                        self.save_img_button.place(x=370, y=440)
                    else:
                        if "e" in user_access_level_id[1].split(", "):
                            self.forget_elements()
                            messagebox.showerror("Помилка",
                                                 "Ви не маєте право на читання чи редагування даного файлу! Ви лише можете запускати виконуванні файли!")
                            return
                    if self.file_path:
                        # завантаження зображення використовуючи бібліотеку Pillow
                        self.image = Image.open(self.file_path)
                        # показати зображення в canvas
                        self.canvas_image = ImageTk.PhotoImage(self.image)
                        self.canvas.create_image(0, 0, image=self.canvas_image, anchor="nw")
                elif file_path1[-1].split(".")[-1] == "exe":
                    if "e" in user_access_level_id[1].split(", "):
                        self.forget_elements()
                        self.run_button.place(x=365, y=250)
                    else:
                        self.forget_elements()
                        messagebox.showerror("Помилка", "Ви не маєте право запускати цей файл!")
                        return
                else:
                    messagebox.showerror("Помилка",
                                         "Вибрано невідомий файл! Можна вибирати файли з наступними розширеннями: .txt, .jpg, .exe")

    # Збереження файлу
    def save_file(self):
        if not self.file_path:
            messagebox.showerror("Помилка",
                                 "Спочатку виберіть файл")
            return
        with open(self.file_path, 'w', encoding='utf-8') as file:
            file.write(self.text.get(1.0, tk.END))
            messagebox.showinfo("Готово", "Файл успішно редагований та збережений!")

    # Збереження картинки
    def save_image(self):
        if not self.file_path:
            messagebox.showerror("Помилка",
                                 "Спочатку виберіть файл")
            return
        self.image.save(self.file_path)
        messagebox.showinfo("Готово", "Зображення успішно редаговане та збережене!")

    # Перевернення картинки на 90 градусів
    def rotate_image(self):
        self.image = self.image.rotate(-90)
        self.canvas_image = ImageTk.PhotoImage(self.image)
        self.canvas.create_image(0, 0, image=self.canvas_image, anchor="nw")

    # Запуск виконуваного файлу
    def run_exe(self):
        if not self.file_path:
            messagebox.showerror("Помилка",
                                 "Спочатку виберіть файл")
            return
        subprocess.Popen(["cmd", "/c", self.file_path], stdout=subprocess.PIPE)


# сторінка адміна
class AdminMainPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        tk.Label(self, textvariable=self.controller.shared_data["username"], font=('Helvetica', 18, "bold")).pack(
            side="top", fill="x", pady=5)

        button1 = tk.Button(self, text="Створити нового користувача", font=("Arial", 13),
                            command=lambda: controller.show_frame(CreateUsersPage))
        button1.place(x=100, y=60)

        button2 = tk.Button(self, text="Редагувати користувача", font=("Arial", 13),
                            command=lambda: controller.show_frame(EditMenuPage))
        button2.place(x=460, y=60)

        button3 = tk.Button(self, text="Додати новий ресурс до системи", font=("Arial", 13),
                            command=lambda: controller.show_frame(AddNewFilePage))
        button3.place(x=100, y=120)

        button4 = tk.Button(self, text="Вихід", font=("Arial", 15),
                            command=lambda: controller.show_frame(LoginPage))
        button4.place(x=730, y=450)


class AddNewFilePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        tk.Label(self, text="Додавання нового файлу", font=('Helvetica', 18, "bold")).pack(side="top",
                                                                                           fill="x", pady=5)
        l1 = tk.Label(self, text="Назва файлу з розширенням", font=("Arial Bold", 12), bg='ivory')
        l1.place(x=50, y=50)
        self.file_name_entry = tk.Entry(self, width=30, bd=5)
        self.file_name_entry.place(x=320, y=50)

        l2 = tk.Label(self, text="Виберіть мітку конфіденційності:", font=("Arial Bold", 12), bg='ivory')
        l2.place(x=50, y=110)

        self.combo_box = ttk.Combobox(self,
                                      values=["Not secretly",
                                              "Secretly",
                                              "Completely secret",
                                              "Of particular importance",
                                              ], width=24, state="readonly")
        self.combo_box.set("Not secretly")
        self.combo_box.place(x=340, y=110)

        button1 = tk.Button(self, text="Підтвердити", font=("Arial", 15),
                            command=self.change_user_access)
        button1.place(x=250, y=170)

        button = tk.Button(self, text="Назад", font=("Arial", 15), command=lambda: controller.show_frame(AdminMainPage))
        button.place(x=722, y=450)

    def change_user_access(self):

        with sqlite3.connect("Sqlite.sqlite3") as db:
            cursor = db.cursor()
            select_txt = "SELECT FileName FROM Files WHERE FileName = ?"
            cursor.execute(select_txt, (self.file_name_entry.get(),))

            if cursor.fetchone() is not None:
                self.file_name_entry.delete(0, tk.END)
                messagebox.showerror("Помилка", "Файл з такою назвою вже існує, введіть іншу!")

            elif self.file_name_entry.get() != '':
                combo = self.combo_box.get()
                query = f"INSERT INTO Files (FileName, FileAccessLevelId) SELECT '{self.file_name_entry.get()}', Id FROM AccessLevels WHERE AccessLevelName = '{combo}';"
                cursor.execute(query)
                db.commit()
                messagebox.showinfo('Готово',
                                    f'Додано новий файл - {self.file_name_entry.get()} з міткою конфіденційності - {combo}')
                self.file_name_entry.delete(0, tk.END)
                self.combo_box.set("Not secretly")
            else:
                messagebox.showerror('Помилка', 'Введіть назву файлу')


class EditMenuPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        tk.Label(self, text="Меню для редагування користувачів", font=('Helvetica', 18, "bold")).pack(side="top",
                                                                                                      fill="x", pady=5)

        button1 = tk.Button(self, text="1. Змінити пароль для користувача", font=("Arial", 12),
                            command=lambda: controller.show_frame(EditPasswordPage))
        button1.place(x=100, y=60)

        button2 = tk.Button(self, text="2. Змінити рівень доступу користувача", font=("Arial", 12),
                            command=lambda: controller.show_frame(EditAccessPage))
        button2.place(x=100, y=110)

        button3 = tk.Button(self, text="Вихід", font=("Arial", 15),
                            command=lambda: controller.show_frame(AdminMainPage))
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
                    select_txt2 = f"INSERT INTO users(UserName, Password, PasswordTypeId, UserAccessLevelId, Mod) VALUES('{self.user_name_entry.get()}', '{self.user_password_entry.get()}', {self.password_option.get()}, 2, 'r')"
                    cursor.execute(select_txt2)
                    db.commit()
                    self.result_label.config(text=f"Користувача {self.user_name_entry.get()} успішно створено!",
                                             fg="green")
                    self.clear_entries()

            if self.password_option.get() == 1 and self.user_name_entry.get() != '' and self.user_password_entry.get() != '':
                select_txt3 = f"INSERT INTO users(UserName, Password, PasswordTypeId, UserAccessLevelId, Mod) VALUES('{self.user_name_entry.get()}', '{self.user_password_entry.get()}', {self.password_option.get()}, 2, 'r')"
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
class EditPasswordPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        tk.Label(self, text="Редагування паролю для користувачів", font=('Helvetica', 18, "bold")).pack(side="top",
                                                                                                        fill="x",
                                                                                                        pady=5)

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
        r1 = tk.Radiobutton(self, text="Простий пароль", font=("Arial Bold", 10), variable=self.password_option,
                            value=1)
        r1.place(x=50, y=140)

        r2 = tk.Radiobutton(self, text="Складний пароль", font=("Arial Bold", 10), variable=self.password_option,
                            value=2)
        r2.place(x=200, y=140)

        button1 = tk.Button(self, text="Підтвердити", font=("Arial", 15),
                            command=self.change_users_parameters)
        button1.place(x=160, y=180)

        button = tk.Button(self, text="Назад", font=("Arial", 15), command=lambda: controller.show_frame(EditMenuPage))
        button.place(x=722, y=450)

    # метод для зміни паролю
    def change_users_parameters(self):
        with sqlite3.connect("Sqlite.sqlite3") as db:
            cursor = db.cursor()

            user_name_entry = self.t1.get()
            new_user_password = self.t2.get()

            select_txt = "SELECT UserName FROM users"
            cursor.execute(select_txt)
            i = 1
            for name in cursor:
                if name[0] == user_name_entry:
                    i = 0
                    query1 = f'UPDATE Users SET Password = "{new_user_password}", PasswordTypeId = {self.password_option.get()} WHERE UserName = "{user_name_entry}";'
                    if self.password_option.get() == 1:
                        cursor.execute(query1)
                        db.commit()
                        messagebox.showinfo('Готово',
                                            f'Встановлено новий пароль для користувача - {user_name_entry}')
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
                            cursor.execute(query1)
                            db.commit()
                            messagebox.showinfo('Готово',
                                                f'Встановлено новий пароль для користувача - {user_name_entry}')
                            self.t1.delete(0, tk.END)
                            self.t2.delete(0, tk.END)
                    else:
                        messagebox.showinfo('Нагадування', 'Виберіть один з режимів складності для паролю!')
            if i:
                messagebox.showerror('Помилка', 'Такого користувача не існує!')
                self.t1.delete(0, tk.END)
                self.t2.delete(0, tk.END)


class EditAccessPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        tk.Label(self, text="Редагування рівнів доступу для користувачів", font=('Helvetica', 18, "bold")).pack(
            side="top",
            fill="x", pady=5)

        l1 = tk.Label(self, text="Введіть ім'я користувача", font=("Arial Bold", 12), bg='ivory')
        l1.place(x=50, y=70)
        self.t1 = tk.Entry(self, width=30, bd=5)
        self.t1.place(x=325, y=70)

        l2 = tk.Label(self, text="Виберіть рівень доступу:", font=("Arial Bold", 12), bg='ivory')
        l2.place(x=50, y=120)

        self.combo_box = ttk.Combobox(self,
                                      values=[
                                          "Block",
                                          "Not secretly",
                                          "Secretly",
                                          "Completely secret",
                                          "Of particular importance",
                                      ], width=25, state="readonly")
        self.combo_box.set("Not secretly")
        self.combo_box.place(x=325, y=120)

        l3 = tk.Label(self, text="Виберіть можливості:", font=("Arial Bold", 12), bg='ivory')
        l3.place(x=50, y=170)

        self.mod = ttk.Combobox(self,
                                values=[
                                    "r",
                                    "r, w",
                                    "e",
                                    "r, w, e"
                                ], width=15, state="readonly")
        self.mod.set("r")
        self.mod.place(x=325, y=170)

        button1 = tk.Button(self, text="Підтвердити", font=("Arial", 15),
                            command=self.change_user_access)
        button1.place(x=250, y=215)

        button = tk.Button(self, text="Назад", font=("Arial", 15), command=lambda: controller.show_frame(EditMenuPage))
        button.place(x=722, y=450)

    def change_user_access(self):
        with sqlite3.connect("Sqlite.sqlite3") as db:
            cursor = db.cursor()
            select_query = read_file("Resourсe/SelectAllFromUsers.txt")
            cursor.execute(select_query)
            user_name_entry = self.t1.get()
            for row in cursor:
                user = Users(*row)
                if user.user_name == user_name_entry:
                    combo = self.combo_box.get()
                    query = f'UPDATE Users SET UserAccessLevelId = ( SELECT Id FROM AccessLevels WHERE AccessLevelName = "{combo}" ), Mod = "{self.mod.get()}" WHERE UserName = "{user_name_entry}";'
                    cursor.execute(query)
                    db.commit()
                    messagebox.showinfo('Готово',
                                        f'Встановлено новий рівень доступу для користувача - {user_name_entry}')
                    self.t1.delete(0, tk.END)
                    self.combo_box.set("Not secretly")
                    self.mod.set("r")
            if self.t1.get() != '':
                messagebox.showerror('Помилка', 'Такого користувача не існує!')


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
        for F in (LoginPage, MainPage, AdminMainPage, CreateUsersPage, EditPasswordPage, EditAccessPage, EditMenuPage,
                  AddNewFilePage):
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
