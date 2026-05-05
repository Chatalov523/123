import json
import os
import requests
from tkinter import *
from tkinter import ttk, messagebox
from datetime import datetime
from PIL import Image, ImageTk
from io import BytesIO

class GitHubUserFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub User Finder - Поиск пользователей GitHub")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)

        # Файл для хранения избранных
        self.favorites_file = "github_favorites.json"
        self.favorites = self.load_favorites()

        # Переменные
        self.search_query = StringVar()
        self.current_user_data = None

        self.create_widgets()
        self.update_favorites_list()

    def create_widgets(self):
        # Рамка для поиска
        search_frame = LabelFrame(self.root, text="🔍 Поиск пользователей GitHub", padx=15, pady=10, 
                                   font=("Arial", 12, "bold"))
        search_frame.pack(fill="x", padx=10, pady=5)

        Label(search_frame, text="Введите имя пользователя:", font=("Arial", 10)).pack(side="left", padx=5)
        
        self.search_entry = Entry(search_frame, textvariable=self.search_query, width=30, font=("Arial", 10))
        self.search_entry.pack(side="left", padx=5, pady=5)
        
        self.search_btn = Button(search_frame, text="🔎 Поиск", command=self.search_user,
                                 bg="#2196F3", fg="white", font=("Arial", 10, "bold"), padx=15)
        self.search_btn.pack(side="left", padx=5)
        
        self.clear_btn = Button(search_frame, text="Очистить", command=self.clear_search,
                                bg="#9E9E9E", fg="white", font=("Arial", 10), padx=10)
        self.clear_btn.pack(side="left", padx=5)

        # Рамка для результатов поиска
        results_frame = LabelFrame(self.root, text="📊 Результат поиска", padx=15, pady=10, 
                                    font=("Arial", 12, "bold"))
        results_frame.pack(fill="x", padx=10, pady=5)

        # Фрейм для аватара и информации
        info_frame = Frame(results_frame)
        info_frame.pack(fill="x", pady=5)

        # Аватар
        self.avatar_label = Label(info_frame, text="Аватар не загружен", font=("Arial", 9))
        self.avatar_label.pack(side="left", padx=10)

        # Информация о пользователе
        user_info_frame = Frame(info_frame)
        user_info_frame.pack(side="left", padx=20, fill="both", expand=True)

        self.username_label = Label(user_info_frame, text="", font=("Arial", 14, "bold"))
        self.username_label.pack(anchor="w")

        self.name_label = Label(user_info_frame, text="", font=("Arial", 11))
        self.name_label.pack(anchor="w")

        self.location_label = Label(user_info_frame, text="", font=("Arial", 10))
        self.location_label.pack(anchor="w")

        self.company_label = Label(user_info_frame, text="", font=("Arial", 10))
        self.company_label.pack(anchor="w")

        self.bio_label = Label(user_info_frame, text="", font=("Arial", 10), wraplength=400, justify="left")
        self.bio_label.pack(anchor="w", pady=5)

        # Статистика
        stats_frame = Frame(results_frame)
        stats_frame.pack(fill="x", pady=10)

        self.repos_label = Label(stats_frame, text="📚 Репозитории: 0", font=("Arial", 10, "bold"))
        self.repos_label.pack(side="left", padx=15)

        self.followers_label = Label(stats_frame, text="👥 Подписчики: 0", font=("Arial", 10, "bold"))
        self.followers_label.pack(side="left", padx=15)

        self.following_label = Label(stats_frame, text="📌 Подписки: 0", font=("Arial", 10, "bold"))
        self.following_label.pack(side="left", padx=15)

        self.gists_label = Label(stats_frame, text="📝 Gists: 0", font=("Arial", 10, "bold"))
        self.gists_label.pack(side="left", padx=15)

        # Кнопки действий
        actions_frame = Frame(results_frame)
        actions_frame.pack(fill="x", pady=5)

        self.fav_btn = Button(actions_frame, text="⭐ Добавить в избранное", command=self.add_to_favorites,
                              bg="#FF9800", fg="white", font=("Arial", 10, "bold"), padx=10)
        self.fav_btn.pack(side="left", padx=5)

        self.open_profile_btn = Button(actions_frame, text="🌐 Открыть профиль в браузере", command=self.open_github_profile,
                                       bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), padx=10)
        self.open_profile_btn.pack(side="left", padx=5)

        # Рамка для избранных пользователей
        favorites_frame = LabelFrame(self.root, text="⭐ Избранные пользователи", padx=10, pady=10, 
                                      font=("Arial", 12, "bold"))
        favorites_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Список избранных
        scrollbar = Scrollbar(favorites_frame)
        scrollbar.pack(side="right", fill="y")

        self.favorites_listbox = Listbox(favorites_frame, yscrollcommand=scrollbar.set, 
                                         font=("Courier", 10), height=8)
        self.favorites_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.favorites_listbox.yview)

        # Привязка события выбора из списка
        self.favorites_listbox.bind('<<ListboxSelect>>', self.on_favorite_select)

        # Кнопки управления избранным
        fav_control_frame = Frame(favorites_frame)
        fav_control_frame.pack(fill="x", pady=5)

        Button(fav_control_frame, text="❌ Удалить из избранного", command=self.remove_from_favorites,
               bg="#f44336", fg="white", font=("Arial", 9, "bold"), padx=10).pack(side="left", padx=5)
        
        Button(fav_control_frame, text="🔄 Обновить список", command=self.update_favorites_list,
               bg="#2196F3", fg="white", font=("Arial", 9, "bold"), padx=10).pack(side="left", padx=5)

        # Статусная строка
        self.status_label = Label(self.root, text="✅ Готов к поиску", bd=1, relief=SUNKEN, anchor=W, 
                                   font=("Arial", 9), bg="#f0f0f0")
        self.status_label.pack(side="bottom", fill="x")

        # Информация о количестве избранных
        self.info_label = Label(self.root, text="", font=("Arial", 9), fg="#666")
        self.info_label.pack(side="bottom", fill="x", pady=2)

    def search_user(self):
        """Поиск пользователя GitHub по username"""
        username = self.search_query.get().strip()
        
        # Проверка на пустое поле
        if not username:
            messagebox.showerror("Ошибка", "Поле поиска не может быть пустым!")
            return
        
        self.status_label.config(text=f"⏳ Поиск пользователя '{username}'...")
        self.root.update()
        
        try:
            # Запрос к GitHub API
            url = f"https://api.github.com/users/{username}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                user_data = response.json()
                self.display_user_info(user_data)
                self.current_user_data = user_data
                self.status_label.config(text=f"✅ Пользователь '{username}' найден!")
            elif response.status_code == 404:
                messagebox.showerror("Ошибка", f"Пользователь '{username}' не найден на GitHub!")
                self.clear_user_info()
                self.status_label.config(text="❌ Пользователь не найден")
            else:
                messagebox.showerror("Ошибка", f"Ошибка API: {response.status_code}")
                self.status_label.config(text="❌ Ошибка при поиске")
                
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Ошибка", f"Не удалось подключиться к GitHub API:\n{str(e)}")
            self.status_label.config(text="❌ Ошибка подключения")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка:\n{str(e)}")
            self.status_label.config(text="❌ Неизвестная ошибка")

    def display_user_info(self, user_data):
        """Отображение информации о пользователе"""
        # Очищаем предыдущие данные
        self.clear_user_info()
        
        # Основная информация
        username = user_data.get('login', 'N/A')
        name = user_data.get('name', 'Не указано')
        location = user_data.get('location', 'Не указано')
        company = user_data.get('company', 'Не указано')
        bio = user_data.get('bio', 'Нет описания')
        
        self.username_label.config(text=f"@{username}")
        self.name_label.config(text=f"Имя: {name}")
        self.location_label.config(text=f"📍 {location}" if location != 'Не указано' else "📍 Локация не указана")
        self.company_label.config(text=f"🏢 {company}" if company != 'Не указано' else "🏢 Компания не указана")
        self.bio_label.config(text=f"📝 {bio[:200]}{'...' if len(bio) > 200 else ''}")
        
        # Статистика
        repos = user_data.get('public_repos', 0)
        followers = user_data.get('followers', 0)
        following = user_data.get('following', 0)
        gists = user_data.get('public_gists', 0)
        
        self.repos_label.config(text=f"📚 Репозитории: {repos}")
        self.followers_label.config(text=f"👥 Подписчики: {followers}")
        self.following_label.config(text=f"📌 Подписки: {following}")
        self.gists_label.config(text=f"📝 Gists: {gists}")
        
        # Загрузка аватара (в отдельном потоке для UI)
        avatar_url = user_data.get('avatar_url')
        if avatar_url:
            self.load_avatar(avatar_url)
        
        # Сохраняем данные пользователя
        self.current_user_data = user_data

    def load_avatar(self, url):
        """Загрузка аватара пользователя"""
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                img_data = response.content
                img = Image.open(BytesIO(img_data))
                img = img.resize((100, 100), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.avatar_label.config(image=photo, text="")
                self.avatar_label.image = photo  # Сохраняем ссылку
            else:
                self.avatar_label.config(text="❌ Не удалось загрузить аватар", image="")
        except Exception as e:
            self.avatar_label.config(text="❌ Ошибка загрузки", image="")

    def clear_user_info(self):
        """Очистка информации о пользователе"""
        self.username_label.config(text="")
        self.name_label.config(text="")
        self.location_label.config(text="")
        self.company_label.config(text="")
        self.bio_label.config(text="")
        self.repos_label.config(text="📚 Репозитории: 0")
        self.followers_label.config(text="👥 Подписчики: 0")
        self.following_label.config(text="📌 Подписки: 0")
        self.gists_label.config(text="📝 Gists: 0")
        self.avatar_label.config(image="", text="Аватар не загружен")
        self.current_user_data = None

    def clear_search(self):
        """Очистка поиска"""
        self.search_query.set("")
        self.clear_user_info()
        self.status_label.config(text="✅ Готов к поиску")

    def add_to_favorites(self):
        """Добавление текущего пользователя в избранное"""
        if not self.current_user_data:
            messagebox.showwarning("Внимание", "Сначала найдите пользователя!")
            return
        
        username = self.current_user_data['login']
        
        # Проверка, не добавлен ли уже пользователь
        if any(fav['login'] == username for fav in self.favorites):
            messagebox.showinfo("Информация", f"Пользователь @{username} уже в избранном!")
            return
        
        # Добавляем пользователя в избранное
        favorite = {
            "login": username,
            "name": self.current_user_data.get('name', 'Не указано'),
            "avatar_url": self.current_user_data.get('avatar_url', ''),
            "added_date": datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
            "html_url": self.current_user_data.get('html_url', ''),
            "repos": self.current_user_data.get('public_repos', 0),
            "followers": self.current_user_data.get('followers', 0)
        }
        
        self.favorites.append(favorite)
        self.save_favorites()
        self.update_favorites_list()
        self.status_label.config(text=f"⭐ Пользователь @{username} добавлен в избранное")
        messagebox.showinfo("Успех", f"Пользователь @{username} добавлен в избранное!")

    def remove_from_favorites(self):
        """Удаление пользователя из избранного"""
        selection = self.favorites_listbox.curselection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите пользователя для удаления!")
            return
        
        index = selection[0]
        favorite = self.favorites[index]
        username = favorite['login']
        
        if messagebox.askyesno("Подтверждение", f"Удалить @{username} из избранного?"):
            self.favorites.pop(index)
            self.save_favorites()
            self.update_favorites_list()
            self.status_label.config(text=f"❌ Пользователь @{username} удалён из избранного")

    def update_favorites_list(self):
        """Обновление списка избранных пользователей"""
        self.favorites_listbox.delete(0, END)
        
        if not self.favorites:
            self.favorites_listbox.insert(END, "  ⭐ Избранных пользователей пока нет")
        else:
            for fav in self.favorites:
                display_text = f"⭐ @{fav['login']} — {fav['name'][:30]} (⭐ {fav['followers']} подписчиков)"
                self.favorites_listbox.insert(END, display_text)
        
        # Обновляем информационную метку
        total = len(self.favorites)
        self.info_label.config(text=f"📊 Всего избранных пользователей: {total}")

    def on_favorite_select(self, event):
        """Обработка выбора пользователя из избранного"""
        selection = self.favorites_listbox.curselection()
        if selection:
            index = selection[0]
            favorite = self.favorites[index]
            username = favorite['login']
            
            # Загружаем информацию о выбранном пользователе
            self.search_query.set(username)
            self.search_user()

    def open_github_profile(self):
        """Открытие профиля GitHub в браузере"""
        if not self.current_user_data:
            messagebox.showwarning("Внимание", "Сначала найдите пользователя!")
            return
        
        import webbrowser
        url = self.current_user_data.get('html_url')
        if url:
            webbrowser.open(url)
            self.status_label.config(text=f"🌐 Открыт профиль {self.current_user_data['login']}")
        else:
            messagebox.showerror("Ошибка", "Не удалось открыть профиль!")

    def save_favorites(self):
        """Сохранение избранных пользователей в JSON"""
        try:
            with open(self.favorites_file, 'w', encoding='utf-8') as f:
                json.dump(self.favorites, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить избранное: {e}")

    def load_favorites(self):
        """Загрузка избранных пользователей из JSON"""
        if os.path.exists(self.favorites_file):
            try:
                with open(self.favorites_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return []
        return []

if __name__ == "__main__":
    root = Tk()
    app = GitHubUserFinder(root)
    root.mainloop()