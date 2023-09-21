import os
import ast
import nltk
from nltk.stem.snowball import SnowballStemmer

snow_stemmer = SnowballStemmer(language='english')

class GetClassNameAnalyser(ast.NodeVisitor):
    def __init__(self):
        self.classNames = []

    def get_classes(self):
        return self.classNames

    def visit_ClassDef(self, node):

        if 'test' in node.name.lower():

            self.classNames.append(node.name.lower())

firstPri = {

                'Loss Function':['loss', 'entropy'],
                'Metric': ['metric', 'score', 'chart', 'matric'],
                'Optimizer':['optimizer','optim', 'adam'],
                'Activation Function':['activation', 'relu', 'sigmoid', 'tanh', 'gelu', 'leaky', 'swish', 'mish', 'prelu', 'maxout','selu'],
                'Layer':['model','layer', 'norm', 'attention', 'module', 'net'],
                'Util':['util', 'dataset', 'database', 'db', 'preprocess','postprocess'],
}

checkTypes = {'Util':['util', 'dataset', 'database', 'db', 'preprocess','postprocess', 'librar', 'token', 'config', 'pretrain', 'scheduler', 'dataload', 'build', 'ops', 'load', 'data', 'env', 'feature', 'processing', 'batch', 'import', 'vocab', 'param', 'get', 'eval', 'save', 'cpu', 'gpu', 'arch', 'matcher', 'slice', 'search', 'misc'],
              'Loss Function':['loss', 'focal', 'triplet', 'infonce', 'hinge', 'entropy'],
              'Metric': ['metric', 'score', 'chart', 'rate', 'matric'],
              'Optimizer':['optimizer','optim', 'adam', 'SGD','RMSProp', 'ADMM', 'LAMB', 'SAGA', 'TTUR'],
              'Activation Function':['activation', 'relu', 'sigmoid', 'tanh', 'gelu', 'leaky', 'swish', 'mish', 'prelu', 'maxout','selu', 'softsign', '-glu-', '_glu_'],
              'Layer':['model','layer', 'norm', 'attention', 'module', 'net', 'cnn', 'rnn', 'gan', 'encoder', 'extractor', 'decoder', 'vgg', 'adversa', 'nn', 'core', 'fast', '-run-','train', 'run_', 'dpg', 'embedding', 'transformer', 'classifi','node', 'gaussian', 'block','input', 'output', 'mnist', 'word2vec', 'glove', 'large', 'small', 'predict', '_mae', 'algo', '_vae', 'vae', 'tensorflow', 'baseline'],
              }
fileTypes = {
    'Util': [],
    'Loss Function': [],
    'Optimizer': [],
    'Activation Function': [],
    'Layer': [],
    'Metric': [],
    'Others': [],
    'Integration': []
}

if __name__ == "__main__":
    count = 0
    for root, dirs, files in os.walk(""):
        for file in files:
            if file.endswith(".py"):
                if 'test' in file:
                    fileName = file.replace('.py','').lower()
                    flag = False
                    for key in firstPri.keys():
                        for item in firstPri[key]:
                            if item in fileName:
                                flag = True
                                fileTypes[key].append(fileName)
                                break
                        if flag:
                            break
                    if flag:
                        continue
                    for key in checkTypes.keys():
                        for item in checkTypes[key]:
                            if item in fileName:
                                flag = True
                                fileTypes[key].append(fileName)
                                break
                        if flag:
                            break
                    if not flag:
                        # check class name
                        try:
                            with open(os.path.join(root, file), "r") as source:
                                tree = ast.parse(source.read())
                            analyzer = GetClassNameAnalyser()
                            analyzer.visit(tree)
                            classes = analyzer.get_classes()
                            secondFlag = False
                            for key in checkTypes.keys():
                                for item in checkTypes[key]:
                                    for className in classes:
                                        if item in className:
                                            secondFlag = True
                                            fileTypes[key].append(fileName)
                                            break
                                    if secondFlag:
                                        break
                                if secondFlag:
                                    break
                            if not secondFlag:
                                # print(classes)
                                fileTypes['Others'].append(fileName)
                        except:
                            fileTypes['Others'].append(fileName)

                    # print(fileName)
                    count+=1

        # if count > 200:
        #     break
    count = 0


    for key in fileTypes.keys():
        with open(f'types/{key}.txt', 'w+') as f:
            for file in fileTypes[key]:
                f.write(f'{file}\n')