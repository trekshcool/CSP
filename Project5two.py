import sys
import numpy as np
from typing import NamedTuple
from Solve import CSP, putInBag, removeFromBag


# def backtrack(variable, value, limits, unary_inclusive, unary_exclusive, binary_equal, binary_not_equals, binary_simultaneous):
# if complete, return bags
# Select the MRV variable to fill
# Fill in a value and solve further (recursively),
# backtracking an assignment when stuck
# Finds 90% rounded down


def maximum_capacity_helper(capacity):
    return round(0.9 * capacity)

def merge(list1, list2):
    merged_list = [(list1[i], list2[i]) for i in range(0, len(list1))]
    return merged_list

def LCVHeusitic(items, inclusives, exclusives, equals, notEquals, simultaneous, outputs):
    item_key = []
    constraining_values_key =[]
    #Check per item
    for item in items:
        item_key.append(item)
        #the number of places in total the other items can go in given item in a bag
        constraining = 0

        #itrates through putting the item in each bag
        for value in values:
            #list of items that not the one in the bag.
            nonUsedItems = items.remove(item)
            #intrate though the remaining items
            for nonMainItems in nonUsedItems:
                #try to put remaining item in each bag so that we can add to constraining
                for value2 in values:
                    #temporairly put in the value to see if constraints fit in this bag.
                    putInBag(outputs, value2, nonMainItems)
                    #check if output fits all constraits
                    #NEEDS TO BE COMPLETED!!!
                    if(outputs fits all constraits)
                        # Add 1 to constraining for each value that fits all the constraits
                        constraining += 1
                    #take out the item to prevent output contamination.
                    removeFromBag(outputs, value2, nonMainItems)
        constraining_values_key.append(constraining)
    #merged list with key and items
    item_constraint_tuples = merge(item_key,constraining_values_key)
    #sorting tuple list into acending order.
    return sorted(item_constraint_tuples, key=lambda item_constraint_tuples: item_constraint_tuples[1]).reverse()



def MRVHeusitic(items, inclusives, exclusives, equals, notEquals, simultaneous):
    heuristics = []
    for item in items:
        itemHeuristic = []
        itemHeuristic.append(item)
        #Check constraints in ascending order of importance
        count, binarySimultaneousItems, binarySimultaneousBags = CheckSimultaneousConstraints(item, simultaneous)
        itemHeuristic.append(count)
        count, binaryNotEquals = CheckBinaryConstraints(item, notEquals)
        itemHeuristic.append(count)
        count, unaryExclusive = CheckUnaryConstraints(item, exclusives)
        itemHeuristic.append(count)
        count, binaryEquals = CheckBinaryConstraints(item, equals)
        itemHeuristic.append(count)
        count, unaryInclusive = CheckUnaryConstraints(item, inclusives)
        itemHeuristic.append(count)
        #Sum the weighted number of constraints an item has
        sum = 0
        for i in range(len(itemHeuristic)-1):
            sum += itemHeuristic[i+1] * (i+1)
        itemHeuristic.append(sum)
        itemHeuristic.append(ConstraintItems(binarySimultaneousItems, binarySimultaneousBags, binaryNotEquals, unaryExclusive, binaryEquals, unaryInclusive))
        #Add to the list
        heuristics.append(itemHeuristic)
    #Decide item with max heuristic and break ties if any
    max = -1
    maxHeuristicItem = ''
    for itemHeuristic in heuristics:
        if itemHeuristic[6] == max:
            maxHeuristicItem = DegreeHeuristic(maxHeuristicItem, itemHeuristic)
        elif itemHeuristic[6] > max:
            max = itemHeuristic[6]
            maxHeuristicItem = itemHeuristic
    #Return item with highest heuristic
    print(maxHeuristicItem)
    return maxHeuristicItem


class CSP(object):
    def __init__(self, items, bags):
        self.bags = bags
        self.items = items

        for item_name in self.items:
            self.items[item_name].possible_bags = self.bags.copy()


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

if len(sys.argv) != 2:
    sys.exit("Must specify input file")
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

CSP(variables, values, limits, inclusives, exclusives, equals, notEquals, simultaneous)
print(variables)
print(values)
print(limits)
