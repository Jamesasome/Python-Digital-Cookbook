import re 
import logging
import sqlite3 
from config import constants
from RecipeDataClass import normalize_key, Recipe, Ingredient, Step

class RecipeRepository:
    def __init__(self, db_path="database.db"):
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

        self.ingredient_cache = {}
        self.unit_cache = {}

        self.init_db()

    def init_db(self):
        """Initialize database with FULL schema from nutrition data script"""
        self.cursor.executescript("""
            DROP VIEW IF EXISTS recipe_nutrition;
            DROP VIEW IF EXISTS recipe_nutrition_per_serving;
        """)
        self.cursor.executescript("""
               PRAGMA foreign_keys = ON;
    
                -- =========================
                -- INGREDIENTS
                -- =========================
                CREATE TABLE IF NOT EXISTS ingredients (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE COLLATE NOCASE,
                    cofid TEXT,
                    cofid_group TEXT,
                    description TEXT,
                    source TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE INDEX IF NOT EXISTS idx_ingredients_name
                ON ingredients(name);
                
                -- =========================
                -- INGREDIENT ALIASES
                -- =========================
                CREATE TABLE IF NOT EXISTS ingredient_aliases (
                    id INTEGER PRIMARY KEY,
                    ingredient_id INTEGER NOT NULL,
                    alias TEXT NOT NULL COLLATE NOCASE,
                
                    FOREIGN KEY (ingredient_id)
                        REFERENCES ingredients(id)
                        ON DELETE CASCADE
                );
                
                CREATE INDEX IF NOT EXISTS idx_alias_lookup
                ON ingredient_aliases(alias);
                
                -- =========================
                -- NUTRIENT TYPES
                -- =========================
                CREATE TABLE IF NOT EXISTS nutrient_types (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    display_name TEXT,
                    unit TEXT,
                    unit_display TEXT
                );
                
                CREATE INDEX IF NOT EXISTS idx_nutrients_name
                ON nutrient_types(name);
                
                -- =========================
                -- INGREDIENT NUTRIENTS
                -- =========================
                CREATE TABLE IF NOT EXISTS ingredient_nutrients (
                    ingredient_id INTEGER NOT NULL,
                    nutrient_id INTEGER NOT NULL,
                    amount REAL NOT NULL CHECK(amount >= 0),
                
                    PRIMARY KEY (ingredient_id, nutrient_id),
                
                    FOREIGN KEY (ingredient_id)
                        REFERENCES ingredients(id)
                        ON DELETE CASCADE,
                
                    FOREIGN KEY (nutrient_id)
                        REFERENCES nutrient_types(id)
                        ON DELETE CASCADE
                );
                
                CREATE INDEX IF NOT EXISTS idx_ing_nutrients_ing
                ON ingredient_nutrients(ingredient_id);
                
                CREATE INDEX IF NOT EXISTS idx_ing_nutrients_nut
                ON ingredient_nutrients(nutrient_id);
                
                -- =========================
                -- RECIPES
                -- =========================
                CREATE TABLE IF NOT EXISTS recipes (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE COLLATE NOCASE,
                    servings REAL,
                    description TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE INDEX IF NOT EXISTS idx_recipes_name
                ON recipes(name);
                
                -- =========================
                -- UNITS
                -- =========================
                CREATE TABLE IF NOT EXISTS units (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    grams_per_unit REAL,
                    ml_per_unit REAL
                );
                
                CREATE INDEX IF NOT EXISTS idx_units_name
                ON units(name);
                
                -- =========================
                -- RECIPE INGREDIENTS
                -- =========================
                CREATE TABLE IF NOT EXISTS recipe_ingredients (
                    recipe_id INTEGER NOT NULL,
                    ingredient_id INTEGER NOT NULL,
                    amount REAL NOT NULL CHECK(amount > 0),
                    unit_id INTEGER,
                
                    PRIMARY KEY (recipe_id, ingredient_id, unit_id),
                
                    FOREIGN KEY (recipe_id)
                        REFERENCES recipes(id)
                        ON DELETE CASCADE,
                
                    FOREIGN KEY (ingredient_id)
                        REFERENCES ingredients(id)
                        ON DELETE CASCADE,
                
                    FOREIGN KEY (unit_id)
                        REFERENCES units(id)
                );
                
                CREATE INDEX IF NOT EXISTS idx_recipe_ingredients_recipe
                ON recipe_ingredients(recipe_id);
                
                -- =========================
                -- RECIPE STEPS
                -- =========================
                CREATE TABLE IF NOT EXISTS recipe_steps (
                    id INTEGER PRIMARY KEY,
                    recipe_id INTEGER NOT NULL,
                    step_index INTEGER NOT NULL CHECK(step_index > 0),
                    instruction TEXT NOT NULL,
                
                    FOREIGN KEY (recipe_id)
                        REFERENCES recipes(id)
                        ON DELETE CASCADE
                );
                
                CREATE INDEX IF NOT EXISTS idx_recipe_steps_recipe_order
                ON recipe_steps(recipe_id, step_index);
                
                -- =========================
                -- NUTRITION VIEW (TOTAL)
                -- =========================
                CREATE VIEW IF NOT EXISTS recipe_nutrition AS
                SELECT
                    ri.recipe_id,
                    nt.id AS nutrient_id,
                    nt.name AS nutrient_name,
                    nt.display_name,
                    nt.unit,
                    COALESCE(nt.unit_display, nt.unit) AS unit_display,
                    SUM(inut.amount * ri.amount) AS total_amount
                FROM recipe_ingredients ri
                JOIN ingredient_nutrients inut
                    ON ri.ingredient_id = inut.ingredient_id
                JOIN nutrient_types nt
                    ON nt.id = inut.nutrient_id
                GROUP BY ri.recipe_id, nt.id;
                
                -- =========================
                -- NUTRITION VIEW (PER SERVING)
                -- =========================
                CREATE VIEW IF NOT EXISTS recipe_nutrition_per_serving AS
                SELECT
                    r.id AS recipe_id,
                    r.name AS recipe_name,
                    nt.id AS nutrient_id,
                    nt.name AS nutrient_name,
                    nt.display_name,
                    nt.unit,
                    COALESCE(nt.unit_display, nt.unit) AS unit_display,
                    SUM(inut.amount * ri.amount) / COALESCE(r.servings, 1) AS amount_per_serving
                FROM recipes r
                JOIN recipe_ingredients ri
                    ON r.id = ri.recipe_id
                JOIN ingredient_nutrients inut
                    ON ri.ingredient_id = inut.ingredient_id
                JOIN nutrient_types nt
                    ON nt.id = inut.nutrient_id
                GROUP BY r.id, nt.id;
                
                -- =========================
                -- FULL TEXT SEARCH (RECIPES)
                -- =========================
                CREATE VIRTUAL TABLE IF NOT EXISTS recipe_search USING fts5(
                    name,
                    description,
                    tokenize='unicode61 remove_diacritics 2',
                    prefix='2 3 4'
                );
                
                -- =========================
                -- FULL TEXT SEARCH (INGREDIENTS)
                -- =========================
                CREATE VIRTUAL TABLE IF NOT EXISTS ingredient_search USING fts5(
                    name,
                    tokenize='unicode61 remove_diacritics 2',
                    prefix='2 3 4'
                );
                
                -- =========================
                -- FULL TEXT SEARCH (ALIASES)
                -- =========================
                CREATE VIRTUAL TABLE IF NOT EXISTS ingredient_alias_search USING fts5(
                    alias,
                    tokenize='unicode61 remove_diacritics 2',
                    prefix='2 3 4'
                );
                
                -- =========================
                -- TRIGGERS: RECIPES
                -- =========================
                CREATE TRIGGER IF NOT EXISTS recipes_ai AFTER INSERT ON recipes BEGIN
                  INSERT INTO recipe_search(rowid, name, description)
                  VALUES (new.id, new.name, COALESCE(new.description,''));
                END;
                
                CREATE TRIGGER IF NOT EXISTS recipes_au AFTER UPDATE ON recipes BEGIN
                  UPDATE recipe_search
                  SET name = new.name,
                      description = COALESCE(new.description,'')
                  WHERE rowid = new.id;
                END;
                
                CREATE TRIGGER IF NOT EXISTS recipes_ad AFTER DELETE ON recipes BEGIN
                  DELETE FROM recipe_search WHERE rowid = old.id;
                END;
                
                -- =========================
                -- TRIGGERS: INGREDIENTS
                -- =========================
                CREATE TRIGGER IF NOT EXISTS ingredients_ai AFTER INSERT ON ingredients BEGIN
                  INSERT INTO ingredient_search(rowid, name)
                  VALUES (new.id, new.name);
                END;
                
                CREATE TRIGGER IF NOT EXISTS ingredients_ad AFTER DELETE ON ingredients BEGIN
                  DELETE FROM ingredient_search WHERE rowid = old.id;
                END;
                
                -- =========================
                -- TRIGGERS: ALIASES
                -- =========================
                CREATE TRIGGER IF NOT EXISTS aliases_ai AFTER INSERT ON ingredient_aliases BEGIN
                  INSERT INTO ingredient_alias_search(rowid, alias)
                  VALUES (new.id, new.alias);
                END;
                
                CREATE TRIGGER IF NOT EXISTS aliases_ad AFTER DELETE ON ingredient_aliases BEGIN
                  DELETE FROM ingredient_alias_search WHERE rowid = old.id;
                END;
        """)
        
        self.conn.commit()
            
        # Initialize default units if table is empty
        self._init_default_units()
   
    def _init_default_units(self):
        """Insert default units only if none exist"""
        self.cursor.execute("SELECT COUNT(*) FROM units")
        if self.cursor.fetchone()[0] == 0:
            default_units = [
                ("g", 1.0, None),
                ("kg", 1000.0, None),
                ("g/ml", None, None),
                
                ("mg", 0.001, None),
                ("µg", 0.000001, None),

                ("ml", 1.0, 1.0),
                ("l", 1000.0, 1000.0),

                ("tsp", 5.0, 5.0),
                ("tbsp", 15.0, 15.0),

                ("cup", 240.0, 240.0),

                ("oz", 28.35, None),
                ("lb", 453.592, None),

                ("pinch", 0.36, None),
                ("dash", 0.60, None),

                ("clove", 5.0, None),
                ("slice", 30.0, None),

                ("piece", 50.0, None),

                ("can", 400.0, None),
                ("packet", 50.0, None),

                ("egg", 50.0, None)
            ]

            self.cursor.executemany("""
                INSERT OR IGNORE INTO units
                (name, grams_per_unit, ml_per_unit)
                VALUES (?, ?, ?)
            """, default_units)

            self.conn.commit()
        self.unit_cache.clear()

    # ---------- ingredient helper ----------
    def get_ingredient_id(self, name: str, allow_create=False):
        """Get or create ingredient by name"""
        key = normalize_key(name)
        
        if len(self.ingredient_cache) > constants.MAX_INGREDIENT_CACHE:
            self.ingredient_cache.clear()
        
        if key in self.ingredient_cache:
            return self.ingredient_cache[key]
        
        cleaned_name = re.sub(r"\s+", " ", name).strip()
        self.cursor.execute("SELECT id FROM ingredients WHERE name = ? COLLATE NOCASE", (cleaned_name,))
        row = self.cursor.fetchone()
        
        if row:
            self.ingredient_cache[key] = row[0]
            return row[0]

        if not allow_create:
            raise ValueError(
                f"Ingredient '{cleaned_name}' not found. "
                f"Create it in the 'Add Ingredient' tab first."
            )
        
        # Only auto-create if explicitly allowed
        self.cursor.execute("INSERT INTO ingredients (name, source) VALUES (?, ?)", (name, "user"))
        iid = self.cursor.lastrowid
        self.ingredient_cache[key] = iid
        
        return iid

    # ---------- CRUD ----------
    def add(self, recipe: Recipe):
        """Add a new recipe"""
        try:
            with self.conn:
                self.cursor.execute(
                    "INSERT INTO recipes (name, servings, description) VALUES (?, ?, ?)",
                    (recipe.name, recipe.servings, recipe.description)
                )

                recipe_id = self.cursor.lastrowid

                for ing in recipe.ingredients:
                    ingredient_id = self.get_ingredient_id(ing.display_name)
                
                    # Validate unit_id if provided
                    if ing.unit_id is not None:
                        self.cursor.execute("SELECT id FROM units WHERE id = ?", (ing.unit_id,))
                        if not self.cursor.fetchone():
                            raise ValueError(f"Unit ID {ing.unit_id} is invalid")
                
                    self.cursor.execute("""
                        INSERT INTO recipe_ingredients
                        (recipe_id, ingredient_id, amount, unit_id)
                        VALUES (?, ?, ?, ?)
                    """, (recipe_id, ingredient_id, ing.amount, ing.unit_id))

                for step in recipe.steps:
                    self.cursor.execute("""
                        INSERT INTO recipe_steps
                        (recipe_id, step_index, instruction)
                        VALUES (?, ?, ?)
                    """, (recipe_id, step.index, step.text))

        except Exception as e:
            logging.exception(e)
            self.ingredient_cache.clear()
            self.unit_cache.clear()
            raise

    def update(self, recipe_id: int, recipe: Recipe):
        """Update an existing recipe"""
        try:
            with self.conn:
                # Check if new name conflicts with existing recipe
                self.cursor.execute(
                    "SELECT id FROM recipes WHERE LOWER(name) = LOWER(?) AND id != ?",
                    (recipe.name, recipe_id)
                )
                if self.cursor.fetchone():
                    raise ValueError(f"Recipe '{recipe.name}' already exists")
                
                
                self.cursor.execute("""
                    UPDATE recipes
                    SET name = ?, servings = ?, description = ?
                    WHERE id = ?
                """, (recipe.name, recipe.servings, recipe.description, recipe_id))

                self.cursor.execute("DELETE FROM recipe_ingredients WHERE recipe_id = ?", (recipe_id,))
                self.cursor.execute("DELETE FROM recipe_steps WHERE recipe_id = ?", (recipe_id,))

                for ing in recipe.ingredients:
                    ingredient_id = self.get_ingredient_id(ing.display_name)
                
                    # Validate unit_id if provided
                    if ing.unit_id is not None:
                        self.cursor.execute(
                            "SELECT id FROM units WHERE id = ?",
                            (ing.unit_id,)
                        )
                
                        if not self.cursor.fetchone():
                            raise ValueError(
                                f"Invalid unit_id: {ing.unit_id}"
                            )
                
                    self.cursor.execute("""
                        INSERT INTO recipe_ingredients
                        (recipe_id, ingredient_id, amount, unit_id)
                        VALUES (?, ?, ?, ?)
                    """, (
                        recipe_id,
                        ingredient_id,
                        ing.amount,
                        ing.unit_id
                    ))

                for step in recipe.steps:
                    self.cursor.execute("""
                        INSERT INTO recipe_steps
                        (recipe_id, step_index, instruction)
                        VALUES (?, ?, ?)
                    """, (recipe_id, step.index, step.text))

            self.cleanup_unused_ingredients()

        except Exception as e:
            logging.exception(e)
            self.ingredient_cache.clear()
            self.unit_cache.clear()
            raise
            
    def get_recipe_name(self, recipe_id: int):
        """Get a recipes name by id"""
        self.cursor.execute("""
            SELECT name
            FROM recipes WHERE id = ?
            """, (recipe_id,))
        name = self.cursor.fetchone()
        if not name:
            return None
        else:
            return name[0]

    def get(self, recipe_id: int):
        """Get a recipe by ID with all its data"""
        self.cursor.execute("""
            SELECT name, servings, description
            FROM recipes WHERE id = ?
        """, (recipe_id,))
        row = self.cursor.fetchone()
        if not row:
            return None

        name, servings, description = row

        self.cursor.execute("""
            SELECT i.name, ri.amount, ri.unit_id, u.name
            FROM recipe_ingredients ri
            JOIN ingredients i ON i.id = ri.ingredient_id
            LEFT JOIN units u ON u.id = ri.unit_id
            WHERE ri.recipe_id = ?
            ORDER BY i.name
        """, (recipe_id,))
        
        ingredients = [
            Ingredient(
                name=n,
                amount=a,
                unit_id=uid,
                display_name=n,
                unit_name=uname or ""
            )
            for n, a, uid, uname in self.cursor.fetchall()
        ]

        self.cursor.execute("""
            SELECT step_index, instruction
            FROM recipe_steps
            WHERE recipe_id = ?
            ORDER BY step_index
        """, (recipe_id,))

        steps = [Step(i, t) for i, t in self.cursor.fetchall()]

        return Recipe(name, servings or 0, description or "", ingredients, steps)
    
    def get_units(self):
        """Get all available units"""
        self.cursor.execute("""
            SELECT id, name FROM units ORDER BY name
        """)
        return self.cursor.fetchall()
    
    def get_unit_id(self, unit_name: str):
        """Get unit ID by name"""
        if not unit_name:
            return None
        
        key = normalize_key(unit_name)
        if len(self.unit_cache) > constants.MAX_UNIT_CACHE:
            self.unit_cache.clear()
        
        if key in self.unit_cache:
            return self.unit_cache[key]
        
        self.cursor.execute("SELECT id FROM units WHERE name = ? COLLATE NOCASE",
                            (unit_name,))
        row = self.cursor.fetchone()
        
        if row:
            self.unit_cache[key] = row[0]
            return row[0]
        
        return None
    
    def get_ingredient_info(self, name: str):
        name = name.strip()
        self.cursor.execute("""
                            SELECT id, name, cofid, cofid_group, description 
                            FROM ingredients
                            WHERE name = ?
                            """, (name,))
        return self.cursor.fetchall()

    def search(self, query: str):
        query = query.strip()
    
        # empty query → return all recipes
        if not query:
            self.cursor.execute("""
                SELECT id, name
                FROM recipes
                ORDER BY name
            """)
            return self.cursor.fetchall()
    
        query_clean = query.replace('"', '')
        like_query = f"%{query_clean}%"
        fts_query = f"{query_clean}*"
    
        self.cursor.execute("""
            SELECT id, name, MIN(score) as score
            FROM (
    
                -- FULL-TEXT SEARCH (BEST MATCHES)
                SELECT
                    r.id AS id,
                    r.name AS name,
                    bm25(recipe_search) AS score
                FROM recipe_search
                JOIN recipes r ON r.id = recipe_search.rowid
                WHERE recipe_search MATCH ?
    
                UNION ALL
    
                -- FALLBACK LIKE SEARCH (LOW PRIORITY)
                SELECT
                    r.id AS id,
                    r.name AS name,
                    999 AS score
                FROM recipes r
                WHERE r.name LIKE ?
    
            )
            GROUP BY id, name
            ORDER BY score ASC
        """, (fts_query, like_query))
    
        return self.cursor.fetchall()
    
    def delete(self, recipe_id):
        """Delete a recipe"""
        with self.conn:
            self.conn.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))
            self.cleanup_unused_ingredients()

            
    def cleanup_unused_ingredients(self):
        """
        Remove ONLY user-created ingredients (source='user') that are not used in recipes.
        NEVER delete mccance nutrition database ingredients.
        """
        with self.conn:
            self.conn.execute("""
                DELETE FROM ingredients
                WHERE source = 'user'
                AND NOT EXISTS (
                    SELECT 1
                    FROM recipe_ingredients ri
                    WHERE ri.ingredient_id = ingredients.id
                )
            """)
        self.ingredient_cache.clear()
        self.unit_cache.clear()
        
    def get_ingredient_nutrition(self, ingredient_name: str):
        """
        Returns all nutrients for a single ingredient (per gram).
        """
        self.cursor.execute("""
            SELECT nt.display_name, nt.unit_display, inut.amount
            FROM ingredient_nutrients inut
            JOIN ingredients i ON i.id = inut.ingredient_id
            JOIN nutrient_types nt ON nt.id = inut.nutrient_id
            WHERE LOWER(i.name) = LOWER(?)
            ORDER BY nt.display_name
        """, (ingredient_name,))

        return self.cursor.fetchall()
    
    def get_ingredient_nutrition_id(self, ingredient_id: str):
        """
        Returns all nutrients for a single ingredient (per gram).
        """
        self.cursor.execute("""
            SELECT nt.name, nt.unit_display, inut.amount
            FROM ingredient_nutrients inut
            JOIN ingredients i ON i.id = inut.ingredient_id
            JOIN nutrient_types nt ON nt.id = inut.nutrient_id
            WHERE i.id = ?
            ORDER BY nt.name
        """, (ingredient_id,))

        return self.cursor.fetchall()

    def get_recipe_nutrition(self, recipe_id: int):
        """
        Get all nutrients for a recipe from the view.
        Returns (display_name, unit_display, total_amount) tuples.
        """
        self.cursor.execute("""
            SELECT display_name, unit_display, total_amount
            FROM recipe_nutrition
            WHERE recipe_id = ?
            ORDER BY display_name
        """, (recipe_id,))
    
        return self.cursor.fetchall()
    
    def get_recipe_nutrition_per_serving(self, recipe_id: int):
        """
        Get nutrients per serving from the view.
        Returns (nutrient name, unit_display, amount_per_serving) tuples.
        """
        self.cursor.execute("""
            SELECT nutrient_name, unit_display, amount_per_serving
            FROM recipe_nutrition_per_serving
            WHERE recipe_id = ?
            ORDER BY nutrient_name
        """, (recipe_id,))
    
        return self.cursor.fetchall()
    
    def search_ingredients(self, query: str):
        query = query.strip()
    
        if not query:
            self.cursor.execute("""
                SELECT name
                FROM ingredients
                ORDER BY name
            """)
            return [r[0] for r in self.cursor.fetchall()]
    
        query_clean = query.replace('"', '')
        query_clean = query.replace(",", " ")
        prefix_query = f"{query_clean}*"
        starts_query = f"{query_clean}%"
        like_query = f"%{query_clean}%"
    
        self.cursor.execute("""
            SELECT name
            FROM (
                -- 1. Exact name match
                SELECT
                    name,
                    1 AS priority,
                    0.0 AS score
                FROM ingredients
                WHERE LOWER(name) = LOWER(?)
    
                UNION ALL
    
                -- 2. Name starts with query
                SELECT
                    name,
                    2 AS priority,
                    0.0 AS score
                FROM ingredients
                WHERE LOWER(name) LIKE LOWER(?)
    
                UNION ALL
    
                -- 3. Ingredient FTS (ranked with bm25)
                SELECT
                    i.name,
                    3 AS priority,
                    bm25(ingredient_search) AS score
                FROM ingredient_search
                JOIN ingredients i
                    ON i.id = ingredient_search.rowid
                WHERE ingredient_search MATCH ?
    
                UNION ALL
    
                -- 4. Alias FTS (ranked with bm25)
                SELECT
                    i.name,
                    4 AS priority,
                    bm25(ingredient_alias_search) AS score
                FROM ingredient_alias_search
                JOIN ingredients i
                    ON i.id = ingredient_alias_search.rowid
                WHERE ingredient_alias_search MATCH ?
    
                UNION ALL
    
                -- 5. General substring match
                SELECT
                    name,
                    5 AS priority,
                    0.0 AS score
                FROM ingredients
                WHERE LOWER(name) LIKE LOWER(?)
            )
            GROUP BY name
            ORDER BY
                MIN(priority),
                MIN(score),
                LENGTH(name),
                name
        """, (
            query_clean,
            starts_query,
            prefix_query,
            prefix_query,
            like_query,
        ))
    
        return [row[0] for row in self.cursor.fetchall()]

    
    def get_all_nutrient_names(self):
        self.cursor.execute(
            "SELECT name FROM nutrient_types"
        )
        return [r[0] for r in self.cursor.fetchall()]
    
    def add_ingredient_with_nutrients(self, ingredient_name: str, description: str,
                                      nutrients: list[tuple[str, float]]):
        # -------------------------
        # VALIDATION
        # -------------------------
        ingredient_name = ingredient_name.strip()
        
        if not ingredient_name:
            raise ValueError("Ingredient name required")
        
        if not nutrients:
            raise ValueError("At least one nutrient value required")
        
        # duplicate check
        self.cursor.execute("""
            SELECT id
            FROM ingredients
            WHERE name = ?
            COLLATE NOCASE
        """, (ingredient_name,))
        
        if self.cursor.fetchone():
            raise ValueError(
                f"Ingredient '{ingredient_name}' already exists"
            )
        
        for nutrient_name, amount in nutrients:
        
            if amount < 0:
                raise ValueError(
                    f"{nutrient_name}: amount cannot be negative"
                )
        
        # -------------------------
        # DATABASE WORK
        # -------------------------
        with self.conn:
    
            # ingredient
            self.cursor.execute("""
                INSERT INTO ingredients(name, description, source)
                VALUES (?, ?, 'user')
            """, (ingredient_name, description,))
    
            ingredient_id = self.cursor.lastrowid
    
            for nutrient_name, amount in nutrients:
    
                self.cursor.execute("""
                    SELECT id
                    FROM nutrient_types
                    WHERE name = ?
                """, (nutrient_name,))
    
                row = self.cursor.fetchone()
    
                if not row:
                    raise ValueError(
                        f"Unknown nutrient: {nutrient_name}"
                    )
    
                nutrient_id = row["id"]
    
                self.cursor.execute("""
                    INSERT INTO ingredient_nutrients
                    (
                        ingredient_id,
                        nutrient_id,
                        amount
                    )
                    VALUES (?, ?, ?)
                """, (
                    ingredient_id,
                    nutrient_id,
                    amount
                ))

    def close(self):
        """Close database connection"""
        self.conn.close()