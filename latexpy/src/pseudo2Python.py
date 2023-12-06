# Python program to parse LaTeX formulas and produce Python/Prover9 expressions

# by Peter Jipsen 2023-4-6 distributed under LGPL 3 or later.
# Terms are read using Vaughn Pratt's top-down parsing algorithm.

# Modified by Jared Amaral, Jose Arellano, Nathan Nguyen, Alex Wunderli in May 2023 for usage in their Algorithm Analysis course project. 

# List of symbols handled by the parser (at this point)
# =====================================================
# \And \approx \backslash \bb \bigcap \bigcup \bot \cap \cc \cdot  
# \circ \Con \cup \equiv \exists \forall \ge \implies \in \le \ln \m 
# \mathbb \mathbf \mathcal \mid \Mod \models \ne \neg \ngeq \nleq \Not 
# \nvdash \oplus \Or \Pre \setminus \sim \subset \subseteq \supset \supseteq 
# \times \to \top \vdash \vee \vert \wedge + * / ^ _ ! = < > ( ) [ ] \{ \} | | $

# Greek letters and most other LaTeX symbols can be used as variable names.
# A LaTeX symbol named \abc... is translated to the Python variable _abc...

#!pip install provers
#from provers import *
import math, itertools, re, sys, subprocess
subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'latex2sympy2'])
from sympy import *
x, y, z, t, i, n, m = symbols('x y z t i n m') # x, y, z, t = symbols('x y z t') # init_session()
from latex2sympy2 import *
from IPython.display import Markdown, Latex

# The macros below are used to simplify the input that needs to be typed.
macros=r"""
\renewcommand{\And}{\ \text{and}\ }
\renewcommand{\Or}{\ \text{or}\ }
\renewcommand{\Not}{\text{not}\ }
\renewcommand{\m}{\mathbf}
\renewcommand{\bb}{\mathbb}
\renewcommand{\cc}{\mathcal}
\renewcommand{\s}{\text}
\renewcommand{\bsl}{\backslash}
\renewcommand{\sm}{{\sim}}
\renewcommand{\tup}[1]{(#1)}
\renewcommand{\Mod}{\text{Mod}}
\renewcommand{\Con}{\text{Con}}
\renewcommand{\Pre}{\text{Pre}}
\newcommand{\If}{\If}
\newcommand{\State}{\State}
\newcommand{\algb}{\begin{algorithmic}}
\newcommand{\alge}{\end{algorithmic}}
"""

# \renewcommand{\If}{\If}
# \renewcommand{\State}{\State}
display(Markdown("$"+macros+"$"))
RunningInCOLAB = 'google.colab' in str(get_ipython())
if not RunningInCOLAB: macros=""

p9options=[ # redeclare Prover9 syntax
    "redeclare(conjunction, and)",
    "redeclare(disjunction, or)",
    "redeclare(negation, not)",
    'redeclare(implication, "==>")',
    'redeclare(backward_implication, "<==")',
    'redeclare(equivalence, "<=>")',
    'redeclare(equality, "==")']

P9 = False
global exp_out
exp_out = []

def p9st(t):
  global P9
  P9=True;ps=str(t);P9=False
  return ps

# Prover 9 Function
def pr9(assume_list, goal_list, mace_seconds=2, prover_seconds=60, cardinality=None, params='', info=False):
    global prover9
    if type(cardinality) == int or cardinality == None:
        return prover9(assume_list, goal_list, mace_seconds, prover_seconds, cardinality, params=params, info=info, options=p9options)
    else:
        algs = [[], [1]]+[[] for i in range(2, cardinality[0]+1)]
        for i in range(2, cardinality[0]+1):
            algs[i] = prover9(assume_list, goal_list, mace_seconds, prover_seconds, i, params=params, info=info, options=p9options)
        print("Fine spectrum: ", [len(x) for x in algs[1:]])
        return algs

# Setting pi and e constants
from IPython.display import *
import math, itertools, re
_pi = sympy.pi
_e = math.e

# Integration Function
def integrate2(a, b):
    return str(integrate(a, b) + "+ C")

# Postfic check function
def is_postfix(t):
    return hasattr(t,'leftd') and len(t.a)==1

