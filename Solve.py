import time
from typing import NamedTuple
import random
import math


initialTime = 0
endTime = 0

class Variable(NamedTuple):
    item: chr
    weight: int

class OutputBag(NamedTuple):
    bag: chr
    items: str
    numItems: int
    totalCapacity: int
    usedCapacity: int
    wastedCapacity: int
    requiredCapacity: int

class ConstraintItems(NamedTuple):
    binarySimultaneousItems: str
    binarySimultaneousBags: str
    binaryNotEquals: str
    unaryExclusive: str
    binaryEquals: str
    unaryInclusive: str

#prints the outputs
def printOutput(outputs):
    if len(outputs) == 0:
        print('No such assignment is possible')
    else:
        for output in outputs:
            print(output.bag, end=' ')
            for item in output.items:
                print(item, end=' ')
            print()
            print('number of items: %i' % output.numItems)
            print('total weight: %i/%i' % (output.usedCapacity, output.totalCapacity))
            print('wasted capacity: %i' % output.wastedCapacity)
            print()

#Breaks ties when two items have the same MRVHeusitic based on the total number of constraints each item has
def DegreeHeuristic(current, new):
    sumCurrent = 0
    for i in range(len(current)-2):
        sumCurrent += current[i + 1]
    sumNew = 0
    for i in range(len(new)-2):
        sumNew += new[i + 1]

    if sumCurrent >= sumNew:
        return current
    else:
        return new

#Helper for MRVHeusitic, iterates through unary constraints to check if the item has that constraint
def CheckUnaryConstraints(itemName, constraint):
    relatedElements =[]
    for line in constraint:
        if line.item == itemName:
            relatedElements = line.bags
            return 1, relatedElements
    return 0, relatedElements

#Helper for MRVHeusitic, iterates through binary constraints to check if the item has that constraint
def CheckBinaryConstraints(itemName, constraint):
    relatedElements =[]
    counter = 0
    for line in constraint:
        for element in line.items:
            if element == itemName:
                for ele in line.items:
                    if ele != itemName:
                        relatedElements.append(ele)
                counter += 1
    return counter, relatedElements

#Helper for MRVHeusitic, iterates through binary constraints to check if the item has that constraint
def CheckSimultaneousConstraints(itemName, constraint):
    relatedItems = []
    relatedBags = []
    counter = 0
    for line in constraint:
        for element in line.items:
            if element == itemName:
                for ele in line.items:
                    if ele != itemName:
                        relatedItems.append(ele)
                for ele in line.bags:
                    relatedBags.append(ele)
                counter += 1
    return counter, relatedItems, relatedBags

#Returns the item with the highest heuristic value based on its weighted constraints
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
    return maxHeuristicItem

#Helper for forward checking, iterates through constraints and returns the appropriate variables
def BinaryNotEqualsForward(variable, weight, constraints, outputs, limits, possibleBags):
    if not possibleBags:
        for outputBag in outputs:
            if (outputBag.numItems < limits[0].upperBound) and (outputBag.wastedCapacity >= weight):
                possibleBags.append(outputBag.bag)
                if outputBag.items:
                    for i1 in outputBag.items:
                        for i2 in constraints.binaryNotEquals:
                            if i1 == i2:
                                possibleBags.remove(outputBag.bag)
    else:
        for bag in possibleBags:
            for outputBag in outputs:
                if outputBag.bag == bag:
                    if outputBag.items:
                        for i1 in outputBag.items:
                            for i2 in constraints.binaryNotEquals:
                                if i1 == i2:
                                    possibleBags.remove(bag)

    for outputBag in outputs:
        if (outputBag.numItems < limits[0].upperBound) and (outputBag.wastedCapacity >= weight):
            possibleBags.append(outputBag.bag)
    max = 0
    chosenBag = 0
    for bag in possibleBags:
        for outputBag in outputs:
            if outputBag.bag == bag:
                if (outputBag.numItems < limits[0].upperBound) and (
                        (outputBag.usedCapacity + weight) == outputBag.totalCapacity):
                    if max < 3:
                        max = 3
                        chosenBag = bag
                if (outputBag.numItems == 0):
                    if max < 2:
                        max = 2
                        chosenBag = bag
                if (outputBag.numItems < limits[0].upperBound) and (
                        outputBag.usedCapacity < outputBag.requiredCapacity):
                    if max < 1:
                        max = 1
                        chosenBag = bag
    if max > 0:
        return chosenBag, variable
    else:
        if possibleBags:
            return random.choice(possibleBags), variable
        else:
            return '0', variable

