from typing import Callable

### PASTE YOUR CODE HERE ('solve' function) ###




################################################


def test_function(list_input: list, list_output: list, solve_fn: Callable) -> int:
    """
    Test the provided 'solve' function over a list of test cases.
    
    Parameters:
        list_input (list): A list of tuples, each representing the input for a single test case.
        list_output (list): A list of expected outputs, one for each test case.
        solve_fn (callable): The 'solve' function to be tested.
        
    Returns:
        int: The number of test cases correctly solved by the 'solve' function.
    """
    
    n_test = len(list_input)
    n_correct = 0

    for i in range(n_test):

        # Try to call the solve function with the current test case input
        try:
            result = solve_fn(*list_input[i])
            print(f'True result: {list_output[i]}')
            print(f'Predicted result: {result}')
            
            # Compare the result with the expected output
            if list_output[i] == result:
                n_correct += 1
            print('---------------------------')
        
        # If the function call raises an exception, print an error message and continue with the next test case
        except Exception as e:
            print(f'The function that was generated causes a runtime error when executed: {e}')
            print('---------------------------')
    
    print(f'Number of correct answer: {n_correct}')
    print('======================================')
    
    return n_correct

if __name__ == '__main__':

    # Define input test cases and their expected outputs for the problem
    list_input = [
        (3, [5, 5, 5]),
        (4, [2, 3, 2, 4]),
        (1, [3]),
        (3, [2, 100, 2]),
        (5, [2, 4, 2, 11, 2])
    ]

    list_output = [
        0,
        2,
        0,
        0,
        1
    ]

test_function(list_input, list_output, solve)