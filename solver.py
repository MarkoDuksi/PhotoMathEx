#!/usr/bin/env python
# coding: utf-8

import re
import operator


operators = {
    '+': operator.add,
    '-': operator.add,    # this is not a mistake
    '*': operator.mul,
    '/': operator.truediv,
}

op_precedences = [
    # extracts content between innermost parentheses
    r'\(([^()]+)\)',
    # extracts higher order operator (* or /) and its adjoining operands
    r'(-?\d+(?:\.\d+)?)\s*([*/])\s*(-)?\s*(\d+(?:\.\d+)?)',
    # extracts lower order operator (+ or -) and its adjoining operands
    r'(-?\d+(?:\.\d+)?)\s*([+-])\s*(-)?\s*(\d+(?:\.\d+)?)',
]


def operate(match):
    # evaluating parenthesized expressions if present
    if len(match.groups()) == 1:
        subresult = evaluate(match.group(1), noparentheses=True)
        return str(subresult)

    # after exhausting all parenthesized subexpressions
    left, right = match.group(1, 4)
    operator = operators[match.group(2)]

    # the two-signs construct allows for more flexible expressions
    sign1 = match.group(2)
    if sign1 == '-':
        sign1 = -1
    else:
        sign1 = 1
    sign2 = match.group(3)
    if sign2 == '-':
        sign2 = -1
    else:
        sign2 = 1

    result = operator(float(left), sign1 * sign2 * float(right))
    if result == round(result):
        result = int(result)

    return str(result)


def evaluate(expression, noparentheses=False):
    # colapse even number of consecutive negative signs
    reduced = re.sub(r'(?:--)+', ' ', expression)

    # evaluate in order of operator precedences
    noparentheses = int(noparentheses)
    for order in range(noparentheses, 3):
        # initial update is None
        updated = None
        while True:
            updated = re.sub(op_precedences[order], operate, reduced, count=noparentheses)
            if (updated == reduced):    # if done with this level of operator precedence
                break    # proceed to a lower level
            reduced = updated    # otherwise repeat

    # if the result is a whole number, cast it to int
    result = float(reduced)
    if result == round(result):
        result = int(result)

    return result


# helper func for `validate`
def check_parentheses(expression):
    """Check parentheses for missmatch

    Receive a candidate expression as a string and return True if all
    parentheses are properly closed. Nesting is allowed. If an error is
    detected, return False. If no parentheses are present, return True.
    """

    if re.search(r'\(\s*\)', expression):
        return False

    parentheses = re.findall(r'[()]', expression)

    count = 0
    counter = {
        '(': 1,
        ')': -1
    }

    for parenthesis in parentheses:
        count += counter[parenthesis]
        if count < 0:    # if before any position there are more ")" than "("
            return False
    if count:
        return False     # if by the end there are more "(" than ")"
    return True          # if by the end the `count` stays or returns to zero


def validate(expression):
    """Validator/reformatter for expressions

    Receive a candidate expression as a string of space-separated
    characters. Valid characters are all of: 0123456789.+-*/().
    Basic checking is performed as well as reformatting. If valid,
    return a reformatted expression as a string, otherwise return
    None.
    """

    # check parentheses for missmatch
    if not check_parentheses(expression):
        return None

    # redistribute spaces around negation sign
    processed = re.sub(r'\(\s*-\s+([\d\(])', r'( -\1', expression)
    # join digits separated only by spaces
    processed = re.sub(r'(?<=\d)\s+(?=\d)', r'', processed)
    # join operators separated only by spaces
    processed = re.sub(r'(?<=[-+*/])\s+(?=[-+*/])', r'', processed)
    # enclose in parentheses for convenience
    processed = re.sub(r'^(.+)$', r'( \1 )', processed)

    if re.search(r'[-+*/]{2,}', processed):    # neighbouring operators
        return None

    return processed


def main():
    tests = {
        '18/(6*-3)+(3*2)': None,
        '-18/(6*-3)+(3*2)': None,
        '2 * 6 / 3 + (3 * 1))': None,
        '(2 * 6 / 3 + (3 * 1)': None,
        '2 * 6 / 3 + )(3 * 1)(': None,
        '3*- ( 6)': None,
        '-18/ -(6* -3)+(-3*2)': None,
        '()': None,
        '4 + ( ) 3': None,
        '2 * 6 / 3 + (3 * 1)': 7,
        '2 * (6 / 3) + (3 * 1)': 7,
        '18 / 6 * 3 + (3 * 2)': 15,
        '18 / (6 * 3) + (3 * 2)': 7,
        '-18 / (-(6 * (-3))) + (-3 * 2)': -7,
        '(2 * 6 / 3 + (3 * 1))': 7,
        '((2 * 6 / 3 + (3 * 1)))': 7,
        '(((2 * 6) / 3 + (((3) * (1)))))': 7,
        '2 + 1 - 2 + 3 - 10': -6,
        '2 + (1 - 2) + 3 - 10': -6,
        '2 + (1 - 2)': 1,
        '2.5 * 4 / (1/3) + (0.1 * 20)': 32,
        '2.5 * 4 / (1/3) + (0.15555 * 20)': 33.111,
        '0 + 1 + 2 + 3 - 4 - 5 * ( 6 + 7 - ( 8 + 9) )': 22,
        '3 * 8 - 4 * 2 / 4 * ( - ( 3 + 3 ) )': 36,
        '3 * (- 6)': -18,
        '4 + 6 - ( 10 - 3 ) * 2 / 8 * 3': 4.75,
        '4 0 0 + 6 - ( 1 0 0 - 3 ) * 2 / 8 * 3': 333.25,
        # there are some limitation to representing large numbers
        # due to double-precission floating point type specs (IEEE 754):
        # '12345678901234567890': 12345678901234567890,   # AssertionError
        # '12345678901234*1000000 + 567890': 12345678901234567890,   # AssertionError
    }

    for k, value in tests.items():
        validated = validate(k)
        if validated:
            result = evaluate(validated)
            print(f'{result == value} -> valid expression: {k} = {result}')
            assert result == value
        else:
            print(f'{validated is value} -> invalid expression: {k}')
            assert validated is value


if __name__ == '__main__':
    main()
