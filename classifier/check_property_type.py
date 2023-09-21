import ast
import os
import random

IOArgs = [
    'input',
    'output',
    'res',
    '.shape',
    'getshape',
    'get_shape',
]

SecondIOArgs = [
    'out', # secondary may link with assert
    'expected', # secondary may link with assert
    '.eval(', # secondary may link with assert
    'decode', # secondary may link with assert
    'result',
    "'x'",
    "'y'"
]

VariableArgs = [
    'variab',

]

SecondVariableArgs = [
    'var', # secondary
    'args', # secondary
    'attr'
]

ConfigArgs = [
    'name',
    'config',
    'param',
    'cfg'
]

ConfigAssert = ['equal', '==']

MetricFunNames = [
    'loss',
    'activation',
    'gradient',
    'entropy',
    # 'max',
    # 'min',
    'metric',
    'acc',
    'score',
    'grad',
]

# MetricSecondName = [
#     # 'size',
#     # 'mean'
# ]

IOAssertions = [
    'notallclose'
    'almostequal',
    'almost_equal'

]

class PropertyAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.functions = {}
        self.stats = {"from": []}
        self.currentFunc = ''
        self.currentCall = []
        self.assertArgs = []
        self.func_methods = {}
        self.calledAttrs = {}
        self.runAttrs = []
        self.setUpAttrs = []
        self.otherAttrs = {}
        self.importTime = False
        self.hasAssert = False
        self.types = []


    def visit_ExceptHandler(self, node):
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        self.hasClass = True

        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        if node.parent and not isinstance(node.parent, ast.FunctionDef):
            self.currentFunc = node.name
        if 'test' in node.name.lower():
            self.calledAttrs[node.name]= []
        self.functions[self.currentFunc] = {}

        for funcName in MetricFunNames:
            if funcName in node.name.lower():
                self.types.append('Metric')

        if '__init__' != node.name:
            self.generic_visit(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and 'assert' in node.func.id.lower():
            # print(ast.unparse(node.func))
            for arg in node.args:
                for argName in ConfigArgs:
                    if argName in ast.unparse(arg).lower():
                        for assertSec in ConfigAssert:
                            if assertSec in ast.unparse(node).lower():
                                self.types.append('Config')
                                return

                for argName in MetricFunNames:
                    if argName in ast.unparse(arg).lower():
                        self.types.append('Metric')
                        return


                for argName in IOArgs:
                    if argName in ast.unparse(arg).lower():
                        self.types.append('I/O')
                        return
                # else:
                #     self.assertArgs.append(arg.n)
                for argName in VariableArgs:
                    if argName in ast.unparse(arg).lower():
                        self.types.append('Variable')
                        return



                # Secondary turn
                for argName in SecondIOArgs:
                    if argName in ast.unparse(arg).lower():
                        self.types.append('I/O')
                        return

                for argName in SecondVariableArgs:
                    if argName in ast.unparse(arg).lower():
                        self.types.append('Variable')
                        return

                # check if IO in the third roll
                if 'equal' in ast.unparse(node).lower():
                    if 'sess' in ast.unparse(node.parent.parent) or '.fit' in ast.unparse(node.parent.parent):
                        self.types.append('I/O')
                        return
                for argName in self.stats['from']:
                    if argName in ast.unparse(arg).lower():
                        self.types.append('I/O')
                        return
                for argName in self.runAttrs:
                    if argName in ast.unparse(arg).lower():
                        self.types.append('I/O')
                        return
        self.generic_visit(node)


    def visit_Attribute(self, node):
        if 'self.' in ast.unparse(node) and 'assert' not in ast.unparse(node) and self.currentFunc != 'setUp' and 'test' in self.currentFunc.lower():
            if self.currentFunc in self.calledAttrs.keys():
                self.calledAttrs[self.currentFunc].append(ast.unparse(node))
            else:
                self.calledAttrs[self.currentFunc] = [ast.unparse(node)]

        if 'assert' in node.attr:
            # print(node.attr)
            self.hasAssert = True
            if len(self.functions[self.currentFunc]) == 0:
                self.functions[self.currentFunc] = [node.parent]
            else:
                self.functions[self.currentFunc].append(node.parent)

            thisCall = node.parent
            argCount = len(thisCall.args)
            # print(thisCall.args)
            # print(ast.unparse(thisCall).lower())
            for arg in thisCall.args:
                # print(ast.unparse(arg))

                for argName in ConfigArgs:
                    if argName in ast.unparse(arg).lower():
                        for assertSec in ConfigAssert:
                            if assertSec in ast.unparse(thisCall).lower():
                                self.types.append('Config')
                                return

                for argName in MetricFunNames:
                    if argName in ast.unparse(arg).lower():
                        self.types.append('Metric')
                        return


                for argName in IOArgs:
                    if argName in ast.unparse(arg).lower():
                        self.types.append('I/O')
                        return
                # else:
                #     self.assertArgs.append(arg.n)
                for argName in VariableArgs:
                    if argName in ast.unparse(arg).lower():
                        self.types.append('Variable')
                        return



                # Secondary turn
                for argName in SecondIOArgs:
                    if argName in ast.unparse(arg).lower():
                        self.types.append('I/O')
                        return

                for argName in SecondVariableArgs:
                    if argName in ast.unparse(arg).lower():
                        self.types.append('Variable')
                        return

                # check if IO in the third roll
                if 'equal' in ast.unparse(thisCall).lower():
                    if 'sess' in ast.unparse(thisCall.parent.parent) or '.fit' in ast.unparse(thisCall.parent.parent):
                        self.types.append('I/O')
                        return
                for argName in self.stats['from']:
                    if argName in ast.unparse(arg).lower():
                        self.types.append('I/O')
                        return
                for argName in self.runAttrs:
                    if argName in ast.unparse(arg).lower():
                        self.types.append('I/O')
                        return
        self.generic_visit(node)

    def visit_Assert(self, node):
        if len(self.functions[self.currentFunc]) != 0:
            self.functions[self.currentFunc].append(node)
        else:
            self.functions[self.currentFunc] = [node]
        self.hasAssert = True

        sentence = ast.unparse(node).lower().replace('assert', '').replace(' ', '')
        for argName in IOArgs:
            if argName in sentence:
                self.types.append('I/O')
                return
        for argName in MetricFunNames:
            if argName in sentence:
                self.types.append('Metric')
                return

        for argName in self.stats['from']:
            if argName in sentence:
                self.types.append('I/O')
                return

        for argName in self.runAttrs:
            if argName in sentence:
                self.types.append('I/O')
                return
        for argName in SecondIOArgs:
            if argName in sentence:
                self.types.append('I/O')
                return

        self.generic_visit(node)

    def visit_Assign(self, node):
        assValue= ast.unparse(node.value)
        if '.fit' in assValue or '.run' in assValue:
            for target in node.targets:
                self.runAttrs.append(ast.unparse(target))
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        # print(ast.dump(node))
        for alias in node.names:
            if 'test' not in alias.name.lower():
                self.stats["from"].append(alias.name)
        self.generic_visit(node)

    def get_hasClass(self):
        return self.hasClass

    def get_types(self):
        return self.types

def checkType(fileName):
    myTypes = []

    with open(fileName, "r") as source:
        tree = ast.parse(source.read())

    tree.parent = None
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            child.parent = node

    analyzer = PropertyAnalyzer()
    analyzer.visit(tree)

    tempTypes = list(set(analyzer.get_types()))
    # print(tempTypes)
    if len(myTypes) > 0:
        for type in myTypes:
            if type not in tempTypes:
                tempTypes.append(type)


    return tempTypes




if __name__ == "__main__":

    myTypes = ['Error Raising', 'I/O', 'Variable', 'Config', 'Metric']
    allDict = {
        'Error Raising': [],
        'I/O': [],
        'Variable': [],
        'Config': [],
        'Metric': [],
        'Others': []
    }
    countTypes = {}
    countEmpty = 0
    emptyFiles = []
    for root, dirs, files in os.walk(""):
        for file in files:
            if file.endswith(".py"):
                try:
                    # print(os.path.join(root, file))
                    myFilePath = os.path.join(root, file)
                    with open(os.path.join(root, file), "r") as source:
                        tree = ast.parse(source.read())
                    sourceCode = ast.unparse(tree).lower()

                    # print(ast.dump(tree))
                    types = checkType(os.path.join(root, file))

                    if len(types) == 0:
                        emptyFiles.append(myFilePath)
                        countEmpty += 1
                        allDict['Others'].append(myFilePath)
                    for type in types:
                        allDict[type].append(file)
                        if type in countTypes.keys():
                            countTypes[type] += 1
                        else:
                            countTypes[type] = 1
                except Exception as e:
                    print(e)
                    pass

    for key in allDict.keys():

        with open('result/'+key.replace('/','') + '.txt', 'w') as f:
            for file in allDict[key]:
                f.write(file.split('/')[-1] + '\n')
