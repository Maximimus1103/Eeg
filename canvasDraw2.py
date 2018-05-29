import tkFont
from Tkinter import *
import networkx as nx
from PIL import ImageTk, Image


class Node:
    """node attributes"""

    active1 = None
    active2 = None

    def __init__(self, number, name, x, y, color):
        self.number = number
        self.name = name
        self.color = color
        self.x = x / 1.6 - 40
        self.y = y * 1.15 - 10
        self.connected_edges = []
        self.oval = None
        self.text = None
        self.bc = None
        self.local_efficiency = None


class Edge:
    """edge attributes"""

    def __init__(self, node1, node2):
        self.node1 = node1
        self.node2 = node2
        self.active = False
        self.line = None


class ConnectivityMatrix:
    """initialize matrix"""

    def __init__(self, matrix, names, coordinates, colors):
        self.num_of_nodes = 0
        self.nodes = []
        self.edges = []
        self.set_connectivity_matrix(matrix, names, coordinates, colors)
        self.graphnx = self.built_graph()
        self.calculate_bc(self.graphnx)
        self.global_efficiency = nx.global_efficiency(self.graphnx)
        self.set_local_efficiency()

    def calculate_bc(self, graph):
        """calculate Betweeness centrality"""

        bc = nx.betweenness_centrality(graph, k=None, normalized=False, weight=None, endpoints=False, seed=None)
        for i in range(len(self.nodes)):
            self.nodes[i].bc = round(bc[i], 2)

    def set_connectivity_matrix(self, matrix, names, coordinates, colors):
        """set value in matrix"""

        self.num_of_nodes = len(matrix)
        for i in range(self.num_of_nodes):
            self.nodes.append(Node(i, names[i], coordinates[i][0], coordinates[i][1], colors[i]))

        for i in range(self.num_of_nodes):
            for j in range(i + 1, self.num_of_nodes):  # only upper triangle (symmetrical matrix)
                if matrix[i][j] > 0:  # and Edge(self.nodes[j], self.nodes[i]) not in self.edges
                    egg = Edge(self.nodes[i], self.nodes[j])
                    self.edges.append(egg)
                    self.nodes[i].connected_edges.append(egg)
                    self.nodes[j].connected_edges.append(egg)

    def built_graph(self):
        """building graph"""
        graph = nx.Graph()
        for i in range(len(self.nodes)):
            graph.add_node(self.nodes[i].number)
        for i in range(len(self.edges)):
            graph.add_edge(self.edges[i].node1.number, self.edges[i].node2.number)  # specify edge data
        return graph

    @staticmethod
    def my_global_efficiency(graph):
        """calculate global efficiency"""
        n = len(graph)
        if n < 2:
            return 0
        inv_lengths = []
        for node in graph:
            lengths = nx.single_source_shortest_path_length(graph, node)
            inv = [1 / x for x in lengths.values() if x is not 0]
            inv_sum = sum(inv)
            inv_lengths.append(inv_sum)

        return sum(inv_lengths) / (n * (n - 1.0))

    def set_local_efficiency(self):
        """set value in parameter"""
        for n in self.graphnx:
            self.nodes[n].local_efficiency = round(nx.global_efficiency(nx.ego_graph(self.graphnx, n)), 2)


