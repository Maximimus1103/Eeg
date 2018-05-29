import random


def random_connectivity(num):
    view_size = num
    num_of_nodes = view_size * view_size  # 25 nodes
    connectivity_matrix = []
    for i in range(num_of_nodes):
        connectivity_matrix.append([])
        for j in range(num_of_nodes):
            connectivity_matrix[i].append(0)

    for i in range(num_of_nodes):
        for j in range(i + 1, num_of_nodes):
            if random.random() > 0.94:
                connectivity_matrix[i][j] = 1
                connectivity_matrix[j][i] = 1
            else:
                connectivity_matrix[i][j] = 0
                connectivity_matrix[j][i] = 0
                # print connectivity_matrix[i]
    return connectivity_matrix