def w(t,i): # decide when to add parentheses during printing of terms
    subt = t.a[i] if len(t.a)>i else "index out of range"
    return str(subt) if subt.lbp < t.lbp or subt.a==[] or \
        (subt.sy==t.sy and subt.lbp==t.lbp) or \
        (not hasattr(subt,'leftd') or not hasattr(t,'leftd')) or \
        (is_postfix(subt) and is_postfix(t)) else "("+str(subt)+")"

# Similar to w function but modified for calculus functions
def w2(t,i):
  subt = t.a[i] if len(t.a)>i else "index out of range"
  return str(subt) if subt.lbp < t.lbp or subt.a==[] \
        or (not hasattr(subt,'leftd') and subt.lbp==1200) \
        else "("+str(subt)+")"

def w3(t,i): # always add parentheses
  subt = t.a[i] if len(t.a)>i else "index out of range"
  return "("+str(subt)+")"

# Creates arbitrary constant C (for integration) 
def letter(c): return 'a'<=c<='z' or 'A'<=c<='Z'
def alpha_numeric(c): return 'a'<=c<='z' or 'A'<=c<='Z' or '0'<=c<='9'

# Base Symbol Class
class symbol_base(object):
    a = []
    def __repr__(self): 
        if   len(self.a) == 0: return self.sy.replace("\\","_").replace("{","").replace("}","")
        elif len(self.a) == 2:
         return w(self,0)+" "+self.sy+" "+w(self,1)
        else:
         return self.sy+"("+",".join([w(self,j) for j in range(len(self.a))])+")"

# Symbol Function
def symbol(id, bp=1200): # identifier, binding power; LOWER binds stronger
    if id in symbol_table:
        s = symbol_table[id]    # look symbol up in table
        s.lbp = min(bp, s.lbp)  # update left binding power
    else:
        class s(symbol_base):   # create class for this symbol
            pass
        s.sy = id
        s.lbp = bp
        s.nulld = lambda self: self
        symbol_table[id] = s
    return s

def advance(id=None):
    global token
    if id and token.sy != id:
        raise SyntaxError("Expected "+id+" got "+token.sy)
    token = next()

def nulld(self): # null denotation
    expr = expression()
    advance(")")
    return expr

def nulldbr(self): # null denotation
    expr = expression()
    advance("}")
    return expr

#prefix2:
  # \frac d{dx}(\sin x)
  # ("\frac", "d","dx",("\sin","x"))

# Prefix2 is utilized for differentiation
def prefix2(id, bp=0): # parse n-ary prefix operations
  global token
  def nulld(self): # null denotation
    self.a = [expression(bp), expression(bp)]
    if self.a[0].sy=="d" and self.a[1].sy[0]=="d": 
      self.a.append(expression(bp))
    return self
  s = symbol(id, bp)
  s.nulld = nulld
  return s

# Prefix3 is utilized for integration, limits, and summation
def prefix3(id, bp=0, nargs=1): # parse prefix operator \int, \lim, \sum
  global token
  def nulld(self): # null denotation
    global token
    #print('token.sy',token.sy,'self.sy',self.sy)
    self.a = []
    if token.sy=="_":
      advance("_")
      self.a += [expression(300)]
      if token.sy=="^":
        advance("^")
        self.a += [expression(300)]
    self.a = ([expression(bp)] if nargs==1 else [expression(bp), expression(bp)])+self.a
    return self
  s = symbol(id, bp)
  s.nulld = nulld
  return s

# General prefix function for general mathematics functions
def prefix(id, bp=0): # parse n-ary prefix operations
    global token
    def nulld(self): # null denotation
        global token
        if token.sy not in ["(","[","{"] and self.sy not in ["\\forall","\\exists"]:
            #print('token.sy',token.sy,'self.sy',self.sy)
            self.a = [] if token.sy in [",",")","}",":","=","!="] else [expression(bp)]
            if self.sy=="|": advance("|")
            return self
        else:
            closedelim = ")" if token.sy=="(" else "]" if token.sy=="[" else "}"
            token = next()
            self.a = []
            if token.sy != ")":
                while 1:
                    self.a.append(expression())
                    if token.sy != ",":
                        break
                    advance(",")
            advance(closedelim)
            if closedelim=="}" and token.sy=="(": #make \cmd{v}(...) same as \cmd c(...)
              prefix(self.a[0].sy)
              token = next()
              self.a[0].a = []
              if token.sy != ")":
                while 1:
                    self.a[0].a.append(expression())
                    if token.sy != ",":
                        break
                    advance(",")
              advance(")")
            return self
    s = symbol(id, bp)
    s.nulld = nulld
    return s

