import os.path
import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import re
from PIL import Image, ImageTk
import subprocess
import datetime


# клас для роботи з табличкою Users
class Users(object):
    def __init__(self, id, user_name, password, is_admin, password_type_id, user_access_level_id, mod, access_model_id,
                 created):
        self.id = id
        self.user_name = user_name
        self.password = password
        self.is_admin = is_admin
        self.password_type_id = password_type_id
        self.user_access_level_id = user_access_level_id
        self.mod = mod
        self.access_model_id = access_model_id
        self.created = created

    def get_access_model_name(self):
        with sqlite3.connect("Sqlite.sqlite3") as db:
            cursor = db.cursor()
            select_query = f"SELECT ModelName FROM AccessModels WHERE Id={self.access_model_id}"
            cursor.execute(select_query)
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                return "Невідома модель"


class Files(object):
    def __init__(self, id, file_name, file_access_level_id, created):
        self.id = id
        self.file_name = file_name
        self.file_access_level_id = file_access_level_id
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

        border = tk.LabelFrame(self, text='Вхід', bg='ivory', bd=10, font=("Arial", 20))
        border.pack(fill="both", expand="yes", padx=150, pady=150)

        tk.Label(border, text="Логін", font=("Arial Bold", 15), bg='ivory').place(x=50, y=20)
        self.username_entry = tk.Entry(border, width=30, bd=5)
        self.username_entry.place(x=180, y=20)

        tk.Label(border, text="Пароль", font=("Arial Bold", 15), bg='ivory').place(x=50, y=80)
        self.password_entry = tk.Entry(border, width=30, show='*', bd=5)
        self.password_entry.place(x=180, y=80)

        b1 = tk.Button(border, text="Підтвердити", font=("Arial", 12), command=self.verify)
        b1.place(x=372, y=120)

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
        try:
            self.timer.pack_forget()
        except Exception:
            pass

    def open_file(self):
        with sqlite3.connect("Sqlite.sqlite3") as db:
            cursor = db.cursor()
            self.file_path = filedialog.askopenfilename(
                initialdir="D:\IV-курс\ІІ-семестр\Технології безпечного доступу\TBD_Biletskyi\Data")
            file_path1 = self.file_path.split("/")
            access_model_id_query = f"SELECT Id, AccessModelId FROM Users WHERE UserName = '{self.controller.shared_data['username'].get()}';"
            cursor.execute(access_model_id_query)
            for row in cursor:
                access_model = row
            if access_model[1] == 1:
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
            if access_model[1] == 2:
                try:
                    select_file_id = f"SELECT Id FROM Files WHERE FileName = '{file_path1[-1]}'"
                    cursor.execute(select_file_id)
                    for row in cursor:
                        file_id = row[0]
                    select_discretionary_matrix = f"SELECT FileId, ActionTypeId, AllowFrom, AllowTo FROM DiscretionaryMatrix WHERE UserId = {access_model[0]};"
                    cursor.execute(select_discretionary_matrix)
                    now = datetime.datetime.now()
                    time_now = now.strftime("%H:%M:%S")
                    for row in cursor:
                        if row[0] == file_id:
                            if row[2] <= time_now < row[3]:
                                self.allow_from = datetime.datetime.strptime(row[2], '%H:%M:%S').time()
                                self.allow_to = datetime.datetime.strptime(row[3], '%H:%M:%S').time()
                                self.remaining = None
                                select_action_type = f"SELECT ActionName FROM ActionTypes WHERE Id = {row[1]}"
                                cursor.execute(select_action_type)
                                for action_name in cursor:
                                    action_type = action_name[0].split(", ")
                                self.file_name.config(
                                    text=f"Вибрано файл - {file_path1[-1]} ({', '.join(action_type)})",
                                    fg='black')
                                if file_path1[-1].split(".")[-1] == "txt":
                                    self.delete_timer()
                                    self.create_widgets()
                                    self.canvas.place_forget()
                                    self.rotate_button.place_forget()
                                    self.save_img_button.place_forget()
                                    self.text.place(x=200, y=100)
                                    if "w" in action_type:
                                        self.save_txt_button.place(x=370, y=440)
                                    else:
                                        self.save_txt_button.place_forget()
                                    with open(self.file_path, 'r', encoding='utf-8') as file:
                                        file_contents = file.read()
                                        self.text.delete(1.0, tk.END)
                                        self.text.insert(tk.END, file_contents)
                                    return
                                elif file_path1[-1].split(".")[-1] == "jpg":
                                    self.delete_timer()
                                    self.create_widgets()
                                    self.save_txt_button.place_forget()
                                    self.text.place_forget()
                                    self.canvas.place(x=200, y=80)
                                    if "w" in action_type:
                                        self.rotate_button.place(x=650, y=250)
                                        self.save_img_button.place(x=370, y=440)
                                    else:
                                        self.rotate_button.place_forget()
                                        self.save_img_button.place_forget()
                                    if self.file_path:
                                        # завантаження зображення використовуючи бібліотеку Pillow
                                        self.image = Image.open(self.file_path)
                                        # показати зображення в canvas
                                        self.canvas_image = ImageTk.PhotoImage(self.image)
                                        self.canvas.create_image(0, 0, image=self.canvas_image, anchor="nw")
                                        return
                                elif file_path1[-1].split(".")[-1] == "exe":
                                    self.delete_timer()
                                    self.forget_elements()
                                    self.create_widgets()
                                    self.run_button.place(x=365, y=250)
                                    return
                                else:
                                    messagebox.showerror("Помилка",
                                                         "Вибрано невідомий файл! Можна вибирати файли з наступними розширеннями: .txt, .jpg, .exe")
                                    return
                            else:
                                messagebox.showerror("Помилка", f"Ви можете відкрити даний файл з {row[2]} по {row[3]}")
                                return
                    messagebox.showerror("Помилка", "Ви не маєте жодних прав до цього файлу!")
                except UnboundLocalError:
                    self.file_name.config(text="Файл не вибрано!", fg='red')
                    messagebox.showerror("Помилка", "Невідомий файл!")
                    return

    def create_widgets(self):
        self.top_frame = tk.Frame(self)
        self.top_frame.pack(side="top", fill="x")
        self.top_frame.lower()
        self.timer = tk.Label(self.top_frame, font=('Helvetica', 12))
        self.timer.pack(side="right", padx=10)

        self.update()

    def update(self):
        now = datetime.datetime.now().time()

        if now > self.allow_to:
            self.timer.config(text='Дозволений час вийшов.\nВихід з файлу.', fg='red')
            self.after(2000, self.exit_file)
        else:
            self.remaining = datetime.datetime.combine(datetime.date.today(),
                                                       self.allow_to) - datetime.datetime.combine(
                datetime.date.today(), now)
            self.remaining = str(self.remaining).split(".")[0]
            self.timer.config(text=f'Залишилось часу: {self.remaining}', fg='green')

            self.after(1000, self.update)

    def delete_timer(self):
        try:
            # Видалення всіх дочірніх елементів top_frame
            for child in self.top_frame.winfo_children():
                child.destroy()

            # Видалення самого top_frame
            self.top_frame.destroy()
        except AttributeError:
            pass

    def delete_frame_timer(self):
        try:
            # Видалення всіх дочірніх елементів top_frame
            for child in self.top_frame.winfo_children():
                child.destroy()
        except Exception:
            # Видалення самого top_frame
            self.top_frame.destroy()

    def exit_file(self):
        self.forget_elements()
        self.run_button.place_forget()
        self.delete_frame_timer()
        self.file_name.config(text="Файл не вибрано!", font=("Arial", 12))
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
                            command=self.change_file_access)
        button1.place(x=250, y=170)

        button = tk.Button(self, text="Назад", font=("Arial", 15), command=lambda: controller.show_frame(AdminMainPage))
        button.place(x=722, y=450)

    def change_file_access(self):

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

        button2 = tk.Button(self, text="2. Змінити модель доступу користувача", font=("Arial", 12),
                            command=lambda: controller.show_frame(EditAccessPage))
        button2.place(x=100, y=110)

        button3 = tk.Button(self, text="Назад", font=("Arial", 15),
                            command=lambda: controller.show_frame(AdminMainPage))
        button3.place(x=722, y=450)


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
        self.user_name_entry = ''

        tk.Label(self, text="Редагування моделей доступу для користувачів", font=('Helvetica', 14, "bold")).pack(
            side="top",
            fill="x", pady=5)

        self.l1 = tk.Label(self, text="Введіть ім'я користувача", font=("Arial Bold", 12), bg='ivory')
        self.l1.place(x=50, y=100)
        self.t1 = tk.Entry(self, width=30, bd=5)
        self.t1.place(x=325, y=100)

        self.model_type = tk.IntVar()
        self.model_type.set(0)

        self.l2 = tk.Label(self, text="Виберіть модель доступу:", font=("Arial Bold", 12), bg='ivory')
        self.l2.place(x=50, y=150)

        self.r1 = tk.Radiobutton(self, text="Мандатна", font=("Arial Bold", 10), variable=self.model_type,
                                 value=1)
        self.r1.place(x=325, y=150)

        self.r2 = tk.Radiobutton(self, text="Дискреційна", font=("Arial Bold", 10), variable=self.model_type,
                                 value=2)
        self.r2.place(x=425, y=150)

        self.button1 = tk.Button(self, text="Далі", font=("Arial", 12),
                                 command=self.select_model)
        self.button1.place(x=250, y=210)

        self.l3 = tk.Label(self, text="Виберіть рівень доступу:", font=("Arial Bold", 12), bg='ivory')

        self.combo_box = ttk.Combobox(self,
                                      values=[
                                          "Block",
                                          "Not secretly",
                                          "Secretly",
                                          "Completely secret",
                                          "Of particular importance",
                                      ], width=25, state="readonly")
        self.combo_box.set("Not secretly")

        self.l4 = tk.Label(self, text="Виберіть можливості:", font=("Arial Bold", 12), bg='ivory')

        self.mod = ttk.Combobox(self,
                                values=[
                                    "r",
                                    "r, w",
                                    "e",
                                    "r, w, e"
                                ], width=15, state="readonly")
        self.mod.set("r")

        self.l5 = tk.Label(self, text="Перелік файлів", font=("Arial Bold", 12), bg='ivory')
        self.files_label = tk.Label(self, text="", font=("Arial Bold", 10))

        self.l6 = tk.Label(self, text="Права доступу", font=("Arial Bold", 12), bg='ivory')

        self.l7 = tk.Label(self, text="Години доступу", font=("Arial Bold", 12), bg='ivory')

        self.l00 = tk.Label(self, text="Мандатна модель доступу", font=("Arial Bold", 12), bg='ivory')
        self.l01 = tk.Label(self, text="Дискреційна модель доступу", font=("Arial Bold", 12), bg='ivory')

        self.button2 = tk.Button(self, text="Підтвердити", font=("Arial", 12),
                                 command=self.change_user_mandated_access)

        self.button = tk.Button(self, text="Назад", font=("Arial", 15), command=lambda: controller.show_frame(EditMenuPage))
        self.button.place(x=722, y=450)

        self.button0 = tk.Button(self, text="Назад", font=("Arial", 15), command=self.back_button)

        self.button3 = tk.Button(self, text="Підтвердити", font=("Arial", 12),
                                 command=self.change_user_discretionary_access)

    def select_model(self):
        with sqlite3.connect("Sqlite.sqlite3") as db:
            cursor = db.cursor()
            select_query = read_file("Resourсe/SelectAllFromUsers.txt")
            cursor.execute(select_query)
            self.user_name_entry = self.t1.get()
            if self.user_name_entry == '':
                messagebox.showerror("Помилка", "Введіть ім'я користувача!")
                return
            if self.model_type.get() == 0:
                messagebox.showerror('Помилка', 'Виберіть одну із запропонованих моделей доступу!')
                return
            for row in cursor:
                user = Users(*row)
                if user.user_name == self.user_name_entry:
                    self.user_id = user.id

                    self.l1.place_forget()
                    self.t1.place_forget()
                    self.l2.place_forget()
                    self.r1.place_forget()
                    self.r2.place_forget()
                    self.button1.place_forget()
                    self.button.place_forget()
                    self.t1.delete(0, tk.END)
            if self.t1.get() != '':
                messagebox.showerror('Помилка', 'Такого користувача не існує!')
                return
            if self.model_type.get() == 1:
                self.l00.place(x=300, y=45)
                self.l3.place(x=50, y=100)
                self.combo_box.place(x=325, y=100)
                self.l4.place(x=50, y=150)
                self.mod.place(x=325, y=150)
                self.button2.place(x=200, y=210)
                self.button0.place(x=722, y=450)
            elif self.model_type.get() == 2:
                self.l01.place(x=300, y=45)

                query2 = read_file("Resourсe/SelectAllFromFiles.txt")
                cursor.execute(query2)
                self.file_list = []
                for row in cursor:
                    file = Files(*row)
                    self.file_list.append([file.file_name, file.id])
                # Створити рядок з назвами файлів та їх нумерацією
                files_string = ""
                self.file_mods = {}
                for i, file in enumerate(self.file_list, start=1):
                    files_string += f"{i}. {file[0]}\n\n"
                    mod_var = tk.StringVar(value="-")  # за замовчуванням режим "-"

                    if file[0].split(".")[1] == "txt" or file[0].split(".")[1] == "jpg":
                        self.mod_box = ttk.Combobox(self, name=f"mod_box{i}", values=["-", "r", "r, w"], width=15,
                                                    textvariable=mod_var, state="readonly")
                        self.mod_box.place(x=220, y=110 + 34 * i)  # розміщення на формі, де i - поточний індекс файлу

                    if file[0].split(".")[1] == "exe":
                        self.mod_box = ttk.Combobox(self, name=f"mod_box{i}", values=["-", "e"], width=15,
                                                    textvariable=mod_var, state="readonly")
                        self.mod_box.place(x=220, y=110 + 34 * i)  # розміщення на формі, де i - поточний індекс файлу

                    self.l8 = tk.Label(self, name=f"l8{i}", text="З:", font=("Arial Bold", 10), bg='ivory')
                    self.l8.place(x=370, y=110 + 34 * i)

                    self.l9 = tk.Label(self, name=f"l9{i}", text="До:", font=("Arial Bold", 10), bg='ivory')
                    self.l9.place(x=560, y=110 + 34 * i)

                    # Додати поля введення Spinbox для вказання часових рамок

                    # Часові рамки з
                    self.hour_var_from = tk.StringVar(value='00')
                    self.hour_spinbox_from = tk.Spinbox(self, name=f"hour_spinbox_from{i}", from_=0, to=23, wrap=True,
                                                        textvariable=self.hour_var_from, width=5)
                    self.hour_spinbox_from.place(x=390, y=110 + 34 * i)

                    self.minute_var_from = tk.StringVar(value='00')
                    self.minute_spinbox_from = tk.Spinbox(self, name=f"minute_spinbox_from{i}", from_=0, to=59, wrap=True,
                                                          textvariable=self.minute_var_from,
                                                          width=5)
                    self.minute_spinbox_from.place(x=440, y=110 + 34 * i)

                    self.second_var_from = tk.StringVar(value='00')
                    self.second_spinbox_from = tk.Spinbox(self, name=f"second_spinbox_from{i}", from_=0, to=59, wrap=True,
                                                          textvariable=self.second_var_from,
                                                          width=5)
                    self.second_spinbox_from.place(x=490, y=110 + 34 * i)

                    # Часові рамки до
                    self.hour_var_to = tk.StringVar(value='23')
                    self.hour_spinbox_to = tk.Spinbox(self, name=f"hour_spinbox_to{i}", from_=0, to=23, wrap=True,
                                                      textvariable=self.hour_var_to, width=5)
                    self.hour_spinbox_to.place(x=590, y=110 + 34 * i)

                    self.minute_var_to = tk.StringVar(value='59')
                    self.minute_spinbox_to = tk.Spinbox(self, name=f"minute_spinbox_to{i}", from_=0, to=59, wrap=True,
                                                        textvariable=self.minute_var_to,
                                                        width=5)
                    self.minute_spinbox_to.place(x=640, y=110 + 34 * i)

                    self.second_var_to = tk.StringVar(value='59')
                    self.second_spinbox_to = tk.Spinbox(self, name=f"second_spinbox_to{i}", from_=0, to=59, wrap=True,
                                                        textvariable=self.second_var_to,
                                                        width=5)
                    self.second_spinbox_to.place(x=690, y=110 + 34 * i)

                    self.file_mods[file[1]] = [mod_var, self.hour_var_from, self.minute_var_from, self.second_var_from,
                                               self.hour_var_to, self.minute_var_to, self.second_var_to]
                # Відобразити список файлів у Label
                self.l5.place(x=50, y=100)
                self.l6.place(x=220, y=100)
                self.l7.place(x=510, y=100)
                self.files_label.config(text=files_string)
                self.files_label.place(x=50, y=150)
                self.button0.place(x=722, y=450)
                self.button3.place(x=280, y=370)

    def change_user_mandated_access(self):
        with sqlite3.connect("Sqlite.sqlite3") as db:
            cursor = db.cursor()
            select_query = read_file("Resourсe/SelectAllFromUsers.txt")
            cursor.execute(select_query)
            for row in cursor:
                user = Users(*row)
                if user.user_name == self.user_name_entry:
                    combo = self.combo_box.get()
                    query = f'UPDATE Users SET UserAccessLevelId = ( SELECT Id FROM AccessLevels WHERE AccessLevelName = "{combo}" ), Mod = "{self.mod.get()}" WHERE UserName = "{self.user_name_entry}";'
                    cursor.execute(query)
                    db.commit()
                    messagebox.showinfo('Готово',
                                        f'Встановлено новий рівень доступу для користувача - {self.user_name_entry}')
                    self.t1.delete(0, tk.END)
                    self.combo_box.set("Not secretly")
                    self.mod.set("r")
            if self.t1.get() != '':
                messagebox.showerror('Помилка', 'Такого користувача не існує!')

    def change_user_discretionary_access(self):
        try:
            for key, value in self.file_mods.items():
                if int(value[1].get()) < 0 or int(value[1].get()) > 23:
                    messagebox.showerror("Помилка!", "Некоректні години для часової рамки 'з'")
                    return
                if int(value[2].get()) < 0 or int(value[2].get()) > 59:
                    messagebox.showerror("Помилка!", "Некоректні хвилини для часової рамки 'з'")
                    return
                if int(value[3].get()) < 0 or int(value[3].get()) > 59:
                    messagebox.showerror("Помилка!", "Некоректні секунди для часової рамки 'з'")
                    return
                if int(value[4].get()) < 0 or int(value[4].get()) > 23:
                    messagebox.showerror("Помилка!", "Некоректні години для часової рамки 'до'")
                    return
                if int(value[5].get()) < 0 or int(value[5].get()) > 59:
                    messagebox.showerror("Помилка!", "Некоректні хвилини для часової рамки 'до'")
                    return
                if int(value[6].get()) < 0 or int(value[6].get()) > 59:
                    messagebox.showerror("Помилка!", "Некоректні секунди для часової рамки 'до'")
                    return
            for key, value in self.file_mods.items():
                time_str_from = f"{value[1].get()}:{value[2].get()}:{value[3].get()}"
                time_str_to = f"{value[4].get()}:{value[5].get()}:{value[6].get()}"

                time_obj_from = datetime.datetime.strptime(time_str_from, '%H:%M:%S').time()
                time_obj_to = datetime.datetime.strptime(time_str_to, '%H:%M:%S').time()

                with sqlite3.connect("Sqlite.sqlite3") as db:
                    cursor = db.cursor()
                    select_action_id_query = f"SELECT Id FROM ActionTypes WHERE ActionName = '{value[0].get()}';"
                    cursor.execute(select_action_id_query)
                    try:
                        for row in cursor:
                            if row[0] != 1:
                                insert_discretionary_matrix_query = f"INSERT INTO DiscretionaryMatrix (UserId, FileId, ActionTypeId, AllowFrom, AllowTo) VALUES ({self.user_id}, {key}, {row[0]}, '{time_obj_from}', '{time_obj_to}');"
                                cursor.execute(insert_discretionary_matrix_query)
                                db.commit()
                            else:
                                delete_discretionary_matrix_query = f"DELETE FROM DiscretionaryMatrix WHERE FileId = {key} AND UserId = {self.user_id};"
                                cursor.execute(delete_discretionary_matrix_query)
                                db.commit()
                    except sqlite3.IntegrityError:
                        update_discretionary_matrix_query = f"UPDATE DiscretionaryMatrix SET AllowFrom='{time_obj_from}', AllowTo='{time_obj_to}' WHERE FileId={key};"
                        cursor.execute(update_discretionary_matrix_query)
                        db.commit()
            messagebox.showinfo("Готово!",
                                f"Для користувача - {self.user_name_entry}, успішно встановлені дані налаштування")
            with sqlite3.connect("Sqlite.sqlite3") as db:
                cursor = db.cursor()
                query1 = f"UPDATE Users SET AccessModelId = {self.model_type.get()} WHERE Id = {self.user_id};"
                cursor.execute(query1)
                db.commit()
        except ValueError:
            messagebox.showerror("Помилка!", "Некоректні дані для часової рамки!")
            return

    def back_button(self):
        self.l3.place_forget()
        self.combo_box.place_forget()
        self.l4.place_forget()
        self.mod.place_forget()
        self.button2.place_forget()
        self.button0.place_forget()
        self.l00.place_forget()
        self.l01.place_forget()
        self.l5.place_forget()
        self.files_label.place_forget()
        self.l6.place_forget()
        self.l7.place_forget()
        self.button3.place_forget()
        try:
            for i in range(1, len(self.file_mods)+1):
                self.nametowidget(f"l8{i}").place_forget()
                self.nametowidget(f"l9{i}").place_forget()
                self.nametowidget(f"mod_box{i}").place_forget()
                self.nametowidget(f"hour_spinbox_from{i}").place_forget()
                self.nametowidget(f"minute_spinbox_from{i}").place_forget()
                self.nametowidget(f"second_spinbox_from{i}").place_forget()
                self.nametowidget(f"hour_spinbox_to{i}").place_forget()
                self.nametowidget(f"minute_spinbox_to{i}").place_forget()
                self.nametowidget(f"second_spinbox_to{i}").place_forget()
        except AttributeError:
            pass
        self.l1.place(x=50, y=100)
        self.t1.place(x=325, y=100)
        self.l2.place(x=50, y=150)
        self.r1.place(x=325, y=150)
        self.r2.place(x=425, y=150)
        self.button.place(x=722, y=450)
        self.button1.place(x=250, y=210)


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


