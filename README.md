# Digital Cookbook

> **Nutrition-aware Recipe Management Application**
> 
> This application's database comes preloaded with ingredient and nutritional data from *Widdowson’s Food Composition Tables* and *McCance and Widdowson (2022)*.

## Overview

Digital Cookbook is a desktop application built with **Python**,
**PyQt6**, and **SQLite** for creating, editing, searching, and
analysing recipes. It combines recipe management with nutritional
analysis and generates nutrition labels and printable PDFs.

## Features

- Recipe CRUD
- Ingredient database
- Nutrient tracking
- SQLite database
- Full-text search (FTS5)
- Autocomplete
- User-created ingredients
- Nutrition calculations
- PNG nutrition labels
- PDF export
- Validation
- Dynamic step editor

## Architecture

```text
                                    GUI
                                     │
                              Recipe Repository
                                     │
                               SQLite Database
                                     │
                              Nutrition Tables
                                     │
                          Nutrition Label Renderer
```

## Database

The application automatically creates tables for:

- recipes
- ingredients
- recipe_ingredients
- recipe_steps
- nutrient_types
- ingredient_nutrients
- ingredient_aliases
- units

It also creates:

- FTS5 search tables
- nutrition views
- triggers
- indexes

## Main Components:

### RecipeRepository

Responsible for:

- database initialisation
- CRUD operations
- searching
- nutrition calculations
- ingredient management
- unit management
- cache management

### RecipeApp

Provides the graphical interface.

Tabs include:

- Recipes
- Add Recipe
- Ingredient Database
- Add Ingredient

### LabelGen.py

Responsible for rendering nutrition labels using Pillow.

Pipeline:

1. Read JSON configuration
2. Calculate label size
3. Draw rows
4. Apply themes
5. Sharpen image
6. Save PNG files

### config.py

Contains:

- nutrient definitions
- nutrition label templates
- display names
- units

## Search

The application combines:

- SQLite FTS5
- BM25 ranking
- Prefix matching
- LIKE fallback
- Alias searching

## Validation

Recipes are validated for:

- name
- servings
- duplicate ingredients
- positive quantities
- sequential steps

## Export

Supports:

- Nutrition PNG labels
- PDF recipe export

## Dependencies

- PyQt6
- Pillow
- xhtml2pdf
- sqlite3