# General prefix function for general mathematics functions
def prefixAlg(id, bp=0): # parse n-ary prefix operations
    global token
    right = False
    def leftd(self, left): # left denotation
        self.a = [left]
        self.a.append(expression(bp+(1 if right else 0)))
        return self
    def nulld(self): # null denotation
        global token
        if token.sy not in ["(","[","{"] and self.sy not in ["\\forall","\\exists"]:
            #print('token.sy',token.sy,'self.sy',self.sy)
            self.a = [] if token.sy in [",",")","}",":","=","!="] else [expression(bp)]
            if self.sy=="|": advance("|")
            return self
        else:
            closedelim = ")" if token.sy=="(" else "]" if token.sy=="[" else "}"
            token = next()
            self.a = []
            if token.sy != ")":
                while 1:
                    self.a.append(expression())
                    if token.sy != ",":
                        break
                    advance(",")
            advance(closedelim)
            if closedelim=="}" and token.sy=="(": #make \cmd{v}(...) same as \cmd c(...)
              prefix(self.a[0].sy)
              token = next()
              self.a[0].a = []
              if token.sy != ")":
                while 1:
                    self.a[0].a.append(expression())
                    if token.sy != ",":
                        break
                    advance(",")
              advance(")")
            return self
    s = symbol(id, bp)
    s.nulld = nulld
    s.leftd = leftd
    return s

# Determines infix
def infix(id, bp, right=False):
    def leftd(self, left): # left denotation
        self.a = [left]
        self.a.append(expression(bp+(1 if right else 0)))
        return self
    s = symbol(id, bp)
    s.leftd = leftd
    return s

# Determines whether expression is pre or infix
def preorinfix(id, bp, right=True): # used for minus
    def leftd(self, left): # left denotation
        self.a = [left]
        self.a.append(expression(bp+(1 if right else 0)))
        return self
    def nulld(self): # null denotation
        global token
        self.a = [expression(bp)]
        return self
    s = symbol(id, bp)
    s.leftd = leftd
    s.nulld = nulld
    return s

def plist(id, bp=0): #parse a parenthesized comma-separated list
    global token
    def nulld(self): # null denotation
        global token
        self.a = []
        if token.sy not in ["]","\\}"]:
            while True:
                self.a.append(expression())
                if token.sy != ",": break
                advance(",")
        advance()
        return self
    s = symbol(id, bp)
    s.nulld = nulld
    return s

# Postfix is utilized for postfix expressions
def postfix(id, bp):
    def leftd(self,left): # left denotation
        self.a = [left]
        return self
    s = symbol(id, bp)
    s.leftd = leftd
    return s

# Symbol table dictionary
symbol_table = {}

# The parsing rules  below decode a string of tokens into an abstract syntax tree with methods .sy 
# for symbol (a string) and .a for arguments.

