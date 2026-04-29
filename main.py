"# GitHub User Finder" 
import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os
from datetime import datetime

class GitHubUserFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub User Finder")
        self.root.geometry("700x500")
        self.root.resizable(False, False)

        # Данные
        self.favorites_file = "favorites.json"
        self.favorites = self.load_favorites()

        # Интерфейс
        self.create_widgets()
        self.update_favorites_list()

    # ------------------- UI Components -------------------
    def create_widgets(self):
        # Поиск
        search_frame = tk.Frame(self.root)
        search_frame.pack(pady=10)

        tk.Label(search_frame, text="Введите имя пользователя GitHub:").pack(side=tk.LEFT, padx=5)
        self.search_entry = tk.Entry(search_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<Return>", lambda event: self.search_user())

        tk.Button(search_frame, text="🔍 Найти", command=self.search_user).pack(side=tk.LEFT, padx=5)

        # Результаты поиска
        tk.Label(self.root, text="Результаты поиска:", font=("Arial", 10, "bold")).pack(anchor="w", padx=10)
        self.results_listbox = tk.Listbox(self.root, height=8, width=80)
        self.results_listbox.pack(pady=5, padx=10)
        self.results_listbox.bind("<Double-Button-1>", self.add_to_favorites_from_results)

        tk.Button(self.root, text="⭐ Добавить выбранного в избранное", command=self.add_selected_to_favorites).pack(pady=5)

        # Избранное
        tk.Label(self.root, text="⭐ Избранные пользователи:", font=("Arial", 10, "bold")).pack(anchor="w", padx=10)
        self.favorites_listbox = tk.Listbox(self.root, height=8, width=80)
        self.favorites_listbox.pack(pady=5, padx=10)
        self.favorites_listbox.bind("<Double-Button-1>", self.remove_from_favorites)

        tk.Button(self.root, text="❌ Удалить выбранного из избранного", command=self.remove_selected_from_favorites).pack(pady=5)

    # ------------------- API Logic -------------------
    def search_user(self):
        username = self.search_entry.get().strip()
        if not username:
            messagebox.showwarning("Ошибка ввода", "Поле поиска не может быть пустым!")
            return

        try:
            url = f"https://api.github.com/users/{username}"
            response = requests.get(url)

            if response.status_code == 200:
                user_data = response.json()
                self.results_listbox.delete(0, tk.END)
                info = f"{user_data['login']} — {user_data.get('name', 'Имя не указано')} — Подписчики: {user_data['followers']} — Репозитории: {user_data['public_repos']}"
                self.results_listbox.insert(0, info)
                # Сохраняем данные пользователя в атрибут для дальнейшего добавления
                self.last_found_user = user_data
            elif response.status_code == 404:
                messagebox.showerror("Не найдено", f"Пользователь '{username}' не найден на GitHub.")
            else:
                messagebox.showerror("Ошибка API", f"Ошибка {response.status_code}: {response.text}")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Сетевая ошибка", f"Не удалось подключиться к GitHub API:\n{e}")

    # ------------------- Favorites Logic -------------------
    def load_favorites(self):
        if os.path.exists(self.favorites_file):
            try:
                with open(self.favorites_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []

    def save_favorites(self):
        with open(self.favorites_file, "w", encoding="utf-8") as f:
            json.dump(self.favorites, f, indent=4, ensure_ascii=False)

    def add_to_favorites(self, user_data):
        # Проверяем, нет ли уже в избранном
        for fav in self.favorites:
            if fav["login"] == user_data["login"]:
                messagebox.showinfo("Уже в избранном", f"{user_data['login']} уже добавлен(а) в избранное.")
                return

        favorite_info = {
            "login": user_data["login"],
            "name": user_data.get("name", "Имя не указано"),
            "followers": user_data["followers"],
            "public_repos": user_data["public_repos"],
            "added_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.favorites.append(favorite_info)
        self.save_favorites()
        self.update_favorites_list()
        messagebox.showinfo("Успешно", f"{user_data['login']} добавлен(а) в избранное!")

    def add_selected_to_favorites(self):
        if hasattr(self, 'last_found_user') and self.results_listbox.curselection():
            self.add_to_favorites(self.last_found_user)
        else:
            messagebox.showwarning("Нет выбора", "Сначала найдите пользователя и выберите его в результатах поиска.")

    def add_to_favorites_from_results(self, event):
        self.add_selected_to_favorites()

    def update_favorites_list(self):
        self.favorites_listbox.delete(0, tk.END)
        for fav in self.favorites:
            display = f"{fav['login']} — {fav['name']} — ★ {fav['followers']} — 📁 {fav['public_repos']} — 📅 {fav['added_at']}"
            self.favorites_listbox.insert(tk.END, display)

    def remove_from_favorites(self, event):
        self.remove_selected_from_favorites()

    def remove_selected_from_favorites(self):
        selected = self.favorites_listbox.curselection()
        if not selected:
            messagebox.showwarning("Нет выбора", "Выберите пользователя в списке избранного для удаления.")
            return

        index = selected[0]
        removed_user = self.favorites.pop(index)
        self.save_favorites()
        self.update_favorites_list()
        messagebox.showinfo("Удалено", f"{removed_user['login']} удалён(а) из избранного.")

# ------------------- Запуск -------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = GitHubUserFinder(root)
    root.mainloop()