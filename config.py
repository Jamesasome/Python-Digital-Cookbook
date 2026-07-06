class config:
    def __init__(self):
        self.items = [
            {'id': 6, 'name': 'KCALS', 'display_name': 'Energy (kcal)', 'unit': 'kcal', 'display_unit': 'kcal'},
            {'id': 1, 'name': 'DGPML', 'display_name': 'Density (g/ml)', 'unit': 'g/ml', 'display_unit': 'g/ml'},
            {'id': 2, 'name': 'WATER', 'display_name': 'Water (g)', 'unit': 'g', 'display_unit': 'g'},
            {'id': 3, 'name': 'PROT', 'display_name': 'Protein (g)', 'unit': 'g', 'display_unit': 'g'},
            {'id': 4, 'name': 'FAT', 'display_name': 'Fat (g)', 'unit': 'g', 'display_unit': 'g'},
            {'id': 82, 'name': 'UNSATFOD', 'display_name': 'Unsaturated Fat (g)', 'unit': 'g', 'display_unit': 'g'},
            {'id': 17, 'name': 'SATFOD', 'display_name': 'Saturated Fat (g)', 'unit': 'g', 'display_unit': 'g'},
            {'id': 20, 'name': 'MONOFOD', 'display_name': 'Monounsaturated Fat (g)', 'unit': 'g', 'display_unit': 'g'},
            {'id': 21, 'name': 'POLYFOD', 'display_name': 'Polyunsaturated Fat (g)', 'unit': 'g', 'display_unit': 'g'},
            {'id': 22, 'name': 'FODTRANS', 'display_name': 'Trans Fats (g)', 'unit': 'g', 'display_unit': 'g'},
            {'id': 18, 'name': 'TOTn6PFOD', 'display_name': 'Omega-6 (g)', 'unit': 'g', 'display_unit': 'g'},
            {'id': 19, 'name': 'TOTn3PFOD', 'display_name': 'Omega-3 (g)', 'unit': 'g', 'display_unit': 'g'},
            {'id': 64, 'name': 'FOD18:3cn3', 'display_name': 'ALA (g)', 'unit': 'g', 'display_unit': 'g'},
            {'id': 65, 'name': 'FOD20:5cn3', 'display_name': 'EPA (g)', 'unit': 'g', 'display_unit': 'g'},
            {'id': 66, 'name': 'FOD22:5cn3', 'display_name': 'DPA (g)', 'unit': 'g', 'display_unit': 'g'},
            {'id': 67, 'name': 'FOD22:6cn3', 'display_name': 'DHA (g)', 'unit': 'g', 'display_unit': 'g'},
            {'id': 68, 'name': 'FOD18:2cn6', 'display_name': 'Linoleic Acid (g)', 'unit': 'g', 'display_unit': 'g'},
            {'id': 69, 'name': 'FOD20:4cn6', 'display_name': 'Arachidonic Acid (g)', 'unit': 'g', 'display_unit': 'g'},
            {'id': 23, 'name': 'CHOL', 'display_name': 'Cholesterol (mg)', 'unit': 'mg', 'display_unit': 'mg'},
            {'id': 16, 'name': 'ALCO', 'display_name': 'Alcohol (g)', 'unit': 'g', 'display_unit': 'g'},
            {'id': 5, 'name': 'CHO', 'display_name': 'Carbohydrates (g)', 'unit': 'g', 'display_unit': 'g'},
            {'id': 81, 'name': 'FIB', 'display_name': 'Fibre (g)', 'unit': 'g', 'display_unit': 'g'},
            {'id': 7, 'name': 'STAR', 'display_name': 'Starch (g)', 'unit': 'g', 'display_unit': 'g'},
            {'id': 8, 'name': 'OLIGO', 'display_name': 'Oligosaccharide (g)', 'unit': 'g', 'display_unit': 'g'},
            {'id': 9, 'name': 'TOTSUG', 'display_name': 'Total sugars (g)', 'unit': 'g', 'display_unit': 'g'},
            {'id': 10, 'name': 'GLUC', 'display_name': 'Glucose (g)', 'unit': 'g', 'display_unit': 'g'},
            {'id': 11, 'name': 'GALACT', 'display_name': 'Galactose (g)', 'unit': 'g', 'display_unit': 'g'},
            {'id': 12, 'name': 'FRUCT', 'display_name': 'Fructose (g)', 'unit': 'g', 'display_unit': 'g'},
            {'id': 13, 'name': 'SUCR', 'display_name': 'Sucrose (g)', 'unit': 'g', 'display_unit': 'g'},
            {'id': 14, 'name': 'MALT', 'display_name': 'Maltose (g)', 'unit': 'g', 'display_unit': 'g'},
            {'id': 15, 'name': 'LACT', 'display_name': 'Lactose (g)', 'unit': 'g', 'display_unit': 'g'},
            {'id': 24, 'name': 'NA', 'display_name': 'Sodium (mg)', 'unit': 'mg', 'display_unit': 'mg'},
            {'id': 25, 'name': 'K', 'display_name': 'Potassium (mg)', 'unit': 'mg', 'display_unit': 'mg'},
            {'id': 26, 'name': 'CA', 'display_name': 'Calcium (mg)', 'unit': 'mg', 'display_unit': 'mg'},
            {'id': 27, 'name': 'MG', 'display_name': 'Magnesium (mg)', 'unit': 'mg', 'display_unit': 'mg'},
            {'id': 28, 'name': 'P', 'display_name': 'Phosphorus (mg)', 'unit': 'mg', 'display_unit': 'mg'},
            {'id': 29, 'name': 'FE', 'display_name': 'Iron (mg)', 'unit': 'mg', 'display_unit': 'mg'},
            {'id': 31, 'name': 'ZN', 'display_name': 'Zinc (mg)', 'unit': 'mg', 'display_unit': 'mg'},
            {'id': 30, 'name': 'CU', 'display_name': 'Copper (mg)', 'unit': 'mg', 'display_unit': 'mg'},
            {'id': 33, 'name': 'MN', 'display_name': 'Manganese (mg)', 'unit': 'mg', 'display_unit': 'mg'},
            {'id': 34, 'name': 'SE', 'display_name': 'Selenium (µg)', 'unit': 'µg', 'display_unit': 'µg'},
            {'id': 35, 'name': 'I', 'display_name': 'Iodine (µg)', 'unit': 'µg', 'display_unit': 'µg'},
            {'id': 32, 'name': 'CL', 'display_name': 'Chloride (mg)', 'unit': 'mg', 'display_unit': 'mg'},
            {'id': 38, 'name': 'RETEQU', 'display_name': 'Retinol Equivalent (A) (µg)', 'unit': 'µg', 'display_unit': 'µg'},
            {'id': 39, 'name': 'VITD', 'display_name': 'Vitamin D (µg)', 'unit': 'µg', 'display_unit': 'µg'},
            {'id': 40, 'name': 'VITE', 'display_name': 'Vitamin E (mg)', 'unit': 'mg', 'display_unit': 'mg'},
            {'id': 41, 'name': 'VITK1', 'display_name': 'Vitamin K1 (µg)', 'unit': 'µg', 'display_unit': 'µg'},
            {'id': 42, 'name': 'THIA', 'display_name': 'Thiamin (B1) (mg)', 'unit': 'mg', 'display_unit': 'mg'},
            {'id': 43, 'name': 'RIBO', 'display_name': 'Riboflavin (B2) (mg)', 'unit': 'mg', 'display_unit': 'mg'},
            {'id': 44, 'name': 'NIAC', 'display_name': 'Niacin (B3) (mg)', 'unit': 'mg', 'display_unit': 'mg'},
            {'id': 48, 'name': 'PANTO', 'display_name': 'Pantothenate (B5) (mg)', 'unit': 'mg', 'display_unit': 'mg'},
            {'id': 45, 'name': 'VITB6', 'display_name': 'Vitamin B6 (mg)', 'unit': 'mg', 'display_unit': 'mg'},
            {'id': 49, 'name': 'BIOT', 'display_name': 'Biotin (B7) (µg)', 'unit': 'µg', 'display_unit': 'µg'},
            {'id': 47, 'name': 'FOLT', 'display_name': 'Folate (B9) (µg)', 'unit': 'µg', 'display_unit': 'µg'},
            {'id': 46, 'name': 'VITB12', 'display_name': 'Vitamin B12 (µg)', 'unit': 'µg', 'display_unit': 'µg'},
            {'id': 50, 'name': 'VITC', 'display_name': 'Vitamin C (mg)', 'unit': 'mg', 'display_unit': 'mg'},
            {'id': 36, 'name': 'RET', 'display_name': 'Retinol (µg)', 'unit': 'µg', 'display_unit': 'µg'},
            {'id': 37, 'name': 'CAREQU', 'display_name': 'Carotene (µg)', 'unit': 'µg', 'display_unit': 'µg'},
            {'id': 51, 'name': 'ACAR', 'display_name': 'Alpha-carotene (µg)', 'unit': 'µg', 'display_unit': 'µg'},
            {'id': 52, 'name': 'BCAR', 'display_name': 'Beta-carotene (µg)', 'unit': 'µg', 'display_unit': 'µg'},
            {'id': 53, 'name': 'CRYPT', 'display_name': 'Cryptoxanthins (µg)', 'unit': 'µg', 'display_unit': 'µg'},
            {'id': 54, 'name': 'LUT', 'display_name': 'Lutein (µg)', 'unit': 'µg', 'display_unit': 'µg'},
            {'id': 55, 'name': 'LYCO', 'display_name': 'Lycopene (µg)', 'unit': 'µg', 'display_unit': 'µg'},
            {'id': 56, 'name': '25OHD3', 'display_name': '25-hydroxy vitamin D3 (µg)', 'unit': 'µg', 'display_unit': 'µg'},
            {'id': 57, 'name': 'VITD3', 'display_name': 'Cholecalciferol (D3) (µg)', 'unit': 'µg', 'display_unit': 'µg'},
            {'id': 58, 'name': 'ATOPH', 'display_name': 'Alpha-tocopherol (mg)', 'unit': 'mg', 'display_unit': 'mg'},
            {'id': 59, 'name': 'BTOPH', 'display_name': 'Beta-tocopherol (mg)', 'unit': 'mg', 'display_unit': 'mg'},
            {'id': 61, 'name': 'GTOPH', 'display_name': 'Gamma-tocopherol (mg)', 'unit': 'mg', 'display_unit': 'mg'},
            {'id': 60, 'name': 'DTOPH', 'display_name': 'Delta-tocopherol (mg)', 'unit': 'mg', 'display_unit': 'mg'},
            {'id': 62, 'name': 'ATOTR', 'display_name': 'Alpha-tocotrienol (mg)', 'unit': 'mg', 'display_unit': 'mg'},
            {'id': 63, 'name': 'GTOTR', 'display_name': 'Gamma-tocotrienol (mg)', 'unit': 'mg', 'display_unit': 'mg'},
            {'id': 70, 'name': 'Total PHYTO', 'display_name': 'Total Phytosterols (mg)', 'unit': 'mg', 'display_unit': 'mg'},
            {'id': 71, 'name': 'PHYTO', 'display_name': 'Phytosterol (mg)', 'unit': 'mg', 'display_unit': 'mg'},
            {'id': 72, 'name': 'BSITPHYTO', 'display_name': 'Beta-sitosterol (mg)', 'unit': 'mg', 'display_unit': 'mg'},
            {'id': 74, 'name': 'CAMPHYTO', 'display_name': 'Campesterol (mg)', 'unit': 'mg', 'display_unit': 'mg'},
            {'id': 78, 'name': 'STIGPHYTO', 'display_name': 'Stigmasterol (mg)', 'unit': 'mg', 'display_unit': 'mg'},
            {'id': 73, 'name': 'BRASPHYTO', 'display_name': 'Brassicasterol (mg)', 'unit': 'mg', 'display_unit': 'mg'},
            {'id': 75, 'name': 'D5AVEN', 'display_name': 'Delta-5-avenasterol (mg)', 'unit': 'mg', 'display_unit': 'mg'},
            {'id': 76, 'name': 'D7AVEN', 'display_name': 'Delta-7-avenasterol (mg)', 'unit': 'mg', 'display_unit': 'mg'},
            {'id': 77, 'name': 'D7STIG', 'display_name': 'Delta-7-stigmastenol (mg)', 'unit': 'mg', 'display_unit': 'mg'},
            {'id': 79, 'name': 'CITA', 'display_name': 'Citric acid (g)', 'unit': 'g', 'display_unit': 'g'},
            {'id': 80, 'name': 'MALA', 'display_name': 'Malic acid (g)', 'unit': 'g', 'display_unit': 'g'}
        ]    
        
        self.nutrition_json = {
          "labels": [
            {
              "title": "Nutrition Information",
              "rows": [
                {
                  "type": "energy",
                  "left": "Energy",
                  "right": "{{KCALS}} kcal",
                  "bold": True
                },
                {
                  "type": "macronutrient",
                  "left": "Total Fat",
                  "right": "{{FAT}} g",
                  "bold": True
                },
                {
                  "type": "fat",
                  "indent": 1,
                  "left": "Total Unsaturated Fat",
                  "right": "{{UNSATFOD}} g"
                },
                {
                  "type": "fat",
                  "indent": 2,
                  "left": "Monounsaturated Fat",
                  "right": "{{MONOFOD}} g"
                },
                {
                  "type": "fat",
                  "indent": 2,
                  "left": "Polyunsaturated Fat",
                  "right": "{{POLYFOD}} g"
                },
                
                {
                  "type": "fat",
                  "indent": 3,
                  "left": "Omega-3",
                  "right": "{{TOTn3PFOD}} g"
                },
                {
                  "type": "fat",
                  "indent": 3,
                  "left": "Omega-6",
                  "right": "{{TOTn6PFOD}} g"
                },
                {
                  "type": "fat",
                  "indent": 1,
                  "left": "Total Saturated Fat",
                  "right": "{{SATFOD}} g"
                },
                {
                  "type": "fat",
                  "indent": 1,
                  "left": "Total Trans Fat",
                  "right": "{{FODTRANS}} g"
                },
                {
                  "type": "fat",
                  "indent": 1,
                  "left": "Cholesterol",
                  "right": "{{CHOL}} mg"
                },

                {
                  "type": "carbs",
                  "left": "Carbohydrate",
                  "right": "{{CHO}} g",
                  "bold": True
                },
                {
                  "type": "carbs",
                  "indent": 1,
                  "left": "Total Starch",
                  "right": "{{STAR}} g"
                },
                {
                  "type": "carbs",
                  "indent": 1,
                  "left": "Total Sugars",
                  "right": "{{TOTSUG}} g"
                },
                {
                  "type": "carbs",
                  "indent": 1,
                  "left": "Total Fibre",
                  "right": "{{FIB}} g"
                },

                {
                  "type": "protein",
                  "left": "Protein",
                  "right": "{{PROT}} g",
                  "bold": True
                },

                {
                  "type": "other",
                  "left": "Water",
                  "right": "{{WATER}} g"
                },
                {
                  "type": "other",
                  "left": "Alcohol",
                  "right": "{{ALCO}} g"
                },
              ]
            },
            
            {
              "title": "Fats",
              "rows": [
                {
                  "type": "macronutrient",
                  "left": "Total Fat",
                  "right": "{{FAT}} g",
                  "bold": True
                },
                {
                  "type": "fat",
                  "indent": 1,
                  "left": "Total Unsaturated Fat",
                  "right": "{{UNSATFOD}} g"
                },
                {
                  "type": "fat",
                  "indent": 2,
                  "left": "Monounsaturated Fat",
                  "right": "{{MONOFOD}} g"
                },
                {
                  "type": "fat",
                  "indent": 2,
                  "left": "Polyunsaturated Fat",
                  "right": "{{POLYFOD}} g"
                },
                {
                  "type": "fat",
                  "indent": 3,
                  "left": "Omega-3",
                  "right": "{{TOTn3PFOD}} g"
                },
                {
                  "type": "fat",
                  "indent": 4,
                  "left": "ALA",
                  "right": "{{FOD18:3cn3}} g"
                },
                {
                  "type": "fat",
                  "indent": 4,
                  "left": "EPA",
                  "right": "{{FOD20:5cn3}} g"
                },
                {
                  "type": "fat",
                  "indent": 4,
                  "left": "DPA",
                  "right": "{{FOD22:5cn3}} g"
                },
                {
                  "type": "fat",
                  "indent": 4,
                  "left": "DHA",
                  "right": "{{FOD22:6cn3}} g"
                },

                {
                  "type": "fat",
                  "indent": 3,
                  "left": "Omega-6",
                  "right": "{{TOTn6PFOD}} g",
                },
                {
                  "type": "fat",
                  "indent": 4,
                  "left": "Linoleic Acid",
                  "right": "{{FOD18:2cn6}} g"
                },
                {
                  "type": "fat",
                  "indent": 4,
                  "left": "Arachidonic Acid",
                  "right": "{{FOD20:4cn6}} g"
                },
                {
                  "type": "fat",
                  "indent": 1,
                  "left": "Total Saturated Fat",
                  "right": "{{SATFOD}} g"
                },
                {
                  "type": "fat",
                  "indent": 1,
                  "left": "Total Trans Fat",
                  "right": "{{FODTRANS}} g"
                },
                {
                  "type": "fat",
                  "indent": 1,
                  "left": "Cholesterol",
                  "right": "{{CHOL}} mg"
                }
             ]
            },
            {
             "title": "Carbohydrates",
             "rows": [
                 {
                   "type": "carbs",
                   "left": "Carbohydrate",
                   "right": "{{CHO}} g",
                   "bold": True
                 },
                 {
                   "type": "carbs",
                   "indent": 1,
                   "left": "Starch",
                   "right": "{{STAR}} g"
                 },
                 {
                   "type": "carbs",
                   "indent": 1,
                   "left": "Oligosaccharides",
                   "right": "{{OLIGO}} g"
                 },
                 {
                   "type": "carbs",
                   "indent": 1,
                   "left": "Total Sugars",
                   "right": "{{TOTSUG}} g"
                 },
                 {
                   "type": "carbs",
                   "indent": 2,
                   "left": "Glucose",
                   "right": "{{GLUC}} g"
                 },
                 {
                   "type": "carbs",
                   "indent": 2,
                   "left": "Galactose",
                   "right": "{{GALACT}} g"
                 },
                 {
                   "type": "carbs",
                   "indent": 2,
                   "left": "Fructose",
                   "right": "{{FRUCT}} g"
                 },
                 {
                   "type": "carbs",
                   "indent": 2,
                   "left": "Sucrose",
                   "right": "{{SUCR}} g"
                 },
                 {
                   "type": "carbs",
                   "indent": 2,
                   "left": "Maltose",
                   "right": "{{MALT}} g"
                 },
                 {
                   "type": "carbs",
                   "indent": 2,
                   "left": "Lactose",
                   "right": "{{LACT}} g"
                 },
                 {
                   "type": "carbs",
                   "indent": 1,
                   "left": "Fibre",
                   "right": "{{FIB}} g"
                 }
                ]
             },
             
            {
              "title": "Vitamins",
              "rows": [
                { "type": "fatvit", "left": "Vitamin A (Retinol Equivalent)", "right": "{{RETEQU}} µg", "bold": True},
                { "type": "fatvit", "indent": 1, "left": "Retinol", "right": "{{RET}} µg" },
                { "type": "fatvit", "indent": 1, "left": "Carotene", "right": "{{CAREQU}} µg"},
                { "type": "fatvit", "indent": 2, "left": "Alpha-carotene", "right": "{{ACAR}} µg" },
                { "type": "fatvit", "indent": 2, "left": "Beta-carotene", "right": "{{BCAR}} µg" },
                { "type": "fatvit", "indent": 2, "left": "Cryptoxanthins", "right": "{{CRYPT}} µg" },
                { "type": "fatvit", "indent": 2, "left": "Lutein", "right": "{{LUT}} µg" },
                { "type": "fatvit", "indent": 2, "left": "Lycopene", "right": "{{LYCO}} µg" },

                { "type": "fatvit", "left": "Vitamin D", "right": "{{VITD}} µg", "bold": True},
                { "type": "fatvit", "indent": 1, "left": "Cholecalciferol (D3)", "right": "{{VITD3}} µg" },
                { "type": "fatvit", "indent": 1, "left": "25-hydroxy Vitamin D3", "right": "{{25OHD3}} µg" },

                { "type": "fatvit", "left": "Vitamin E (Total)", "right": "{{VITE}} mg", "bold": True},
                { "type": "fatvit", "indent": 1, "left": "Alpha-tocopherol", "right": "{{ATOPH}} mg" },
                { "type": "fatvit", "indent": 1, "left": "Beta-tocopherol", "right": "{{BTOPH}} mg" },
                { "type": "fatvit", "indent": 1, "left": "Gamma-tocopherol", "right": "{{GTOPH}} mg" },
                { "type": "fatvit", "indent": 1, "left": "Delta-tocopherol", "right": "{{DTOPH}} mg" },
                { "type": "fatvit", "indent": 1, "left": "Alpha-tocotrienol", "right": "{{ATOTR}} mg" },
                { "type": "fatvit", "indent": 1, "left": "Gamma-tocotrienol", "right": "{{GTOTR}} mg" },

                { "type": "fatvit", "left": "Vitamin K1", "right": "{{VITK1}} µg" },
                { "type": "bvit", "left": "Thiamin (B1)", "right": "{{THIA}} mg" },
                { "type": "bvit", "left": "Riboflavin (B2)", "right": "{{RIBO}} mg" },
                { "type": "bvit", "left": "Niacin (B3)", "right": "{{NIAC}} mg" },
                { "type": "bvit", "left": "Pantothenate (B5)", "right": "{{PANTO}} mg" },
                { "type": "bvit", "left": "Vitamin B6", "right": "{{VITB6}} mg" },
                { "type": "bvit", "left": "Biotin (B7)", "right": "{{BIOT}} µg" },
                { "type": "bvit", "left": "Folate (B9)", "right": "{{FOLT}} µg" },
                { "type": "bvit", "left": "Vitamin B12", "right": "{{VITB12}} µg" },

                { "type": "vitc", "left": "Vitamin C", "right": "{{VITC}} mg" },
                
                {
                    "type": "note",
                    "text": "Vitamin Colour Guide:\n• Purple = Fat-soluble vitamins\n• Blue = B-complex vitamins\n• Rose = Vitamin C (immune + antioxidant)"
                }
              ]
            },

            {
              "title": "Minerals",
              "rows": [
                { "type": "mineral-electrolyte", "left": "Sodium", "right": "{{NA}} mg" },
                { "type": "mineral-electrolyte", "left": "Potassium", "right": "{{K}} mg" },
                { "type": "mineral-electrolyte", "left": "Chloride", "right": "{{CL}} mg" },

                { "type": "mineral-structural", "left": "Calcium", "right": "{{CA}} mg" },
                { "type": "mineral-structural", "left": "Magnesium", "right": "{{MG}} mg" },
                { "type": "mineral-structural", "left": "Phosphorus", "right": "{{P}} mg" },

                { "type": "mineral-trace", "left": "Iron", "right": "{{FE}} mg" },
                { "type": "mineral-trace", "left": "Zinc", "right": "{{ZN}} mg" },
                { "type": "mineral-trace", "left": "Copper", "right": "{{CU}} mg" },
                { "type": "mineral-trace", "left": "Manganese", "right": "{{MN}} mg" },
                { "type": "mineral-trace", "left": "Selenium", "right": "{{SE}} µg" },
                { "type": "mineral-trace", "left": "Iodine", "right": "{{I}} µg" },
                
                {
                    "type": "note",
                    "text": "Mineral Colour Guide:\n• Teal = Electrolytes (hydration & balance)\n• Slate = Structural (bones & support)\n• Amber = Trace minerals (enzymes & metabolism)"
                }
              ]
            },

            {
              "title": "Phytosterols & Other Bioactives",
              "rows": [
                { "type": "phyto", "left": "Total Phytosterols", "right": "{{TOTPHYTO}} mg", "bold": True},
                { "type": "phyto", "indent": 1, "left": "Beta-sitosterol", "right": "{{BSITPHYTO}} mg" },
                { "type": "phyto", "indent": 1, "left": "Campesterol", "right": "{{CAMPHYTO}} mg" },
                { "type": "phyto", "indent": 1, "left": "Stigmasterol", "right": "{{STIGPHYTO}} mg" },
                { "type": "phyto", "indent": 1, "left": "Brassicasterol", "right": "{{BRASPHYTO}} mg" },
                { "type": "phyto", "indent": 1, "left": "Delta-5-avenasterol", "right": "{{D5AVEN}} mg" },
                { "type": "phyto", "indent": 1, "left": "Delta-7-avenasterol", "right": "{{D7AVEN}} mg" },
                { "type": "phyto", "indent": 1, "left": "Delta-7-stigmastenol", "right": "{{D7STIG}} mg" },

                { "type": "organic-acid", "left": "Citric Acid", "right": "{{CITA}} g" },
                { "type": "organic-acid", "left": "Malic Acid", "right": "{{MALA}} g" }
              ]
            }
          ]
        }

        self.by_id = {item["id"]: item for item in self.items}
        self.by_name = {item["name"]: item for item in self.items}
        self.by_display_name = {item["display_name"]: item for item in self.items}
        
        self.MAX_INGREDIENT_CACHE = 1000
        self.MAX_UNIT_CACHE = 200
        
        self.STEP_WIDGET_WIDTH = 70
        self.STEP_DELETE_BTN_WIDTH = 30
        self.STEP_WIDGET_LAYOUT_SPACING = 6
        self.STEP_WIDGET_MIN_HEIGHT = 40
        self.STEP_WIDGET_MAX_HEIGHT = 200
        self.STEP_WIDGET_ADJUST_HEIGHT_NEW_HEIGHT_PADDING = 10
        
        self.RECIPE_DELEGATE_SIZEHINT = 48
        self.RECIPE_DELEGATE_CARD_RECT = (6, 4, -6, -4)
        self.RECIPE_DELEGATE_BTN_RECT = 26
        self.RECIPE_DELEGATE_PAINT_HOVER_LIGHT = 115
        self.RECIPE_DELEGATE_PAINT_TEXT_CARD_ADJUST = (12, 0, -40, 0)
        
        self.MAIN_WINDOW_WIDTH = 1000
        self.MAIN_WINDOW_LENGTH = 700
        self.LIST_VIEW_SPACING = 6
        self.RECIPE_APP_OPEN_IMAGE_POPUP_T_WIDTH = 600
        self.RECIPE_APP_OPEN_IMAGE_POPUP_T_WIDTH_PADDING = 20
        self.RECIPE_APP_OPEN_IMAGE_POPUP_LENGTH = 700



constants = config()