# Intializes table of mathematical symbols, utilizes lamba calculus
def init_symbol_table():
    global symbol_table
    symbol_table = {}
    symbol("(").nulld = nulld
    symbol(")")
    symbol("{").nulld = nulldbr
    symbol("}")
    prefix("|").__repr__ = lambda x: "len("+str(x.a[0])+")" #interferes with p|q from Prover9
    plist("[").__repr__ = lambda x: "["+",".join([strorval(y) for y in x.a])+"]"
    plist("\\tup{").__repr__ = lambda x: "("+",".join([strorval(y) for y in x.a])+")"
    plist("\\{").__repr__ = lambda x: "frozenset(["+x.a[0].a[0].a[0].sy+" for "+str(x.a[0].a[0])+\
      " if "+str(x.a[0].a[1]).replace(" = "," == ")+"])"\
      if len(x.a)==1 and x.a[0].sy=="\\mid" and x.a[0].a[0].sy=="\\in"\
      else "frozenset(["+str(x.a[0].a[0])+" for "+str(x.a[0].a[1].a[0])+\
      " if "+str(x.a[0].a[1].a[1]).replace(" = "," == ")+"])"\
      if len(x.a)==1 and x.a[0].sy=="\\mid" and x.a[0].a[1].sy=="\\And" and x.a[0].a[1].a[0].sy=="\\in"\
      else "frozenset(["+str(x.a[0].a[0])+" for "+str(x.a[0].a[1])+"])"\
      if len(x.a)==1 and x.a[0].sy=="\\mid" and x.a[0].a[1].sy=="\\in"\
      else "frozenset(["+",".join([strorval(y) for y in x.a])+"])"\
      if len(x.a)<2 or x.a[1].sy!='\\dots' else "frozenset(range("+str(x.a[0])+","+str(x.a[2])+"+1))"
    symbol("]")
    symbol("\\}")
    symbol(",")
    postfix("!",300).__repr__ =       lambda x: "math.factorial("+str(x.a[0])+")"
    postfix("f",300).__repr__ =       lambda x: "f"+w3(x,0)
    postfix("'",300).__repr__ =       lambda x: str(x.a[0])+"'"
    prefix("\\ln",310).__repr__ =     lambda x: "math.log("+str(x.a[0])+")"
    prefix("\\sin",310).__repr__ =    lambda x: "sin("+str(x.a[0])+")"  # use math.sin if sympy is not loaded
    infix(":", 450).__repr__ =        lambda x: str(x.a[0])+": "+w3(x,1) # for f:A\to B
    infix("^", 300).__repr__ =        lambda x: "converse("+str(x.a[0])+")"\
      if len(x.a)>1 and str(x.a[1].sy)=='\\smallsmile' else "O("+str(x.a[0])+")"\
      if P9 and len(x.a)>0 and str(x.a[1])=="-1" else w2(x,0)+"\\wedge "+w2(x,1)\
      if P9 else w2(x,0)+"**"+w2(x,1)                                       # power
    infix("_", 300).__repr__ =        lambda x: str(x.a[0])+"["+w(x,1)+"]"  # sub
    infix(";", 303).__repr__ =        lambda x: "relcomposition("+w(x,0)+","+w(x,1)+")" # relation composition
    infix("\\circ", 303).__repr__ =   lambda x: "relcomposition("+w(x,1)+","+w(x,0)+")" # function composition
    infix("*", 311).__repr__ =        lambda x: w2(x,0)+"\\cdot "+w2(x,1)   # times
    infix("\\cdot", 311).__repr__ =   lambda x: w2(x,0)+"*"+w2(x,1)         # times
    infix("/", 312).__repr__ =        lambda x: w2(x,0)+"/"+w2(x,1)         # over
    infix("+", 313).__repr__ =        lambda x: w2(x,0)+" + "+w2(x,1)       # plus
    preorinfix("-",313).__repr__ =    lambda x: "-"+w(x,0) if len(x.a)==1 else str(x.a[0])+" - "+w(x,1) #negative or minus
    symbol("\\top").__repr__ =        lambda x: "T"
    symbol("\\bot").__repr__ =        lambda x: "0"
    infix("\\times", 322).__repr__ =  lambda x: "frozenset(itertools.product("+w(x,0)+","+w(x,1)+"))" #product
    infix("\\cap", 323).__repr__ =    lambda x: w(x,0)+" & "+w(x,1)         # intersection
    infix("\\cup", 324).__repr__ =    lambda x: w(x,0)+" | "+w(x,1)         # union
    infix("\\setminus", 325).__repr__=lambda x: w(x,0)+" - "+w(x,1)         # setminus
    infix("\\oplus", 326).__repr__ =  lambda x: w(x,0)+" ^ "+w(x,1)         # symmetric difference
    prefix("\\bigcap",350).__repr__ = lambda x: "intersection("+str(x.a[0])+")" # intersection of a set of sets
    prefix("\\bigcup",350).__repr__ = lambda x: "union("+str(x.a[0])+")"    # union of a set of sets
    prefix("\\mathcal{P}",350).__repr__=lambda x: "powerset("+str(x.a[0])+")" #powerset of a set
    prefix("\\cc{P}",350).__repr__=   lambda x: "powerset("+str(x.a[0])+")" # powerset of a set
    prefix("\\mathbf",350).__repr__ = lambda x: "_mathbf"+str(x.a[0].sy)    # algebra or structure or theory
    prefix("\\m",350).__repr__ =      lambda x: "_m"+str(x.a[0].sy)         # algebra or structure or theory
    prefix("\\mathbb",350).__repr__ = lambda x: "_mathbb"+str(x.a[0].sy)    # blackboard bold
    prefix("\\bb",350).__repr__ =     lambda x: "_bb"+str(x.a[0].sy)        # blackboard bold

    # Trigonometic Functions
    prefix("\\sin",310).__repr__ =    lambda x: "sin("+str(x.a[0])+")"
    prefix("\\cos",310).__repr__ =    lambda x: "cos("+str(x.a[0])+")"
    prefix("\\tan",310).__repr__ =    lambda x: "tan("+str(x.a[0])+")"
    prefix("\\arcsin",310).__repr__ = lambda x: "asin("+str(x.a[0])+")"
    prefix("\\arccos",310).__repr__ = lambda x: "acos("+str(x.a[0])+")"
    prefix("\\arctan",310).__repr__ = lambda x: "atan("+str(x.a[0])+")"

    # Differentation
    prefix2("\\frac",310).__repr__ =  lambda x: "latex(diff("+str(x.a[2])+","+x.a[1].sy[1:]+"))" if x.a[0].sy=="d" and x.a[1].sy[0]=="d"\
      else "sympy.simplify("+ str(x.a[0]) + "/" + str(x.a[1]) + ")"
    # Integration
    prefix3("\\int",313,2).__repr__ =   lambda x: "addplusC(integrate("+str(x.a[0])+","+x.a[1].sy[1:]+"))" if len(x.a)<=2\
      else "latex(integrate("+str(x.a[0])+",("+x.a[1].sy[1:]+","+w(x,2)+","+w(x,3)+")))"
    # Limits
    prefix3("\\lim",313).__repr__ =   lambda x: "latex(limit("+str(x.a[0])+", "+ str(x.a[1].a[0])+", "+str(x.a[1].a[1])+"))" 
    # Summation
    prefix3("\\sum",313).__repr__ =   lambda x: "latex(summation("+str(x.a[0])+", ("+str(x.a[0])+","+str(x.a[1].a[1])+","+str(x.a[2])+")))"

    # Psuedocode w/ {algpseudocodex}
    prefixAlg("\\algb",500).__repr__ = lambda x: (x.a[0].sy)
    prefixAlg("\\alge",500).__repr__ = lambda x: (x.a[0].sy)
    
    prefixAlg("\\If",310).__repr__ = lambda x: "if " + str(x.a[0]) + ":"
    prefixAlg("\\ElsIf",310).__repr__ = lambda x: "elif " + str(x.a[0]) + ":"
    prefix("\\Else",310).__repr__ = lambda x: "else: "
    prefixAlg("\\State",360).__repr__ = lambda x: "\t" + str(x.a[0])
    prefixAlg("\\Output",360).__repr__ = lambda x: "print(" + str(x.a[0]) + ")"
    prefixAlg("\\Return",360).__repr__ = lambda x: "return " + str(x.a[0])
    prefixAlg("\\While",310).__repr__ = lambda x: "while " + str(x.a[0]) + ":"
    prefixAlg("\\For",310).__repr__ = lambda x: "for " + str(x.a[0]) + ":"
    infix("\\gets",345).__repr__ = lambda x: w2(x,0) + " = "+ w2(x,1)
    prefix2("\\Function",310).__repr__ = lambda x: "def " + str(x.a[0]) + "(" + str(x.a[1]) + "):"
    
    
    
    #########################
    infix("\\vert", 365).__repr__ =   lambda x: w(x,1)+"%"+w(x,0)+"==0"     # divides
    infix("\\in", 370).__repr__ =     lambda x: w(x,0)+" in "+w(x,1)        # element of
    infix("\\subseteq", 370).__repr__=lambda x: w(x,0)+" <= "+w(x,1)        # subset of
    infix("\\subset", 370).__repr__ = lambda x: w(x,0)+" < "+w(x,1)         # proper subset of
    infix("\\supseteq", 370).__repr__=lambda x: w(x,1)+" <= "+w(x,0)        # supset of
    infix("\\supset", 370).__repr__ = lambda x: w(x,1)+" < "+w(x,0)         # proper subset of
    infix("=", 405).__repr__ =        lambda x: w(x,0)+" == "+w(x,1)          # assignment or identity
    infix("==", 405).__repr__ =       lambda x: w(x,0)+" = "+w(x,1)         # assignment or identity
    infix("\\ne", 405).__repr__ =     lambda x: w(x,0)+" != "+w(x,1)        # nonequality
    infix("!=", 405).__repr__ =       lambda x: w(x,0)+"\\ne "+w(x,1)       # nonequality
    infix("\\le", 405).__repr__ =     lambda x: w2(x,0)+" <= "+str(x.a[1])  # less or equal
    infix("<=", 405).__repr__ =       lambda x: w2(x,0)+"\\le "+str(x.a[1]) # less or equal in Python
    infix("\\ge", 405).__repr__ =     lambda x: w2(x,0)+">="+str(x.a[1])    # greater or equal
    infix("<", 405).__repr__ =        lambda x: w2(x,0)+" < "+str(x.a[1])   # less than
    infix(">", 405).__repr__ =        lambda x: w2(x,0)+" > "+str(x.a[1])   # greater than
    infix("\\nleq", 405).__repr__ =   lambda x: "not("+w2(x,0)+"<="+str(x.a[1])+")" # not less or equal
    infix("\\ngeq", 405).__repr__ =   lambda x: "not("+w2(x,1)+"<="+str(x.a[0])+")" # not greater or equal