#Helper for forward checking, iterates through constraints and returns the appropriate variables
def UnaryExclusiveForward(variable, weight, constraints, outputs, limits, possibleBags):
    if not possibleBags:
        for outputBag in outputs:
            if (outputBag.numItems < limits[0].upperBound) and (outputBag.wastedCapacity >= weight):
                possibleBags.append(outputBag.bag)
                for bag in constraints.unaryExclusive:
                    if outputBag.bag == bag:
                        possibleBags.remove(bag)
    else:
        for b1 in possibleBags:
            for b2 in constraints.unaryExclusive:
                if b1 == b2:
                    possibleBags.remove(b1)

    if constraints.binaryNotEquals:
        return BinaryNotEqualsForward(variable, weight, constraints, outputs, limits, possibleBags)
    else:
        for outputBag in outputs:
            if (outputBag.numItems < limits[0].upperBound) and (outputBag.wastedCapacity >= weight):
                possibleBags.append(outputBag.bag)
        max = 0
        chosenBag = 0
        for bag in possibleBags:
            for outputBag in outputs:
                if outputBag.bag == bag:
                    if (outputBag.numItems < limits[0].upperBound) and ((outputBag.usedCapacity + weight) == outputBag.totalCapacity):
                        if max < 3:
                            max = 3
                            chosenBag = bag
                    if (outputBag.numItems == 0):
                        if max < 2:
                            max = 2
                            chosenBag = bag
                    if (outputBag.numItems < limits[0].upperBound) and (outputBag.usedCapacity < outputBag.requiredCapacity):
                        if max < 1:
                            max = 1
                            chosenBag = bag
        if max > 0:
            return chosenBag, variable
        else:
            if possibleBags:
                return random.choice(possibleBags), variable
            else:
                return '0', variable

#Helper for forward checking, iterates through constraints and returns the appropriate variables
def BinarySimultaneousForward(variable, weight, constraints, outputs, limits, possibleBags):
    if not possibleBags:
        for outputBag in outputs:
            for b1 in constraints.binarySimultaneousBags:
                if outputBag.bag == b1:
                    for i1 in constraints.binarySimultaneousItems:
                        if outputBag.items:
                            for i2 in outputBag.items:
                                if i1 == i2:
                                    for b2 in constraints.binarySimultaneousBags:
                                        if outputBag.bag != b2:
                                            possibleBags.append(b2)
        for outputBag in outputs:
            for bag in possibleBags:
                if bag == outputBag.bag:
                    if not ((outputBag.numItems < limits[0].upperBound) and (outputBag.wastedCapacity >= weight)):
                        possibleBags.remove(bag)
    else:
        oldPossibleBags = possibleBags
        possibleBags = []
        for b1 in possibleBags:
            for outputBag in outputs:
                if outputBag.bag == b1:
                    for b2 in constraints.binarySimultaneousBags:
                        if b1 == b2:
                            for i1 in constraints.binarySimultaneousItems:
                                if outputBag.items:
                                    for i2 in outputBag.items:
                                        if i1 == i2:
                                            for b3 in constraints.binarySimultaneousBags:
                                                if b1 != b3:
                                                    possibleBags.append(b3)
        for outputBag in outputs:
            for bag in possibleBags:
                if bag == outputBag.bag:
                    if not ((outputBag.numItems < limits[0].upperBound) and (outputBag.wastedCapacity >= weight)):
                        possibleBags.remove(bag)
        if not possibleBags:
            possibleBags = oldPossibleBags

    if constraints.unaryExclusive:
        return UnaryExclusiveForward(variable, weight, constraints, outputs, limits, possibleBags)
    elif constraints.binaryNotEquals:
        return BinaryNotEqualsForward(variable, weight, constraints, outputs, limits, possibleBags)
    else:
        for outputBag in outputs:
            if (outputBag.numItems < limits[0].upperBound) and (outputBag.wastedCapacity >= weight):
                possibleBags.append(outputBag.bag)
        max = 0
        chosenBag = 0
        for bag in possibleBags:
            for outputBag in outputs:
                if outputBag.bag == bag:
                    if (outputBag.numItems < limits[0].upperBound) and ((outputBag.usedCapacity + weight) == outputBag.totalCapacity):
                        if max < 3:
                            max = 3
                            chosenBag = bag
                    if (outputBag.numItems == 0):
                        if max < 2:
                            max = 2
                            chosenBag = bag
                    if (outputBag.numItems < limits[0].upperBound) and (outputBag.usedCapacity < outputBag.requiredCapacity):
                        if max < 1:
                            max = 1
                            chosenBag = bag
        if max > 0:
            return chosenBag, variable
        else:
            if possibleBags:
                return random.choice(possibleBags), variable
            else:
                return '0', variable