def canvas_draw(canvas1, canvas2, c_matrix1, c_matrix2, width, height, labels_to_change1, labels_to_change2,
                similarity_vector):
    """drawing the brain"""

    canvas1.configure(bd=1, relief=RIDGE)
    canvas2.configure(bd=1, relief=RIDGE)
    try:
        image = Image.open('brain3.jpg')
        image = image.resize((width, height), Image.ANTIALIAS)  # The (250, 250) is (height, width)
        canvas1.photo = ImageTk.PhotoImage(image)
        canvas2.photo = ImageTk.PhotoImage(image)
        canvas1.image = canvas1.create_image(0, 0, image=canvas1.photo, anchor=NW)
        canvas2.image = canvas2.create_image(0, 0, image=canvas2.photo, anchor=NW)
    except:
        canvas1.configure(background="#86A390")
        canvas2.configure(background="#86A390")
    canvases = (canvas1, canvas2)
    font1 = tkFont.Font(family='Helvetica', size=10, weight='bold')
    font2 = tkFont.Font(family='Helvetica', size=14, weight='bold')

    node_names = ["FP1", "FPz", "FP2", "AF7", "AF3", "AF4", "AF8", "F7", "F5", "F3", "F1",
                  "Fz", "F2", "F4", "F6", "F8", "FT7", "FC5", "FC3", "FC1", "FCz", "FC2",
                  "FC4", "FC6", "FT8", "T7", "C5", "C3", "C1", "Cz", "C2", "C4", "C6",
                  "T8", "TP7", "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6", "TP8",
                  "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8", "PO7", "PO3",
                  "POz", "PO4", "PO8", "O1", "Oz", "O2", "TP9", "TP10", "P9", "P10"]
    x_coordinates = [307, 384, 461, 239, 311, 460, 530, 182, 233, 285, 336, 384, 434, 485, 538, 588, 149,
                     209, 267, 328, 384, 441, 502, 561, 620, 136, 198, 258, 323, 384, 449, 511, 573, 634,
                     151, 208, 267, 327, 384, 441, 502, 562, 619, 183, 233, 283, 336, 384, 433, 485, 537,
                     587, 239, 307, 384, 462, 530, 307, 384, 461, 91, 677, 136, 632]
    y_coordinates = [423, 431, 422, 394, 378, 377, 393, 350, 342, 336, 334, 331, 332, 335, 342, 351, 299,
                     290, 286, 283, 281, 284, 286, 289, 299, 233, 233, 233, 233, 233, 233, 233, 233, 233,
                     169, 177, 180, 183, 183, 183, 180, 177, 168, 116, 125, 132, 133, 135, 133, 132, 125,
                     116, 73, 88, 92, 88, 73, 46, 34, 46, 153, 153, 93, 93]
    coordinates = zip(x_coordinates, y_coordinates)

    normal_param = ["white", 5,
                    "black", 1,
                    "white", 5,
                    "black", 1,
                    "khaki3", 1,
                    "black", font1]
    info_param = ["red", 5,
                  "black", 3,
                  "red", 5,
                  "black", 1,
                  "gray10", 1,
                  "black", font1]
    select_param = ["white", 7,
                    "blue", 3,
                    "white", 5,
                    "blue", 1,
                    "royal blue", 2,  # "royal blue"
                    "brown4", font2]
    color_step = (max(similarity_vector) - min(similarity_vector)) / 4
    reds = min(similarity_vector) + color_step
    oranges = reds + color_step
    yellows = oranges + color_step
    color_vector = []
    for similarity in similarity_vector:
        if similarity < reds:
            color_vector.append("firebrick1")  # red
        elif similarity < oranges:
            color_vector.append("orange2")  # orange  "DarkOrange1"
        elif similarity < yellows:
            color_vector.append("yellow")  # yellow
        else:
            color_vector.append("forest green")  # green

    connectivity_matrix1 = ConnectivityMatrix(c_matrix1, node_names, coordinates, color_vector)
    connectivity_matrix2 = ConnectivityMatrix(c_matrix2, node_names, coordinates, color_vector)

    labels = zip(labels_to_change1, labels_to_change2)
    nodes = zip(connectivity_matrix1.nodes, connectivity_matrix2.nodes)
    draw_lines(canvases, connectivity_matrix1, connectivity_matrix2, normal_param)
    draw_nodes(canvases, nodes, normal_param, select_param, info_param, labels, color_vector)


def draw_lines(canvases, connectivity_matrix1, connectivity_matrix2, prm):
    """drawing edges"""

    (node_color, node_size, node_line_color, node_line_wid,
     nbr_color, nbr_size, nbr_line_color, nbr_line_wid,
     line_color, line_size, text_color, font) = prm
    r = line_size
    for edge in connectivity_matrix1.edges:
        xi = edge.node1.x
        yi = edge.node1.y
        xj = edge.node2.x
        yj = edge.node2.y
        edge.line = canvases[0].create_line(xi, yi, xj, yj, width=line_size, fill=line_color)

    for edge in connectivity_matrix2.edges:
        xi = edge.node1.x
        yi = edge.node1.y
        xj = edge.node2.x
        yj = edge.node2.y
        edge.line = canvases[1].create_line(xi, yi, xj, yj, width=line_size, fill=line_color)


