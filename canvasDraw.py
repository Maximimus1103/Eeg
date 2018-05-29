import tkFont
from Tkinter import *
import networkx
from networkx import Graph, \
    single_source_shortest_path_length, \
    betweenness_centrality, global_efficiency, ego_graph
from PIL import Image, ImageTk


class Node:

    active = None

    def __init__(self, number, name, x, y):
        """node attributes"""

        self.number = number
        self.name = name
        self.x = x / 1.6 - 40
        self.y = y * 1.15 - 10
        self.connected_edges = []
        self.oval = None
        self.text = None
        self.bc = None
        self.local_efficiency = None


class Edge:

    def __init__(self, node1, node2):
        """Edge attributes"""

        self.node1 = node1
        self.node2 = node2
        self.active = False
        self.line = None





class ConnectivityMatrix:
    def __init__(self, matrix, names, coordinates):
        """initialize matrix"""

        self.num_of_nodes = 0
        self.nodes = []
        self.edges = []
        self.set_connectivity_matrix(matrix, names, coordinates)
        self.graphnx = self.built_graph()
        self.calculate_bc(self.graphnx)
        self.global_efficiency = global_efficiency(self.graphnx)
        self.set_local_efficiency()


    def calculate_bc(self, graph):
        """calculate Betweeness centrality"""

        bc = betweenness_centrality(graph, k=None, normalized=False, weight=None, endpoints=False, seed=None)
        for i in range(len(self.nodes)):
            self.nodes[i].bc = round(bc[i], 2)

    def set_connectivity_matrix(self, matrix, names, coordinates):
        """set value in matrix"""

        self.num_of_nodes = len(matrix)
        for i in range(self.num_of_nodes):
            self.nodes.append(Node(i, names[i], coordinates[i][0], coordinates[i][1]))

        for i in range(self.num_of_nodes):
            for j in range(i + 1, self.num_of_nodes):  # only upper triangle (symmetrical matrix)
                if matrix[i][j] > 0:  # and Edge(self.nodes[j], self.nodes[i]) not in self.edges
                    egg = Edge(self.nodes[i], self.nodes[j])
                    self.edges.append(egg)
                    self.nodes[i].connected_edges.append(egg)
                    self.nodes[j].connected_edges.append(egg)


    def built_graph(self):
        """building graph"""

        graph = Graph()
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
            lengths = single_source_shortest_path_length(graph, node)
            inv = [1 / x for x in lengths.values() if x is not 0]
            inv_sum = sum(inv)
            inv_lengths.append(inv_sum)

        return sum(inv_lengths) / (n * (n - 1.0))

    def set_local_efficiency(self):
        """set value in parameter"""

        for n in self.graphnx:
            self.nodes[n].local_efficiency = round(global_efficiency(ego_graph(self.graphnx, n)), 2)



def canvas_draw(canvas, c_matrix, width, height, labels_to_change):
    """drawing the brain"""
    canvas.configure(borderwidth="2", relief=RIDGE)
    try:
        image = Image.open('brain3.jpg')
        image = image.resize((width, height), Image.ANTIALIAS)  # The (250, 250) is (height, width)
        canvas.photo = ImageTk.PhotoImage(image)
        canvas.image = canvas.create_image(0, 0, image=canvas.photo, anchor=NW)
    finally:
        canvas.configure(background="#86A390")
    font1 = tkFont.Font(family='Helvetica', size=10, weight='bold')
    font2 = tkFont.Font(family='Helvetica', size=12, weight='bold')
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
                  "black", 1,
                  "red", 5,
                  "black", 1,
                  "gray10", 1,
                  "black", font1]
    select_param = ["white", 7,
                    "blue", 3,
                    "white", 5,
                    "blue", 1,
                    "royal blue", 2,
                    "brown4", font2]

    connectivity_matrix = ConnectivityMatrix(c_matrix, node_names, coordinates)

    draw_lines(canvas, connectivity_matrix, normal_param)
    draw_nodes(canvas, connectivity_matrix, normal_param, select_param, info_param, labels_to_change)


