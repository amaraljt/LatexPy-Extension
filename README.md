# LatexPy

## Contributors
- Jared Amaral: Published LaTeXPy to the VSCode Extension Marketplace. Implemented the functionality for parsing pseudocode in LaTeX. Added capabilities for parsing trig functions, limits, summations and integrations.
- Alex Haberman
- Maverick Wadman

## Motivation
Latex is utilized in mathematics, physics, economics, and more as the leading text formatting language for typesetting mathematics. The interest for language lies mostly for those who wish to type mathematics in a formal, simple and clean method, allowing others to easily see documents related to math easily and clearly. Current versions of Latex, however, cannot perform operations within text, which would a useful function for calculating mathematical expressions while typsetting instead of going onto an external site. Our project extends Dr. Peter Jipsen's project and current work with the LatexPy program, and includes functionality seen in Calculus, such as derivatives, summations, integrals, limits, and trigometric functions.

The aim of this project is to use LaTeX as a high-level mathematical calculator and pseudocode syntax that can be used in undergraduate education by students who know or learn some basic LaTeX, but they should not need to know any Python.

LaTeXPy can parse LaTeX math and pseudocode expressions and (attempts to) translate them to valid Python code. If the math expression is an assignment, the value of the right hand side is assigned to a Python variable with a similar name and can be used in subsequent LaTeX expressions.

## Setup Instructions
Note: If the extension does not work, you can follow [these](https://github.com/amaraljt/LatexPy-Extension/blob/main/docs/alt-instructions.md) instructions for an alternate way to try out LaTeXPy

1. Open VSCode and go to the Extensions tab
2. Search for 'LatexPy' and install
3. Open a file and type the input in LaTeX
4. Highlight a section to be parsed, if not, the entire document will be parsed
5. Do ``Ctrl+Shift+P`` to open the Command Palette and search for the command 'Pseudocode to Python' and hit enter
6. LaTeX input will be parsed and printed out on at the bottom of the file

![](https://imgur.com/a/Md9GjdX)

### Videos
[General Overview](https://youtu.be/e984FVpi2Lk) \
[Technical Overview](https://www.youtube.com/watch?v=KRNCYhavNjk)

## Future Work
- Add more mathematical and pseudocode parsing capabilities
- Improve the extension UI for more user-friendly interactions