#Helper for forward checking, iterates through constraints and returns the appropriate variables
def BinaryEqualsForward(variable, weight, constraints, outputs, limits, possibleBags):
    if not possibleBags:
        for outputBag in outputs:
            if outputBag.items:
                for i1 in outputBag.items:
                    for i2 in constraints.binaryEquals:
                        if i1 == i2:
                            if (outputBag.numItems < limits[0].upperBound) and (outputBag.wastedCapacity >= weight):
                                possibleBags.append(outputBag.bag)
        if not possibleBags:
            for outputBag in outputs:
                if (outputBag.numItems < limits[0].upperBound) and (outputBag.wastedCapacity >= weight):
                    possibleBags.append(outputBag.bag)
    else:
        for bag in possibleBags:
            flag = 0
            for outputBag in outputs:
                if bag == outputBag.bag:
                    if outputBag.items:
                        for i1 in outputBag.items:
                            for i2 in constraints.binaryEquals:
                                if i1 == i2:
                                    flag = 1
            if not flag:
                possibleBags.remove(bag)

    if constraints.binarySimultaneousBags:
        return BinarySimultaneousForward(variable, weight, constraints, outputs, limits, possibleBags)
    elif constraints.unaryExclusive:
        return UnaryExclusiveForward(variable, weight, constraints, outputs, limits, possibleBags)
    elif constraints.binaryNotEquals:
        return BinaryNotEqualsForward(variable, weight, constraints, outputs, limits, possibleBags)
    else:
        for outputBag in outputs:
            if (outputBag.numItems < limits[0].upperBound) and (outputBag.wastedCapacity >= weight):
                possibleBags.append(outputBag.bag)
        max = 0
        chosenBag = 0
        for bag in possibleBags:
            for outputBag in outputs:
                if outputBag.bag == bag:
                    if (outputBag.numItems < limits[0].upperBound) and ((outputBag.usedCapacity + weight) == outputBag.totalCapacity):
                        if max < 3:
                            max = 3
                            chosenBag = bag
                    if (outputBag.numItems == 0):
                        if max < 2:
                            max = 2
                            chosenBag = bag
                    if (outputBag.numItems < limits[0].upperBound) and (outputBag.usedCapacity < outputBag.requiredCapacity):
                        if max < 1:
                            max = 1
                            chosenBag = bag
        if max > 0:
            return chosenBag, variable
        else:
            if possibleBags:
                return random.choice(possibleBags), variable
            else:
                return '0', variable

