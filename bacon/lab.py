"""
6.101 Lab:
Bacon Number
"""

#!/usr/bin/env python3

import pickle

# import typing # optional import
# import pprint # optional import

# NO ADDITIONAL IMPORTS ALLOWED!


def transform_data(raw_data):
    """The raw data comes in the form of (actorid1, actor_id2, movie_id).
    I want to turn into two dictionary, one which stores
    the relation of actors to other actors
    and one which stores the relation of actors to movies they play.

    Args:
        raw_data (list_of_tuples): (actorid1, actor_id2, movie_id

    Returns: tuple: {actorid1:{actorid2, actorid3}},
            {(actor1, actor2): {movie_id1, movid_id2...}}
    """
    out_id_dict = {}
    out_movie_dict = {}
    for actor_id1, actor_id2, movie_id in raw_data:
        # creating the movie dictionary
        id1, id2 = sorted((actor_id1, actor_id2))  # so that we don't have to check
        if (id1, id2) not in out_movie_dict:
            out_movie_dict[(id1, id2)] = {movie_id}
        else:
            out_movie_dict[(id1, id2)].add(movie_id)

        ## Creating the id connection dictionary
        if actor_id1 not in out_id_dict:
            out_id_dict[actor_id1] = {actor_id2}
        else:
            out_id_dict[actor_id1].add(actor_id2)

        if actor_id2 not in out_id_dict:
            out_id_dict[actor_id2] = {actor_id1}
        else:
            out_id_dict[actor_id2].add(actor_id1)

    return out_id_dict, out_movie_dict


def retrieve_names(names_db, id__):
    """Given the names database {'name': id}, this functions retrieves the name
    for a given id__.  Works for both actor name database as well as movie name database.
    """
    for name, test_id in names_db.items():
        if test_id == id__:
            return name
    return None


def get_movies(transformed_data, movies_db, connection_list):
    """Given the transformed data as the output
    of the transform function, the movies database,
    and the connection list of actors id, the function
    returns the name of the movies that connects them.
    """

    _, movie_dict = transformed_data
    connected_movies = []
    movies_id = []
    movies_names = []

    for i in range(len(connection_list) - 1):
        actor1, actor2 = sorted((connection_list[i], connection_list[i + 1]))
        movie_ids = movie_dict[(actor1, actor2)]
        movie_name = retrieve_names(
            movies_db, min(movie_ids)
        )  # An arbitrary movie selected
        movies_id.append(min(movie_ids))
        movies_names.append(movie_name)
    return movies_id, movies_names


def get_actors_for_movie(moviedict, movieid):
    """Given the moviedict, the function returns the actors who have
    played in the movie of the movieid."""
    out_actors = set()
    for actors, movie_ids in moviedict.items():
        if movieid in movie_ids:
            out_actors.update({*actors})  # add the actors into the out_set
        else:
            continue
    return out_actors


def acted_together(transformed_data, actor_id_1, actor_id_2):
    """The function evaluates whether two actors have played together"""
    transformed_data, _ = transformed_data
    if actor_id_1 == actor_id_2:
        return True
    # check for whether the actors are in the transformed data
    if actor_id_1 not in transformed_data:
        return False
    if actor_id_2 not in transformed_data:
        return False

    # Since ids are in the dictionary
    out_actor1 = transformed_data[actor_id_1]
    out_actor2 = transformed_data[actor_id_2]

    return (actor_id_1 in out_actor2) or (actor_id_2 in out_actor1)


def actors_with_bacon_number(transformed_data, n):
    """Given the transformed data, the function returns all actors who are of
    n bacon numbers"""
    actor_to_actors, _ = transformed_data
    if n == 0:
        return {4724}
    else:
        seen_set = {4724}  # bacon id
        prev_bacon_set = {4724}
        for _ in range(1, n + 1):  # go to the next bacon set
            curr_bacon_set = set()
            for main_actor in prev_bacon_set:  # the connecting node
                sub_actors = actor_to_actors[main_actor]
                for sub_actor in sub_actors:
                    if (
                        sub_actor not in seen_set
                    ):  # being seen implies that they are one of the main actors
                        curr_bacon_set.add(sub_actor)
                        seen_set.add(sub_actor)
                    else:
                        continue
            prev_bacon_set = curr_bacon_set
            if (
                prev_bacon_set == set()
            ):  # if there is no main actor, we have reached the end
                break
    return prev_bacon_set


def bacon_path(transformed_data, actor_id):
    """Given an actor, the function returns a list that highlights one of the shortest
    path from the start(Kevin Bacon) to the given actor"""
    bacon_id = 4724
    return actor_to_actor_path(transformed_data, bacon_id, actor_id)


def actor_to_actor_path(transformed_data, actor_id_1, actor_id_2):
    """Given two actors and the transformed data, the function
    returns the shortest path between the two."""
    test_function = lambda id__: id__ == actor_id_2
    return actor_path(transformed_data, actor_id_1, test_function)