def draw_nodes(canvas, connectivity_matrix, normal_param, select_param, info_param, labels_to_change):
    """drawing node"""

    (node_color, node_size, node_line_color, node_line_wid,
     nbr_color, nbr_size, nbr_line_color, nbr_line_wid,
     line_color, line_size, text_color, font) = normal_param
    r = node_size
    for node in connectivity_matrix.nodes:
        xi = node.x
        yi = node.y
        node.oval = canvas.create_oval(xi - r, yi - r, xi + r, yi + r,
                                       outline=node_line_color,
                                       fill=node_color,
                                       width=node_line_wid)
        node.text = canvas.create_text(xi + 0 * r, yi - 3 * r,
                                       text=node.name,  # +str(node.x*2)+"|"+str(node.y)
                                       font=font,
                                       fill=text_color)
        canvas.tag_bind(node.oval, "<Enter>", lambda event, c=canvas, n=node, p=select_param: above(event, c, n, p))
        canvas.tag_bind(node.oval, "<Leave>", lambda event, c=canvas, n=node, p=normal_param: above(event, c, n, p))
        canvas.tag_bind(node.oval, "<Button-1>",
                        lambda event, c=canvas, n=node, p=info_param, n_p=normal_param, l=labels_to_change:
                        click_on_node(event, c, n, p, n_p, l))


def click_on_node(event, canvas, node, prm, n_p, labels_to_change):
    """what happening if you click on node"""

    (node_color, node_size, node_line_color, node_line_wid,
     nbr_color, nbr_size, nbr_line_color, nbr_line_wid,
     line_color, line_size, text_color, font) = prm

    active_node = Node.active
    if active_node is not None:

        canvas.itemconfig(active_node.oval, fill=n_p[0])
        labels_to_change[0].configure(text="                  Node name:  {}".format("---"))  # unset node name
        labels_to_change[1].configure(text="                          Degree:  {}".format("---"))  # unset node degree
        labels_to_change[2].configure(text="Betweennes centrality:  {}".format("---"))  # unset node bc
        labels_to_change[3].configure(text="           Local efficiency:  {}".format("---"))  # unset node local efficiency
        if active_node is node:

            Node.active = None
            return
    Node.active = node

    canvas.itemconfig(node.oval, fill=node_color)
    labels_to_change[0].configure(text="                  Node name:  {}".format(node.name))
    labels_to_change[1].configure(text="                          Degree:  {}".format(len(node.connected_edges)))
    labels_to_change[2].configure(text="Betweennes centrality:  {}".format(node.bc))
    labels_to_change[3].configure(text="           Local efficiency:  {}".format(node.local_efficiency))


def draw_lines(canvas, connectivity_matrix, prm):
    """drawing edges"""

    (node_color, node_size, node_line_color, node_line_wid,
     nbr_color, nbr_size, nbr_line_color, nbr_line_wid,
     line_color, line_size, text_color, font) = prm
    r = line_size
    for edge in connectivity_matrix.edges:
        xi = edge.node1.x
        yi = edge.node1.y
        xj = edge.node2.x
        yj = edge.node2.y
        edge.line = canvas.create_line(xi, yi, xj, yj, width=line_size, fill=line_color)


def above(event, canvas, node, prm):
    (node_color, node_size, node_line_color, node_line_wid,
     nbr_color, nbr_size, nbr_line_color, nbr_line_wid,
     line_color, line_size, text_color, font) = prm
    # update lines
    for edge in node.connected_edges:
        canvas.itemconfig(edge.line, width=line_size, fill=line_color)  # update line
        if event.type is "7":  # "7" means "<Enter>"
            canvas.tag_raise(edge.line)  # raise line

    # update neighbours
    for edge in node.connected_edges:
        # select neighbour
        nbr_node = edge.node1 if edge.node1.name != node.name else edge.node2
        # update neighbour and text
        canvas.itemconfig(nbr_node.text, font=font, fill=text_color)
        if nbr_node is not node.active:
            canvas.itemconfig(nbr_node.oval, fill=nbr_color)
        canvas.itemconfig(nbr_node.oval, outline=nbr_line_color, width=nbr_line_wid)

        canvas.tag_raise(nbr_node.text)  # raise text above lines
        canvas.tag_raise(nbr_node.oval)  # raise neighbour above lines

        if event.type is "8":  # "7" means "<Enter>", "8" means "<Leave>"
            canvas.tag_lower(edge.line)
    if event.type is "8":
        canvas.tag_lower(canvas.image)

    if node is not node.active:
        canvas.itemconfig(node.oval, fill=node_color)
    canvas.itemconfig(node.oval, outline=node_line_color, width=node_line_wid)
    canvas.itemconfig(node.text, font=font, fill=text_color)
    canvas.tag_raise(node.text)
    canvas.tag_raise(node.oval)  # raise event_node above lines(AND ABOVE TEXT)
