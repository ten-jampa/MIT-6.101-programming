"""
6.101 Lab:
Recipes
"""

import pickle
import sys

# import typing # optional import
# import pprint # optional import

sys.setrecursionlimit(20_000)
# NO ADDITIONAL IMPORTS!


def atomic_ingredient_costs(recipes_db):
    """
    Given a recipes database, a list containing compound and atomic food tuples,
    make and return a dictionary mapping each atomic food name to its cost.
    """
    atomic_dict = {}
    for ingredient in recipes_db:
        if ingredient[0] == "atomic":
            atomic_dict[ingredient[1]] = ingredient[2]
    return atomic_dict


def compound_ingredient_possibilities(recipes_db):
    """
    Given a recipes database, a list containing compound and atomic food tuples,
    make and return a dictionary that maps each compound food name to a
    list of all the ingredient lists associated with that name.
    """
    compound_dict = {}
    for ingredient in recipes_db:
        if ingredient[0] == "compound":
            if ingredient[1] not in compound_dict:
                compound_dict[ingredient[1]] = [ingredient[2]]
            else:
                compound_dict[ingredient[1]] += [ingredient[2]]
    return compound_dict


def lowest_cost(recipes_db, food_name, restrictions=()):
    """
    Given a recipes database and the name of a food (str), return the lowest
    cost of a full recipe for the given food item or None if there is no way
    to make the food_item.
    """
    atomic_ingredient_costs__ = atomic_ingredient_costs(recipes_db)
    compound_ingredient_possibilities__ = compound_ingredient_possibilities(recipes_db)
    restrictions = set(restrictions)

    ##Defining the recursive function
    def cost_recursion(food_name__):
        # Base case 1: if the food is in the dietary restrictions:
        if food_name__ in restrictions:
            # print('I enter the restriction condition', flush = True)
            return None

        # Base case 2: if the food is an atomic food
        if food_name__ in atomic_ingredient_costs__:
            return atomic_ingredient_costs__[food_name__]

        # Base case 3: if the food is not in the recipes_db
        possibilities = compound_ingredient_possibilities__.get(food_name__, [])
        if not possibilities:
            return None

        # Recursive Case: the food is a compound food
        cost = []
        for sub_ingredients in possibilities:
            sub_cost = 0
            for sub_food, quantity in sub_ingredients:
                recursive_cost = cost_recursion(sub_food)
                if recursive_cost is None:
                    sub_cost = None
                    break
                else:
                    sub_cost += quantity * recursive_cost  # when it's not a None object

            if sub_cost is None:
                continue  # You just don't add it to the list
            else:
                cost.append(sub_cost)
        if not cost:
            return None
        return min(cost)

    return cost_recursion(food_name)


def scaled_recipe(recipe_dict, n):
    """
    Given a dictionary of ingredients mapped to quantities needed, returns a
    new dictionary with the quantities scaled by n.
    """
    return {key: n * val for key, val in recipe_dict.items()}


def add_recipes(recipe_dicts):
    """
    Given a list of recipe dictionaries that map food items to quantities,
    return a new dictionary that maps each ingredient name
    to the sum of its quantities across the given recipe dictionaries.

    For example,
        add_recipes([{'milk':1, 'chocolate':1}, {'sugar':1, 'milk':2}])
    should return:
        {'milk':3, 'chocolate': 1, 'sugar': 1}
    """
    added_reciped_dict = {}
    for sub_recipes in recipe_dicts:
        for key, val in sub_recipes.items():
            added_reciped_dict[key] = added_reciped_dict.get(key, 0) + val
    return added_reciped_dict

