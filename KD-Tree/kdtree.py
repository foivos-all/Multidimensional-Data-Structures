from airports import airport
import time

dim = 2
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

# Makes the KD-Tree for fast lookup,
# as instances this function takes the list of points and the dimensions of the tree (in our case 2D)
def make_kd_tree(points, dim, i=0):
    if len(points) > 1:
        points.sort(key=lambda x: x[i]) # Lamba function that returns the key to sort.
        i = (i + 1) % dim # Rotating our axis.
        half = len(points) >> 1 # Shifting the bits one spot to the right (taking the half value).
        return [
            make_kd_tree(points[: half], dim, i), # Calls the function on one half
            make_kd_tree(points[half + 1:], dim, i), # and then the other half.
            points[half]
        ]
    elif len(points) == 1:
        return [None, None, points[0]]

# Adds a point to the kd-tree
# as instances it takes the node, the point and the dimensions.
def add_point(kd_node, point, dim, i=0):
    if kd_node is not None:
        dx = kd_node[2][i] - point[i] # Calculates the distance between the given node and the point.
        i = (i + 1) % dim # Simulates the rotation of the axis.
        # iterates through every node to find the closest one to the given point
        for j, c in ((0, dx >= 0), (1, dx < 0)):
            if c and kd_node[j] is None: # if both c and the given node are empty
                kd_node[j] = [None, None, point] # the new point becomes the given node
            elif c:
                # if not, it calls the function recursively until a suitable position is found
                add_point(kd_node[j], point, dim, i)

# Functions that help calculate the distance between two points.
def dist_sq(a, b, dim):
    # Calculates the sum of the squares of the difference
    # between two points for each coordinate
    return sum((a[i] - b[i]) ** 2 for i in range(dim))

# Calls the distance function with the dimensions
def dist_sq_dim(a, b):
    return dist_sq(a, b, dim)

# For the closest neighbor
# as instances it takes the kd node, the point from which to search for,
# the dimensions and the distance function.
def get_nearest(kd_node, point, dim, dist_func, return_distances=True, i=0, best=None):
    if kd_node is not None:
        # First, it calculates the distance between the point and the node using the distance function.
        dist = dist_func(point, kd_node[2])
        # and then it calculates the distance between the point and the node.
        dx = kd_node[2][i] - point[i]
        if not best: # If the best table is empty
            # it inserts the calculated distance from the function and the points of the node
            # to the best table
            best = [dist, kd_node[2]]
        elif dist < best[0]: # If the distance from the distance function is less than the best distance
            # the best distances are replaced with the calculated distance
            # and the points of the node
            best[0], best[1] = dist, kd_node[2]
        i = (i + 1) % dim # and then rotates the axis.
        # Goes into the left branch, and then the right branch if needed
        for b in [dx < 0] + [dx >= 0] * (dx * dx < best[0]):
            # and calls the function recursively
            get_nearest(kd_node[b], point, dim, dist_func, return_distances, i, best)
    return best if return_distances else best[1]

# k nearest neighbors
# takes as instances the kd node, the point from which to search for,
# the number of neighbors we wish to find, the dimensions and the distance function.
def get_knn(kd_node, point, k, dim, dist_func, return_distances=True, i=0, heap=None):
    import heapq # Using the heap library
    is_root = not heap
    if is_root:
        heap = []
    if kd_node is not None:
        # First, it calculates the distance between the point and the node using the distance function.
        dist = dist_func(point, kd_node[2])
        # and then it calculates the distance between the point and the node.
        dx = kd_node[2][i] - point[i]
        if len(heap) < k: # If the size of the heap is smaller than the number of neighbors we seek
            # it pushes the distance (but negative) and the coordinates of the node to the heap.
            # Making the numbers negative because the largest distance becomes the smallest.
            heapq.heappush(heap, (-dist, kd_node[2]))
        elif dist < -heap[0][0]: # Else, if the distance is smaller than the first item in the heap
            # pushes the dist and the coordinates of the node on the heap
            # and then pop and return the smallest item from the heap.
            # The smallest item is the largest distance.
            heapq.heappushpop(heap, (-dist, kd_node[2]))
        i = (i + 1) % dim # and rotates the axis.
        # Goes into the left branch, and then the right branch if needed
        for b in [dx < 0] + [dx >= 0] * (dx * dx < -heap[0][0]):
            # and calls the function recursively.
            get_knn(kd_node[b], point, k, dim, dist_func, return_distances, i, heap)
    if is_root:
        neighbors = sorted((-h[0], h[1]) for h in heap) # Sorts the neighbors
        return neighbors if return_distances else [n[1] for n in neighbors] # and returns them

def range_search(points, range_min, range_max):
    result = []

    for i in points: # For every point in our tree
        if (i[0] >= range_min[0]) and (i[0] <= range_max[0]) \
                and (i[1] >= range_min[1]) and (i[1] <= range_max[1]): # we check our latitude and then our longitude.
            result.append(i) # If the point is within the range we append it to the result list

    return result # and finally we return the result.

def main():
    global kd_tree, search, air, i, n, points
    file = open("data", "r") # Open the file in reading mode.
    choice = 0
    air = put_into_list(file) # Get the airports and their fields and put them in a list.
    points = get_points(air) # Extract the coordinates of each point.
    kd_tree = make_kd_tree(points, dim) # Create the kd tree

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
            knn = get_knn(kd_tree, search, n, dim, dist_sq_dim)  # Call the function to find the knn.
            print("\n--- %s seconds ---\n" % (time.time() - start_time))  # Ending time and print the result.

            for i in range(len(air)):
                for j in knn:
                    if (air[i].latitude == j[1][0]) and (air[i].longitude == j[1][1]):
                        print(air[i].name)  # Print the names of the closest neighbors.
        elif choice == 2:
            search_min = [0, 0]
            search_max = [0, 0]
            search_min[0] = float(input("Please give the minimum latitude: "))
            search_min[1] = float(input("Please give the minimum longitude: "))
            search_max[0] = float(input("Please give the maximum latitude: "))
            search_max[1] = float(input("Please give the maximum longitude: "))

            start_time = time.time()  # Starting time.
            result = range_search(points, search_min, search_max)  # Call the function to find the airports within the given coordinates.
            print("\n--- %s seconds ---\n" % (time.time() - start_time))  # Ending time and print the result.

            for i in range(len(air)):
                for j in result:
                    if (air[i].latitude == j[0]) and (air[i].longitude == j[1]):
                        print(air[i].name)  # Print the names of the airports within the given range.

    file.close() # Closing the file.

if __name__ == "__main__":
    main()