#    infix("\\approx", 405).__repr__ = lambda x: w2(x,0)+" Aprx "+str(x.a[1]) # approximately
#    infix("\\equiv", 405).__repr__ =  lambda x: w2(x,0)+" Eq "+str(x.a[1])   # equivalence relation
    prefix("\\neg",450).__repr__=     lambda x: "not "+w(x,0)               # negation symbol
    prefix("\\Not",450).__repr__=     lambda x: "not "+w3(x,0)              # logical negation
    prefix("\\forall",450).__repr__ = lambda x: "all("+str(x.a[-1]).replace(" = "," == ")+\
            "".join(" for "+str(x) for x in x.a[:-1])+")"                   # universal quantifier
    prefix("\\exists",450).__repr__ = lambda x: "any("+str(x.a[-1]).replace(" = "," == ")+\
            "".join(" for "+str(x) for x in x.a[:-1])+")"                   # existential quantifier
    infix("\\Or", 503).__repr__=      lambda x: w(x,0)+(" or ")+w(x,1)      # disjunction
    infix("\\And", 503).__repr__=     lambda x: w(x,0)+(" and ")+w(x,1)     # conjunction
    infix("\\implies", 504).__repr__ =lambda x: "not "+w3(x,0)+" or "+w3(x,1) # implication
    infix("\\iff", 505).__repr__ =    lambda x: w3(x,0)+" <=> "+w3(x,1)     # if and only if
    infix("\\mid", 550).__repr__ =    lambda x: str(x.a[0])+" mid "+str(x.a[1]) # such that
    prefix("primefactors",310).__repr__ = lambda x: "latex(primefactors("+str(x.a[0])+"))" # factor an integer
    prefix("ls",310).__repr__ =       lambda x: "latex2latex("+str(x.a[0])+")" # use the latex2sympy2 parser and sympy to calculate
    prefix("factor",310).__repr__ =   lambda x: "latex(factor("+str(x.a[0])+("" if len(x.a)==1 else ","+str(x.a[1]))+"))" # factor a polynomial
    prefix("solve",310).__repr__ =    lambda x: "latex(solve("+(str(x.a[0].a[0])+"-("+str(x.a[0].a[1])+")" if x.a[0].sy=="=" else str(x.a[0]))+\
      ("" if len(x.a)==1 else ","+str(x.a[1]))+"))" # solve a (list of) equations
    prefix("show",310).__repr__ =     lambda x: "show("+str(x.a[0])+(")" if len(x.a)==1 else ","+str(x.a[1])+")") # show poset or (semi)lattice
    postfix("?", 600).__repr__ =      lambda x: str(x.a[0])+"?"             # calculate value and show it
    symbol("(end)")

