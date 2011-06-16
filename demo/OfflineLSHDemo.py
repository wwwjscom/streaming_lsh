'''
A demo for clustering text document using locality sensitive hashing.

Command to run the demo: python OfflineLSHDemo.py

The training and test documents used in this demo are in the following format:
<cluster_id> <document>

Example:
1 abc def efe tert ertre
2 sdf ertr frf frfe
1 sdfds sdfdsf dsfewf

Created on Jun 15, 2011

@author: kykamath
'''

import sys
sys.path.append('../')
import numpy
from classes import Permutation, Document
from library.vector import Vector, VectorGenerator
from library.clustering import EvaluationMetrics
from collections import defaultdict
from operator import itemgetter

def iterateLinesFromFile(filePath):
    for line in open(filePath):
        if not line.startswith('#'): yield line.strip()

class OfflineLSHDemo:
    @staticmethod
    def demo():
        wordToDimensionMap = {}
        def createDocumentFromLine(docId, line):
            vector = Vector()
            words = line.split()
            for word in words[1:]:
                if word not in wordToDimensionMap: wordToDimensionMap[word]=len(wordToDimensionMap)
                wordDimension = wordToDimensionMap[word]
                if wordDimension not in vector: vector[wordDimension]=1
                else: vector[wordDimension]+=1
            return Document(docId, vector, clusterType=words[0])
        
        dimensions = 52
        signatureLength=13
        numberOfPermutations = 5
        
        unitRandomVectors = [VectorGenerator.getRandomGaussianUnitVector(dimensions, 0, 1) for i in range(signatureLength)]
        permutations = [Permutation(signatureLength) for i in range(numberOfPermutations)]
        
        # Build LSH Model.
        # Read training documents.
        traningDocumentsMap = {}
        for docId, l in enumerate(iterateLinesFromFile('../data/train.dat')): traningDocumentsMap[docId] = createDocumentFromLine(docId, l)
        # Construct cluster vectors.
        clusterToDocumentsMap = defaultdict(list)
        for document in traningDocumentsMap.values(): clusterToDocumentsMap[document.clusterType].append(document.vector)
        clusterMap = {}
        for k, v in clusterToDocumentsMap.iteritems(): clusterMap[k]=Document(docId=k, vector=Vector.getMeanVector(v), clusterType=k)
        
        # Create signatures and permutations for all the clusters.
        map(lambda document: document.setDocumentSignatureUsingUnitRandomVectors(unitRandomVectors), clusterMap.values())
        for permutation in permutations:
            for document in clusterMap.values(): permutation.addDocument(document)
        
        # Testing the model.
        # Read testing documents.
        testDocumentsMap = {}
        for docId, l in enumerate(iterateLinesFromFile('../data/test.dat')): testDocumentsMap[docId] = createDocumentFromLine(docId, l)
        # Create signatures for test documents
        map(lambda document: document.setDocumentSignatureUsingUnitRandomVectors(unitRandomVectors), testDocumentsMap.values())
        
        predicted, labels = [], []
        for t in testDocumentsMap.values():
            possibleNearestClusters = reduce(lambda x,y:x.union(y), (permutation.getNearestDocuments(t) for permutation in permutations), set())
            predictedClass = max(((clusterType, clusterMap[clusterType].vector.cosineSimilarity(t.vector)) for clusterType in possibleNearestClusters), key=itemgetter(1))
            predicted.append(predictedClass[0])
            labels.append(t.clusterType)
        return EvaluationMetrics.purity(predicted, labels)
            
if __name__ == '__main__':
    print numpy.mean([OfflineLSHDemo.demo() for i in range(10)])
