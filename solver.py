#!/usr/bin/env python
# coding: utf-8

import re
import operator

operators = {
    '+': operator.add,
    '-': operator.sub,
    '*': operator.mul,
    '/': operator.truediv,
}

op_precedences = [
    # extract content between innermost parentheses - highest precedence
    r'\(\s*([^()]+)\)',

    # extract higher precedence operator (* or /) and its adjoining operands
    r'(\d+(?:\.\d+)?)\s*([*/])\s*(-?\s*\d+(?:\.\d+)?)',

    # extract lower precedence operator (+ or -) and its adjoining operands
    r'(-?\s*\d+(?:\.\d+)?)\s*([+-])\s*(-?\s*\d+(?:\.\d+)?)',
]


def validate(expression):
    """Expression validator and reformatter

    Receive a candidate expression as a string of space-separated
    characters. Valid characters are all of "0123456789.+-*/() ".
    Basic checking is performed as well as reformatting. If valid,
    return a reformatted expression as a string, otherwise return
    None.
    """

    # check for characters not in a valid set, not just for the
    # purpose of validating an expression but also to guard against
    # malicious code injections
    if re.search(r'[^\d.+\-*/() ]', expression):
        return None

    # disallow expressions starting with any of "+", "*" or "/"
    if re.search(r'^\s*[+*/]', expression):
        return None

    # check parentheses for mismatch
    if not check_parentheses(expression):
        return None

    # manage space around negation sign - subtraction operator
    processed = re.sub(r'(?<=\()-\s+([\d\(])', r' -\1', expression)
    processed = re.sub(r'(?<=\(\s)-\s+([\d\(])', r'-\1', processed)

    # join digits separated only by space
    processed = re.sub(r'(?<=\d)\s+(?=\d)', r'', processed)

    # join operators separated only by space
    processed = re.sub(r'(?<=[-+*/])\s+(?=[-+*/])', r'', processed)

    # disallow neighboring operators
    if re.search(r'[-+*/]{2,}', processed):
        return None

    # disallow "+","*" or "/" between two identical parentheses
    if re.search(r'([\(\)])\s*[+*/]\s*\1', processed):
        return None

    # disallow "-" between two closing parentheses
    if re.search(r'\)\s*-\s*\)', processed):
        return None

    # enclose everything in parentheses for convenience
    processed = re.sub(r'^(.+)$', r'( \1 )', processed)

    return processed


# helper function for `validate`
def check_parentheses(expression):
    """Check parentheses for mismatch

    Receive a candidate expression as a string and return True if all
    parentheses are properly matched. Nesting is allowed. If an error is
    detected, return False. If no parentheses are present, return True.
    """

    # disallow paired parentheses containing only space and/or
    # operator(s) or nothing at all
    if re.search(r'\([\s+*/-]*\)', expression):
        return False

    # construct a list of parentheses to check
    parentheses = re.findall(r'[()]', expression)

    #  parity
    count = 0
    counter = {
        '(': 1,
        ')': -1
    }

    for parenthesis in parentheses:
        count += counter[parenthesis]

        # if left of any point there is more closed than opened parentheses
        if count < 0:
            return False

    # if after counting through the entire expression
    # there is more opened than closed parentheses (count > 0)
    if count:
        return False

    return True


def evaluate(expression, noparentheses=False):
    """Evaluator functionality of the solver module

    Receive a validated and reformatted expression from `validate`. If
    it is None, return None. If it passed validation, evaluate it in
    order of operator precedence, second only to order enforced by
    parentheses. If the result is a whole number cast it to int. Return the result.
    """

    # skip the zero precedence if no parentheses are present
    noparentheses = int(noparentheses)

    # evaluate expression in order of operator precedences
    for order in range(noparentheses, 3):
        # "initial" update is not a thing, therefore:
        updated = None

        # for the current level of precedence
        while True:
            # call `operate` on an appropriate re.match object
            updated = re.sub(op_precedences[order], operate, expression, count=noparentheses)

            # cancel out even number of consecutive negative signs
            updated = re.sub(r'(?:--)+', '+', updated)

            #
            updated = re.sub(r'^\+', '0+', updated)

            # when done with this level of operator precedence
            if (updated == expression):
                # proceed to a lower level (higher `order` count)
                break

            # otherwise repeat the while loop
            # reducing the expression stepwise from left to right
            expression = updated

    # if the result is a whole number, cast it to int
    result = float(expression)
    if result == round(result):
        result = int(result)

    return result