init_symbol_table()

# tokenize(st):
  # \frac{d}{dx}

# Determines tokens from an expression
def tokenize(st):
    i = 0
    # loop the length of the string
    while i<len(st):
        tok = st[i]
        j = i+1
        # \lim_
        if j<len(st) and (st[j]=="{" or st[j]=="}") and tok=='\\':
          j += 1
          tok = st[i:j]
          symbol(tok)
        elif letter(tok) or tok=='\\': #read consecutive letters or digits
            while j<len(st) and letter(st[j]): j+=1 # grabs the symbol name i.e. \If
            tok = st[i:j]
            if tok=="\\" and j<len(st) and st[j]==" ": j+=1
            if tok=="\\text": j = st.find("}",j)+1 if st[j]=="{" else j #extend token to include {...} part
            if tok=="\\s": j = st.find("}",j)+1 if st[j]=="{" else j
            if tok=="\\mathcal": j = st.find("}",j)+1 if st[j]=="{" else j
            if tok=="\\cc": j = st.find("}",j)+1 if st[j]=="{" else j
            if tok=="\\tup": j += 1 if st[j]=="{" else j
            tok = st[i:j]
            symbol(tok)
            if j<len(st) and st[j]=='(': prefix(tok, 1200) #promote tok to function
        elif "0"<=tok<="9": #read (decimal) number in scientific notation
            while j<len(st) and ('0'<=st[j]<='9' or st[j]=='.'):# in ['.','e','E','-']):
                j+=1
            tok = st[i:j]
            symbol(tok)
        elif tok =="-" and st[j]=="-": pass
        elif tok not in " '(,)[]{}\\|\n": #read operator string
            while j<len(st) and not alpha_numeric(st[j]) and \
                  st[j] not in " '(,)[]{}\\\n": j+=1
            tok = st[i:j]
            if tok not in symbol_table: symbol(tok)
        i = j
        if tok not in [' ','\\newline','\\ ','\\quad','\\qquad','\n']: #skip these tokens
            symb = symbol_table[tok]
            if not symb: #symb = symbol(tok)
                raise SyntaxError("Unknown operator")
