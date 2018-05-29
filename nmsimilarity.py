class NmSimilarity:
    def __init__(self, graph_a, graph_b, epsilon):
        """initialize similarity"""

        self.graphA = graph_a
        self.graphB = graph_b
        self.epsilon = epsilon
        self.NodeListA = graph_a.degreeNodeList
        self.NodeListB = graph_b.degreeNodeList
        self.graphSizeA = graph_a.graphSize
        self.graphSizeB = graph_b.graphSize
        self.nodeSimilarity = None
        self.initialize_node_similarity()
        self._final_graph_similarity = None
        self.connection_vector = []

    def initialize_node_similarity(self):
        """initialize node similarity"""

        self.nodeSimilarity = []
        for i in range(self.graphSizeA):
            self.nodeSimilarity.append([])
            for j in range(self.graphSizeB):
                max_degree = max(len(self.NodeListA[i]), len(self.NodeListB[j]))
                if max_degree == 0:
                    self.nodeSimilarity[i].append(1.)
                else:
                    self.nodeSimilarity[i].append(min(len(self.NodeListA[i]), len(self.NodeListB[j])) / float(max_degree))


    def measure_similarity(self):
        """calculate the similarity"""

        terminate = False
        new_node_similarity = list()
        for i in range(self.graphSizeA):
            new_node_similarity.append(list())
            for j in range(self.graphSizeB):
                new_node_similarity[i].append(1.)
        while not terminate:
            max_difference = 0.
            for i in range(self.graphSizeA):
                for j in range(self.graphSizeB):
                    max_degree = max(len(self.NodeListA[i]), len(self.NodeListB[j]))
                    min_degree = min(len(self.NodeListA[i]), len(self.NodeListB[j]))
                    if min_degree == max_degree:
                        similarity_sumAB = self.enumeration_function(self.NodeListA[i], self.NodeListB[j], 0)
                        similarity_sumBA = self.enumeration_function(self.NodeListB[j], self.NodeListA[i], 1)
                        similarity_sum = max(similarity_sumAB, similarity_sumBA)
                    elif min_degree == len(self.NodeListA[i]):
                        similarity_sum = self.enumeration_function(self.NodeListA[i], self.NodeListB[j], 0)
                    else:
                        similarity_sum = self.enumeration_function(self.NodeListB[j], self.NodeListA[i], 1)
                    new_node_similarity[i][j] = self.nodeSimilarity[i][j]

                    if max_degree == 0. and similarity_sum == 0.:
                        new_node_similarity[i][j] = 1.
                    elif max_degree == 0.:  
                        new_node_similarity[i][j] = 0.
                    else:
                        new_node_similarity[i][j] = similarity_sum / max_degree
            for i in range(self.graphSizeA):
                for j in range(self.graphSizeB):
                    delta_i_j = abs(self.nodeSimilarity[i][j] - new_node_similarity[i][j])
                    if delta_i_j > max_difference:
                        max_difference = delta_i_j
                    self.nodeSimilarity[i][j] = new_node_similarity[i][j]

            if max_difference < self.epsilon:
                terminate = True
        for i in range(self.graphSizeA):
            self.connection_vector.append(self.nodeSimilarity[i][i])

    def enumeration_function(self, neighbor_list_min, neighbor_list_max, mode):
        """matched between neighboors"""

        similarity_sum = 0.
        value_map = {}
        if mode == 0:
            for node in neighbor_list_min:
                max_value = 0.
                max_index = -1
                for key in neighbor_list_max:
                    if key not in value_map:
                        if max_value < self.nodeSimilarity[node][key]:
                            max_value = self.nodeSimilarity[node][key]
                            max_index = key
                value_map[max_index] = max_value
        else:
            for node in neighbor_list_min:
                max_value = 0.
                max_index = -1
                for key in neighbor_list_max:
                    if key not in value_map:
                        if max_value < self.nodeSimilarity[key][node]:
                            max_value = self.nodeSimilarity[key][node]
                            max_index = key
                value_map[max_index] = max_value

        for key, value in value_map.iteritems():
            similarity_sum += value
        return similarity_sum

    @property
    def final_graph_similarity(self):
        """the final similarity graph"""

        if self._final_graph_similarity is not None:
            return self._final_graph_similarity
        self.measure_similarity()
        
        enum_resultAB = self.enumeration_function(self.graphA.nodeList, self.graphA.nodeList, 0)
        enum_resultBA = self.enumeration_function(self.graphA.nodeList, self.graphA.nodeList, 1)
        enum_result = max(enum_resultAB, enum_resultBA)
        self._final_graph_similarity = enum_result / self.graphSizeA

        self._final_graph_similarity = round(self.final_graph_similarity * 100, 4)
        return self._final_graph_similarity


class nmGraph:
    def __init__(self, matrix):
        """initialize graph"""

        self.graph = matrix  # list of lists
        self.graphSize = len(self.graph)
        self.nodeList = list(range(len(self.graph)))
        self.degreeNodeList = []

        for i in range(self.graphSize):
            self.degreeNodeList.append([])
        for i in range(self.graphSize):
            for j in range(self.graphSize):
                if self.graph[i][j] != 0 and i != j:
                    self.degreeNodeList[i].append(j)