def show_users():
    with sqlite3.connect("Sqlite.sqlite3") as db:
        cursor = db.cursor()
        select_query = read_file("Resourсe/SelectAllFromUsers.txt")
        cursor.execute(select_query)
        user_list = []
        for row in cursor:
            user = Users(*row)
            user_list.append(f"{user.user_name} (модель доступу - {user.get_access_model_name()})")
        # Показати список імен користувачів у новому вікні
        user_list_window = tk.Toplevel()
        user_list_window.title("Список користувачів")
        user_list_window.geometry("300x300")
        # Створити список для відображення імен користувачів
        user_listbox = tk.Listbox(user_list_window)
        user_listbox.pack(expand=True, fill="both")
        # Додати імена користувачів до списку
        for user in user_list:
            user_listbox.insert("end", user)


def main():
    app = Application()
    app.title('ТБД_Білецький')
    app.geometry("800x500")
    app.resizable(width=False, height=False)
    main_menu = tk.Menu(app)
    app.config(menu=main_menu)
    file_menu = tk.Menu(main_menu)
    users_menu = tk.Menu(main_menu)
    main_menu.add_cascade(label="Про автора", menu=file_menu)
    file_menu.add_command(label="БІ-442, Білецький Дмитро")
    main_menu.add_cascade(label="Користувачі", menu=users_menu)
    users_menu.add_command(label="Список користувачів", command=show_users)
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