#            print tok, 'ST', symbol_table.keys()
            yield symb()
    symb = symbol_table["(end)"]
    yield symb()


def expression(rbp=1200): # read an expression from token stream
    global token
    t = token
    try:
      token = next() # {
      #print(token.sy)
    except:
      token = ttt
    left = t.nulld()
    while rbp > token.lbp:
        t = token
        token = next()
        left = t.leftd(left)
    return left

# parse(str):
  # \sin{}

# Parser of expressions
def parse(str):
    global token, next
    next = tokenize(str).__next__ # next is an iterator that tokenizes the next token
    token = next()
    # by this point the entire expression should be tokenized???
    return expression() # expression() is called 'next' times

ttt=parse(".")

def ast(t):
    if len(t.a)==0: return '"'+t.sy+'"'
    return '("'+t.sy+'",'+", ".join(ast(s) for s in t.a)+")"

# Convert (a subset of) LaTeX input to valid Python(sympy) code
# Display LaTeX with calculated answers inserted
# Return LaTeX and/or Python code as a string

#nextmath(st, index):
  # checks if the string is enclosed in '$' or '$$'

  # st - string input from user
  # index - st starting index

def nextmath(st,i): #find next j,k>=i such that st[j:k] is inline or display math
  # find first occurence of '$'
  j = st.find("$",i)
  # if '$' is not found, return j=-1,k=0,d=false
  if j==-1: return (-1,0,False)
  # check if the math string is just "$$"
  if st[j+1]=="$":
    # set k equal to the starting index of "$$"
    k = st.find("$$",j+2)
    # j = index after the double "$$"
    # k = starting index of "$$"
    # d = True (found "$$")
    return (j+2,k,True)
  else:
    # j = index after first '$'
    # k = index of second '$' (if there is one)
    # d = False (did not find "$$")
    return (j+1,st.find("$",j+1),False)


# convert st (a LaTeX string) to Python/Prover9 code and evaluate it
# creates syntax tree and decides the hierarchy of functions to use first
# process(st, info, nocolor):
  # st - string input
  # info - show ast (1 or 0)
