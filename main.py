import numpy as np
from PIL import Image, ImageDraw
import shapely
from shapely.geometry import LineString, Point


class node:
    def __init__(self, location):
        self.location = location
        self.children = []
        self.parent = None

    def add_child(self, child):
        child.parent = self
        self.children.append(child)

    def distance(self, point):
        p1 = np.array(self.location)
        p2 = np.array(point)
        dist = np.linalg.norm(p1-p2)
        return dist


def nearestnode(point, nodelist):
    mindist = 10000
    for i in nodelist:
        if i.distance(point) <= mindist:
            mindist = i.distance(point)
            # print(i.distance(point))
            j = i

    return j


def finder(nearest_node, ran, edge):
    x0 = nearest_node.location[0]
    y0 = nearest_node.location[1]
    d = nearest_node.distance(ran)
    if d == 0:
        return nearest_node.location
    t = edge/d
    x = (1-t)*x0 + t*ran[0]
    y = (1-t)*y0 + t*ran[1]
    #print(f"x,y  {x,y}")
    return (x, y)


def check(A, B, C, D):  # fUNCTION TO CHECK IF LINES BW POINTS A,B AND C,D INTERSECT AT A POINT WITHIN A,B,C,D
    line1 = LineString([A, B])
    line2 = LineString([C, D])

    # int_pt = line1.intersection(line2)
    # point_of_intersection = int_pt.x, int_pt.y
    return (line1.intersects(line2))


def intersects(a, b, o):
    p, m, q, n = o
    Vertices = [[p, m], [p, n], [q, n], [q, m]]
    for i in range(2):
        if check(a, b, Vertices[i], Vertices[i+1]):
            return True

    if check(a, b, Vertices[3], Vertices[0]):
        return True

    return False


def in_rect(a, o):

    if (a[0] >= min(o[0], o[2])) and (a[0] <= max(o[0], o[2])) and (a[1] >= min(o[1], o[3])) and (a[1] <= max(o[1], o[3])):
        return True
    else:
        return False


if __name__ == '__main__':

    # _________________Setting up map as a png image and inserting components______________________

    # A 512 by 512 numpy array used as our grid
    a = np.full((512, 512, 3), 255, dtype=np.uint8)
    image = Image.fromarray(a, "RGB")
    draw = ImageDraw.Draw(image)

    # Define home, destination, destination radius and edge
    home = (10, 10)
    destination = (400, 400)
    destination_radius = 10
    edge = 10
    switch = False
    dist = 100

    # Plotting the home and destination on image as green circles with radius r
    r = 20
    homeel = [home[0]-r, home[1]-r, home[0]+r, home[1]+r]
    draw.ellipse(homeel, fill=(0, 255, 0), outline=(255, 255, 255))
    destinationel = [destination[0]-r, destination[1] -
                     r, destination[0]+r, destination[1]+r]
    draw.ellipse(destinationel, fill=(0, 255, 0), outline=(255, 255, 255))

    # plotting obstacles in image. You may add or change obstacle features by modifying the list Obstacles. 
    # (Upper left x coordinate, upper left y coordinate, lower right x coordinate, lower right y coordinate) -- Syntax for rectangle obstacle
    
    Obstacles = [[20, 50, 200, 180], [300, 100, 400, 250]]
    for i in Obstacles:
        draw.rectangle(i, fill=(255, 0, 0), outline=(255, 255, 255))
   

    # ___________________Configuring the path_________________________________
    node_list = []  # Stores all the nodes in order of creation
    node_list.append(node(home))
    while True:
        # Generates random point on map
        ran = (np.random.randint(512), np.random.randint(512))
        # Finds node closest to point
        nearest_node = nearestnode(ran, node_list)
        # Finds point next to closest node in required direction
        point_in_required_direction = finder(nearest_node, ran, edge)

        # _______ Checks if obtained point or corresponding path interacts with obtacle_____
        for i in Obstacles:
            # checks if created point lies inside rectangle
            if in_rect(point_in_required_direction, i):
                switch = False
                break

            # checks if created path intersects with obstacle edge
            if (intersects(nearest_node.location, point_in_required_direction, i)):
                switch = False
                break
            else:
                switch = True  # The point qualifies

        if switch:
            newchild = node(point_in_required_direction)  # New node created
            # Node added as child of Parent node
            nearest_node.add_child(newchild)
            node_list.append(newchild)  # Master node list appended

            # _____________Plotting path due to new node. Basically plots the entire tree in black____________________
            line = newchild.location + nearest_node.location
            draw.line(line, fill=(0, 0, 0), width=2)
            dist = newchild.distance(destination)

        if dist <= destination_radius:  # Stops finding if a node falls inside the destination radius
            break

    # __________________Draws the feasable path in blue_____________________________
    present_node = newchild
    while present_node.parent:
        print(present_node.location)
        p = present_node.parent
        line = present_node.location + p.location
        draw.line(line, fill=(0, 0, 255), width=2)
        present_node = p

    # Visual representation

    image.save("map.png", "PNG")
