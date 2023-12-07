import sys
import PseudocodePy

file_path = sys.argv[1]

try:
    with open(file_path, 'r') as file:
        multiline_string = file.read()
        # Assuming you want to process the multiline string
        print(multiline_string)
except FileNotFoundError:
    print(f"Error: File not found at {file_path}")
except Exception as e:
    print(f"Error: {e}")

print("-------------------")

result = PseudocodePy.p(str(multiline_string))

#print(result)

print('latexpy_result\n' + result)