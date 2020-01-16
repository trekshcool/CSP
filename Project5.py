import sys
import numpy as np
from typing import NamedTuple
from Solve import CSP

'''
# def backtrack(variable, value, limits, unary_inclusive, unary_exclusive, binary_equal, binary_not_equals, binary_simultaneous):
# if complete, return bags
# Select the MRV variable to fill
# Fill in a value and solve further (recursively),
# backtracking an assignment when stuck
# Finds 90% rounded down

#finds the max bag capasity
def maximum_capacity_helper(capacity):
    return round(0.9 * capacity)


all = ["bag", "constraint", "csp", "item", "solver"]

# attemmpt as csp
class CSP(object):
    def __init__(self, items, bags):
        self.bags = bags
        self.items = items

        for item_name in self.items:
            self.items[item_name].possible_bags = self.bags.copy()

# item object for easy use
class Item(object):
    def __init__(self, name, weight):
        # Name of the Item
        self.name = name
        # Weight of the item
        self.weight = int(weight)
        # The bag that item is in
        self.bag = None
        # Possible bags
        self.possible_bags = {}
        # Constraints of item
        self.constraints = []

    def __eq__(self, other):
        if isinstance(other, Item):
            return self.name == other.name
        return NotImplemented

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result

    def putInBag(self, bag):
        if self.bag:
            self.bag.items = [s for s in self.bag.items if s.name is not self.name]
        bag.items.append(self)
        self.bag = bag
'''

class Variable(NamedTuple):
    item: chr
    weight: int

class Value(NamedTuple):
    bag: chr
    capacity: int

class Limits(NamedTuple):
    lowerBound: int
    upperBound: int

class UnaryInclusive(NamedTuple):
    item: chr
    bags: str

class UnaryExclusive(NamedTuple):
    item: chr
    bags: str

class BinaryEqual(NamedTuple):
    items: str

class BinaryNotEquals(NamedTuple):
    items: str

class BinarySimultaneous(NamedTuple):
    items: str
    bags: str

if len(sys.argv) != 3:
    sys.exit('Must specify input and output files')
inputFile = sys.argv[1]
data = np.loadtxt(inputFile, delimiter='\n', dtype='str')
inputData = []
for element in data:
    element = element.split()
    inputData.append(element)

variables = []
values = []
limits = []
inclusives = []
exclusives = []
equals = []
notEquals = []
simultaneous = []

category = 0
counter = 0
file = open(inputFile, "r")
for line in file:
    line = line.strip()
    if line[0] == '#':
        category += 1
    else:
        if category == 1:
            weight = int(inputData[counter][1])
            variables.append(Variable(inputData[counter][0], weight))
        elif category == 2:
            capacity = int(inputData[counter][1])
            values.append(Value(inputData[counter][0], capacity))
        elif category == 3:
            lowerBound = int(inputData[counter][0])
            upperBound = int(inputData[counter][1])
            limits.append(Limits(lowerBound, upperBound))
        elif category == 4:
            bags = []
            for i in range(len(inputData[counter])):
                if i == 0:
                    item = inputData[counter][i]
                else:
                    bags.append(inputData[counter][i])
            inclusives.append(UnaryInclusive(item, bags))
        elif category == 5:
            bags = []
            for i in range(len(inputData[counter])):
                if i == 0:
                    item = inputData[counter][i]
                else:
                    bags.append(inputData[counter][i])
            exclusives.append(UnaryExclusive(item, bags))
        elif category == 6:
            items = []
            for i in range(len(inputData[counter])):
                items.append(inputData[counter][i])
            equals.append(BinaryEqual(items))
        elif category == 7:
            items = []
            for i in range(len(inputData[counter])):
                items.append(inputData[counter][i])
            notEquals.append(BinaryNotEquals(items))
        else:
            items = []
            bags = []
            for i in range(len(inputData[counter])):
                if ord(inputData[counter][i]) < 97:
                    items.append(inputData[counter][i])
                else:
                    bags.append(inputData[counter][i])
            simultaneous.append(BinarySimultaneous(items, bags))
        counter += 1

if not limits:
    limits.append(Limits(1,999))
outputs = CSP(variables, values, limits, inclusives, exclusives, equals, notEquals, simultaneous)

outputFile = sys.argv[2]
with open(outputFile, 'w') as infile:
    if not outputs:
        infile.write('No such assignment is possible')
    else:
        for output in outputs:
            infile.write(output.bag + ' ' + ' '.join(output.items) + '\n')
            infile.write('number of items: ' + str(output.numItems) + '\n')
            infile.write('total weight ' + str(output.usedCapacity) + '/' + str(output.totalCapacity) + '\n')
            infile.write('wasted capacity: ' + str(output.wastedCapacity) + '\n')
            infile.write('\n')
