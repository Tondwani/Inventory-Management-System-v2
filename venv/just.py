def open_employee_manager(root, main_menu_callback):
    employee_window = tk.Toplevel(root)
    EmployeeManager(employee_window, main_menu_callback)


        def sales(self):
        self.new_win=tk.Toplevel(self.root)
        self.new_obj=salesManager(self.new_win)


            # Placeholder methods for menu items

    def toggle_menu(self):
        if self.menu_visible:
            self.hide_menu()
        else:
            self.show_menu()

    def show_menu(self):
        self.menu_frame.place(x=0)
        self.menu_visible = True

    def hide_menu(self):
        self.menu_frame.place(x=-200)
        self.menu_visible = False

    def open_categories(self):
        print("Opening Categories")

    def open_billing(self):
        print("Opening Billing")

    def open_employee(self):
        print("Opening employee")

    def open_products(self):
        print("Opening Products")

    def open_suppliers(self):
        print("Opening Suppliers")

    def open_settings(self):
        print("Opening Settings")


                # KPI Section
        self.kpi_frame = tk.Frame(self.main_content, bg="white")
        self.kpi_frame.pack(fill=tk.X, padx=10, pady=10)

        self.total_inventory_value = tk.StringVar()
        self.total_sales = tk.StringVar()
        self.low_stock_count = tk.StringVar()

        kpis = [
            ("Total Inventory Value", self.total_inventory_value),
            ("Total Sales", self.total_sales),
            ("Low Stock Items", self.low_stock_count)
        ]

        for i, (label, variable) in enumerate(kpis):
            frame = tk.Frame(self.kpi_frame, bg="light grey", padx=10, pady=10)
            frame.grid(row=0, column=i, padx=5)
            tk.Label(frame, text=label, bg="light grey").pack()
            tk.Label(frame, textvariable=variable, bg="light grey", font=("Arial", 16, "bold")).pack()

        self.canvas = tk.Canvas(self.main_frame)
        self.vertical_scrollbar = ttk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.horizontal_scrollbar = ttk.Scrollbar(self.main_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=self.vertical_scrollbar.set, xscrollcommand=self.horizontal_scrollbar.set)

        self.vertical_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.horizontal_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.main_content = tk.Frame(self.canvas, bg="white")
        self.canvas.create_window((0, 0), window=self.main_content, anchor="nw")
        self.main_content.bind("<Configure>", self.on_frame_configure)

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        # Charts
        self.charts_frame = tk.Frame(self.main_content, bg="white")
        self.charts_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.create_sales_trend_chart()
        self.create_top_products_chart()
        self.create_category_distribution_chart()

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def create_sales_trend_chart(self):
        fig, ax = plt.subplots(figsize=(4, 3), dpi=100)
        canvas = FigureCanvasTkAgg(fig, master=self.charts_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.grid(row=0, column=0, padx=5, pady=5)

        self.sales_trend_ax = ax
        self.sales_trend_canvas = canvas

    def create_top_products_chart(self):
        fig, ax = plt.subplots(figsize=(4, 3), dpi=100)
        canvas = FigureCanvasTkAgg(fig, master=self.charts_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.grid(row=0, column=1, padx=5, pady=5)

        self.top_products_ax = ax
        self.top_products_canvas = canvas

    def create_category_distribution_chart(self):
        fig, ax = plt.subplots(figsize=(4, 3), dpi=100)
        canvas = FigureCanvasTkAgg(fig, master=self.charts_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.grid(row=1, column=0, padx=5, pady=5)

        self.category_distribution_ax = ax
        self.category_distribution_canvas = canvas 



    def start_real_time_updates(self):
        def update_loop():
            while True:
                self.update_kpis()
                self.update_charts()
                time.sleep(5)  # Update every 5 seconds

        thread = threading.Thread(target=update_loop, daemon=True)
        thread.start()

    def update_kpis(self):
        self.total_inventory_value.set(f"${random.randint(100000, 500000)}")
        self.total_sales.set(f"${random.randint(50000, 200000)}")
        self.low_stock_count.set(str(random.randint(5, 20)))

    def update_charts(self):
        self.update_sales_trend()
        self.update_top_products()
        self.update_category_distribution()

    def update_sales_trend(self):
        dates = pd.date_range(start="2024-01-01", periods=30)
        sales = [random.randint(1000, 5000) for _ in range(30)]
        
        self.sales_trend_ax.clear()
        self.sales_trend_ax.plot(dates, sales)
        self.sales_trend_ax.set_title("Sales Trend")
        self.sales_trend_ax.set_xlabel("Date")
        self.sales_trend_ax.set_ylabel("Sales")
        self.sales_trend_ax.tick_params(axis='x', rotation=45)
        plt.tight_layout()
        self.sales_trend_canvas.draw()

    def update_top_products(self):
        products = ['A', 'B', 'C', 'D', 'E']
        sales = [random.randint(100, 1000) for _ in range(5)]
        
        self.top_products_ax.clear()
        self.top_products_ax.bar(products, sales)
        self.top_products_ax.set_title("Top 5 Products")
        self.top_products_ax.set_xlabel("Product")
        self.top_products_ax.set_ylabel("Sales")
        self.top_products_ax.tick_params(axis='x', rotation=45)
        plt.tight_layout()
        self.top_products_canvas.draw()

    def update_category_distribution(self):
        categories = ['Category 1', 'Category 2', 'Category 3', 'Category 4']
        sizes = [random.randint(10, 100) for _ in range(4)]
        
        self.category_distribution_ax.clear()
        self.category_distribution_ax.pie(sizes, labels=categories, autopct='%1.1f%%', startangle=90)
        self.category_distribution_ax.set_title("Category Distribution")
        plt.tight_layout()
        self.category_distribution_canvas.draw()