def cheapest_flat_recipe(recipes_db, food_name, restrictions=()):
    """
    Given a recipes database and the name of a food (str), return a dictionary
    (mapping atomic food items to quantities) representing the cheapest full
    recipe for the given food item.

    Returns None if there is no possible recipe.
    """
    atomic_ingredients_costs__ = atomic_ingredient_costs(recipes_db)
    compound_ingredient_possibilities__ = compound_ingredient_possibilities(recipes_db)
    restrictions = set(restrictions)

    def is_cheapest(recipe_dicts):
        cheapest_dict_index = None
        cheapest = float("inf")
        for i, recipe_dict in enumerate(recipe_dicts):
            total_cost = sum(
                [
                    quantity * atomic_ingredients_costs__[ingr]
                    for ingr, quantity in recipe_dict.items()
                ]
            )
            if total_cost < cheapest:
                cheapest = total_cost
                cheapest_dict_index = i
        return recipe_dicts[cheapest_dict_index]

    # let's define the recursive function:
    def recipe_recursion(food_name__):

        # Base Case 1: If the food is restricted:
        if food_name__ in restrictions:
            # print('I am in the restrictions')
            return None

        # Base Case 2: If the food is atomic:
        if food_name__ in atomic_ingredients_costs__:
            # print(f'I have hit the base case {food_name__}')
            return {food_name__: 1}

        # Base Case 3: If the food is not in atomic nor compound:
        possibilities = compound_ingredient_possibilities__.get(food_name__, [])
        if not possibilities:
            # print('I am here in the third base case')
            return None

        # Recursive Case:
        out_recipes = []
        for sub_ingredients in possibilities:
            # print(sub_ingredients)
            sub_recipes = []
            for sub_food, quantity in sub_ingredients:
                recursive_recipe = recipe_recursion(sub_food)  # {'atomic ingredient':1}
                # print(recursive_recipe, flush = True)
                if recursive_recipe is None:
                    sub_recipes.append(None)  # Anything below is not usable
                    break
                else:
                    scaled_recursive_recipe = scaled_recipe(recursive_recipe, quantity)
                    sub_recipes.append(scaled_recursive_recipe)
                    # print(sub_recipes)

            if (
                None in sub_recipes
            ):  # this chain of subingredients is useless, move on to the next one
                continue
            else:
                out_recipes.append(add_recipes(sub_recipes))

        if not out_recipes:
            return None
        else:
            return is_cheapest(out_recipes)

    return recipe_recursion(food_name)


def combine_recipes(nested_recipes):
    """
    Given a list of lists of recipe dictionaries, where each inner list
    represents all the recipes for a certain ingredient, compute and return a
    list of recipe dictionaries that represent all the possible combinations of
    ingredient recipes.
    """
    ###
    # Base case
    if len(nested_recipes) == 1:  # the list only has recipe of one food
        return nested_recipes[0]

    # Recursive case
    first, rest = nested_recipes[0], nested_recipes[1:]  # first will be a list
    # first will be a list of dictionarys
    out = []
    for ing_dict1 in first:
        for ing_dict2 in combine_recipes(rest):
            out.append(add_recipes([ing_dict1, ing_dict2]))
    return out


def all_flat_recipes(recipes_db, food_name, restrictions=()):
    """
    Given a recipes database, the name of a food (str), produce a list (in any
    order) of all possible flat recipe dictionaries for that category.

    Returns an empty list if there are no possible recipes
    """
    atomic_ingredients_costs__ = atomic_ingredient_costs(recipes_db)
    # print(atomic_ingredients_costs__)
    compound_ingredient_possibilities__ = compound_ingredient_possibilities(recipes_db)
    # print(compound_ingredient_possibilities__)
    restrictions = set(restrictions)

    def flat_recipe_recursion(food_name__):
        # Base Case 1: If the food is restricted:
        if food_name__ in restrictions:
            # print('I have reached the first base case')
            # print('I am in the restrictions')
            return []
        # Base Case 2: If the food is atomic:
        if food_name__ in atomic_ingredients_costs__:
            # print('I have reached the second base case')
            return [{food_name__: 1}]
        # Base Case 3: If the food is not in atomic nor compound:
        possibilities = compound_ingredient_possibilities__.get(food_name__, [])
        if not possibilities:
            # print('I have reached the third base case')
            return []

        # Recursive Case:
        all_recipes = []
        for sub_ingredients in possibilities:
            # print(f'sub: {sub_ingredients}')
            # print(out_recipes, flush =True)
            sub_recipes = []
            valid = True

            for sub_food, quantity in sub_ingredients:
                # print(sub_food)
                recursive_recipes = flat_recipe_recursion(
                    sub_food
                )  # {'atomic ingredient':1}
                # print(recursive_recipe, flush = True)
                if not recursive_recipes:
                    valid = False  # Anything below is not usable
                    break
                scaled_recursive_recipes = [
                    scaled_recipe(recipe, quantity) for recipe in recursive_recipes
                ]
                sub_recipes.append(scaled_recursive_recipes)

            if not valid:
                continue
                # print(out_recipes)

            if not sub_recipes:
                all_recipes.append({})
            else:
                combined = combine_recipes(sub_recipes)
                all_recipes.extend(combined)
        return all_recipes

    return flat_recipe_recursion(food_name)