def draw_nodes(canvases, nodes, normal_param, select_param, info_param, labels, color_vector):
    """drawing node"""
    (node_color, node_size, node_line_color, node_line_wid,
     nbr_color, nbr_size, nbr_line_color, nbr_line_wid,
     line_color, line_size, text_color, font) = normal_param
    r = node_size

    for node_i in nodes:
        node1 = node_i[0]
        node2 = node_i[1]
        xi = node1.x
        yi = node1.y

        node1.oval = canvases[0].create_oval(xi - r, yi - r, xi + r, yi + r,
                                             outline=node_line_color,
                                             fill=node1.color,
                                             width=node_line_wid)
        node2.oval = canvases[1].create_oval(xi - r, yi - r, xi + r, yi + r,
                                             outline=node_line_color,
                                             fill=node2.color,
                                             width=node_line_wid)
        node1.text = canvases[0].create_text(xi + 0 * r, yi - 3 * r,
                                             text=node1.name,
                                             font=font,
                                             fill=text_color)
        node2.text = canvases[1].create_text(xi + 0 * r, yi - 3 * r,
                                             text=node2.name,
                                             font=font,
                                             fill=text_color)
        canvases[0].tag_bind(node1.oval, "<Enter>",
                             lambda event, c=canvases, n=node_i, s_p=select_param: above(event, c, n, s_p, None))
        canvases[0].tag_bind(node1.oval, "<Leave>",
                             lambda event, c=canvases, n=node_i, i_p=info_param, n_p=normal_param:
                             above(event, c, n, n_p, i_p))
        canvases[0].tag_bind(node1.oval, "<Button-1>",
                             lambda event, c=canvases, n=node_i, i_p=info_param, n_p=normal_param, l=labels:
                             click_on_node(event, c, n, i_p, n_p, l))

        canvases[1].tag_bind(node2.oval, "<Enter>",
                             lambda event, c=canvases, n=node_i, s_p=select_param: above(event, c, n, s_p, None))
        canvases[1].tag_bind(node2.oval, "<Leave>",
                             lambda event, c=canvases, n=node_i, i_p=info_param, n_p=normal_param:
                             above(event, c, n, n_p, i_p))
        canvases[1].tag_bind(node2.oval, "<Button-1>",
                             lambda event, c=canvases, n=node_i, i_p=info_param, n_p=normal_param, l=labels:
                             click_on_node(event, c, n, i_p, n_p, l))


def click_on_node(event, canvases, node_i, i_p, n_p, labels_to_change):
    """what happening if you click on node"""

    (node_color, node_size, node_line_color, node_line_wid,
     nbr_color, nbr_size, nbr_line_color, nbr_line_wid,
     line_color, line_size, text_color, font) = i_p

    if Node.active1 is not None:

        canvases[0].itemconfig(Node.active1.oval, fill=Node.active1.color, outline=n_p[2], width=n_p[3])
        labels_to_change[0][0].configure(
            text="                  Node name:  {}".format("---"))  # unset node name
        labels_to_change[1][0].configure(
            text="                          Degree:  {}".format("---"))  # unset node degree
        labels_to_change[2][0].configure(
            text="Betweennes centrality:  {}".format("---"))  # unset node bc
        labels_to_change[3][0].configure(
            text="           Local efficiency:  {}".format("---"))  # unset node local efficiency

        canvases[1].itemconfig(Node.active2.oval, fill=Node.active2.color, outline=n_p[2], width=n_p[3])
        labels_to_change[0][1].configure(
            text="                  Node name:  {}".format("---"))  # unset node name
        labels_to_change[1][1].configure(
            text="                          Degree:  {}".format("---"))  # unset node degree
        labels_to_change[2][1].configure(
            text="Betweennes centrality:  {}".format("---"))  # unset node bc
        labels_to_change[3][1].configure(
            text="           Local efficiency:  {}".format("---"))  # unset node local efficiency
        if Node.active1 is node_i[0]:
            Node.active1 = None
            Node.active2 = None
            return

    Node.active1 = node_i[0]

    canvases[0].itemconfig(node_i[0].oval, fill=node_i[0].color, outline=node_line_color, width=node_line_wid)
    labels_to_change[0][0].configure(
        text="                  Node name:  {}".format(node_i[0].name))
    labels_to_change[1][0].configure(
        text="                          Degree:  {}".format(len(node_i[0].connected_edges)))
    labels_to_change[2][0].configure(
        text="Betweennes centrality:  {}".format(node_i[0].bc))
    labels_to_change[3][0].configure(
        text="           Local efficiency:  {}".format(node_i[0].local_efficiency))

    Node.active2 = node_i[1]

    canvases[1].itemconfig(node_i[1].oval, fill=node_i[1].color, outline=node_line_color, width=node_line_wid)
    labels_to_change[0][1].configure(
        text="                  Node name:  {}".format(node_i[1].name))
    labels_to_change[1][1].configure(
        text="                          Degree:  {}".format(len(node_i[1].connected_edges)))
    labels_to_change[2][1].configure(
        text="Betweennes centrality:  {}".format(node_i[1].bc))
    labels_to_change[3][1].configure(
        text="           Local efficiency:  {}".format(node_i[1].local_efficiency))