def process(st, info=False, nocolor=False):
  
  # tokenizes and grabs the value from the token
  t = parse(st)
  
  if str(t) in exp_out or str(t) == '(end)' or '_' in str(t) or str(t) == '\t(end)': 
    pass
  else: 
    exp_out.append(str(t))
    
  
  if info:
    print("Abstract syntax tree:", ast(t))
    print("Expression:", t)
    
  # print("expression out:")
  # print(exp_out[:])
    
  if t.sy!="?": # check if t is not asking to be evaluated
    if t.sy!="=": # check if t is an assignment
      if t.sy=="show": # check if t is a show command
        try:
          exec(str(t),globals())
        except:
          if info: print("no result")
          return macros+st
        return ("" if nocolor else "\color{green}")+macros+st
      return macros+st
    ss = str(t).replace("==","=",1)
    try:
      exec(ss,globals())
    except:
      if info: print("no result")
      return macros+st
    print(macros)
    print(st)
    return ("" if nocolor else "\color{green}")+macros+st
  tt = t.a[0]
  st = st.replace("?","")
  if tt.sy=="=":
    ss = str(tt).replace("==","=",1)
    try:
      exec(ss,globals())
    except:
      if info: print("no result")
      return macros+st
    return ("" if nocolor else "\color{green}")+macros+st+("" if nocolor else "\color{deepskyblue}")+" = "+pyla(eval(str(tt.a[0])))
  try:
    val=eval(str(tt))
    if info: print("Value:", val)
    ltx = val if str(tt)[:5] in ["latex","addpl"] else pyla(val)
  except:
    return ("" if nocolor else "\color{green}")+macros+st
  return ("" if nocolor else "\color{green}")+macros+st+("" if nocolor else "\color{deepskyblue}")+" = "+ltx

  # Main function to translate valid LaTeX/Markdown string st
def l(st, info=False, output=False, nocolor=False):
  # assuming this is used to get r""" ?
  global macros
  st = re.sub("\n%.*?\n","\n",st) #remove LaTeX comments
  st = re.sub("%.*?\n","\n",st) #remove LaTeX comments
  # look for '$' in the string and update indices (j,k)
  (j,k,d) = nextmath(st,0)
  # out = the first '$'
  out = st[0:j]
  # while there are two '$'
  while j!=-1 and k!=-1:
    # process the math equation in latex
    out += process(st[j:k],info,nocolor)
    out = removeDollar(out)
    p = k
    (j,k,d) = nextmath(st,k+(2 if d else 1))
    out += st[p:j] if j!=-1 else st[p:]
    #print("out: " + out)
  #display(Markdown(out))
  if output: print(out)
  
def p(st, info=False, output=False, nocolor=False):
  # Save string formatted string for markdown display
  st_mark = format_for_markdown(st)
  
  # Split the string into lines
  lines = st.strip().split('\n')
  
  # Add dollar signs to the beginning and end of each line
  formatted_lines = ['$' + line.strip() + '$' for line in lines]
  
  # Join the formatted lines back into a single string
  st = '\n'.join(formatted_lines)
  l(st, info, output, nocolor)
  
  
  # ---------------URGENT--------------------
  # Grab the entire expression and try to create an ast!!!
  # -------------------------------------------
  
  print("expression out:")
  print(exp_out[:])
  
  # Display input in markdown
  display(Markdown("### LaTeX Input"))
  display(Markdown(st_mark))
  
  str_out = expressions_to_str(exp_out)
  md_str_out = "```python\n" + str_out + "\n```"
  
  display(Markdown("### Python Output"))
  display(Markdown(md_str_out))
  
  try:
    # Execute the generated code using eval()
    display(Markdown("### Result"))
    eval(compile(str_out, '<string>', 'exec'))
  except Exception as e:
    print(f"An error occurred: {e}")
    
  # clear exp_out list
  exp_out.clear()
    
  

def removeDollar(st):
  # Remove dollar signs from the beginning and end of each line
  lines = st.strip().split('\n')
  formatted_lines = [line.strip('$').strip() for line in lines]

  # Join the formatted lines back into a single string
  st = '\n'.join(formatted_lines)
  return st

def format_for_markdown(st):
  # Create a code block using triple backticks
  st = "```latex\n" + st + "\n```"
  
  # return formatted string
  return st
  
def expressions_to_str(exp_list):
  # Initialize an empty code string
  code = ""
  
  # Iterate through the expressions and build the code
  for expr in exp_list:
    if expr == '(end)':
        code += '\n'
    elif expr[0] == '_':
        code += '    pass\n'
    else:
        code += expr + '\n'
        
  return code
    
  
prvrs="Model" in dir() # check if provers module is loaded