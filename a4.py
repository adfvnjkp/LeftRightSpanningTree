import csv
import glob
import strokes
import numpy as np
from scipy.spatial.distance import cdist
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import minimum_spanning_tree


def add_ele(arr):
    new_arr =[]
    for i in range(len(arr)-1):
        new_arr.append([arr[i]] + [arr[i+1]] + ['Right'])
    return new_arr


def left_right_stroke(new_stroke):
    values = []
    for k in range(len(new_stroke.feature_list)):
        x_coordinate = []
        for a in range(len(new_stroke.feature_list[k])):
            x_coordinate.append(new_stroke.feature_list[k][a][0])
        values.append((new_stroke.href_list[k], new_stroke.id_list[k], min(x_coordinate)))
    values.sort(key=lambda x: x[2])
    return add_ele([val[0] for val in values])


def left_right_symbol(new_stroke):
    values = []
    for k in range(len(new_stroke.symbol_feature_lis)):
        x_coordinate = []
        for a in range(len(new_stroke.symbol_feature_lis[k])):
            x_coordinate.append(new_stroke.symbol_feature_lis[k][a][0])
        values.append([new_stroke.symbol_href_lis[k], new_stroke.symbol_id_list[k], min(x_coordinate)])
    values.sort(key=lambda x: x[2])
    return add_ele([str(val[0]) for val in values])


def min_distance(feature_list):
    min_dis = [[0.0]*len(feature_list) for _ in range(len(feature_list))]
    for i in range(0, len(feature_list)):
        for j in range(0, len(feature_list)):
            min_dis[i][j] = np.min(cdist(feature_list[i], feature_list[j]))
    return min_dis


def take_direction(lg_file):
    file = open(lg_file, "r")
    direction = list(csv.reader(file))
    index = direction.index(["# Relations from SRT:"])
    if ["# Unused Strokes:"] in direction:
        end = direction.index(["# Unused Strokes:"])
        a = []
        for line in direction[index + 1: end]:
            a.append(line[1: 4])
    else:
        a = []
        for line in direction[index + 1:]:
            a.append(line[1: 4])
    return a


def mst_stroke(new_stroke, lg_relationship):
    square_matrix = min_distance(new_stroke.feature_list)
    x = csr_matrix(square_matrix)
    Tcsr = minimum_spanning_tree(x)
    mst_matrix = Tcsr.toarray().astype(float)
    href = []
    for i in range(len(mst_matrix)):
        for j in range(len(mst_matrix[i])):
            if mst_matrix[i][j] != 0.0:
                href.append([' ' + new_stroke.href_list[i], ' ' + new_stroke.href_list[j]])
    lg_href = []
    for i in href:
        found = False
        for j in lg_relationship:
            if i == j[:2]:
                found = True
                lg_href.append(i + [j[2]])
                break
        if not found:
            lg_href.append(i + ["_"])
    return lg_href


def mst_symbol(new_stroke, lg_relationship):
    square_matrix = min_distance(new_stroke.symbol_feature_list())
    x = csr_matrix(square_matrix)
    Tcsr = minimum_spanning_tree(x)
    mst_matrix = Tcsr.toarray().astype(float)
    href = []
    for i in range(len(mst_matrix)):
        for j in range(len(mst_matrix[i])):
            if mst_matrix[i][j] != 0.0:
                href.append([' ' + new_stroke.symbol_href_list()[i], ' ' + new_stroke.symbol_href_list()[j]])
    lg_href = []
    for i in href:
        found = False
        for j in lg_relationship:
            if i == j[:2]:
                found = True
                lg_href.append(i + [j[2]])
                break
        if not found:
            lg_href.append(i + ["_"])
    return lg_href


def main():
    """
    read the inkml file, parse it, and store in new dictionary in lg form
    """
    inkml_path = "data/inkml/*"
    for directory_1 in glob.glob(inkml_path):
        for file_name in glob.glob(f"{directory_1}/*"):
            # new_stroke = strokes.strokes("data/inkml/MathBrush/200924-1331-238.inkml")
            # lg_relationship = take_direction("lg/200924-1331-238.lg")
            # new_stroke = strokes.strokes("data/inkml/MathBrush/200922-947-7.inkml")
            # lg_relationship = take_direction("lg/200922-947-7.lg")
            new_stroke = strokes.strokes(file_name)
            a = left_right_stroke(new_stroke)
            b = left_right_symbol(new_stroke)
            # left right stroke oracle
            new_stroke.receive_values(a)
            new_stroke.writingOutput('a')
            # left right symbol oracle
            new_stroke.receive_values(b)
            new_stroke.writingOutput('b')

            if file_name != "data/inkml/MfrDB/MfrDB3088.inkml" and \
                    file_name != "data/inkml/MfrDB/MfrDB0104.inkml":
                new_filename = "/".join(
                    ["lg", file_name.split("/")[3].split(".")[0] + ".lg"])
                lg_relationship = take_direction(new_filename)
                c = mst_stroke(new_stroke, lg_relationship)
                d = mst_symbol(new_stroke, lg_relationship)
                # mst stroke oracle
                new_stroke.receive_values(c)
                new_stroke.writingOutput('c')
                # mst symbol oracle
                new_stroke.receive_values(d)
                new_stroke.writingOutput('d')


if __name__ == "__main__":
    main()