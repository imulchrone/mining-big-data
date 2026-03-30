# Ian Mulchrone
# Mining Big Data
# Assignment 5

import sys

def run_length_encoding(input_str) -> str:
    output_str = ''
    count = 1
    if len(input_str) == 1: #handles strings with one character
        output_str += f"{input_str[0]},{count};"
        return output_str
    else:
        for char in range(1,len(input_str)):
            current_char = input_str[char]
            if input_str[char-1] == current_char:
                count += 1
            else:
                count = 1

            if char == 1 and count == 1: #handles strings when first character count = 1
                output_str += f"{input_str[char-1]},{count};"

            if char == (len(input_str)-1):
                output_str += f"{current_char},{count}"
                return output_str
            elif input_str[char+1] != current_char:
                output_str += f"{current_char},{count};"
            

def main():
    input_str = sys.stdin.read().strip().strip('"')
    print(run_length_encoding(input_str))

if __name__ == '__main__':
    main()