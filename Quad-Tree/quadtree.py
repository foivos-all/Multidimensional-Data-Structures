from math import sqrt
from airports import airport
import time

# Simple point class containing only the x and y coordinates
class Point():
    def __init__(self, x, y):
        self.x = x
        self.y = y

# Node objects need to be able to store points so that when the number of points reaches a specified limit,
# the tree will subdivide.
class Node():
    def __init__(self, x0, y0, w, h, points):
        self.x0 = x0
        self.y0 = y0
        self.width = w
        self.height = h
        self.points = points
        self.children = []

    def get_width(self):
        return self.width # Returns the width of the Node.

    def get_height(self):
        return self.height # Returns the height of the Node.

    def get_points(self):
        return self.points # Returns the points inside the Node.

# Quadtree class containing the max number of the points inside a Node(threshold)
# as well as the points of each Node.
class QTree():
    def __init__(self, k, points):
        self.threshold = k
        self.points = points
        self.root = Node(0, 0, 90, 180, self.points) # Creates a Node object using the points.

    def add_point(self, x, y):
        self.points.append(Point(x, y)) # Everytime we add a point it creates a Point object.

    def get_points(self):
        return self.points # Returns the points inside the tree

    def subdivide(self):
        recursive_subdivide(self.root, self.threshold) # After the threshold limit is reached, the Node must subdivide.

def recursive_subdivide(node, k):
    if len(node.points) <= k:
        return # If the maximum number of points in a Node is not met, then return

    w_ = float(node.width / 2) # Calculating half the width
    h_ = float(node.height / 2) # and half the height.

    p = contains(node.x0, node.y0, w_, h_, node.points) # We gather the points that must go to another Node
    x1 = Node(node.x0, node.y0, w_, h_, p) # and then we create that Node.
    recursive_subdivide(x1, k) # We call our function recursively until each Node has 1 set of Points.

    p = contains(node.x0, node.y0 + h_, w_, h_, node.points) # We repeat this process for each child.
    x2 = Node(node.x0, node.y0 + h_, w_, h_, p)
    recursive_subdivide(x2, k)

    p = contains(node.x0 + w_, node.y0, w_, h_, node.points)
    x3 = Node(node.x0 + w_, node.y0, w_, h_, p)
    recursive_subdivide(x3, k)

    p = contains(node.x0 + w_, node.y0 + h_, w_, h_, node.points)
    x4 = Node(node.x0 + w_, node.y0 + h_, w_, h_, p)
    recursive_subdivide(x4, k)

    node.children = [x1, x2, x3, x4]

def contains(x, y, w, h, points):
    pts = []
    for point in points:
        if point.x >= x and point.x <= x + w and point.y >= y and point.y <= y + h:
            pts.append(point) # If our points are inside the specified limits we append them
    return pts # and return them.

# Helper function that returns the children of a node
def find_children(node):
    if not node.children:
        return [node] # If there are no children, then the node is a leaf and we return it.
    else:
        children = []
        for child in node.children: # If not, for every child
            children += (find_children(child)) # we call the function recursively and add every child we find
    return children # and then return it.

# Helper function that calculates the euclidean dist between two points.
def euclidean_dist(a, b):
    distance = (a[0] - b.x)**2 + (a[1] - b.y)**2 # Calculates the distance
    return sqrt(distance) # and returns the square root of the distance.

# Function that returns the knn of a point.
def get_knn(qt, point, k):
    distances = list() # We initialize an empty list that will contain our distances.
    for i in qt.points: # For all the points in our tree
        dist = euclidean_dist(point, i) # we calculate the distance between the given point and the point of the tree
        distances.append((i, dist)) # and we append the point, as well as the distance.
    distances.sort(key=lambda x: x[1]) # We sort our list according to distance.
    neighbors = list()
    for i in range(k): # Finally, we return the closest to it, according to distance
        neighbors.append(distances[i][0]) # and we append the k nn to a list
    return neighbors # and return it.

def range_search(qt, range_min, range_max):
    result = []

    for i in qt.points: # For every point in our tree
        if (i.x >= range_min[0]) and (i.x <= range_max[0]) \
                and (i.y >= range_min[1]) and (i.y <= range_max[1]): # we check our latitude and then our longitude.
            result.append(i) # If the point is within the range we append it to the result list

    return result # and finally we return the result.

NUM_OF_COLUMNS = 12

