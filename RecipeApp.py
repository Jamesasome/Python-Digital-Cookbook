import re 
import logging
import sqlite3 
import hashlib 
from html import escape
from xhtml2pdf import pisa
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtWidgets import QFileDialog
from pathlib import Path
from LabelGen import render_all
from config import constants
from RecipeRepository import RecipeRepository
from RecipeDelegate import RecipeDelegate
from StepWidget import StepWidget
from RecipeDataClass import Ingredient, Recipe, Step, IngredientInput


class RecipeApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Digital Cookbook")
        self.resize(constants.MAIN_WINDOW_WIDTH, constants.MAIN_WINDOW_LENGTH)

        # =========================
        # CENTRAL WIDGET
        # =========================
        self.central = QtWidgets.QWidget()
        self.setCentralWidget(self.central)

        self.main_layout = QtWidgets.QVBoxLayout(self.central)

        # =========================
        # TABS 
        # =========================
        self.tabs = QtWidgets.QTabWidget()
        self.main_layout.addWidget(self.tabs)
        
        # =========================
        # ADD AUTOCOMPLETE
        # =========================
        self.ingredient_model = QtCore.QStringListModel()
        self.ingredient_completer = QtWidgets.QCompleter(self.ingredient_model)
        self.ingredient_completer.setCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)
        self.ingredient_completer.setFilterMode(QtCore.Qt.MatchFlag.MatchContains)

        # =========================
        # DATABASE
        # =========================
        self.repo = RecipeRepository()
        
        # Edit state tracking
        self.editing_recipe_id = None
        
        self.current_recipe_id = None

        self.editing_ingredient_name = None

        self.last_query = ""
        
        self.units = self.repo.get_units()

        self.unit_map = {u["name"]: u["id"] for u in self.units}
        
        # build tabs
        self.build_search_tab()
        self.build_add_tab()  
        self.build_add_ing()      # Add ingredient BEFORE view ingredient
        self.build_ingredient()   # View ingredient LAST
        
        # Temp File Cleaning
        # Clean up any stale temp files from previous runs
        temp_dir = Path("./temp")
        if temp_dir.exists():
            for i in range(1, 7):
                label_file = temp_dir / f"label_{i}.png"
                if label_file.exists():
                    try:
                        label_file.unlink()
                        logging.info(f"Cleaned up stale temp file: {label_file}")
                    except Exception as e:
                        logging.warning(f"Failed to clean up {label_file}: {e}")

        QtCore.QTimer.singleShot(0, self.search)

        
    # =====================================================
    # SEARCH TAB
    # =====================================================
    def build_search_tab(self):
        self.search_tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(self.search_tab)
    
        # =========================
        # STACK (search + detail)
        # =========================
        self.search_stack = QtWidgets.QStackedWidget()
        layout.addWidget(self.search_stack)
    
        # =========================
        # PAGE 1: SEARCH
        # =========================
        self.search_page = QtWidgets.QWidget()
        search_layout = QtWidgets.QVBoxLayout(self.search_page)
    
        # --- top bar ---
        top_bar = QtWidgets.QHBoxLayout()
    
        self.search_box = QtWidgets.QLineEdit()
        self.search_box.setPlaceholderText("Search recipes...")
        self.search_box.returnPressed.connect(self.search)
    
        self.search_btn = QtWidgets.QPushButton("Search")
        self.search_btn.clicked.connect(self.search)
    
        top_bar.addWidget(self.search_box)
        top_bar.addWidget(self.search_btn)
    
        search_layout.addLayout(top_bar)
    
        # =========================
        # MODEL 
        # =========================
        self.model = QtGui.QStandardItemModel(self)
    
        # =========================
        # LIST VIEW
        # =========================
        self.list_view = QtWidgets.QListView()
        self.list_view.setModel(self.model)
    
        self.list_view.setMouseTracking(True)
        self.list_view.viewport().setMouseTracking(True)
    
        self.list_view.setSpacing(constants.LIST_VIEW_SPACING)
        self.list_view.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.list_view.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
    
        self.list_view.setStyleSheet("""
            QListView {
                background: white;
                border: none;
            }
    
            QListView::item {
                background: transparent;
            }
    
            QListView::item:selected {
                background: transparent;
            }
        """)
    
        # =========================
        # DELEGATE
        # =========================
        self.list_view.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_view.customContextMenuRequested.connect(self.show_context_menu)

        self.list_view.setItemDelegate(
            RecipeDelegate(
                parent=self.list_view,
                colour_func=self.colour_decide,
                open_callback=self.open_recipe
            )
        )
    
        search_layout.addWidget(self.list_view)
            
        # =========================
        # PAGE 2: DETAIL (CLEAN VERSION)
        # =========================
        
        self.detail_page = QtWidgets.QWidget()
        detail_layout = QtWidgets.QVBoxLayout(self.detail_page)
        
        # -------------------------
        # TOP BUTTONS
        # -------------------------
        button_layout = QtWidgets.QHBoxLayout()
        
        back_btn = QtWidgets.QPushButton("← Back")
        back_btn.clicked.connect(
            lambda: (
                Path("./temp/label_1.png").unlink(missing_ok=True),
                Path("./temp/label_2.png").unlink(missing_ok=True),
                Path("./temp/label_3.png").unlink(missing_ok=True),
                Path("./temp/label_4.png").unlink(missing_ok=True),
                Path("./temp/label_5.png").unlink(missing_ok=True),
                Path("./temp/label_6.png").unlink(missing_ok=True),
                self.search_stack.setCurrentWidget(self.search_page),
            )
        )
        
        edit_btn = QtWidgets.QPushButton("Edit Recipe")
        edit_btn.clicked.connect(self.handle_edit)
        
        pdf_btn = QtWidgets.QPushButton("Export to PDF")
        pdf_btn.clicked.connect(self.handle_export)
        
        button_layout.addWidget(back_btn)
        button_layout.addWidget(edit_btn)
        button_layout.addWidget(pdf_btn)
        
        detail_layout.addLayout(button_layout)
        
        # =========================
        # SINGLE SCROLL AREA
        # =========================
        self.scroll = QtWidgets.QScrollArea()
        self.scroll.setWidgetResizable(True)
        
        self.detail_container = QtWidgets.QWidget()
        self.detail_layout = QtWidgets.QVBoxLayout(self.detail_container)
        self.detail_layout.setContentsMargins(10, 10, 10, 10)
        self.detail_layout.setSpacing(12)
        
        self.scroll.setWidget(self.detail_container)
        detail_layout.addWidget(self.scroll)
        
        # =========================
        # RECIPE TEXT
        # =========================
        self.scroll_content = QtWidgets.QTextBrowser()
        self.scroll_content.setOpenExternalLinks(True)

        
        self.detail_layout.addWidget(self.scroll_content)
        
        # =========================
        # NUTRITION CBAR
        # =========================
        self.nutrition_layout = QtWidgets.QVBoxLayout()
        self.nutrition_layout.setContentsMargins(0, 0, 0, 0)
        self.nutrition_layout.setSpacing(4)
        
        self.nutrition_title = QtWidgets.QLabel("Nutrient Labels: (Per Serving)")
        self.nutrition_title.setStyleSheet("""
            font-weight: bold;
            font-size: 14px;
            margin-top: 10px;
        """)
        
        self.nutrition_layout.addWidget(self.nutrition_title)
  
        self.nutrition_row = QtWidgets.QWidget()
        self.nutrition_row_layout = QtWidgets.QHBoxLayout(self.nutrition_row)
        self.nutrition_row_layout.setContentsMargins(0, 0, 0, 0)
        self.nutrition_row_layout.setSpacing(6)
        
        self.nutrition_layout.addWidget(self.nutrition_row)
        self.detail_layout.addLayout(self.nutrition_layout)
        
        # add pages
        self.search_stack.addWidget(self.search_page)
        self.search_stack.addWidget(self.detail_page)
        
        self.tabs.addTab(self.search_tab, "Recipes")
        
    ############################################################################
    def build_add_tab(self):
        self.add_tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(self.add_tab)

        
        ###################################################
        top_bar = QtWidgets.QHBoxLayout()
        title = QtWidgets.QLabel("<h3>Recipe Name:</h3>")
        top_bar.addWidget(title)

        self.name_box = QtWidgets.QLineEdit()
        self.name_box.setPlaceholderText("Recipe Name")

        serving_label = QtWidgets.QLabel("<h3>Servings:</h3>")
        self.servings = QtWidgets.QLineEdit()
        self.servings.setPlaceholderText("Servings (per no. of people)")

        top_bar.addWidget(self.name_box, stretch=7)
        top_bar.addWidget(serving_label)
        top_bar.addWidget(self.servings, stretch=3)
        
        layout.addLayout(top_bar)
        ###################################################
        desc_bar = QtWidgets.QHBoxLayout()
        desc_label = QtWidgets.QLabel("<h3>Description:</h3>")
        self.description = QtWidgets.QLineEdit()
        self.description.setPlaceholderText("Brief description (optional)")
        
        desc_bar.addWidget(desc_label)
        desc_bar.addWidget(self.description)
        layout.addLayout(desc_bar)
        
        ###################################################
        #mid bar
        mid_bar = QtWidgets.QVBoxLayout()
        sub_mid_bar = QtWidgets.QHBoxLayout()
        ing = QtWidgets.QLabel("<h3>Ingredients:</h3>")
        mid_bar.addWidget(ing)
        
        plus_btn = QtWidgets.QPushButton("Add Ingredient")
        
        minus_btn = QtWidgets.QPushButton("Remove Ingredient")
        
        sub_mid_bar.addWidget(plus_btn)
        sub_mid_bar.addWidget(minus_btn)
        
        mid_bar.addLayout(sub_mid_bar)
        layout.addLayout(mid_bar)

        ###################################################
        # ingredients area
        # Table with 3 columns
        self.table = QtWidgets.QTableWidget(0, 3)  # start with 0 rows
        self.table.setHorizontalHeaderLabels(["Name", "Amount", "Unit"])
        

        self.table.setSizePolicy(
                QtWidgets.QSizePolicy.Policy.Expanding,
                QtWidgets.QSizePolicy.Policy.Expanding
        )
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)

        # Button to add/remove rows
        plus_btn.clicked.connect(self.add_row)
        minus_btn.clicked.connect(self.remove_row)
        
        self.table.setStyleSheet("background-color: #f0f0f0;")

        # Layout
        table_layout = QtWidgets.QVBoxLayout()
        table_layout.addWidget(self.table)
        
        container = QtWidgets.QWidget()
        container.setLayout(table_layout)
        layout.addWidget(container)
        
        ###################################################
        steps_bar = QtWidgets.QHBoxLayout()
        
        method = QtWidgets.QLabel("<h3>Method:</h3>")
        layout.addWidget(method)
        
        add_step = QtWidgets.QPushButton("Add Step")
        steps_bar.addWidget(add_step)
        
        # =========================
        # STEP EDITOR CONTAINER
        # =========================
        self.step_container = QtWidgets.QWidget()
        self.step_layout = QtWidgets.QVBoxLayout(self.step_container)
        self.step_layout.setContentsMargins(0, 0, 0, 0)
        self.step_layout.setSpacing(6)
        self.step_layout.addStretch()  # keeps items top-aligned
        
        self.step_scroll = QtWidgets.QScrollArea()
        self.step_scroll.setWidgetResizable(True)
        self.step_scroll.setWidget(self.step_container)
        
        layout.addWidget(self.step_scroll)
        add_step.clicked.connect(self.add_step_func)
        
        self.add_step_func()
        layout.addLayout(steps_bar)
        ###################################################
        # bottom bar
        bottom_bar = QtWidgets.QHBoxLayout()
        self.save_btn = QtWidgets.QPushButton("Add Recipe")
        self.save_btn.clicked.connect(self.handle_save_recipe)
        
        layout.addStretch()
        
        bottom_bar.addWidget(self.save_btn)
        
        cancel_btn = QtWidgets.QPushButton("Clear")
        cancel_btn.clicked.connect(self.clear_all)
        bottom_bar.addWidget(cancel_btn)
        
        layout.addLayout(bottom_bar)
        ###################################################
        self.tabs.addTab(self.add_tab, "Add Recipe")
        
    ################################################################
    def build_ingredient(self):
        self.ing_tab = QtWidgets.QWidget()
        layout_ing = QtWidgets.QVBoxLayout(self.ing_tab)
        search_la = QtWidgets.QHBoxLayout()
        layout_ing_h = QtWidgets.QHBoxLayout()

        split_1 = QtWidgets.QVBoxLayout()

        split_2 = QtWidgets.QVBoxLayout()

        buttons = QtWidgets.QHBoxLayout()
        
        ###################################################
        title = QtWidgets.QLabel("<h3>Ingredient Database</h3>")
        layout_ing.addWidget(title)
        
        self.search_box_ing = QtWidgets.QLineEdit()
        self.search_box_ing.setPlaceholderText("Search ingredients...")
        self.search_box_ing.returnPressed.connect(self.search_ing)
        search_box_ing_but = QtWidgets.QPushButton("Search")
        search_box_ing_but.clicked.connect(self.search_ing)
        
        search_la.addWidget(self.search_box_ing)
        search_la.addWidget(search_box_ing_but)
        split_1.addLayout(search_la)
        
        ###################################################
        self.list_ing_widget = QtWidgets.QListWidget()
        rows_ing = self.repo.search_ingredients("")
        self.list_ing_widget.addItems(rows_ing)

        self.list_ing_widget.currentItemChanged.connect(self.populate_ing_nutr_table)
        
        split_1.addWidget(QtWidgets.QLabel("<h3>Ingredients</h3>"))
        split_1.addWidget(self.list_ing_widget)

        ###################################################
        name_row = QtWidgets.QHBoxLayout()

        name_row.addWidget(QtWidgets.QLabel("<h3>Name:</h3>"))
        
        self.name_display = QtWidgets.QLineEdit()
        self.name_display.setReadOnly(True)
        self.name_display.setStyleSheet("""
            QLineEdit {
                background-color: #f0f0f0;
            }
        """)
        name_row.addWidget(self.name_display)
        
        split_2.addLayout(name_row)
        ###################################################
        split_2.addWidget(QtWidgets.QLabel("<h3>Description:</h3>"))

        self.desc_box = QtWidgets.QTextEdit()
        self.desc_box.setReadOnly(True)
        self.desc_box.setStyleSheet("""
            QTextEdit {
                background-color: #f0f0f0;
            }
        """)
        self.desc_box.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding
        )
        
        split_2.addWidget(self.desc_box, 1)
        ###################################################
        
        
        ###################################################
        # Table with 3 columns
        self.table_ingred = QtWidgets.QTableWidget(0, 3)  # start with 0 rows
        self.table_ingred.setHorizontalHeaderLabels(["Nutrients", "Amount", "Unit"])
                    
        self.table_ingred.setSizePolicy(
                QtWidgets.QSizePolicy.Policy.Expanding,
                QtWidgets.QSizePolicy.Policy.Expanding
        )
        
        header = self.table_ingred.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        
        self.table_ingred.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_ingred.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)

        
        self.table_ingred.setStyleSheet("background-color: #f0f0f0;")
        
        split_2.addWidget(self.table_ingred, 3)
        ###################################################
        edit_box_ing_but = QtWidgets.QPushButton("Edit")
        edit_box_ing_but.clicked.connect(self.edit_ingredient)
        
        delete_box_ing_but = QtWidgets.QPushButton("Delete")
        delete_box_ing_but.clicked.connect(self.delete_ingredient)
        
        buttons.addWidget(edit_box_ing_but)
        buttons.addWidget(delete_box_ing_but)
        ###################################################
        layout_ing_h.addLayout(split_1, 1)
        layout_ing_h.addLayout(split_2, 2)
        
        #layout_ing.addLayout(search_la)
        layout_ing.addLayout(layout_ing_h)
        layout_ing.addLayout(buttons)
        ###################################################
        self.tabs.addTab(self.ing_tab, "Ingredients")
        
        
        
    ################################################################
    def build_add_ing(self):
        self.add_ing_tab = QtWidgets.QWidget()
        layout_ing = QtWidgets.QVBoxLayout(self.add_ing_tab)
        layout_ing.setContentsMargins(5, 5, 5, 5)
        layout_ing.setSpacing(6)
        
        ###################################################
        top_bar_ing = QtWidgets.QHBoxLayout()
        title_ing = QtWidgets.QLabel("<h3>Ingredient Name:</h3>")
        top_bar_ing.addWidget(title_ing)

        self.name_box_ing = QtWidgets.QLineEdit()
        self.name_box_ing.setPlaceholderText("Ingredient Name")

        top_bar_ing.addWidget(self.name_box_ing)
        
        layout_ing.addLayout(top_bar_ing)
        ###################################################
        desc_title_ing = QtWidgets.QLabel("<h3>Description:</h3>")
        desc_title_ing.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Preferred,
            QtWidgets.QSizePolicy.Policy.Fixed
        )
        self.desc_box_ing = QtWidgets.QTextEdit()
        self.desc_box_ing.setStyleSheet("""
            QTextEdit {
                background-color: #f0f0f0;
            }
        """)
        
        font_metrics = self.desc_box_ing.fontMetrics()
        line_height = font_metrics.lineSpacing()
        
        self.desc_box_ing.setMinimumHeight(line_height * 2 + 8)
        self.desc_box_ing.setMaximumHeight(line_height * 5 + 12)
        
        mid_top_ing = QtWidgets.QVBoxLayout()
        mid_top_ing.setContentsMargins(0, 0, 0, 0)
        mid_top_ing.setSpacing(4)
        mid_top_ing.addWidget(desc_title_ing)
        mid_top_ing.addWidget(self.desc_box_ing)
        
        layout_ing.addLayout(mid_top_ing)
        ###################################################
        #mid bar
        mid_bar_ing = QtWidgets.QVBoxLayout()
        nutr = QtWidgets.QLabel("<h3>Nutrients:</h3>")
        mid_bar_ing.addWidget(nutr)

        layout_ing.addLayout(mid_bar_ing)

        ###################################################
        # ingredients area
        # Table with 3 columns
        self.table_ing = QtWidgets.QTableWidget(0, 3)  # start with 0 rows
        self.table_ing.setHorizontalHeaderLabels(["Nutrients", "Amount", "Unit"])
        
        self.ing_add_nutrient_table_add()
                    
        self.table_ing.setSizePolicy(
                QtWidgets.QSizePolicy.Policy.Expanding,
                QtWidgets.QSizePolicy.Policy.Expanding
        )

        header = self.table_ing.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        
        self.table_ing.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_ing.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)

        
        self.table_ing.setStyleSheet("background-color: #f0f0f0;")

        # Layout
        table_layout_ing = QtWidgets.QVBoxLayout()
        table_layout_ing.addWidget(self.table_ing)
        
        layout_ing.addLayout(table_layout_ing)
        
        ###################################################
        # bottom bar
        bottom_bar_ing = QtWidgets.QHBoxLayout()
        self.save_btn_ing = QtWidgets.QPushButton("Add Ingredient")
        self.save_btn_ing.clicked.connect(self.handle_save_ingredient)
                                                
        
        bottom_bar_ing.addWidget(self.save_btn_ing)
        
        cancel_btn_ing = QtWidgets.QPushButton("Clear")
        cancel_btn_ing.clicked.connect(self.clear_ingredient_form)
        bottom_bar_ing.addWidget(cancel_btn_ing)
        
        layout_ing.addLayout(bottom_bar_ing)
        
        self.tabs.addTab(self.add_ing_tab, "Add Ingredient")
        

    ################################################################
    def show_context_menu(self, pos):
        index = self.list_view.indexAt(pos)
        if not index.isValid():
            return
    
        recipe_id = index.data(QtCore.Qt.ItemDataRole.UserRole)
    
        menu = QtWidgets.QMenu(self)
    
        open_action = menu.addAction("Open")
        delete_action = menu.addAction("Delete")
    
        action = menu.exec(self.list_view.viewport().mapToGlobal(pos))
    
        if action == open_action:
            self.open_recipe(recipe_id)
    
        elif action == delete_action:
            self.delete_recipe(recipe_id)
        
    def add_row(self):
        row = self.table.rowCount()
        self.table.insertRow(row)
    
        # --- NAME (autocomplete) ---
        name_edit = QtWidgets.QLineEdit()
        name_edit.setCompleter(self.ingredient_completer)
        name_edit.textEdited.connect(self.update_ingredient_suggestions)
        self.table.setCellWidget(row, 0, name_edit)
    
        # --- AMOUNT ---
        amount_edit = QtWidgets.QLineEdit()
        self.table.setCellWidget(row, 1, amount_edit)
    
        # --- UNIT (dropdown) ---
        unit_combo = QtWidgets.QComboBox()
        unit_combo.addItem("")  # Allow empty unit
        unit_combo.addItems(self.unit_map.keys())
        
        # SET DEFAULT TO "g"
        unit_combo.setCurrentText("g")
        
        self.table.setCellWidget(row, 2, unit_combo)
    
    def add_row_ingr(self, name, amount, unit):
        name = str(name)
        amount = str(round(amount, 3))
        unit = str(unit)
        
        row = self.table_ingred.rowCount()
        self.table_ingred.insertRow(row)
    
        # --- NAME ---
        name_edit = QtWidgets.QTableWidgetItem(name)
        self.table_ingred.setItem(row, 0, name_edit)
    
        # --- AMOUNT ---
        amount_edit = QtWidgets.QTableWidgetItem(amount)
        amount_edit.setText(amount)
        self.table_ingred.setItem(row, 1, amount_edit)
    
        # --- UNIT ---
        unit_edit = QtWidgets.QTableWidgetItem(unit)
        self.table_ingred.setItem(row, 2, unit_edit)
            
    def remove_row(self):
        selected = self.table.selectionModel().selectedRows()
    
        if not selected:
            return
    
        for index in sorted(selected, key=lambda x: x.row(), reverse=True):
            self.table.removeRow(index.row())
            
    def ing_add_nutrient_table_add(self):
        nutrients = [
            (item["display_name"], item["unit"])
            for item in constants.by_display_name.values()
        ]
        
        for nutrient in nutrients:
            row = self.table_ing.rowCount()
            self.table_ing.insertRow(row)
        
            # --- NUTRIENT NAME (read-only or editable) ---
            name_item_ing = QtWidgets.QTableWidgetItem(nutrient[0])
            self.table_ing.setItem(row, 0, name_item_ing)
        
            # --- AMOUNT ---
            amount_edit_ing = QtWidgets.QLineEdit()
            self.table_ing.setCellWidget(row, 1, amount_edit_ing)
        
            # --- UNIT ---
            unit_item_ing = QtWidgets.QTableWidgetItem(nutrient[1])
            unit_item_ing.setFlags(
                unit_item_ing.flags() &
                ~QtCore.Qt.ItemFlag.ItemIsEditable
            )
            
            self.table_ing.setItem(row, 2, unit_item_ing)
                
    def get_ingredient_data(self):
        data = []
        
        for row in range(self.table.rowCount()):
            name_widget = self.table.cellWidget(row, 0)
            amount_widget = self.table.cellWidget(row, 1)
            unit_widget = self.table.cellWidget(row, 2)
            
            name = name_widget.text().strip() if name_widget else ""
            
            try:
                text = amount_widget.text().replace(",", ".")
                amount = float(text) if amount_widget else 0.0
            except ValueError:
                raise ValueError(f"Row {row + 1}: Invalid amount")
            
            unit_name = unit_widget.currentText().strip() if unit_widget else ""
            
            if not name and not amount and not unit_name:
                continue
            
            if not name:
                raise ValueError(f"Row {row + 1}: Ingredient name cannot be empty")
            
            if amount <= 0:
                raise ValueError(f"{name}: amount must be > 0")
            
            # Handle empty unit (should be allowed)
            unit_id = self.unit_map.get(unit_name) if unit_name else None
            
            if unit_name and unit_name not in self.unit_map:
                raise ValueError(f"Unit '{unit_name}' not found. Create it first.")
            
            data.append(
                IngredientInput(
                    name=name,
                    amount=amount,
                    unit_name=unit_name,
                    unit_id=unit_id
                )
            )
        
        return data
    
    def get_steps_structured(self):
        steps = []
    
        for i in range(self.step_layout.count()):
            item = self.step_layout.itemAt(i)
            widget = item.widget()
    
            if isinstance(widget, StepWidget):
                text = widget.text()
                if text:
                    steps.append({
                        "index": len(steps) + 1,
                        "text": text
                    })
    
        return steps
    
    def export_pdf(self, recipe_name):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save PDF",
            f"{recipe_name}.pdf",
            "PDF Files (*.pdf)"
        )
    
        if not file_path:
            return
    
        # -----------------------------
        # BUILD HTML PROPERLY
        # -----------------------------
        base_html = self.scroll_content.toHtml()

        images = sorted(Path("temp").resolve().glob("label_*.png"))
        
        img_html = "<table>"
        
        for i, img in enumerate(images):
            if i % 2 == 0:
                img_html += "<tr>"
        
            img_html += f"""
            <td style="text-align:center;padding:5px;">
                <img src="{img}" width="400">
            </td>
            """
        
            if i % 2 == 1:
                img_html += "</tr>"
        
        if len(images) % 2 == 1:
            img_html += "<td></td></tr>"
        
        img_html += "</table>"
        
        full_html = f"""
                <html>
                <head>
                <meta charset="utf-8">
                </head>
                <body>
                {base_html}
                {img_html}
                </body>
                </html>
                """
                
        # enable logging
        pisa.showLogging()
        
        with open(file_path, "w+b") as result_file:
            # convert HTML to PDF
            pisa_status = pisa.CreatePDF(
                full_html,       # page data
                dest=result_file,  # destination file
            )
        
            # Check for errors
            if pisa_status.err:
                print("An error occurred!")
    
    
    def populate_ing_nutr_table(self, current, previous):
        self.table_ingred.setRowCount(0)
        self.name_display.setText("")
        self.desc_box.setText("")
        
        if not current or not hasattr(current, 'text'):
            return
        
        self.name_display.setText(str(current.text()))

        # Safe ingredient info fetch
        ing_info = self.repo.get_ingredient_info(current.text())
        if ing_info:
            self.desc_box.setText(ing_info[0][4] or "")
    
        nutr = self.repo.get_ingredient_nutrition(current.text())
    
        # convert SQL result → dictionary
        data = {
            name: (amount, unit)
            for name, unit, amount in nutr
        }
    
        nutrients = [
            (item["display_name"], item["unit"])
            for item in constants.by_display_name.values()
        ]
        
    
        for name, expected_unit in nutrients:
            if name not in data:
                continue
    
            amount, unit = data[name]
    
            self.add_row_ingr(name, amount, unit)
            
        
        
    def clear_all(self):
        self.table.setRowCount(0)
        self.name_box.clear()
        self.servings.clear()
        self.description.clear()
    
        # clear steps
        self.clear_steps()
    
        self.editing_recipe_id = None
        self.save_btn.setText("Add Recipe")
    
        self.add_step_func()
        
    def clear_ingredient_form(self):
        self.name_box_ing.clear()
        self.desc_box_ing.clear()
        self.editing_ingredient_name = None
        self.save_btn_ing.setText("Add Ingredient")
        
        for row in range(self.table_ing.rowCount()):
            widget = self.table_ing.cellWidget(row, 1)
            if widget:
                widget.clear()
    
    def clear_steps(self):
        # Remove all widgets (including stretch)
        while self.step_layout.count() > 0:
            item = self.step_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        # Add fresh stretch at end
        self.step_layout.addStretch()
        
    def refresh(self):
        self.search_box.setText(self.last_query)
        self.search()
        self.search_box.setFocus()
        
    def add_step_func(self):
        step_index = sum(
                        1 for i in range(self.step_layout.count())
                        if isinstance(self.step_layout.itemAt(i).widget(), StepWidget)
                        )  
    
        step_widget = StepWidget(step_number=step_index + 1)
        step_widget.request_delete.connect(self.delete_step)
        step_widget.height_changed.connect(self.reflow_steps)
    
        self.step_layout.insertWidget(self.step_layout.count() - 1, step_widget)
        self.reflow_steps()
    
    def delete_step(self, step_widget):
        self.step_layout.removeWidget(step_widget)
        step_widget.deleteLater()
        self.reflow_steps()
    
    def reflow_steps(self):
        index = 1
    
        for i in range(self.step_layout.count()):
            item = self.step_layout.itemAt(i)
            widget = item.widget()
    
            if isinstance(widget, StepWidget):
                widget.set_step_number(index)
                index += 1
        
    ################################################################
    # =====================================================
    # SEARCH LOGIC
    # =====================================================
    def search(self):
        query = self.search_box.text().strip()
    
        # store last query (useful for refresh after edits/deletes)
        self.last_query = query
    
        rows = self.repo.search(query) or []
    
        self.model.clear()
    
        if not rows:
            item = QtGui.QStandardItem("No recipes found")
            item.setEnabled(False)
            self.model.appendRow(item)
            return
    
        for recipe_id, name, *_ in rows:
            item = QtGui.QStandardItem()
            item.setData(name, QtCore.Qt.ItemDataRole.DisplayRole)
            item.setData(recipe_id, QtCore.Qt.ItemDataRole.UserRole)
            self.model.appendRow(item)
    
    def search_ing(self):
        query = self.search_box_ing.text().strip()
    
        rows = self.repo.search_ingredients(query)
    
        self.list_ing_widget.clear()
        self.list_ing_widget.addItems(rows)
            
    
    def update_ingredient_suggestions(self, text):
        if not text.strip():
            self.ingredient_model.setStringList([])
            return
    
        results = self.repo.search_ingredients(text)
        self.ingredient_model.setStringList(results)
    
    # Add a method to refresh ingredient cache after adding:
    def refresh_ingredient_completer(self):
        """Call this after adding a new ingredient"""
        self.repo.ingredient_cache.clear()
        # Optionally, refresh current suggestions
        current_text = self.name_box_ing.text()
        if current_text:
            self.update_ingredient_suggestions(current_text)
    
    # =====================================================
    # CARDS
    # =====================================================
    def colour_decide(self, recipe_id):
        h = hashlib.md5(str(recipe_id).encode()).hexdigest()
    
        hue = int(h[0:2], 16) % 360      # stable hue cycle
        sat = 90                        # keep saturation controlled
        val = 240                       # high brightness (key fix)
    
        color = QtGui.QColor()
        color.setHsv(hue, sat, val)
    
        return color

    # =====================================================
    # DETAIL VIEW
    # =====================================================
    def open_recipe(self, recipe_id):
        self.current_recipe_id = recipe_id
    
        recipe = self.get_recipe_by_id(recipe_id)
        if not recipe:
            return
    
        # =========================
        # BASE HTML + STYLES
        # =========================
        html_parts = ["""
        <html>
        <head>
        <style>
            body {
                font-family: "Segoe UI", Arial;
                font-size: 11pt;
                color: #2b2b2b;
                margin: 16px;
                background: white;
            }
    
            h2 {
                color: #2E7D32;
                margin-bottom: 6px;
            }
    
            h3 {
                color: #1565C0;
                margin-top: 8px;
                margin-bottom: 8px;
                border-bottom: 1px solid #E0E0E0;
                padding-bottom: 4px;
            }
    
            .info {
                background: white;
                border: 1px solid #DDD;
                border-radius: 6px;
                padding: 10px;
                margin-bottom: 14px;
            }
    
            .ingredients {
                margin-left: 25px;
            }
            
            .ingredient {
                margin: 3px 0;
                text-indent: -12px;
                padding-left: 12px;
            }
                        
            .step-title {
                font-weight: bold;
                color: #2E7D32;
                margin-bottom: 2px;
                margin-left: 10px;
            }
            
            .step {
                background: #FAFAFA;
                border-left: 5px solid #4CAF50;
                border-radius: 6px;
            
                padding: 10px 12px;
                margin-bottom: 6px;
            

                margin-left: 20px;
            }
            
            p {
                line-height: 1.3;
                margin: 2px 0 4px 0;
            }
        </style>
        </head>
        <body>
        """]
    
        # =========================
        # TITLE
        # =========================
        html_parts.append(f"<h2>{escape(recipe.name)}</h2>")
    
        # =========================
        # SERVINGS
        # =========================
        if recipe.servings:
            html_parts.append(f"""
            <div class="info">
                <b>Servings:</b> {escape(str(recipe.servings))}
            </div>
            """)
    
        # =========================
        # DESCRIPTION
        # =========================
        if recipe.description:
            html_parts.append("<h3>Description:</h3>")
            html_parts.append(f"<p>{escape(recipe.description)}</p>")
    
        # =========================
        # INGREDIENTS
        # =========================
        html_parts.append("<h3>Ingredients:</h3>")
        html_parts.append("<div class='ingredients'>")
        
        for ing in (recipe.ingredients or []):
            unit = ing.unit_name or ""
            html_parts.append(
                f"<p class='ingredient'>"
                f"&#8226;&nbsp;&nbsp;<b>{escape(ing.display_name)}</b>: "
                f"{escape(str(ing.amount))} {escape(unit)}</p>"
            )
        
        html_parts.append("</div>")
    
        # =========================
        # METHOD
        # =========================
        html_parts.append("<h3>Method:</h3>")
    
        for step in recipe.steps:
            step_text = escape(step.text).replace("\n", "<br>")
        
            html_parts.append(f"""
            <div>
                <div class="step-title">
                    Step {step.index}:
                </div>
        
            <div class="step">
                    {step_text}
                </div>
            </div>
            """)
    
        # =========================
        # CLOSE HTML
        # =========================
        html_parts.append("</body></html>")
    
        html = "\n".join(html_parts)
    
        # =========================
        # DISPLAY
        # =========================
        self.scroll_content.setHtml(html)
        self.scroll_content.verticalScrollBar().setValue(0)
    
        # =========================
        # NUTRITION
        # =========================
        success = self.make_nutrition(recipe_id)
        
        if success:
            images = [
                str(Path("./temp/label_1.png").resolve()),
                str(Path("./temp/label_2.png").resolve()),
                str(Path("./temp/label_3.png").resolve()),
                str(Path("./temp/label_4.png").resolve()),
                str(Path("./temp/label_5.png").resolve()),
                str(Path("./temp/label_6.png").resolve()),
            ]
        
            self.set_nutrition_images(images)
        
        else:
            self.clear_layout(self.nutrition_row_layout)
        
            label = QtWidgets.QLabel("No Nutritional Information Available")
            label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        
            self.nutrition_row_layout.addStretch()
            self.nutrition_row_layout.addWidget(label)
            self.nutrition_row_layout.addStretch()
    
        # =========================
        # NAVIGATION
        # =========================
        self.search_stack.setCurrentWidget(self.detail_page)
    
    def open_image_popup(self, path):
        dlg = QtWidgets.QDialog(self)
        dlg.setWindowTitle("Nutrition Label")
    
        layout = QtWidgets.QVBoxLayout(dlg)
        layout.setContentsMargins(0, 0, 0, 0)
    
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(False)
        scroll.setContentsMargins(0, 0, 0, 0)
        scroll.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
    
        scroll.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        scroll.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
    
        # force full background consistency
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: #f2f2f2;
            }
            QScrollArea::viewport {
                background: #f2f2f2;
            }
        """)
    
        label = QtWidgets.QLabel()
        label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
    
        # label must also have explicit background
        label.setStyleSheet("background: #f2f2f2;")
    
        pixmap = QtGui.QPixmap(path)
    
        target_width = constants.RECIPE_APP_OPEN_IMAGE_POPUP_T_WIDTH
    
        scaled_pixmap = pixmap.scaled(
            target_width,
            10_000,
            QtCore.Qt.AspectRatioMode.KeepAspectRatio,
            QtCore.Qt.TransformationMode.SmoothTransformation
        )
    
        label.setPixmap(scaled_pixmap)
        scroll.setWidget(label)

        scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        label.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Fixed,
            QtWidgets.QSizePolicy.Policy.Fixed
        )
    
        layout.addWidget(scroll)
    
        dlg.resize(target_width + constants.RECIPE_APP_OPEN_IMAGE_POPUP_T_WIDTH_PADDING, constants.RECIPE_APP_OPEN_IMAGE_POPUP_LENGTH)
        dlg.exec()
    
    def set_nutrition_images(self, images):
        # clear old buttons
        while self.nutrition_row_layout.count():
            item = self.nutrition_row_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
        labels = [
            "General",
            "Fats",
            "Carbs",
            "Vitamins",
            "Minerals",
            "Phytonutrients",
        ]
    
        for text, path in zip(labels, images):
            btn = QtWidgets.QPushButton(text)
    
            btn.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(
                lambda checked=False, p=path: self.open_image_popup(p)
            )

    
            self.nutrition_row_layout.addWidget(btn, 1)
    
    

    def replace_placeholders(self, obj, values):
        pattern = re.compile(r"\{\{(.*?)\}\}")

        if isinstance(obj, dict):
            return {k: self.replace_placeholders(v, values) for k, v in obj.items()}
        
        elif isinstance(obj, list):
            return [self.replace_placeholders(item, values) for item in obj]
        
        elif isinstance(obj, str):
            def repl(match):
                key = match.group(1)
                return str(values.get(key, match.group(0)))  # fallback keeps original
            
            return pattern.sub(repl, obj)
        
        return obj

    def make_nutrition(self, recipe_id):
        Path("temp").mkdir(parents=True, exist_ok=True)

        # -------------------------------------------------
        # GET ALL NUTRIENTS FROM DB VIEW
        # -------------------------------------------------
        rows = self.repo.get_recipe_nutrition_per_serving(recipe_id)

        g = {}
        for display_name, unit, amount in rows:
            g[display_name] = round(amount, 2)

        for name in self.repo.get_all_nutrient_names():
            if name not in g:
                g[name] = 0
            
        nutrition_json_edit = self.replace_placeholders(constants.nutrition_json, g)
        
        try:
            render_all(nutrition_json_edit, Path("./temp"))
            return True
        except Exception as e:
            logging.error(f"Error rendering nutrition labels: {e}")
            
            Path("./temp/label_1.png").unlink(missing_ok=True)
            Path("./temp/label_2.png").unlink(missing_ok=True)
            Path("./temp/label_3.png").unlink(missing_ok=True)
            Path("./temp/label_4.png").unlink(missing_ok=True)
            Path("./temp/label_5.png").unlink(missing_ok=True)
            Path("./temp/label_6.png").unlink(missing_ok=True)
            return False
        
    def clear_layout(self, layout):
        if layout is None:
            return
    
        while layout.count():
            item = layout.takeAt(0)
    
            widget = item.widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()
    
    def delete_recipe(self, recipe_id):
        if recipe_id is None:  
            return
        
        reply = QtWidgets.QMessageBox.warning(
            self,
            "Confirm Delete",
            "This recipe will be permanently deleted.",
            QtWidgets.QMessageBox.StandardButton.Yes |
            QtWidgets.QMessageBox.StandardButton.Cancel
        )
    
        if reply != QtWidgets.QMessageBox.StandardButton.Yes:
            return
    
        self.repo.delete(recipe_id)
        self.refresh()
    
    # =====================================================
    # EDIT INGREDIENT FUNCTION
    # =====================================================
    def edit_ingredient(self):
        """Load selected ingredient into edit form"""
        current_item = self.list_ing_widget.currentItem()
        
        if not current_item:
            QtWidgets.QMessageBox.warning(self, "Error", "Please select an ingredient to edit")
            return
        
        ingredient_name = current_item.text()
        info = self.repo.get_ingredient_info(ingredient_name)
        
        try:
            # Load ingredient name
            self.name_box_ing.setText(ingredient_name)

            self.desc_box_ing.clear()
            if info:  
                self.desc_box_ing.setText(info[0][4] or "")

            # Reset all nutrient fields
            for row in range(self.table_ing.rowCount()):
                widget = self.table_ing.cellWidget(row, 1)
                if widget:
                    widget.clear()
            
            # Get ingredient's current nutrients
            nutrients = self.repo.get_ingredient_nutrition(ingredient_name)

            
            # Create lookup from database results: DB_display_name -> (amount, unit)
            nutrient_lookup = {
                name: (amount, unit)
                for name, unit, amount in nutrients
            }
            
            # Populate table values
            for row in range(self.table_ing.rowCount()):
                ui_nutrient_name = self.table_ing.item(row, 0).text()
                
                # Get the database name for this UI field
                db_nutrient_name = ui_nutrient_name
                
                if db_nutrient_name and db_nutrient_name in nutrient_lookup:
                    amount, unit = nutrient_lookup[db_nutrient_name]
                    widget = self.table_ing.cellWidget(row, 1)
                    if widget:
                        widget.setText(str(round(amount, 3)))
            
            # Switch to Add Ingredient tab and mark as editing
            self.editing_ingredient_name = ingredient_name
            self.save_btn_ing.setText("Update Ingredient")
            self.tabs.setCurrentWidget(self.add_ing_tab)
            
        except Exception as e:
            logging.exception(e)
            QtWidgets.QMessageBox.critical(
                self,
                "Error",
                f"Failed to edit ingredient: {str(e)}"
            )
        
    
    # =====================================================
    # DELETE INGREDIENT FUNCTION
    # =====================================================
    def delete_ingredient(self):
        """Delete selected ingredient from database"""
        current_item = self.list_ing_widget.currentItem()
        
        if not current_item:
            QtWidgets.QMessageBox.warning(self, "Error", "Please select an ingredient to delete")
            return
        
        ingredient_name = current_item.text()
        
        # Confirm deletion
        reply = QtWidgets.QMessageBox.warning(
            self,
            "Confirm Delete",
            f"Delete ingredient '{ingredient_name}'? This cannot be undone.",
            QtWidgets.QMessageBox.StandardButton.Yes |
            QtWidgets.QMessageBox.StandardButton.Cancel
        )
        
        if reply != QtWidgets.QMessageBox.StandardButton.Yes:
            return
        
        try:
            # Get ingredient ID
            self.repo.cursor.execute(
                "SELECT id FROM ingredients WHERE name = ? COLLATE NOCASE",
                (ingredient_name,)
            )
            row = self.repo.cursor.fetchone()
            
            if not row:
                QtWidgets.QMessageBox.warning(self, "Error", "Ingredient not found")
                return
            
            ingredient_id = row[0]
            
            # Check if ingredient is used in any recipes
            self.repo.cursor.execute(
                "SELECT COUNT(*) FROM recipe_ingredients WHERE ingredient_id = ?",
                (ingredient_id,)
            )
            count = self.repo.cursor.fetchone()[0]
            
            if count > 0:
                QtWidgets.QMessageBox.warning(
                    self,
                    "Cannot Delete",
                    f"This ingredient is used in {count} recipe(s). Remove it from recipes first."
                )
                return
            
            # Delete ingredient and its nutrients
            with self.repo.conn:
                self.repo.cursor.execute(
                    "DELETE FROM ingredient_nutrients WHERE ingredient_id = ?",
                    (ingredient_id,)
                )
                self.repo.cursor.execute(
                    "DELETE FROM ingredients WHERE id = ?",
                    (ingredient_id,)
                )
            
            # Refresh UI
            self.repo.ingredient_cache.clear()
            self.search_ing()
            self.table_ingred.setRowCount(0)
            
            QtWidgets.QMessageBox.information(self, "Success", "Ingredient deleted successfully")
            
        except Exception as e:
            logging.exception(e)
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to delete ingredient: {str(e)}")

    
    def handle_edit(self):
        if self.current_recipe_id is not None:
            self.edit_recipe(self.current_recipe_id)
            
    def handle_export(self):
        if self.current_recipe_id is not None:
            name = self.repo.get_recipe_name(self.current_recipe_id)
            self.export_pdf(name)
            
    def edit_recipe(self, recipe_id):
        recipe = self.get_recipe_by_id(recipe_id)
        if not recipe:
            return
    
        self.editing_recipe_id = recipe_id
        self.save_btn.setText("Update Recipe")
        self.tabs.setCurrentWidget(self.add_tab)
    
        # --- basic fields ---
        self.name_box.setText(recipe.name)
        self.servings.setText(str(recipe.servings))
        self.description.setText(recipe.description)
    
        # --- ingredients ---
        self.table.setRowCount(0)

        for ing in recipe.ingredients:
            self.add_row()
        
            row = self.table.rowCount() - 1
        
            name_widget = self.table.cellWidget(row, 0)
            amount_widget = self.table.cellWidget(row, 1)
            unit_widget = self.table.cellWidget(row, 2)
        
            name_widget.setText(ing.display_name)
            amount_widget.setText(str(ing.amount))
            if ing.unit_name:
                unit_widget.setCurrentText(ing.unit_name)
            else:
                unit_widget.setCurrentIndex(0)  # Select the empty item
    
        # --- steps ---
        # =========================
        # CLEAR OLD STEPS
        # =========================
        self.clear_steps()
        
        # =========================
        # REBUILD STEPS
        # =========================
        for i, step in enumerate(recipe.steps):
            step_widget = StepWidget(
                text=step.text,
                step_number=i + 1
            )
        
            step_widget.request_delete.connect(self.delete_step)
            step_widget.height_changed.connect(self.reflow_steps)
        
            # insert above the stretch spacer
            self.step_layout.insertWidget(
                self.step_layout.count() - 1,
                step_widget
            )
        self.reflow_steps()
        
    def get_nutrient_data(self):
        nutrients_mapping = {
            item["display_name"] : item["name"] 
            for item in constants.by_display_name.values()
        }
    
        nutrients = []
    
        for row in range(self.table_ing.rowCount()):
    
            nutrient_name = self.table_ing.item(row, 0).text()
            nutrient_name = nutrients_mapping[nutrient_name]
    
            amount_widget = self.table_ing.cellWidget(row, 1)
    
            text = amount_widget.text().strip()
    
            if not text:
                continue
    
            try:
                amount = float(text.replace(",", "."))
            except ValueError:
                raise ValueError(
                    f"{nutrient_name}: invalid number"
                )
    
            if amount < 0:
                raise ValueError(
                    f"{nutrient_name}: cannot be negative"
                )
    
            nutrients.append(
                (
                    nutrient_name,
                    amount
                )
            )
    
        return nutrients
        
    def build_recipe_from_ui(self):
        name = self.name_box.text().strip()
        if not name:
            raise ValueError("Recipe name required")
        
        text = self.servings.text().strip()

        try:
            servings = float(text)
            if servings <= 0:
                raise ValueError
        except ValueError:
            raise ValueError("Servings must be a positive number")
        
        ingredients = [
            Ingredient(
                name=i.name.strip(),
                amount=i.amount,
                unit_id=i.unit_id,
                display_name=i.name.strip(),
                unit_name=i.unit_name
            )
            for i in self.get_ingredient_data()
        ]
    
        steps = [
            Step(i + 1, s["text"])
            for i, s in enumerate(self.get_steps_structured())
        ]
    
        return Recipe(
            name=name,
            servings=servings,
            description=self.description.text().strip(),
            ingredients=ingredients,
            steps=steps
        )
    
    def build_ingredient_from_ui(self):
    
        name = self.name_box_ing.text().strip()
        description = self.desc_box_ing.toPlainText().strip()
    
        if not name:
            raise ValueError(
                "Ingredient name required"
            )
    
        nutrients = self.get_nutrient_data()
    
        if not nutrients:
            raise ValueError(
                "Enter at least one nutrient value"
            )
    
        return name, description, nutrients
    
    def get_recipe_by_id(self, recipe_id):
        return self.repo.get(recipe_id)
    
    def handle_save_recipe(self):
        try:
            recipe = self.build_recipe_from_ui()
            recipe.normalize()
            recipe.validate()
            
            for ing in recipe.ingredients:
                try:
                    ingredient_id = self.repo.get_ingredient_id(ing.display_name, allow_create=False)
                except ValueError as e:
                    # get_ingredient_id already raises with message
                    raise ValueError(str(e)) from None
    
            if self.editing_recipe_id:
                self.repo.update(self.editing_recipe_id, recipe)
            else:
                self.repo.add(recipe)
    
            self.clear_all()
            self.refresh()
            self.editing_recipe_id = None
            self.current_recipe_id = None
            
            self.tabs.setCurrentWidget(self.search_tab)
            self.search_stack.setCurrentWidget(self.search_page)

            # restore previous search results
            self.search_box.setText(self.last_query)
    
            QtWidgets.QMessageBox.information(self, "Success", "Recipe Saved!")
    
        except ValueError as e:
            QtWidgets.QMessageBox.warning(self, "Validation Error", str(e))
    
        except sqlite3.IntegrityError as e:
            QtWidgets.QMessageBox.warning(
                self,
                "Database Error",
                f"Recipe already exists or data violates rules: {str(e)}",
            )
    
        except Exception as e:
            logging.exception(e)
            QtWidgets.QMessageBox.critical(self, "Unexpected Error", str(e))

    
    def handle_save_ingredient(self):
        try:
            name, description, nutrients = self.build_ingredient_from_ui()
            
            # Check if editing existing ingredient
            old_ingredient_name = getattr(self, 'editing_ingredient_name', None)
            is_editing = old_ingredient_name is not None
            
            # If name changed, delete old first
            if is_editing and old_ingredient_name.lower() != name.lower():
                self.repo.cursor.execute(
                    "SELECT id FROM ingredients WHERE name = ? COLLATE NOCASE",
                    (old_ingredient_name,)
                )
                row = self.repo.cursor.fetchone()
                
                if row:
                    ingredient_id = row[0]
                    with self.repo.conn:
                        self.repo.cursor.execute(
                            "DELETE FROM ingredient_nutrients WHERE ingredient_id = ?",
                            (ingredient_id,)
                        )
                        self.repo.cursor.execute(
                            "DELETE FROM ingredients WHERE id = ?",
                            (ingredient_id,)
                        )
            
            # If editing with same name, update nutrients
            elif is_editing:
                self.repo.cursor.execute(
                    "SELECT id FROM ingredients WHERE name = ? COLLATE NOCASE",
                    (name,)
                )
                row = self.repo.cursor.fetchone()
                
                if row:
                    ingredient_id = row[0]
                    with self.repo.conn:
                        # update description
                        self.repo.cursor.execute(
                            "UPDATE ingredients SET description = ? WHERE id = ?",
                            (description, ingredient_id)
                        )
            
                        # reset nutrients
                        self.repo.cursor.execute(
                            "DELETE FROM ingredient_nutrients WHERE ingredient_id = ?",
                            (ingredient_id,)
                        )
            
                        for nutrient_name, amount in nutrients:
                            self.repo.cursor.execute(
                                "SELECT id FROM nutrient_types WHERE name = ?",
                                (nutrient_name,)
                            )
                            nut_row = self.repo.cursor.fetchone()
                            if nut_row:
                                nutrient_id = nut_row["id"]
                                self.repo.cursor.execute(
                                    "INSERT INTO ingredient_nutrients (ingredient_id, nutrient_id, amount) VALUES (?, ?, ?)",
                                    (ingredient_id, nutrient_id, amount)
                                )
            else:
                # New ingredient
                self.repo.add_ingredient_with_nutrients(name, description, nutrients)
            
            self.editing_ingredient_name = None
            self.save_btn_ing.setText("Add Ingredient")


            QtWidgets.QMessageBox.information(self, "Success", "Ingredient saved")
            self.clear_ingredient_form()
            self.repo.ingredient_cache.clear()  # Clear cache to ensure fresh data
            self.refresh_ingredient_completer()
            self.search_ing()
            
        except ValueError as e:
            QtWidgets.QMessageBox.warning(self, "Validation Error", str(e))
        except sqlite3.IntegrityError as e:
            QtWidgets.QMessageBox.warning(self, "Database Error", str(e))
        except Exception as e:
            logging.exception(e)
            QtWidgets.QMessageBox.critical(self, "Error", str(e))
        
    def closeEvent(self, event):
        if self.editing_recipe_id is not None:
            reply = QtWidgets.QMessageBox.warning(
                self,
                "Unsaved Changes",
                "You are editing a recipe. Close anyway?",
                QtWidgets.QMessageBox.StandardButton.Yes |
                QtWidgets.QMessageBox.StandardButton.Cancel
            )
            if reply != QtWidgets.QMessageBox.StandardButton.Yes:
                event.ignore()
                return
        
        for i in range(1, 7):
            try:
                Path(f"./temp/label_{i}.png").unlink(missing_ok=True)
            except Exception as e:
                logging.warning(f"Failed to clean up label_{i}.png: {e}")
                
        self.repo.close()
        event.accept()