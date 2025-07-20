from fastapi import FastAPI, UploadFile, File, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

app = FastAPI(
    title="Cake Recipe Finder API",
    description="Backend API for cake recipe suggestion and ingredient recognition.",
    version="0.1.0",
    openapi_tags=[
        {"name": "Ingredients", "description": "Operations related to ingredient input and recognition."},
        {"name": "Recipes", "description": "Recipe suggestion operations."},
        {"name": "Favorites", "description": "Favorites management endpoints."},
        {"name": "Misc", "description": "Other utility endpoints."}
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for demonstration (replace with persistent storage/DB later)
FAKE_USER_ID = "user123"
user_favorites: Dict[str, List[Dict[str, Any]]] = {}

### --------- Data Models ---------
class IngredientTextRequest(BaseModel):
    text: str = Field(..., description="Ingredient(s) as a free-form text string.")

class IngredientImageResponse(BaseModel):
    filename: str = Field(..., description="Stored filename.")
    message: str = Field(..., description="Status message.")

class IngredientRecognitionRequest(BaseModel):
    # Placeholder for now: support text or image (encoded string)
    text: Optional[str] = Field(None, description="Ingredient list as text.")
    image_bytes_b64: Optional[str] = Field(
        None,
        description="Ingredient image file content as base64-encoded string."
    )

class IngredientRecognitionResult(BaseModel):
    ingredients: List[str] = Field(..., description="Recognized ingredient objects.")

class RecipeSuggestRequest(BaseModel):
    ingredients: List[str] = Field(..., description="List of available ingredient names.")

class Recipe(BaseModel):
    id: str = Field(..., description="Unique recipe ID.")
    name: str = Field(..., description="Recipe title.")
    description: str = Field(..., description="Recipe description.")
    ingredients: List[str] = Field(..., description="Ingredients required.")
    steps: List[str] = Field(..., description="Baking/preparation steps.")

class RecipeSuggestResponse(BaseModel):
    recipes: List[Recipe] = Field(..., description="List of suggested recipes.")

class FavoriteAddRequest(BaseModel):
    recipe_id: str = Field(..., description="ID of the recipe to add to favorites.")
    recipe: Recipe = Field(..., description="Recipe details to add to favorites.")

class FavoritesListResponse(BaseModel):
    favorites: List[Recipe] = Field(..., description="List of favorite recipes for the user.")

### --------- API Endpoints ---------

@app.get("/", tags=["Misc"])
# PUBLIC_INTERFACE
def health_check():
    """Health check endpoint to verify the API is running."""
    return {"message": "Healthy"}

# POST /ingredients/text
@app.post("/ingredients/text", tags=["Ingredients"], summary="Input ingredients as text", response_model=IngredientRecognitionResult)
# PUBLIC_INTERFACE
def accept_ingredients_text(ingredient_request: IngredientTextRequest):
    """
    Accept ingredients as a text string.
    Returns placeholder recognized ingredient names.
    """
    # Simulate basic text split
    raw = ingredient_request.text.strip()
    ingredients = [i.strip().lower() for i in raw.split(",") if i.strip()]
    # TODO: Integrate NLP/AI logic here
    return {"ingredients": ingredients}

# POST /ingredients/image
@app.post("/ingredients/image", tags=["Ingredients"], summary="Upload ingredient image", response_model=IngredientImageResponse)
# PUBLIC_INTERFACE
async def accept_ingredient_image(file: UploadFile = File(...)):
    """
    Accept an image file containing ingredients.
    Returns upload confirmation (image not stored, logic stubbed).
    """
    # image_content = await file.read()
    # Here you would save or process image_content; stub only.
    return IngredientImageResponse(filename=file.filename, message="Image received (stub, not processed).")

# POST /ingredients/recognize
@app.post("/ingredients/recognize", tags=["Ingredients"], summary="Recognize ingredients from text/image (stub)", response_model=IngredientRecognitionResult)
# PUBLIC_INTERFACE
def recognize_ingredients(
    req: IngredientRecognitionRequest = Body(...),
):
    """
    Recognize ingredients from a text or image input.
    (Stub implementation: returns fixed set for demo.)
    """
    # In a real implementation, the image bytes/text would go to ML model or external service.
    return IngredientRecognitionResult(ingredients=["egg", "flour", "sugar", "butter"])

# GET /recipes/suggest
@app.get("/recipes/suggest", tags=["Recipes"], summary="Suggest cake recipes based on ingredients", response_model=RecipeSuggestResponse)
# PUBLIC_INTERFACE
def suggest_recipes(ingredients: List[str] = []):
    """
    Suggest one or more cake recipes matching the provided ingredients.
    (Stub implementation with static demo recipes.)
    """
    # Normally, you would query the recipe index for best matches.
    sample_recipes = [
        Recipe(
            id="cake001",
            name="Classic Sponge Cake",
            description="A simple and delicious sponge cake.",
            ingredients=["flour", "egg", "sugar", "butter"],
            steps=[
                "Preheat oven to 180°C.",
                "Mix all ingredients.",
                "Bake 30 minutes."
            ],
        ),
        Recipe(
            id="cake002",
            name="Chocolate Fudge Cake",
            description="Rich chocolate cake for chocolate lovers.",
            ingredients=["flour", "egg", "sugar", "butter", "cocoa powder"],
            steps=[
                "Preheat oven to 180°C.",
                "Mix all ingredients.",
                "Add cocoa powder.",
                "Bake 35 minutes."
            ],
        ),
    ]
    # Stub filtering for present demo
    result = [r for r in sample_recipes if all(i in ingredients for i in r.ingredients[:2])] if ingredients else sample_recipes
    return RecipeSuggestResponse(recipes=result)

# POST /favorites/add
@app.post("/favorites/add", tags=["Favorites"], summary="Add a recipe to favorites")
# PUBLIC_INTERFACE
def add_favorite(fav: FavoriteAddRequest):
    """
    Add a recipe to the user's favorites.
    (Stub: saves to in-memory list by fake user ID.)
    """
    uid = FAKE_USER_ID
    # We'll store favorite recipes as list of unique recipe dicts
    favs = user_favorites.setdefault(uid, [])
    # No duplication
    if not any(f["id"] == fav.recipe.id for f in favs):
        favs.append(fav.recipe.model_dump())
        return {"status": "added"}
    else:
        return {"status": "already in favorites"}

# GET /favorites/list
@app.get("/favorites/list", tags=["Favorites"], summary="List favorite recipes", response_model=FavoritesListResponse)
# PUBLIC_INTERFACE
def list_favorites():
    """
    List current user's favorite recipes.
    (Stub: always returns for fake user ID.)
    """
    uid = FAKE_USER_ID
    favs = user_favorites.get(uid, [])
    return FavoritesListResponse(favorites=favs)