def put_into_list(file):
    temp_airport_ID = ''
    temp_name = ''
    temp_city = ''
    temp_country = ''
    temp_IATA = ''
    temp_ICAO = ''
    temp_latitude = 0.0
    temp_longitude = 0.0
    temp_altitude = 0.0
    temp_DST = ''
    temp_TZ_database_time_zone = ''
    airport_list = []

    for line in file: # For every line in the file
        j = 0 # character counter
        k = 0 # column counter
        for column in range(NUM_OF_COLUMNS): # and for every column from our records.
            content = "" # Firstly, we initialise a string.
            for character in line[j:len(line)]: # Then, we iterate through every string,
                j = j + 1 # we count the characters
                if character == ',': # and if we find a comma
                    k = k + 1 # we add 1 to our column counter, signaling that one column is finished
                    break # and we break from the character loop.
                content = content + character # We add each character to our string value
            # and we assign that string value to our temporary variables, based on the column counter.
            if k == 1: temp_airport_ID = content
            elif k == 2: temp_name = content
            elif k == 3: temp_city = content
            elif k == 4: temp_country = content
            elif k == 5: temp_IATA = content
            elif k == 6: temp_ICAO = content
            elif k == 7: temp_latitude = float(content)
            elif k == 8: temp_longitude = float(content)
            elif k == 9: temp_altitude = float(content)
            elif k == 10: temp_timezone = content
            elif k == 11:
                temp_DST = content
                k = k + 1
            elif k == 12: temp_TZ_database_time_zone = content
        # After we are through with one line, we create the airport object
        temp_airport = airport(temp_airport_ID, temp_name, temp_city, temp_country, temp_IATA, temp_ICAO, temp_latitude,
                               temp_longitude, temp_altitude, temp_timezone, temp_DST, temp_TZ_database_time_zone)
        airport_list.append(temp_airport) # and we add that object to our list of airports

    return airport_list

def get_points(list): # Takes the list of airports as an instance.
    points = [] # Initializing an empty list.

    for i in range(len(list)): # Iterating through the whole list,
        temp_list = [0, 0] # we initialize an empty list with two elements.
        temp_list[0] = list[i].latitude # First, we insert the latitude
        temp_list[1] = list[i].longitude # and secondly the longitude.
        points.append(temp_list) # Finally we append our temporary list to our list of points

    return points # and we return our list of points

def main():
    file = open("data.txt", "r")  # Open the file in reading mode.
    choice = 0
    air = put_into_list(file)  # Get the airports and their fields and put them in a list.
    points = get_points(air)  # Extract the coordinates of each point.
    quad_tree = QTree(1, []) # We create an empty Quad-tree that takes only one point per node.

    for i in range(len(points)):
        quad_tree.add_point(points[i][0], points[i][1])  # We add each point to our node.

    while choice != 3:
        print("\nYour choices are: ")
        print("1. k Nearest Neighbors.")
        print("2. Range Search.")
        print("3. Exit.\n")
        choice = int(input("Press the corresponding number of the action you would like to do: "))

        if choice == 1:
            # Request the IATA of the airport
            airport_search = input("Give the IATA of the airport you want to search it's neighbors: ")
            n = int(input(
                "How many nearby airports do you want to show: "))  # and the number of nearby airports we want to find.

            search = [0, 0]

            # We search for the coordinates of the given airport.
            for i in range(len(air)):
                if air[i].IATA == airport_search:
                    search[0] = air[i].latitude
                    search[1] = air[i].longitude

            start_time = time.time()  # Starting time.
            knn = get_knn(quad_tree, search, n)  # Call the function to find the knn.
            print("--- %s seconds ---" % (time.time() - start_time))  # Ending time and print the result.

            for i in range(len(air)):
                for j in knn:
                    if (air[i].latitude == j.x) and (air[i].longitude == j.y):
                        print(air[i].name)  # Print the names of the closest neighbors.
        elif choice == 2:
            search_min = [0, 0]
            search_max = [0, 0]
            search_min[0] = float(input("Please give the minimum latitude: "))
            search_min[1] = float(input("Please give the minimum longitude: "))
            search_max[0] = float(input("Please give the maximum latitude: "))
            search_max[1] = float(input("Please give the maximum longitude: "))

            start_time = time.time()  # Starting time.
            result = range_search(quad_tree, search_min,
                                  search_max)  # Call the function to find the airports within the given coordinates.
            print("\n--- %s seconds ---\n" % (time.time() - start_time))  # Ending time and print the result.

            for i in range(len(air)):
                for j in result:
                    if (air[i].latitude == j.x) and (air[i].longitude == j.y):
                        print(air[i].name)  # Print the names of airports within the given range.

    file.close()  # Closing the file.

if __name__ == "__main__":
    main()