#Helper for forward checking, iterates through constraints and returns the appropriate variables
def UnaryInclusiveForward(variable, weight, constraints, outputs, limits, possibleBags):
    for bag in constraints.unaryInclusive:
        for outputBag in outputs:
            if outputBag.bag == bag:
                if (outputBag.numItems < limits[0].upperBound) and (outputBag.wastedCapacity >= weight):
                    possibleBags.append(bag)

    if constraints.binaryEquals:
        return BinaryEqualsForward(variable, weight, constraints, outputs, limits, possibleBags)
    elif constraints.binarySimultaneousBags:
        return BinarySimultaneousForward(variable, weight, constraints, outputs, limits, possibleBags)
    elif constraints.unaryExclusive:
        return UnaryExclusiveForward(variable, weight, constraints, outputs, limits, possibleBags)
    elif constraints.binaryNotEquals:
        return BinaryNotEqualsForward(variable, weight, constraints, outputs, limits, possibleBags)
    else:
        for outputBag in outputs:
            if (outputBag.numItems < limits[0].upperBound) and (outputBag.wastedCapacity >= weight):
                possibleBags.append(outputBag.bag)
        max = 0
        chosenBag = 0
        for bag in possibleBags:
            for outputBag in outputs:
                if outputBag.bag == bag:
                    if (outputBag.numItems < limits[0].upperBound) and ((outputBag.usedCapacity + weight) == outputBag.totalCapacity):
                        if max < 3:
                            max = 3
                            chosenBag = bag
                    if (outputBag.numItems == 0):
                        if max < 2:
                            max = 2
                            chosenBag = bag
                    if (outputBag.numItems < limits[0].upperBound) and (outputBag.usedCapacity < outputBag.requiredCapacity):
                        if max < 1:
                            max = 1
                            chosenBag = bag
        if max > 0:
            return chosenBag, variable
        else:
            if possibleBags:
                return random.choice(possibleBags), variable
            else:
                return '0', variable

#forward checking implimentation
def ForwardChecking(itemToExpand, variables, outputs, limits):
    possibleBags = []
    constraints = itemToExpand[7]
    weight = 0
    variable = 0
    for item in variables:
        if item.item == itemToExpand[0]:
            weight = item.weight
            variable = item

    if constraints.unaryInclusive:
        return UnaryInclusiveForward(variable, weight, constraints, outputs, limits, possibleBags)
    elif constraints.binaryEquals:
        return BinaryEqualsForward(variable, weight, constraints, outputs, limits, possibleBags)
    elif constraints.binarySimultaneousBags:
        return BinarySimultaneousForward(variable, weight, constraints, outputs, limits, possibleBags)
    elif constraints.unaryExclusive:
        return UnaryExclusiveForward(variable, weight, constraints, outputs, limits, possibleBags)
    elif constraints.binaryNotEquals:
        return BinaryNotEqualsForward(variable, weight, constraints, outputs, limits, possibleBags)
    else:
        for outputBag in outputs:
            if (outputBag.numItems < limits[0].upperBound) and (outputBag.wastedCapacity >= weight):
                possibleBags.append(outputBag.bag)
        max = 0
        chosenBag = 0
        for bag in possibleBags:
            for outputBag in outputs:
                if outputBag.bag == bag:
                    if (outputBag.numItems < limits[0].upperBound) and ((outputBag.usedCapacity + weight) == outputBag.totalCapacity):
                        if max < 3:
                            max = 3
                            chosenBag = bag
                    if (outputBag.numItems == 0):
                        if max < 2:
                            max = 2
                            chosenBag = bag
                    if (outputBag.numItems < limits[0].upperBound) and (outputBag.usedCapacity < outputBag.requiredCapacity):
                        if max < 1:
                            max = 1
                            chosenBag = bag
        if max > 0:
            return chosenBag, variable
        else:
            if possibleBags:
                return random.choice(possibleBags), variable
            else:
                return '0', variable

#Remove item from output bag
def removeFromBag(outputs, bag, item):
    newOutputBag = 0
    for outputBag in outputs:
        if outputBag.bag == bag:
            outputBag.items.remove(item.item)
            l = list(outputBag)
            l[2] = outputBag.numItems - 1
            l[4] = outputBag.usedCapacity - item.weight
            l[5] = outputBag.wastedCapacity + item.weight
            newOutputBag = OutputBag(l[0], l[1], l[2], l[3], l[4], l[5], l[6])
    for outputBag in outputs:
        if outputBag.bag == bag:
            outputs.remove(outputBag)
    outputs.append(newOutputBag)