def actor_path(transformed_data, actor_id_1, goal_test_function):
    """Given the transformed data and the starting actor, the function
    returns the path to the actor that is closest to the starting actor
    that satisfies the goal_test_function"""

    transformed_data, _ = transformed_data
    start_id = actor_id_1
    if goal_test_function(start_id):
        return [start_id]

    paths = [[start_id]]
    visited = {start_id}
    arrived = False
    while not arrived:
        if paths:
            branch = paths.pop(0)
        else:
            return None
        next_actors = transformed_data[branch[-1]]
        if next_actors:
            for next_actor in next_actors:
                if next_actor in visited:
                    continue
                else:
                    visited.add(next_actor)
                    paths.append(branch + [next_actor])
                if goal_test_function(next_actor):
                    arrived = True
                    break
        else:
            continue
    return paths[-1]


def actors_connecting_films(transformed_data, film1, film2):
    """Given the tranformed data and two films, the function returns
    the shortest path between actors who played in film1 and film2."""
    transformed_data, moviedict = transformed_data
    actors_for_film1 = get_actors_for_movie(moviedict, film1)
    actors_for_film2 = get_actors_for_movie(moviedict, film2)
    movie_test_function = lambda actor: actor in actors_for_film2
    paths = []
    visited = set()
    for actor in actors_for_film1:
        if movie_test_function(actor):
            return [actor]
        paths.append([actor,])
        visited.add(actor)

    while paths:
        branch = paths.pop(0)
        next_actors = transformed_data[branch[-1]]
        if next_actors:
            for next_actor in next_actors:
                cur_branch = branch + [next_actor]
                if next_actor in visited:
                    continue
                else:
                    visited.add(next_actor)
                    paths.append(cur_branch)
                if movie_test_function(next_actor):
                    return cur_branch
        else:
            continue
    return None

    # shortest_path = []
    # shortest_path_length = float("inf")
    # flag = False
    # for actor1 in actors_for_film1:
    #     for actor2 in actors_for_film2:
    #         path_found = actor_to_actor_path(transformed_data, actor1, actor2)
    #         if path_found is None:
    #             continue
    #         if len(path_found) < shortest_path_length:
    #             shortest_path = path_found
    #             shortest_path_length = len(path_found)
    #             flag = True
    # if not flag:  # no paths found
    #     return None
    # else:
    #     return shortest_path


if __name__ == "__main__":
    # ## Loading
    # with open("resources/small.pickle", "rb") as f:
    #     smalldb = pickle.load(f)
    # ##movies database
    # with open("resources/movies.pickle", "rb") as f:
    #     moviesdb = pickle.load(f)
    # # ## Names database
    # with open("resources/names.pickle", "rb") as f:
    #     namesdb = pickle.load(f)
    # with open("resources/tiny.pickle", "rb") as f:
    #     tinydb = pickle.load(f)

    # with open("resources/large.pickle", "rb") as f:
    #     largedb = pickle.load(f)

    # # print(tinydb)
    # tf_large = transform_data(largedb)
    # tf_tiny = transform_data(tinydb)
    # tf_small = transform_data(smalldb)

    # #### Submission 1 ######

    # print(f"Diana Lyubenova's ID no: ", namesdb['Diana Lyubenova']) #1189509
    # print(retrieve_names(namesdb, 108188))
    # #### Submission 2 #######
    # print(acted_together(tf_small,
    #                   namesdb['Jeff Perry'],
    #                   namesdb['Marc Macaulay']))
    # print(acted_together(tf_small,
    #                       namesdb['Francois Perier']
    #                       namesdb['Robert Viharo']))

    # #### Submssion 3 #####
    # ids0 = actors_with_bacon_number(tf_tiny,0)
    # ids1 = actors_with_bacon_number(tf_tiny, 1)
    # ids2 = actors_with_bacon_number(tf_tiny, 2)
    # ids3 = actors_with_bacon_number(tf_tiny, 3)
    # print(ids0, ids1, ids2, ids3)

    # #### Submission 4 ###
    # ids = actors_with_bacon_number(tf_large, 6)
    # print(ids)
    # names_set = set()
    # for id in ids:
    #     names_set.add(retrieve_names(namesdb, id))
    # print(names_set)

    # #### Submission 4 ######

    # end_actor = 1640
    # path_to_endactor = bacon_path(tf_tiny, end_actor)
    # print(path_to_endactor)

    # anita_id = namesdb['Anita Barnes']
    # path_to_anita = bacon_path(tf_large, anita_id)
    # names_to_anita = []
    # for id in path_to_anita:
    #     names_to_anita.append(retrieve_names(namesdb, id))
    # print(names_to_anita)

    # ##### Submission 5 ######

    # marcella_id = namesdb['Marcella Daly']
    # Theresa_id = namesdb['Theresa Russell']
    # path_found = actor_to_actor_path(tf_large, marcella_id, Theresa_id)
    # names_involved = []
    # for id in path_found:
    #     names_involved.append(retrieve_names(namesdb, id))
    # print(names_involved)

    # #### Submission 6 ########

    # emily_id = namesdb['Emily Ann Lloyd']
    # vjeran_id = namesdb['Vjeran Tin Turk']
    # path_found = actor_to_actor_path(tf_large, emily_id, vjeran_id)
    # print(path_found)
    # movies_id, movies_name = get_movies(tf_large, moviesdb, path_found)
    # print(movies_name)

    pass