def above(event, canvases, node_i, prm, i_p):
    (node_color, node_size, node_line_color, node_line_wid,
     nbr_color, nbr_size, nbr_line_color, nbr_line_wid,
     line_color, line_size, text_color, font) = prm
    # update lines
    for edge in node_i[0].connected_edges:
        # if node_i[0] is not node_i[0].active1:
        canvases[0].itemconfig(edge.line, width=line_size, fill=line_color)  # update line
        if event.type is "7":  # "7" means "<Enter>"
            canvases[0].tag_raise(edge.line)  # raise line

    for edge in node_i[1].connected_edges:
        # if node_i[1] is not node_i[1].active2:
        canvases[1].itemconfig(edge.line, width=line_size, fill=line_color)  # update line
        if event.type is "7":  # "7" means "<Enter>"
            canvases[1].tag_raise(edge.line)  # raise line

    if node_i[0] is node_i[0].active1 and event.type is "8":  # the node is  info_node  # "8" means "<Leave>"
        canvases[0].itemconfig(node_i[0].oval, outline=i_p[2], width=i_p[3])
        canvases[1].itemconfig(node_i[1].oval, outline=i_p[2], width=i_p[3])
    else:
        canvases[0].itemconfig(node_i[0].oval, outline=node_line_color, width=node_line_wid)
        canvases[1].itemconfig(node_i[1].oval, outline=node_line_color, width=node_line_wid)
    canvases[0].itemconfig(node_i[0].text, font=font, fill=text_color)  # needs debug
    canvases[1].itemconfig(node_i[1].text, font=font, fill=text_color)  # needs debug
    canvases[0].tag_raise(node_i[0].text)
    canvases[0].tag_raise(node_i[0].oval)  # raise event_node above lines
    canvases[1].tag_raise(node_i[1].text)
    canvases[1].tag_raise(node_i[1].oval)  # raise event_node above lines

    # update neighbours
    for edge in node_i[0].connected_edges:
        # select neighbour
        nbr_node = edge.node1 if edge.node1.name != node_i[0].name else edge.node2
        # update neighbour and text
        canvases[0].itemconfig(nbr_node.text, font=font, fill=text_color)
        if nbr_node is not node_i[0].active1:
            canvases[0].itemconfig(nbr_node.oval, fill=nbr_node.color)
            canvases[0].itemconfig(nbr_node.oval, outline=nbr_line_color, width=nbr_line_wid)

        canvases[0].tag_raise(nbr_node.text)  # raise text above lines
        canvases[0].tag_raise(nbr_node.oval)  # raise neighbour above lines

        if event.type is "8":  # "7" means "<Enter>", "8" means "<Leave>"
            canvases[0].tag_lower(edge.line)

    for edge in node_i[1].connected_edges:
        # select neighbour
        nbr_node = edge.node1 if edge.node1.name != node_i[1].name else edge.node2
        # update neighbour and text
        canvases[1].itemconfig(nbr_node.text, font=font, fill=text_color)
        if nbr_node is not node_i[1].active2:
            canvases[1].itemconfig(nbr_node.oval, fill=nbr_node.color)
            canvases[1].itemconfig(nbr_node.oval, outline=nbr_line_color, width=nbr_line_wid)

        canvases[1].tag_raise(nbr_node.text)  # raise text above lines
        canvases[1].tag_raise(nbr_node.oval)  # raise neighbour above lines

        if event.type is "8":  # "7" means "<Enter>", "8" means "<Leave>"
            canvases[1].tag_lower(edge.line)

    canvases[0].tag_lower(canvases[0].image)
    canvases[1].tag_lower(canvases[1].image)
