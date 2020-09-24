
import sys # used to take arguments from the command line
import pydot # used to draw the Abstract Syntaz Tree

def readIn(fileName):
    variables = []
    constants = []
    predicates = []
    equality = []
    connectives = []
    quantifiers = []
    formula = ''
    inputFile = open(fileName,'r')
    lines = inputFile.readlines()
    i = 0
    while i < len(lines):
        currentLine = lines[i]
        # use lookahead to check for sets or formula split over two lines or more, check if next line contains colon
        if i + 1 < len(lines) and ':' not in lines[i+1]:
            currentLine = currentLine[:-1] + lines[i+1] # [:-1] to remove line break '\n' in middle of definition
            i += 1
        a = currentLine[:-1].split(' ')
        if a[0] == 'variables:':
            for x in range(1,len(a)):
                variables.append(a[x])
        elif a[0] == 'constants:':
            for x in range(1,len(a)):
                constants.append(a[x])
        elif a[0] == 'predicates:':
            for x in range(1,len(a)):
                predicates.append(a[x])
        elif a[0] == 'equality:':
            for x in range(1,len(a)):
                equality.append(a[x])
            if len(equality) != 1:
                error('you must have 1 equality symbol, you have {}'.format(len(equality)))
        elif a[0] == 'connectives:':
            for x in range(1,len(a)):
                connectives.append(a[x])
            if len(connectives) != 5:
                error('you must have 5 connective symbols, you have {}'.format(len(connectives)))
        elif a[0] == 'quantifiers:':
            for x in range(1,len(a)):
                quantifiers.append(a[x])
            if len(quantifiers) != 2:
                error('you must have 2 quantifier symbols, you have {}'.format(len(quantifiers)))
        elif a[0] == 'formula:':
            formula += currentLine[9:]
            if formula[-1] == '\n':
                formula = formula[:-1] # remove line break at end if there is one
        else:
            error('unkown input from file')
        i += 1
    return variables, constants, predicates, equality, connectives, quantifiers, formula

def grammar():
    outFile = open('grammar.txt'.format(fileName),'w')
    if len(equality) != 1:
        error('you must have 1 equality symbol')
    try:
        outFile.write('equality -> {}\n'.format(equality[0])) # set order and number, 1
    except:
        error('invalid equality definition')
    if len(connectives) != 5:
        error('you must have 5 connective symbols')
    try:
        outFile.write('connective -> {} | {} | {} | {}\n'.format(connectives[0],connectives[1],connectives[2],connectives[3])) # set order and number, 4
        outFile.write('not -> {}\n'.format(connectives[4])) # set order and number, 1
    except:
        error('invalid connectives definition')
    if len(quantifiers) != 2:
        error('you must have 2 quantifier symbols')
    try:
        outFile.write('quantifier -> {} | {}\n'.format(quantifiers[0],quantifiers[1])) # set order and number, 2
    except:
        error('invalid quantifiers definition')
    
    if len(variables) != 0:
        out = 'variable -> {}'.format(variables[0])
        for i in range(1,len(variables)):
            out += ' | {}'.format(variables[i])
        outFile.write(out + '\n')
    
    if len(constants) != 0:
        out = 'constant -> {}'.format(constants[0])
        for i in range(1,len(constants)):
            out += ' | {}'.format(constants[i])
        outFile.write(out + '\n')
    
    if len(predicates) != 0:
        out = 'predicate -> {}'.format(predicates[0][:-3])
        for i in range(1,len(predicates)):
            out += ' | {}'.format(predicates[i][:-3])
        outFile.write(out + '\n')
    
    variableRules = []
    if len(variables) != 0:
        variableRules.append('variable')
        variableRules.append('variable,variables')
        outFile.write('variables -> variable | variable,variables\n')
    
    atomRules = []
    if len(constants) != 0 and len(variables) != 0:
        atomRules.append('constant')
        atomRules.append('variable')
        outFile.write('atom -> constant | variable\n')
    elif len(constants) != 0:
        atomRules.append('constant')
        outFile.write('atom -> constant\n')
    elif len(variables) != 0:
        atomRules.append('variable')
        outFile.write('atom -> variable\n')
    
    formulaRules = ['(formula connective formula)', 'not formula']
    out = 'formula -> (formula connective formula) | not formula' # error check
    if len(predicates) != 0: # error check here for predicates definied but not variables
        formulaRules.append('predicate(variables)')
        out += ' | predicate(variables)'
    if len(constants) != 0 or len(variables) != 0:
        formulaRules.append('(atom equality atom)')
        out += ' | (atom equality atom)'
    if len(variables) != 0:
        formulaRules.append('quantifier variable formula')
        out += ' | quantifier variable formula'
    outFile.write(out + '\n')
    
    out = 'terminals: ( ) ,'
    for i in variables:
        out += ' ' + i
    for i in constants:
        out += ' ' + i
    outFile.write(out + '\n')
    out = 'non-terminals:'
    for i in equality:
        out += ' ' + i
    for i in connectives:
        out += ' ' + i
    for i in quantifiers:
        out += ' ' + i
    for i in predicates:
        out += ' ' + i[:-3]
    outFile.write(out + '\n')

    return variableRules, atomRules, formulaRules

