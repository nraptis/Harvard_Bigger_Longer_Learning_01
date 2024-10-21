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
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"

    # Load data from files into memory
    load_data(directory)
        
    buildGraph()

    #source = person_id_for_name(input("Name: "))
    source = person_id_for_name("miley cyrus")

    if source is None:
        sys.exit("Person not found.")
    #target = "dustin hoffman" #person_id_for_name(input("Name: "))
    target = person_id_for_name("danny glover")# #person_id_for_name(input("Name: "))
    
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
        self.cost = int(100000000)
        self.index = 0
        self.connections = []
        self.existing = set()
        self.path_previous_node = None
        self.path_via_movie = None

    # Add a connection (another PathNode)
    def add_connection(self, movie_id: str, destination: Node):
        if (movie_id, destination.person_id) not in self.existing:
            if destination.person_id != self.person_id:
                self.existing.add((movie_id, destination.person_id))
                self.connections.append(Connection(self, movie_id, destination))

class Connection:
    def __init__(self, source: Node, movie_id: str, destination: Node):
        self.source = source
        self.movie_id = movie_id
        self.destination = destination

class MinIndexedHeap:
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
                if self.data[bubble].cost < self.data[parent].cost:
                    self.data[bubble], self.data[parent] = self.data[parent], self.data[bubble]
                    self.data[bubble].index, self.data[parent].index = self.data[parent].index, self.data[bubble].index
                    bubble = parent
                    parent = (bubble - 1) >> 1
                else:
                    break

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
                min_child = left_child
                if right_child < self.count and self.data[right_child].cost < self.data[left_child].cost:
                    min_child = right_child
                if self.data[bubble].cost > self.data[min_child].cost:
                    self.data[bubble], self.data[min_child] = self.data[min_child], self.data[bubble]
                    self.data[bubble].index, self.data[min_child].index = self.data[min_child].index, self.data[bubble].index
                    bubble = min_child
                    left_child = bubble * 2 + 1
                    right_child = left_child + 1
                else:
                    break
            return result
        return None

    def is_empty(self):
        return self.count == 0

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
                min_child = left_child
                if right_child < new_count and self.data[right_child].cost < self.data[left_child].cost:
                    min_child = right_child
                if self.data[bubble].cost > self.data[min_child].cost:
                    self.data[bubble], self.data[min_child] = self.data[min_child], self.data[bubble]
                    self.data[bubble].index, self.data[min_child].index = self.data[min_child].index, self.data[bubble].index
                    bubble = min_child
                    left_child = bubble * 2 + 1
                    right_child = left_child + 1
                else:
                    break

            bubble = index
            parent = (bubble - 1) >> 1
            while bubble > 0:
                if self.data[bubble].cost < self.data[parent].cost:
                    self.data[bubble], self.data[parent] = self.data[parent], self.data[bubble]
                    self.data[bubble].index, self.data[parent].index = self.data[parent].index, self.data[bubble].index
                    bubble = parent
                    parent = (bubble - 1) >> 1
                else:
                    break

        self.count = new_count
        return self.data[new_count]

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

    for person_id in people:
        if person_id not in nodes:
            node = Node(person_id)
            nodes[person_id] = node

    for person_id in people:
        source = nodes[person_id]
        for neighbor in neighbors_for_person(person_id):
            movie_id = neighbor[0]
            if neighbor[1] in nodes:
                destination = nodes[neighbor[1]]
                source.add_connection(movie_id, destination)

def make_path(target):
    current = target
    result = []

    while True:
        if current == None:
            break
        if current.path_via_movie == None:
            break
        result.append([current.path_via_movie, current.person_id])
        current = current.path_previous_node

    result.reverse()

    return result


def shortest_path(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
    """

    source_person_id = source
    target_person_id = target

    if source_person_id in nodes and target_person_id in nodes:
        sourceNode = nodes[source_person_id]
        targetNode = nodes[target_person_id]

        sourceNode.cost = 0
        sourceNode.path_previous_node = None
        sourceNode.path_via_movie = None

        openSet = set()
        closedSet = set()
        
        openHeap = MinIndexedHeap()

        openSet.add(sourceNode)

        openHeap.insert(sourceNode)

        while not openHeap.is_empty():

            current = openHeap.pop()
            if current == targetNode:
                return make_path(targetNode)

            openSet.discard(current)
            closedSet.add(current)

            for connection in current.connections:
                
                destination = connection.destination
                if destination not in closedSet:
                    
                    cost = current.cost + 1
                    if cost < destination.cost:
                        destination.cost = cost

                        destination.path_previous_node = current
                        destination.path_via_movie = connection.movie_id

                    if destination in openSet:
                        openHeap.remove(destination)
                        openHeap.insert(destination)
                    else:
                        openSet.add(destination)
                        openHeap.insert(destination)

    return None


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
    



    