def operate(match):
    """Perform a single calculation on a group of strings

    Receive a re.match object from `evaluate`. The object contains
    subgroups of strings captured by regex groups.

    In case the match contains a single subgroup, it is guaranteed not
    to contain parentheses. Send the string to `evaluate` for next
    level processing.

    In case the match contains 3 subgroups, it is guaranteed to be a
    match of a binary operation. Convert the two operand strings
    (from subgroups 1 and 3) to floats. Resolve the operator string
    (from subgroup 2) to the correct `operator` method. Call the
    `operator` method on the operands in the correct order. If the
    result is a whole number cast it to int. Return the result.
    """

    # evaluate subexpression from inside parentheses, if present
    if len(match.groups()) == 1:
        subresult = evaluate(match.group(1).strip(), noparentheses=True)
        return str(subresult)

    # otherwise treat as a simple binary expression
    left, right = match.group(1, 3)

    # remove space between a "-" sign and operand, if present
    left = re.sub(r'-\s+', '-', left)
    right = re.sub(r'-\s+', '-', right)

    # define the correct operator method to use
    operator_ = operators[match.group(2)]

    # perform the calculation
    result = operator_(float(left), float(right))

    if result == round(result):
        result = int(result)

    return str(result)


def run_tests():
    tests = {
        '( 3 % 2 )': None,
        '3 + 2 f': None,
        '( 3 $ + 2 $)': None,
        '! ( 3 + 2 )': None,
        '( 3 + 2 ) =': None,
        '( 3 + 2 ) :': None,
        '~ 1': None,
        '0 ^ 1': None,
        '3 + 2 \\': None,
        '3 + 2 \0': None,
        '3 + 2 \n': None,
        '3 + 2 \r': None,
        '3 + 2 \t': None,
        '3 + 2 F': None,
        '- 1 8 / ( 6 * - 3 ) + ( 3 * 2 )': None,
        '2 * 6 / 3 + ( 3 * 1 ) )': None,
        '( 2 * 6 / 3 + ( 3 * 1 )': None,
        '2 * 6 / 3 + ) ( 3 * 1 ) (': None,
        '3 * - ( 6 )': None,
        '- 1 8 / - ( 6 * - 3 ) + ( - 3 * 2 )': None,
        '( )': None,
        '2 * 6 / 3 + ( + ( - 3 ) ) + ( 3 * 1 )': None,
        '2 * 6 / 3 + ( * ( - 3 ) ) + ( 3 * 1 )': None,
        '2 * 6 / 3 + ( / ( - 3 ) ) + ( 3 * 1 )': None,
        '2 * 6 / 3 + ( ( - 3 ) * ) + ( 3 * 1 )': None,
        '2 * 6 / 3 + ( ( - 3 ) / ) + ( 3 * 1 )': None,
        '2 * 6 / 3 + ( ( - 3 ) - ) + ( 3 * 1 )': None,
        '2 * 6 / 3 + ( ( - 3 ) + ) + ( 3 * 1 )': None,
        '+ 2 + 2': None,
        '* 2 + 2': None,
        '/ 2 + 2': None,
        '4 + ( + ) 3': None,
        '4 + ( - ) 3': None,
        '4 + ( * ) 3': None,
        '4 + ( / ) 3': None,
        '2 * 6 / 3 + ( 3 * 1 )': '?',
        '2 * 6 / 3 + ( - ( - ( - ( - ( - 3 ) ) ) ) ) + ( 3 * 1 )': '?',
        '2 * 6 / 3 + ( - ( - ( - 3 ) ) ) + ( 3 * 1 )': '?',
        '2 * 6 / 3 + ( ( - ( - 3 ) ) ) + ( 3 * 1 )': '?',
        '2 * ( 6 / 3 ) + ( 3 * 1 )': '?',
        '1 8 / 6 * 3 + ( 3 * 2 )': '?',
        '1 8 / ( 6 * 3 ) + ( 3 * 2 )': '?',
        '- 1 8 / ( - ( 6 * ( - 3 ) ) ) + ( - 3 * 2 )': '?',
        '( 2 * 6 / 3 + ( 3 * 1 ) )': '?',
        '( ( 2 * 6 / 3 + ( 3 * 1 ) ) )': '?',
        '( ( ( 2 * 6 ) / 3 + ( ( ( 3 ) * ( 1 ) ) ) ) )': '?',
        '2 + 1 - 2 + 3 - 1 0': '?',
        '2 + ( 1 - 2 ) + 3 - 1 0': '?',
        '2 + ( 1 - 2 )': '?',
        '- 2 + 2': '?',
        '2.5 * 4 / ( 1 / 3) + ( 0.1 * 2 0 )': '?',
        '2.5 * 4 / ( 1 / 3 ) + ( 0.15555 * 2 0 )': '?',
        '0 + 1 + 2 + 3 - 4 - 5 * ( 6 + 7 - ( 8 + 9 ) )': '?',
        '3 * 8 - 4 * 2 / 4 + ( - ( 3 + 3 ) )': '?',
        '3 * ( - 6 )': '?',
        '4 + 6 - ( 1 0 - 3 ) * 2 / 8 * 3': '?',
        '4 0 0 + 6 - ( 1 0 0 - 3 ) * 2 / 8 * 3': '?',
        '( 3 - 4 ) * ( 5 - 6 ) / ( 5 - 6 )': '?',
        '3 - 4 * 2 ': '?',
        # there are some limitation to representing large numbers
        # due to double-precision floating point type specs (IEEE 754):
        # '12345678901234567890': 12345678901234567890,   # test fails
        # '12345678901234*1000000 + 567890': 12345678901234567890,   # test fails
    }

    tests_condensed = {
        '(3%2)': None,
        '3+2f': None,
        '(3$+2$)': None,
        '!(3+2)': None,
        '(3+2)=': None,
        '(3+2):': None,
        '~1': None,
        '0^1': None,
        '3+2\\': None,
        '3+2\0': None,
        '3+2\n': None,
        '3+2\r': None,
        '3+2\t': None,
        '3+2F': None,
        '-18/(6*-3)+(3*2)': None,
        '2*6/3+(3*1))': None,
        '(2*6/3+(3*1)': None,
        '2*6/3+)(3*1)(': None,
        '3*-(6)': None,
        '-18/-(6*-3)+(-3*2)': None,
        '()': None,
        '2*6/3+(+(-3))+(3*1)': None,
        '2*6/3+(*(-3))+(3*1)': None,
        '2*6/3+(/(-3))+(3*1)': None,
        '2*6/3+((-3)*)+(3*1)': None,
        '2*6/3+((-3)/)+(3*1)': None,
        '2*6/3+((-3)-)+(3*1)': None,
        '2*6/3+((-3)+)+(3*1)': None,
        '+2+2': None,
        '*2+2': None,
        '/2+2': None,
        '4+(+)3': None,
        '4+(-)3': None,
        '4+(*)3': None,
        '4+(/)3': None,
        '2*6/3+(3*1)': '?',
        '2*6/3+(-(-(-(-(-3)))))+(3*1)': '?',
        '2*6/3+(-(-(-3)))+(3*1)': '?',
        '2*6/3+((-(-3)))+(3*1)': '?',
        '2*(6/3)+(3*1)': '?',
        '18/6*3+(3*2)': '?',
        '18/(6*3)+(3*2)': '?',
        '-18/(-(6*(-3)))+(-3*2)': '?',
        '(2*6/3+(3*1))': '?',
        '((2*6/3+(3*1)))': '?',
        '(((2*6)/3+(((3)*(1)))))': '?',
        '2+1-2+3-10': '?',
        '2+(1-2)+3-10': '?',
        '2+(1-2)': '?',
        '-2+2': '?',
        '2.5*4/(1/3)+(0.1*20)': '?',
        '2.5*4/(1/3)+(0.15555*20)': '?',
        '0+1+2+3-4-5*(6+7-(8+9))': '?',
        '3*8-4*2/4+(-(3+3))': '?',
        '3*(-6)': '?',
        '4+6-(10-3)*2/8*3': '?',
        '400+6-(100-3)*2/8*3': '?',
        '(3-4)*(5-6)/(5-6)': '?',
        '3-4*2': '?',
        # there are some limitation to representing large numbers
        # due to double-precision floating point type specs (IEEE 754):
        # '12345678901234567890': 12345678901234567890,   # test fails
        # '12345678901234*1000000 + 567890': 12345678901234567890,   # test fails
    }

    passfail = {
        True: 'passed',
        False: 'failed'
    }

    for expression, value in {**tests, **tests_condensed}.items():
        validated = validate(expression)
        if validated:
            solver_result = evaluate(validated)
            eval_result = eval(validated)
            print(f'{passfail[solver_result == eval_result]} -> valid expression: {expression} = {solver_result}')
            assert solver_result == eval_result
        else:
            print(f'{passfail[validated is value]} -> invalid expression: {expression}')
            assert validated is value


if __name__ == '__main__':
    run_tests()
