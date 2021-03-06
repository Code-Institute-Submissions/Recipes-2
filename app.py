import os
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_pymongo import PyMongo, DESCENDING
from bson.objectid import ObjectId
import re

app = Flask(__name__)

app.config["MONGO_DBNAME"] = 'myRecipes'
app.config['MONGO_URI'] = os.environ.get("MONGO_URI")

mongo = PyMongo(app)

@app.route('/')
@app.route('/index')
def index():
    """This shows a list of 3 recipes which have the highest views"""
    recipes=mongo.db.recipes.find().sort([('views', DESCENDING)]).limit(3)
    return render_template('index.html', title="Home", recipes=recipes)
    
    
@app.route('/recipe_listing')
def recipe_listing():
    """This shows a list of all of the recipes"""
    recipes=mongo.db.recipes.find()
    return render_template('recipe-listing.html', title="Recipes", recipes=recipes)
    
    
@app.route('/recipe/<recipe_id>')
def recipe(recipe_id):
    """This shows all fields in recipes & increments the views by 1"""
    mongo.db.recipes.find_one_and_update(
        {'_id': ObjectId(recipe_id)},
        {'$inc': {'views': 1}}
    )
    recipe = mongo.db.recipes.find_one_or_404({'_id': ObjectId(recipe_id)})
    return render_template('recipe.html', title="Recipe", recipe=recipe)
    
    
@app.route('/create_recipe')
def create_recipe():
    """This shows a list of all of the recipes"""
    recipes_db = mongo.db.recipes
    return render_template('create-recipe.html', title="Create Recipe")
    
    
@app.route('/insert_recipe', methods=['POST'])
def insert_recipe():
    """This will add each field to the database"""
    recipe_db = mongo.db.recipes
    # This is insert a new value for each field
    recipe_db.insert_one(request.form.to_dict())
    return redirect(url_for('recipe_listing'))
    
    
@app.route('/edit_recipe/<recipe_id>')
def edit_recipe(recipe_id):
    """This will find a specific recipe from the database"""
    recipes_db = mongo.db.recipes.find_one({ '_id': ObjectId(recipe_id) })
    return render_template('edit-recipe.html', title="Edit Recipe", recipe=recipes_db)
    

@app.route('/update_recipe/<recipe_id>', methods=['POST'])
def update_recipe(recipe_id):
    """This shows a list of all of the recipes"""
    recipe_db = mongo.db.recipes
    recipe_db.update({ '_id': ObjectId(recipe_id)}, 
    {
        'recipe_name':request.form.get('recipe_name'),
        'recipe_description':request.form.get('recipe_description'),
        'recipe_ingredients': request.form.get('recipe_ingredients'),
        'recipe_instructions': request.form.get('recipe_instructions'),
        'recipe_keywords': request.form.get('recipe_keywords'),
        'recipe_image_url':request.form.get('recipe_image_url')
    })
    return redirect(url_for('recipe_listing'))
    

@app.route('/search')
def search():
    """This is the logic behind the search bars"""
    orig_query = request.args['query']
    # Using regular expressions to search for any case
    query = {'$regex': re.compile('.*{}.*'.format(orig_query)), '$options': 'i'}
    # This will do a find amoungst recipe name, recipe description & recipe instructions
    results = mongo.db.recipes.find({
        '$or': [
            {'recipe_name': query},
            {'recipe_description': query},
            {'recipe_instructions': query},
            {'recipe_keywords': query}
        ]
    })
    
    recipes = []
    for result in results:
        recipes.append(result)
    
    return render_template('search.html', title="Search results for", query=orig_query, results=recipes)
    
    
@app.route('/delete_recipe/<recipe_id>')
def delete_recipe(recipe_id):
    """This shows a list of all of the recipes"""
    mongo.db.recipes.remove({ '_id': ObjectId(recipe_id) })
    return redirect(url_for('recipe_listing'))
    
    
@app.errorhandler(404)
def handle_404(not_found):
    return render_template('error404.html', title="Error 404", not_found=not_found)
    
  
if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
    port=int(os.environ.get('PORT')),
    debug=False)


