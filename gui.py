import tkinter as tk
import sv_ttk
import threading
import asyncio
import heavy_dicts
import re
from tkinter import ttk, messagebox
from googletrans import Translator
from MainTwoGis import TwoGisMapParse
from async_runner import AsyncParserRunner

class MainApplication(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.parent.title("TwoGisParser")
        self.parent.geometry("1000x700")
        
        try:
            icon = tk.PhotoImage(file="static/mappin.png")
            self.parent.iconphoto(True, icon)
        except Exception:
            pass
  
        self.interface_style()
        self.pack(fill=tk.BOTH, expand=True)
        self.create_widgets() 
        self.toggle_parser_mode()
        
        # Для управления парсингом
        self.is_parsing = False
        self.parser_thread = None
        self.parser_instance = None
            
    def interface_style(self):
        sv_ttk.set_theme("light")
        
    def create_widgets(self):
        """Создание всех виджетов интерфейса"""
        self.top_level_menu()
        self.create_parser_controls()
        self.create_status_bar()
        
    def top_level_menu(self):
        """Верхнее меню"""
        menubar = tk.Menu(self.parent)
        self.parent.config(menu=menubar)

        parse_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Парсинг", menu=parse_menu)
        parse_menu.add_command(label="Запустить парсинг", command=self.run_parsing)
        parse_menu.add_separator()
        parse_menu.add_command(label="Выход", command=self.btn_exit)

        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Справка", menu=help_menu)
        help_menu.add_command(label="Руководство пользователя", command=self.user_manual)
        help_menu.add_command(label="О программе", command=self.btn_about)

    def create_parser_controls(self):
        """Создание элементов управления для парсера"""
        # Основной фрейм с grid для точного контроля
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Конфигурация grid - основной контейнер
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Счетчик строк для grid
        row = 0
        
        # 1. Фрейм для выбора режима парсинга
        mode_frame = ttk.LabelFrame(main_frame, text="Режим парсинга", padding=10)
        mode_frame.grid(row=row, column=0, sticky=tk.EW, padx=10, pady=(0, 5))
        mode_frame.config(height=70)
        
        self.parser_mode_key = tk.StringVar(value="keyword")
        
        ttk.Radiobutton(mode_frame, text="Парсер по ключу", 
                       variable=self.parser_mode_key, 
                       value="keyword",
                       command=self.toggle_parser_mode).grid(row=0, column=0, sticky=tk.W, padx=15, pady=0)
        
        ttk.Radiobutton(mode_frame, text="Парсер по URL", 
                       variable=self.parser_mode_key, 
                       value="url",
                       command=self.toggle_parser_mode).grid(row=0, column=1, sticky=tk.W, padx=15, pady=0)
        
        row += 1
        
        # 2. Фрейм для темы парсера
        theme_frame = ttk.LabelFrame(main_frame, text="Тема парсера", padding=10)
        theme_frame.grid(row=row, column=0, sticky=tk.EW, padx=10, pady=(0, 5))
        theme_frame.config(height=70)
        
        self.parser_mode_t = tk.StringVar(value="tlight")
        
        ttk.Radiobutton(theme_frame, text="Светлая тема",
                       variable=self.parser_mode_t,
                       value="tlight",
                       command=self.theme_parser_mode).grid(row=0, column=0, sticky=tk.W, padx=15, pady=0)
        
        ttk.Radiobutton(theme_frame, text="Темная тема",
                       variable=self.parser_mode_t,
                       value="tdark",
                       command=self.theme_parser_mode).grid(row=0, column=1, sticky=tk.W, padx=15, pady=0)
        
        row += 1
        
        # 3. Фрейм для параметров парсинга
        self.params_frame = ttk.LabelFrame(main_frame, text="Параметры парсинга", padding=10)
        self.params_frame.grid(row=row, column=0, sticky=tk.EW, padx=10, pady=(0, 5))
        self.params_frame.config(height=90)
        
        # Создаем оба варианта параметров, но показываем только один
        self.create_keyword_params()
        self.create_url_params()
        
        row += 1
        
        # 4. Дополнительные параметры
        common_frame = ttk.LabelFrame(main_frame, text="Дополнительные параметры", padding=10)
        common_frame.grid(row=row, column=0, sticky=tk.EW, padx=10, pady=(0, 5))
        common_frame.config(height=90)
        
        # Содержимое common_frame
        ttk.Label(common_frame, text="Количество фирм:").grid(row=0, column=0, sticky=tk.W, pady=0)
        self.firm_count_var = tk.IntVar(value=50)
        self.firm_count_spinbox = ttk.Spinbox(common_frame, from_=1, to=1000, 
                                              textvariable=self.firm_count_var, width=17)
        self.firm_count_spinbox.grid(row=0, column=1, padx=5, pady=0, sticky=tk.W)
        
        self.text_url_btn = ttk.Label(common_frame, text="Парсинг по URL:", width=20)
        self.text_url_btn.grid(row=1, column=0, sticky=tk.W, pady=0)
        
        self.generate_url_btn = ttk.Button(common_frame, text="Сгенерировать URL", 
                                          command=self.generate_url, width=25)
        self.generate_url_btn.grid(row=1, column=1, sticky=tk.W, padx=5, pady=0)
        
        row += 1
        
        # 5. Кнопки управления
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, sticky=tk.W, padx=20, pady=(0, 5))
        button_frame.config(height=40)
        
        ttk.Button(button_frame, text="Запустить парсинг", 
                  command=self.run_parsing, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Остановить парсинг", 
                  command=self.stop_parsing, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Очистить лог", 
                  command=self.clear_log, width=20).pack(side=tk.LEFT, padx=5)
        
        row += 1
        
        # Лог выполнения
        log_frame = ttk.LabelFrame(main_frame, text="Лог выполнения", padding=10)
        log_frame.grid(row=row, column=0, sticky=tk.NSEW, padx=10, pady=0)
        
        # Настраиваем вес строки для растягивания лога
        main_frame.grid_rowconfigure(row, weight=1)
        
        # Создаем текстовое поле для логов
        self.log_text = tk.Text(log_frame, height=20, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Добавляем скроллбар
        scrollbar = ttk.Scrollbar(self.log_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.log_text.yview)
        
    def create_keyword_params(self):
        """Создание элементов для парсера по ключу"""
        self.keyword_frame = ttk.Frame(self.params_frame)
        self.keyword_frame.place(x=0, y=0, relwidth=1, relheight=1)  # Занимает весь params_frame
        
        # Ключевое слово
        ttk.Label(self.keyword_frame, text="Ключевое слово:").grid(row=0, column=0, sticky=tk.W, pady=0)
        self.keyword_var = tk.StringVar(value="Мойка")
        self.keyword_entry = ttk.Entry(self.keyword_frame, textvariable=self.keyword_var, width=25)
        self.keyword_entry.grid(row=0, column=1, padx=5, pady=0, sticky=tk.W)
        
        # Город
        ttk.Label(self.keyword_frame, text="Город:").grid(row=1, column=0, sticky=tk.W, pady=0)
        self.city_var = tk.StringVar(value="Челябинск")
        self.city_entry = ttk.Entry(self.keyword_frame, textvariable=self.city_var, width=25)
        self.city_entry.grid(row=1, column=1, padx=5, pady=0, sticky=tk.W)
        
    def create_url_params(self):
        """Создание элементов для парсера по URL"""
        self.url_frame = ttk.Frame(self.params_frame)
        self.url_frame.place(x=0, y=0, relwidth=1, relheight=1)
        
        # URL для парсинга
        ttk.Label(self.url_frame, text="URL страницы 2ГИС:").grid(row=0, column=0, sticky=tk.W, pady=0)
        self.url_var = tk.StringVar(value="https://2gis.ru/chelyabinsk/search/Мойка")
        self.url_entry = ttk.Entry(self.url_frame, textvariable=self.url_var, width=50)
        self.url_entry.grid(row=0, column=1, padx=5, pady=0, sticky=tk.W)
        
        # Пустое пространство для выравнивания
        empty_space = ttk.Frame(self.url_frame, height=30)
        empty_space.grid(row=1, column=0, columnspan=2, pady=0)

    def toggle_parser_mode(self):
        """Переключение между режимами парсинга"""
        if self.parser_mode_key.get() == "keyword":
            # Показываем параметры для парсера по ключу
            self.url_frame.place_forget()
            self.keyword_frame.place(x=0, y=0, relwidth=1, relheight=1)
            self.generate_url_btn.config(state=tk.NORMAL)
            self.status_var.set("Режим: Парсер по ключу")
        else:
            # Показываем параметры для парсера по URL
            self.keyword_frame.place_forget()
            self.url_frame.place(x=0, y=0, relwidth=1, relheight=1)
            self.generate_url_btn.config(state=tk.DISABLED)
            self.status_var.set("Режим: Парсер по URL")

    def theme_parser_mode(self):
        """Переключение между темой парсера"""
        current_geometry = self.parent.geometry()  # Сохраняем текущие размеры окна
        
        if self.parser_mode_t.get() == "tlight":
            sv_ttk.set_theme("light")
            self.status_var.set("Установлена: Светлая тема")
        else:
            sv_ttk.set_theme("dark")
            self.status_var.set("Установлена: Темная тема")
            
        # Принудительно обновляем интерфейс
        self.parent.update_idletasks()
        
        # Восстанавливаем размеры окна
        self.parent.geometry(current_geometry)
        
    async def translate_text(self, sity):
        """Переводим город на английский для удобства"""
        self.translator = Translator()
        a = await self.translator.translate(sity, src="ru", dest="en")
        a = '-'.join(a.text.split())
        return a.lower()

    def generate_url(self):
        """Генерация URL на основе ключевого слова и города"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        keyword = self.keyword_var.get().strip()
        city = loop.run_until_complete(self.translate_text(self.city_var.get().strip()))
        
        if not keyword or not city:
            messagebox.showwarning("Предупреждение", "Введите ключевое слово и город!")
            return

        try:
            city_code = heavy_dicts.city_mapping[self.city_var.get().strip()]
        except:
            city_code = city
        generated_url = f"https://2gis.ru/{city_code}/search/{keyword}"
        
        self.url_var.set(generated_url)
        
        # Предлагаем переключиться на режим по URL
        if messagebox.askyesno("URL сгенерирован", 
                              f"URL успешно сгенерирован:\n{generated_url}\n\n"
                              f"Хотите переключиться на парсер по URL?"):
            self.parser_mode_key.set("url")
            self.toggle_parser_mode()
        self.status_var.set("URL сгенерирован")
            
    def run_parsing(self):
        """Запуск парсинга в зависимости от выбранного режима"""
        if self.is_parsing:
            messagebox.showwarning("Предупреждение", "Парсинг уже выполняется!")
            return
        self.is_parsing = True
        if self.parser_mode_key.get() == "keyword":
            self.run_keyword_parsing()
        else:
            self.run_url_parsing()
            
    def run_keyword_parsing(self):
        """Запуск парсинга по ключу"""
        keyword = self.keyword_var.get()
        city = self.city_var.get()
        firm_count = self.firm_count_var.get()
        
        if not keyword or not city:
            messagebox.showwarning("Предупреждение", "Заполните все поля!")
            return
            
        self.log_message(f"Начало парсинга по ключу: '{keyword}' в {city}, количество: {firm_count}")
        self.status_var.set(f"Парсинг по ключу: {keyword} в {city}")
        
        # Запуск асинхронного парсинга в отдельном потоке
        self.is_parsing = True
        self.parser_instance = TwoGisMapParse(keyword, city, firm_count)
        self.parser_thread = threading.Thread(
            target=self.run_async_parsing,
            args=(self.parser_instance,),
            daemon=True
        )
        self.parser_thread.start()
        
    def run_url_parsing(self):
        """Запуск парсинга по URL - извлекаем город и ключ из URL"""
        url = self.url_var.get()
        firm_count = self.firm_count_var.get()
        
        if not url:
            messagebox.showwarning("Предупреждение", "Введите URL для парсинга!")
            return
            
        # Проверяем, что это URL 2ГИС
        if not url.startswith(('https://2gis.ru/', 'http://2gis.ru/')):
            messagebox.showwarning("Предупреждение", "Введите корректный URL 2ГИС!")
            return
        
        try:
            # Извлекаем город и ключевое слово из URL
            pattern = r'https?://2gis\.ru/([^/]+)/search/(.+)'
            match = re.search(pattern, url)
            
            if match:
                city_code = match.group(1)
                keyword = match.group(2)
                
                # Декодируем URL-кодирование если есть
                from urllib.parse import unquote
                keyword = unquote(keyword)
                
                self.log_message(f"Извлечено из URL: город='{city_code}', ключ='{keyword}'")
                self.status_var.set(f"Парсинг по URL: {city_code} - {keyword}")
                
                # Запускаем парсинг так же, как для ключа
                self.is_parsing = True
                self.parser_instance = TwoGisMapParse(keyword, city_code, firm_count)
                self.parser_thread = threading.Thread(
                    target=self.run_async_parsing,
                    args=(self.parser_instance,),
                    daemon=True
                )
                self.parser_thread.start()
            else:
                messagebox.showwarning("Ошибка", 
                    "Не удалось извлечь данные из URL. Проверьте формат:\n"
                    "Пример: https://2gis.ru/chelyabinsk/search/Мойка\n"
                    "Или: https://2gis.ru/moscow/search/Ресторан")
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Неверный формат URL: {str(e)}")

    def run_async_parsing(self, parser_instance):
        """Запуск асинхронного парсинга в отдельном потоке"""
        try:
            # Создаем и запускаем runner
            runner = AsyncParserRunner(
                parser_instance, 
                update_callback=self.update_gui_from_thread
            )
            self.parser_thread = runner.start()
            
        except Exception as e:
            self.update_gui_from_thread(f"Ошибка запуска: {str(e)}")
            self.is_parsing = False
            
    def update_gui_from_thread(self, message):
        """Обновление GUI из потока"""
        def update():
            self.log_message(message)
            self.status_var.set(message[:50] + "..." if len(message) > 50 else message)
            
        self.after(0, update)

    def stop_parsing(self):
        """Остановка парсинга"""
        if not self.is_parsing:
            messagebox.showinfo("Информация", "Парсинг не выполняется")
            return
        
        # Закрытие страницы в отдельном потоке
        if hasattr(self, 'parser_instance'):
            threading.Thread(
                target=lambda: asyncio.run(self.parser_instance.page.close()) 
                if hasattr(self.parser_instance, 'page') else None,
                daemon=True
            ).start()
        
        self.is_parsing = False
        self.status_var.set("Парсинг остановлен")
        self.log_message("Парсинг остановлен пользователем")
        
    def clear_log(self):
        """Очистка лога"""
        self.log_text.delete(1.0, tk.END)
        self.log_message("Лог очищен")
        self.status_var.set("Лог очищен")
        
    def log_message(self, message):
        """Добавление сообщения в лог"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)

    def user_manual(self):
        """Обработчик кнопки 'Руководство пользователя'"""
        about_text = """
        Руководство пользователя
        
        1. Выберите режим парсинга:
           • Парсер по ключу - поиск по ключевому слову и городу
           • Парсер по URL - парсинг конкретной страницы 2ГИС
        
        2. Заполните параметры:
           • Для парсера по ключу: ключевое слово и город
           • Для парсера по URL: вставьте URL страницы
           • Укажите количество фирм для парсинга
        
        3. Дополнительные параметры:
           • Для парсера по ключу: кнопка "Сгенерировать URL"
        
        4. Нажмите "Запустить парсинг"
        
        Примечания:
            • Парсинг выполняется асинхронно - интерфейс не блокируется
            • Результаты сохраняются в папке 2gis_parse_results/data.xlsx
            • Для работы требуется установленный Playwright
            • Можно остановить парсинг в любой момент
        """
        messagebox.showinfo("Руководство пользователя", about_text, icon="question")

    def btn_about(self):
        """Обработчик кнопки 'О программе'"""
        about_text = """
        Парсер данных 2ГИС
        Версия 3.0.0
        
        Режимы работы:
        1. Парсер по ключу - поиск организаций по ключевому слову и городу
        2. Парсер по URL - парсинг конкретной страницы поиска 2ГИС
        
        Возможности:
        • Асинхронный парсинг с Playwright
        • Сохранение данных в Excel
        • Автоматическая генерация URL
        • Поддержка светлой и темной темы
        
        https://github.com/itrickon/TwoGisParser
        
        Используемые технологии:
        • Python 3.11+
        • Playwright для веб-скрапинга
        • tkinter для графического интерфейса
        • sv_ttk для современных стилей
        • Openpyxl для работы с Excel
        """
        messagebox.showinfo("О программе", about_text)

    def btn_exit(self):
        """Выход из приложения"""
        if self.is_parsing:
            if not messagebox.askyesno("Предупреждение", 
                                      "Парсинг выполняется. Вы уверены, что хотите выйти?"):
                return
        
        if messagebox.askyesno("Выход", "Вы уверены, что хотите выйти?"):
            self.parent.quit()

    def create_status_bar(self):
        """Создание строки состояния"""
        self.status_var = tk.StringVar()
        self.status_var.set("Готов к работе")
        self.status_bar = ttk.Label(self, textvariable=self.status_var, 
                                   relief=tk.SUNKEN, padding=(10, 5))
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)


def main():
    """Точка входа в приложение"""
    root = tk.Tk()
    app = MainApplication(root)
    root.mainloop()


if __name__ == "__main__":
    main()