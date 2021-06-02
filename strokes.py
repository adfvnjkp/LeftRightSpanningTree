import csv
import numpy as np
from bs4 import BeautifulSoup


class strokes():
    """
    each instance of Strokes encapsulate all information could be extracted from corresponded InkMarkup file

    """

    def __init__(self, fileName: str):
        """
        initialization of class stroke instance

        """
        self.fileName = fileName
        inkId, truth_list, href_list, id_list, feature_list, symbol_id_list = self.inkExtraction()
        self.id = inkId
        self.fileOutput_lrstroke = "/".join(
            ["output1", fileName.split("/")[3].split(".")[0] + ".lg"])
        self.fileOutput_lrsymbol = "/".join(
            ["output2", fileName.split("/")[3].split(".")[0] + ".lg"])
        self.fileOutput_mststroke = "/".join(
            ["output3", fileName.split("/")[3].split(".")[0] + ".lg"])
        self.fileOutput_mstsymbol = "/".join(
            ["output4", fileName.split("/")[3].split(".")[0] + ".lg"])
        self.truth_list = truth_list
        self.href_list = href_list
        self.prediction_list_num = None
        self.id_list = id_list
        self.feature_list = feature_list
        self.centralized = self.centralization()
        self.id_truth_dict = self.build_truth_dict()
        self.symbol_id_list = symbol_id_list
        self.href_href_direction = []
        self.symbol_feature_lis = self.symbol_feature_list()
        self.symbol_href_lis = self.symbol_href_list()
        self.symbol_truth_lis = self.symbol_truth_list()

    def symbol_feature_list(self):
        lis = []
        for i in self.symbol_id_list:
            temp = []
            for j in i:
                temp += self.feature_list[self.id_list.index(j)]
            lis.append(temp)
        return lis

    def symbol_href_list(self):
        lis = []
        for i in self.symbol_id_list:
            temp = []
            for j in i:
                temp = self.href_list[self.id_list.index(j)]
            lis.append(temp)
        return lis

    def symbol_truth_list(self):
        lis = []
        for i in self.symbol_id_list:
            temp = []
            for j in i:
                temp = self.truth_list[self.id_list.index(j)]
            lis.append(temp)
        return lis

    def build_truth_dict(self):
        dic = {}
        for __id, __truth in zip(self.id_list, self.truth_list):
            dic[__id] = __truth
        return dic

    def writingOutput(self, oracle_name):
        # loop over
        if oracle_name == 'a':
            file = open(self.fileOutput_lrstroke, "w", newline="")
            writer = csv.writer(file, delimiter=",")
            for href, truth, ids in zip(self.href_list, self.truth_list, self.id_list):
                writer.writerow(["O", ' '+ href, ' '+ truth, " 1.0"] + [' ' + str(idStroke) for idStroke in ids])
            for lis in self.href_href_direction:
                writer.writerow(["R"]+lis+[" 1.0"])

        if oracle_name == 'b':
            file = open(self.fileOutput_lrsymbol, "w", newline="")
            writer = csv.writer(file, delimiter=",")
            for href, truth, ids in zip(self.symbol_href_lis, self.symbol_truth_lis, self.symbol_id_list):
                # print(href, truth)
                writer.writerow(["O", ' '+href, ' '+truth, " 1.0"] + [' '+str(idStroke) for idStroke in ids])
            for lis in self.href_href_direction:
                writer.writerow(["R"]+lis+[" 1.0"])

        if oracle_name == 'c':
            file = open(self.fileOutput_mststroke, "w", newline="")
            writer = csv.writer(file, delimiter=",")
            for href, truth, ids in zip(self.href_list, self.truth_list, self.id_list):
                writer.writerow(["O", ' '+ href, ' '+ truth, " 1.0"] + [' ' + str(idStroke) for idStroke in ids])
            for lis in self.href_href_direction:
                writer.writerow(["R"]+lis+[" 1.0"])

        if oracle_name == 'd':
            file = open(self.fileOutput_mstsymbol, "w", newline="")
            writer = csv.writer(file, delimiter=",")
            for href, truth, ids in zip(self.symbol_href_lis, self.symbol_truth_lis, self.symbol_id_list):
                writer.writerow(["O", ' '+href, ' '+truth, " 1.0"] + [' '+str(idStroke) for idStroke in ids])
            for lis in self.href_href_direction:
                writer.writerow(["R"]+lis+[" 1.0"])


    def receive_values(self, values: list):
        self.href_href_direction = values

    def castingPrediction(self, list_predicted: list):
        self.prediction_list = list_predicted

    def centralization(self):
        list_centralized = []
        for identical_trace in self.feature_list:
            identical_trace = np.array(identical_trace)
            avg_trace = np.mean(identical_trace, axis=0).tolist()
            list_centralized.append(avg_trace)
        return list_centralized

    def inkExtraction(self) -> tuple:
        """
        helper function extract feature and truth from provide InkML file
            multiple exception handled
        :return: addr output1, script id, list traces, in structure of tuple

        """
        # read file as handler
        handler = open(self.fileName, "r")
        # var reserved for traces-list mapping relationship
        if self.fileName == "data/inkml/MfrDB/MfrDB3088.inkml" or \
                self.fileName == "data/inkml/MfrDB/MfrDB0104.inkml":
            return [], [], [], [], [], []
        dictTraces = {}
        # var reservation for current markup file's <trace_id - trace_href - trace_truth - trace_feature>  collection
        lis = []
        listHref, listTruth, listIds = [], [], []
        # BeautifulSoup parsing
        elementsEncapsulated = BeautifulSoup(handler, "xml")
        # fetch current markup id
        idInk = elementsEncapsulated.find(name="annotation", attrs={"type": "UI"})
        # handle empty file exception, output1 current file as blank
        if idInk is None:
            return "", []
        else:
            idInk = idInk.text

        # fetch trace feature in string format
        collectionTraces = elementsEncapsulated.find_all(name="trace")
        for trace in collectionTraces:
            # converting string feature to float feature
            traceFeature = [list(map(lambda number: float(number), item.strip().split(" "))) for item in
                            trace.text.strip().split(",")]
            # append to mapping relationship dictionary
            dictTraces[trace["id"]] = traceFeature

        # nested query for each symbol
        collectionGroups = elementsEncapsulated.find(name="traceGroup").find_all(name="traceGroup")
        # loop over all symbol, re-structuring each trace_id as single list
        symbolIds = []
        for item in collectionGroups:
            truth = item.find(name="annotation", attrs={"type": "truth"}).text
            if item.find(name="annotationXML") is None:
                href = "AUTO"
            else:
                href = item.find(name="annotationXML")["href"]
            # reading each trace instance inside symbol
            symbol_feature = []
            for ins in item.find_all(name="traceView"):
                # read by tag attr
                idIns = ins["traceDataRef"]
                symbol_feature.append(idIns)
                # encapsulate feature
                lis.append(dictTraces[idIns])
                listIds.append(idIns)
                listTruth.append(truth)
                listHref.append(href)
            symbolIds.append(symbol_feature)
        # return as formatted
        return idInk, listTruth, listHref, listIds, lis, symbolIds




