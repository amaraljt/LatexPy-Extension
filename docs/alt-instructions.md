# LaTeXPy Setup Instructions
It is recommended to use this code in a Colab Jupyter notebook freely available at 
https://colab.research.google.com (use a free gmail account to login to Colab).

**Step 1:** Click on the link above, and start a new Colab notebook (use **File->New notebook** on the webpage menu, **not** on your computer menu).

**Step 2:** Copy the following lines into the first notebook cell and click the red start button to install LaTeXPy. This takes a few seconds.
```
!rm -rf LaTeXPy #remove any previous version
!git clone https://github.com/amaraljt/LaTeXPy.git
execfile("/content/LaTeXPy/prototype/PseudocodePy.py")
```
**Step 3:** Copy some of the examples below to see how to do various calculations using the LaTeX syntax that is valid with this script.

The main function of the code is called `p(...)` and takes a LaTeX **r"""raw string"""** as input. (A **rawstring** in Python starts with r" and in such strings the backslash is an ordinary character. The triple-quotes """ are used for strings that extend over several lines. If something doesn't work it may help to add a second input in the form `l(rawstring, 1)` then some diagnostic output is printed as well.)

Below are some example of what is covered (can be copy-pasted as input ).

# Examples

Refer to the [algpseudocodex](https://ctan.math.washington.edu/tex-archive/macros/latex/contrib/algpseudocodex/algpseudocodex.pdf) package documentation for additional typesetting.

## If-Else Statement
```
p(r"""
  \algb
    $a \gets 1$
    $b \gets 2$
    $c \gets 3$
    \If{a = b}
      \State \Output c
    \ElsIf{a > b}
      \State \Output a
    \Else
      \State \Output b
    \EndIf
  \alge
  """)
```

## While Loop
```
p(r"""
  \algb
    $i \gets 3$
    \While{i > 0}
      \State \Output i
      \State $x \gets x - 1$
    \EndWhile
  \alge
  """)
```
## For Loop (in development)
```
p(r"""
  \algb
    $i \gets 1$
    \For{i < 5}
      \State x \gets x \cdot 2
      \State $i \gets i + 1$
    \EndFor
    \State \Output x
  \alge
  """)
```
## Functions
```
p(r"""
  \algb
    \Function{addOne}{n}
      \State \Return n + 1
    \EndFunction
    \Output addOne(9)
  \alge
  """)
```