def parse():
    predicateWords = []
    for x in predicates:
        predicateWords.append(x[:-3])
    elements = formula.replace(',',' , ').replace('(',' ( ').replace(')',' ) ')
    elements = elements.split(' ')
    i = 0
    while i < len(elements): # remove all '' from elements array
        if elements[i] == '':
            elements = elements[:i] + elements[i+1:]
            i -= 1
        i += 1
    i = 0
    parsed = ''
    while i < len(elements):
        if elements[i] != ' ':
            parsed += ' ' + elements[i] + ' '
        else:
            parsed += ' '
        i += 1
    return parsed, predicateWords

def tree(root, parsed): # recursive descent
    global graph
    global x
    p = parsed.split(' ')
    i = 0
    while i < len(p): # remove all '' from elements array
        if p[i] == '':
            p = p[:i] + p[i+1:]
            i -= 1
        i += 1
    if len(p) == 0:
        error('this is an invalid formula')
    if p[0] == '(' and p[-1] == ')' and p.count('(') == p.count(')'):
        if p.count('(') == 1: # equality
            if atomRules == []:
                error('you cannot use an equality when there are no variables or constants defined')
            if p[2] not in equality:
                error('there should be an equality here instead of {}'.format(p[2]))
            addNode(equality[0],root)
            root = pydot.Node(str(x))
            x += 1
            if p[1] not in variables and p[1] not in constants:
                error('an equality can only compare variables and constants')
            addNode(p[1],root)
            x += 1
            if p[3] not in variables and p[3] not in constants:
                error('an equality can only compare variables and constants')
            addNode(p[3],root)
            x += 1
        else: # connective
            stack = []
            i = 1
            while stack != [] or p[i] not in connectives[:4]:
                if p[i] == '(':
                    stack.append('(')
                elif p[i] == ')':
                    if stack == []:
                        error('unnecessary brackets here: {}'.format(parsed))
                    stack.pop(0)
                i += 1
            addNode(p[i],root)
            root = pydot.Node(str(x))
            x += 1
            parsed = ''
            for j in range(1,i):
                parsed += p[j] + ' '
            tree(root, parsed)
            parsed = ''
            for j in range(i+1,len(p)-1):
                parsed += p[j] + ' '
            tree(root, parsed)
    elif p[0] == connectives[4]: # not
        addNode(connectives[4],root)
        root = pydot.Node(str(x))
        x += 1
        parsed = ''
        for j in range(1,i):
            parsed += p[j] + ' '
        tree(root, parsed)
    elif p[0] in predicateWords and p[1] == '(': # predicate
        arity = predicates[predicateWords.index(p[0])]
        arity = arity[len(p[0])+1:-1]
        addNode(p[0],root)
        root = pydot.Node(str(x))
        x += 1
        number = 0
        for j in range(2,len(p)-1,2):
            number += 1
            addNode(p[j],root)
            x += 1
        if number != int(arity):
            error('you gave {} arguments to the predicate {}, when it should take {} arguments'.format(number,p[0],format(arity)))
    elif p[0] in quantifiers and p[1] in variables: # quantifier
        addNode(p[0],root)
        root = pydot.Node(str(x))
        x += 1
        addNode(p[1],root)
        root = pydot.Node(str(x))
        x += 1
        parsed = ''
        for j in range(2,i):
            parsed += p[j] + ' '
        tree(root, parsed)
    elif p[0] in quantifiers:
        error('a quantifier should always be followed by a variable')
    elif p[1] in quantifiers:
        error('quantifiers cannot be used in this way')
    elif p[0] in variables or p[1] in variables:
        error('variables cannot be used in this way')
    else:
        error('no production rule for this grammar fits')
    graph.write_png('AST.png')

def addNode(name,root):
    global graphEmpty
    graph.add_node(pydot.Node(str(x),label=repr(name)[1:-1])) # repr() enables printing of \l etc, [1:-1] gets rid of quotes
    if not graphEmpty:
        graph.add_edge(pydot.Edge(root,str(x)))
    graphEmpty = False

def error(message):
    log = open('parser.log','a')
    log.write('error: {}\n'.format(message))
    log.close()
    raise SystemExit

if __name__ == '__main__':
    if len(sys.argv) == 2:
        fileName = sys.argv[1]
    else:
        fileName = input('enter the input file name > ').strip()
    try:
        variables, constants, predicates, equality, connectives, quantifiers, formula = readIn(fileName)
    except:
        error('problem reading in the file')
    try:
        variableRules, atomRules, formulaRules = grammar()
    except:
        error('problem generating the grammar')
    log = open('parser.log','a')
    log.write('success: correct input file format\n')
    log.close()
    try:
        parsed, predicateWords = parse()
    except:
        error('problem parsing the formula')
    graph = pydot.Dot(graph_type='graph')
    graphEmpty = True
    root = pydot.Node('ROOT', label='formula')
    x = 0
    try:
        tree(root, parsed)
    except:
        error('invalid formula')
    log = open('parser.log','a')
    log.write('success: valid formula\n')
    log.close()