#Put item in output bag
def putInBag(outputs, bag, item):
    newOutputBag = 0
    for outputBag in outputs:
        if outputBag.bag == bag:
            outputBag.items.append(item.item)
            l = list(outputBag)
            l[2] = outputBag.numItems + 1
            l[4] = outputBag.usedCapacity + item.weight
            l[5] = outputBag.wastedCapacity - item.weight
            newOutputBag = OutputBag(l[0], l[1], l[2], l[3], l[4], l[5], l[6])
    for outputBag in outputs:
        if outputBag.bag == bag:
            outputs.remove(outputBag)
    outputs.append(newOutputBag)

#Backtracking implimentaion
def Backtracking(outputs, variables):
    for outputBag in outputs:
        if outputBag.usedCapacity < outputBag.requiredCapacity:
            for bag in outputs:
                if outputBag.bag != bag.bag:
                    for item1 in outputBag.items:
                        for variable1 in variables:
                            if variable1.item == item1:
                                for item2 in bag.items:
                                    for variable2 in variables:
                                        if variable2.item == item2:
                                            if ((outputBag.usedCapacity - variable1.weight + variable2.weight) >= outputBag.requiredCapacity) and ((bag.usedCapacity - variable2.weight + variable1.weight) >= bag.requiredCapacity):
                                                removeFromBag(outputs, outputBag.bag, variable1)
                                                removeFromBag(outputs, bag.bag, variable2)
                                                putInBag(outputs, outputBag.bag, variable2)
                                                putInBag(outputs, bag.bag, variable1)
                                                return
                    for item in bag.items:
                        for variable in variables:
                            if variable.item == item:
                                if ((outputBag.usedCapacity + variable.weight) >= outputBag.requiredCapacity):
                                    removeFromBag(outputs, bag.bag, variable)
                                    putInBag(outputs, outputBag.bag, variable)
                                    return



items = []
bags = []
outputs = []

#CSP implimentation.
def CSP(variables, values, limits, inclusives, exclusives, equals, notEquals, simultaneous):
    initialTime = 0
    endTime = 0
    variablescopy = variables
    valuescopy = values
    initialTime = time.time()
    for bag in values:
        bags.append(bag.bag)
        outputs.append(OutputBag(bag.bag, [], 0, bag.capacity, 0, bag.capacity, math.floor(0.9*bag.capacity)))
    for item in variables:
        items.append(item.item)
    for i in range(len(variables)):
        itemToExpand = MRVHeusitic(items, inclusives, exclusives, equals, notEquals, simultaneous)
        items.remove(itemToExpand[0])
        # Testing for just backtrack, backtrack+MVC, backtrack+MVC+ForwardChecking
        #itemIndex = [i for i, v in enumerate(variablescopy) if v[0] == itemToExpand[0]]
        #item = Variable(itemToExpand[0], variablescopy[itemIndex[0]][1])
        #item = variablescopy[i]
        #bag = random.choice(valuescopy)[0]
        #print(itemIndex[0])
        #print(item)
        #bag = valuescopy[random.randint(0, len(variablescopy))]
        #print(item)
        #print(valuescopy[random.randint(0,len(variablescopy)) ])

        bag, item = ForwardChecking(itemToExpand, variables, outputs, limits)
        if bag == '0':
            noOutput = []
            printOutput(noOutput)
            return
        putInBag(outputs, bag, item)
    Backtracking(outputs, variables)
    endTime = time.time()
    print("time elapsed", str(endTime - initialTime))
    return outputs

#LCV helper function.
def merge(list1, list2):
    merged_list = [(list1[i], list2[i]) for i in range(0, len(list1))]
    return merged_list

def LCVHeusitic(items,values,outputs):
    item_key = []
    constraining_values_key =[]
    #Check per item
    for item in items:
        item_key.append(item)
        #the number of places in total the other items can go in given item in a bag
        constraining = 0
        outputsfitsallconstraits = True

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
                    if(outputsfitsallconstraits):
                        # Add 1 to constraining for each value that fits all the constraits
                        constraining += 1
                    #take out the item to prevent output contamination.
                    removeFromBag(outputs, value2, nonMainItems)
        constraining_values_key.append(constraining)
    #merged list with key and items
    item_constraint_tuples = merge(item_key,constraining_values_key)
    #sorting tuple list into acending order.
    return sorted(item_constraint_tuples, key=lambda item_constraint_tuples: item_constraint_tuples[1]).reverse()