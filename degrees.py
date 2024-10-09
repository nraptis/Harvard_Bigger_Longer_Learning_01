import csv
import sys

from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}

def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass


def main():
    
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "small"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")


    print("Names has ", len(names))
    print("People has ", len(people))
    print("Movies had ", len(movies))
    print("Example \"names\": ", names["tom cruise"])
    print("Example \"people\": ", people["163"])
    print("Example \"movies\"", movies["112384"])

    for tom in names["tom cruise"]:
        naybs = neighbors_for_person(tom)
        print(naybs)
        
    buildGraph()

    source = "kevin bacon" #person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = "tom hanks" #person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")


class Node:
    def __init__(self, person_id: str):
        self.person_id = person_id
        self.g_cost = int(0)
        self.f_cost = int(0)
        self.index = 0
        self.connections = []
        self.existing = set()

    # Add a connection (another PathNode)
    def add_connection(self, movie_id: str, destination: Node):
        if (movie_id, destination.person_id) not in self.existing:
            self.existing.add((movie_id, destination.person_id))
            self.connections.append(Connection(self, movie_id, destination))

    # Define less-than operator based on hCost
    def __lt__(self, other: Node) -> bool:
        return self.h_cost < other.h_cost
    
    def __hash__(self) -> int:
        return hash(self.person_id)
    
class Connection:
    def __init__(self, source: Node, movie_id: str, destination: Node):
        self.source = source
        self.movie_id = movie_id
        self.destination = destination

def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors

# Maps (person_id, movie_id) to a path object
nodes = {}

def buildGraph():
    for name in names:
        person_id = person_id_for_name(name)
        if person_id not in nodes:
            nodes[person_id] = Node(person_id)

    print(nodes)

    for name in names:
        person_id = person_id_for_name(name)
        source = nodes[person_id]
        for neighbor in neighbors_for_person(person_id):
            movie_id = neighbor[0]
            if neighbor[1] in nodes:
                destination = nodes[neighbor[1]]
                source.add_connection(movie_id, destination)
                print(source.connections)

    
    testA = Node("a")
    testB = Node("b")
    testC = Node("c")
    testD = Node("b")

    testA.add_connection("jaws", testB)
    print("a cons 1.0 => ", testA.connections)

    testA.add_connection("jaws", testB)
    print("a cons 1.1 => ", testA.connections)

    testA.add_connection("jaws", testC)
    print("a cons 1.2 => ", testA.connections)

    testA.add_connection("jaws", testB)
    print("a cons 2.0 => ", testA.connections)

    testA.add_connection("jaws", testB)
    print("a cons 2.1 => ", testA.connections)

    testA.add_connection("jaws", testC)
    print("a cons 2.2 => ", testA.connections)


def shortest_path(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
    """

    # TODO
    raise NotImplementedError


def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]





if __name__ == "__main__":
    main()
    



    

class MaxIndexedHeap:
    def __init__(self):
        self.data = []
        self.count = 0

    def insert(self, element):
        if element is not None:
            if self.count < len(self.data):
                self.data[self.count] = element
            else:
                self.data.append(element)

            self.data[self.count].index = self.count
            bubble = self.count
            parent = (bubble - 1) >> 1
            self.count += 1

            while bubble > 0:
                if self.data[bubble] > self.data[parent]:
                    self.data[bubble], self.data[parent] = self.data[parent], self.data[bubble]
                    self.data[bubble].index, self.data[parent].index = self.data[parent].index, self.data[bubble].index
                    bubble = parent
                    parent = (bubble - 1) >> 1
                else:
                    break

    def peek(self):
        if self.count > 0:
            return self.data[0]
        return None

    def pop(self):
        if self.count > 0:
            result = self.data[0]
            self.count -= 1
            self.data[0] = self.data[self.count]
            self.data[0].index = 0
            bubble = 0
            left_child = 1
            right_child = 2
            while left_child < self.count:
                max_child = left_child
                if right_child < self.count and self.data[right_child] > self.data[left_child]:
                    max_child = right_child
                if self.data[bubble] < self.data[max_child]:
                    self.data[bubble], self.data[max_child] = self.data[max_child], self.data[bubble]
                    self.data[bubble].index, self.data[max_child].index = self.data[max_child].index, self.data[bubble].index
                    bubble = max_child
                    left_child = bubble * 2 + 1
                    right_child = left_child + 1
                else:
                    break
            return result
        return None

    def remove(self, element):
        self.remove_at(element.index)

    def remove_at(self, index):
        new_count = self.count - 1
        if index != new_count:
            self.data[index], self.data[new_count] = self.data[new_count], self.data[index]
            self.data[index].index, self.data[new_count].index = self.data[new_count].index, self.data[index].index
            bubble = index
            left_child = bubble * 2 + 1
            right_child = left_child + 1
            while left_child < new_count:
                max_child = left_child
                if right_child < new_count and self.data[right_child] > self.data[left_child]:
                    max_child = right_child
                if self.data[bubble] < self.data[max_child]:
                    self.data[bubble], self.data[max_child] = self.data[max_child], self.data[bubble]
                    self.data[bubble].index, self.data[max_child].index = self.data[max_child].index, self.data[bubble].index
                    bubble = max_child
                    left_child = bubble * 2 + 1
                    right_child = left_child + 1
                else:
                    break

            bubble = index
            parent = (bubble - 1) >> 1
            while bubble > 0:
                if self.data[bubble] > self.data[parent]:
                    self.data[bubble], self.data[parent] = self.data[parent], self.data[bubble]
                    self.data[bubble].index, self.data[parent].index = self.data[parent].index, self.data[bubble].index
                    bubble = parent
                    parent = (bubble - 1) >> 1
                else:
                    break

        self.count = new_count
        return self.data[self.count]