if __name__ == "__main__":
    # load example recipes from section 3 of the write-up
    with open("test_recipes/example_recipes.pickle", "rb") as f:
        example_recipes_db = pickle.load(f)
    # # you are free to add additional testing code here!
    # # print()
    # # print(atomic_ingredient_costs(example_recipes_db))
    # # print()
    # # print(sum([cost for item, cost
    # in atomic_ingredient_costs(example_recipes_db).items()
    # ]))
    # # print()
    # # # print(compound_ingredient_possibilities(example_recipes_db))
    # dairy_recipes_db = [
    #     ("compound", "milk", [("cow", 1), ("milking stool", 1)]),
    #     ("compound", "cheese", [("milk", 1), ("time", 1)]),
    #     ("compound", "cheese", [("cutting-edge laboratory", 11)]),
    #     ("atomic", "milking stool", 5),
    #     ("atomic", "cutting-edge laboratory", 1000),
    #     ("atomic", "time", 10000),
    #     ("atomic", "cow", 100),
    # ]
    # # print(lowest_cost(dairy_recipes_db, 'cheese', ['cutting-edge laboratory', 'cow']))

    # #     cookie_recipes_db = [
    # #     ('compound', 'cookie sandwich', [('cookie', 2), ('ice cream scoop', 3)]),
    # #     ('compound', 'cookie', [('chocolate chips', 3)]),
    # #     ('compound', 'cookie', [('sugar', 10)]),
    # #     ('atomic', 'chocolate chips', 200),
    # #     ('atomic', 'sugar', 5),
    # #     ('compound', 'ice cream scoop', [('vanilla ice cream', 1)]),
    # #     ('compound', 'ice cream scoop', [('chocolate ice cream', 1)]),
    # #     ('atomic', 'vanilla ice cream', 20),
    # #     ('atomic', 'chocolate ice cream', 30),
    # # ]

    # #     print(lowest_cost(cookie_recipes_db, 'cookie sandwich'))
    # # soup = {"carrots": 5, "celery": 3, "broth": 2, "noodles": 1, "chicken": 3, "salt": 10}
    # # carrot_cake = {"carrots": 5, "flour": 8, "sugar": 10, "oil": 5, "eggs": 4, "salt": 3}
    # # bread = {"flour": 10, "sugar": 3, "oil": 3, "yeast": 15, "salt": 5}
    # # recipe_dicts = [soup, carrot_cake, bread]
    # # print(scaled_recipe(soup, 3))
    # # print()
    # # print(add_recipes(recipe_dicts))

    # # print(cheapest_flat_recipe(dairy_recipes_db, 'cheese', ['cow']))
    # # print(cheapest_flat_recipe(example_recipes_db, 'time'))
    # # print(cheapest_flat_recipe(example_recipes_db, 'protein'))
    # # print(cheapest_flat_recipe(example_recipes_db, 'bread'))
    # # print(cheapest_flat_recipe(example_recipes_db, 'burger'))
    # # print(cheapest_flat_recipe(example_recipes_db, 'ketchup'))
    # # print(cheapest_flat_recipe(dairy_recipes_db, 'cheese', ('milking stool',)))
    # cookie_recipes_db = [
    #     ("compound", "cookie sandwich", [("cookie", 2), ("ice cream scoop", 3)]),
    #     ("compound", "cookie", [("chocolate chips", 3)]),
    #     ("compound", "cookie", [("sugar", 10)]),
    #     ("atomic", "chocolate chips", 200),
    #     ("atomic", "sugar", 5),
    #     ("compound", "ice cream scoop", [("vanilla ice cream", 1)]),
    #     ("compound", "ice cream scoop", [("chocolate ice cream", 1)]),
    #     ("atomic", "vanilla ice cream", 20),
    #     ("atomic", "chocolate ice cream", 30),
    # ]
    # print(all_flat_recipes(cookie_recipes_db, "cookie sandwich"))
    # pass
