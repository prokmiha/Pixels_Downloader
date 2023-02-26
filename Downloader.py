import pickle
from tkinter import filedialog

import requests
import os

from tqdm import tqdm
import tkinter as tk


class ImageDownloaderApp:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Загрузка изображений с сервиса pixels.com")
        window_width = 450
        window_height = 300

        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()

        x_cordinate = int((screen_width / 2) - (window_width / 2))
        y_cordinate = int((screen_height / 2) - (window_height / 2))

        self.window.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))
        self.window.resizable(width=False, height=False)

        self.query_label = tk.Label(self.window, text="Тема:")
        self.query_label.pack(pady=5)

        self.query_entry = tk.Entry(self.window, width=30)
        self.query_entry.pack(pady=5)

        self.max_images_label = tk.Label(self.window, text="Количество изображений:")
        self.max_images_label.pack(pady=5)

        self.max_images_entry = tk.Entry(self.window, width=30)
        self.max_images_entry.pack(pady=5)

        self.resolution_label = tk.Label(self.window,
                                         text="Минимльное разрешение фото (формат: Высота \"пробел\" Ширина):")
        self.resolution_label.pack(pady=5)

        self.resolution_entry = tk.Entry(self.window, width=30)
        self.resolution_entry.pack(pady=5)

        self.download_button = tk.Button(self.window, text="Начать загрузку", command=self.download_images)
        self.download_button.pack(pady=5)

        self.folder_button = tk.Button(self.window, text="Выбрать папку", command=self.select_folder)
        self.folder_button.pack(pady=5)

        self.folder_label = tk.Label(self.window, text="")
        self.folder_label.pack(pady=5)

        self.folder_label["text"] = self.load_folder_path()
        self.params = {}
        self.count = 0
        self.full_folder_path = ''

    def download_images(self):
        query = self.query_entry.get()
        folder_path = self.folder_label["text"]
        if not folder_path:
            tk.messagebox.showwarning(title="Warning", message="Пожалуйста, выберите папку для загрузки файлов")
            return
        max_images = int(self.max_images_entry.get())
        min_resolution = tuple(map(int, self.resolution_entry.get().split(" ")))

        url = "https://api.pexels.com/v1/search"
        headers = {
            "Authorization": "your API key"
        }
        self.params = {
            "query": query,
            "per_page": max_images
        }
        response = requests.get(url, headers=headers, params=self.params)

        data = response.json()["photos"]

        if not data:
            tk.messagebox.showwarning(title="Warning", message="По Вашему запросу не найдено фотографий")
            return

        # Создание папки для сохранения картинок
        folder_name = query.replace(" ", "_")
        self.full_folder_path = os.path.join(folder_path, folder_name)
        # breakpoint()
        if not os.path.exists(self.full_folder_path):
            os.makedirs(self.full_folder_path)

        # Загрузка картинок
        for image_data in tqdm(data):
            if self.count == max_images:
                break

            # Проверка разрешения
            if (image_data["width"] >= min_resolution[0]) and (image_data["height"] >= min_resolution[1]):
                image_url = image_data["src"]["original"]
                image_response = requests.get(image_url)
                image_file = open(os.path.join(self.full_folder_path, f"{image_data['id']}.jpg"), "wb")
                image_file.write(image_response.content)
                image_file.close()
                self.count += 1
        self.show_result_window(self.count)

    def save_folder_path(self, folder_path):
        with open('settings.pickle', 'wb') as f:
            pickle.dump(folder_path, f)

    def load_folder_path(self):
        try:
            with open('settings.pickle', 'rb') as f:
                folder_path = pickle.load(f)
        except FileNotFoundError:
            folder_path = ''
        return folder_path

    def select_folder(self):
        folder_path = self.load_folder_path()
        if folder_path:
            folder_path = filedialog.askdirectory(initialdir=folder_path)
            if folder_path:
                self.save_folder_path(folder_path)
        else:
            folder_path = filedialog.askdirectory()
            if not folder_path:
                tk.messagebox.showwarning("Предупреждение",
                                          "Пожалуйста, выберите папку для загрузки файлов")
                return None
            self.save_folder_path(folder_path)

        self.folder_label["text"] = folder_path
        full_path = os.path.join(folder_path, self.query_entry.get().replace(" ", "_"))
        if not os.path.exists(full_path):
            os.makedirs(full_path)

        return full_path

    def open_folder(self):
        folder_path = os.path.abspath(self.full_folder_path)
        # breakpoint()
        os.startfile(folder_path)

    def show_result_window(self, _):
        count = self.count
        total = self.params.get("per_page", 0)
        query = self.params.get("query", 0)
        result_window = tk.Toplevel()
        result_window.title("Завершено")
        main_window_x = self.window.winfo_x()
        main_window_y = self.window.winfo_y()
        main_window_height = self.window.winfo_height()

        result_window_width = 450
        result_window_height = 100
        result_window_x = main_window_x
        result_window_y = main_window_y + main_window_height + 30

        result_window.geometry(f"{result_window_width}x{result_window_height}+{result_window_x}+{result_window_y}")

        message = f"Загружено картинок: {count} из {total}\n" \
                  f'По запросу: "{query}"'
        result_label = tk.Label(result_window, text=message)
        result_label.pack(pady=10)

        open_folder_x = result_window_width // 3 - 25
        open_folder_y = result_window_height - 40
        ok_x = open_folder_x * 2

        ok_button = tk.Button(result_window, text="Закрыть окно", command=result_window.destroy)
        ok_button.place(x=ok_x, y=open_folder_y)

        open_folder_button = tk.Button(result_window, text="Открыть папку", command=self.open_folder)
        open_folder_button.place(x=open_folder_x, y=open_folder_y)


if __name__ == "__main__":
    app = ImageDownloaderApp()
    app.window.mainloop()
