import re 
from dataclasses import dataclass, field


def normalize_key(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().casefold()


@dataclass
class Ingredient:
    name: str
    amount: float
    unit_id: int | None
    display_name: str = ""
    unit_name: str = ""
    
    def normalise_for_lookup(self):
        return normalize_key(self.name)

@dataclass
class Step:
    index: int
    text: str

@dataclass
class Recipe:
    name: str
    servings: float
    description: str = ""
    ingredients: list[Ingredient] = field(default_factory=list)
    steps: list[Step] = field(default_factory=list)

    # In Recipe.normalize() - don't lowercase the stored name
    def normalize(self):
        self.name = self.name.strip()
        self.description = self.description.strip()
    
        for ing in self.ingredients:
            cleaned = ing.name.strip()
    
            ing.display_name = cleaned
            ing.name = cleaned  # preserve original casing
    
            if ing.unit_name:
                ing.unit_name = normalize_key(ing.unit_name)

    def validate(self):
        if not self.name:
            raise ValueError("Recipe name required")

        if self.servings is None or self.servings <= 0:
            raise ValueError("Servings must be > 0")

        if not self.ingredients:
            raise ValueError("At least one ingredient required")

        seen = set()
        for ing in self.ingredients:
            if not ing.name.strip():
                raise ValueError("Ingredient name missing")
            if ing.amount <= 0:
                raise ValueError(f"{ing.name}: amount must be > 0")

            key = normalize_key(ing.name)
            if key in seen:
                raise ValueError(f"Duplicate ingredient: {ing.name}")
            seen.add(key)

        if not self.steps:
            raise ValueError("At least one step required")

        for i, step in enumerate(self.steps, 1):
            if step.index != i:
                raise ValueError("Steps must be sequential starting at 1")
            if not step.text.strip():
                raise ValueError(f"Step {i} is empty")

@dataclass
class IngredientInput:
    name: str
    amount: float
    unit_name: str
    unit_id: int | None