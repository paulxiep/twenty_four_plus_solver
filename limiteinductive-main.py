from dataclasses import dataclass
import itertools
import math
from typing import Sequence


@dataclass
class Expression:
    """
    Represents a mathematical expression derived from game inputs.

    Attributes:
    - value (int): The computed integer result of the expression.
    - string (str): The string representation of the expression in standard mathematical notation.

    The class provides methods for basic arithmetic operations, and
    generates new Expression objects based on those operations. It ensures
    that each resulting Expression maintains both its value and its corresponding
    string representation.
    """

    value: int
    string: str

    def add(self, other: "Expression") -> "Expression":
        """Returns a new Expression representing the sum of self and another Expression."""
        value = self.value + other.value
        string = f"{self.string} + {other.string}"
        return Expression(value=value, string=string)

    def multiply(self, other: "Expression", limit: int = 1800) -> "Expression | None":
        """
        Returns a new Expression representing the product of self and another Expression
        if the result does not exceed a specified limit.
        """
        value = self.value * other.value

        if value <= limit:
            string = f"{self.string} * {other.string}"
            return Expression(value=value, string=string)

        return None

    def divide(self, other: "Expression") -> "Expression | None":
        """Returns a new Expression representing the division of self by another Expression if division is valid."""
        if other.value == 0:
            return None

        value = self.value / other.value

        if value.is_integer():
            string = f"({self.string} / {other.string})"
            return Expression(value=int(value), string=string)

        return None

    def minus(self, other: "Expression") -> "Expression":
        """Returns a new Expression representing the difference of self and another Expression."""
        value = self.value - other.value
        string = f"({self.string} - {other.string})"
        return Expression(value=value, string=string)

    def get_factorial(self, limit: int = 8) -> "Expression | None":
        """
        Returns a new Expression representing the factorial of self
        if the value of self is within a specified limit.
        """
        if 1 <= self.value <= limit:
            value = math.factorial(self.value)
            string = f"({self.string}!)"
            return Expression(value=value, string=string)

    @property
    def opposite(self) -> "Expression":
        """Returns a new Expression representing the opposite of self."""
        value = -self.value
        string = f"(-{self.string})"
        return Expression(value=value, string=string)

    @property
    def sqrt(self) -> "Expression | None":
        """Returns a new Expression representing the square root of self if it's a valid integer."""
        if self.value <= 0:
            return None

        if (value := math.sqrt(self.value)).is_integer():
            string = f"sqrt({self.string})"
            return Expression(value=int(value), string=string)


def get_all_combinations(
    expr_1: Expression, expr_2: Expression, multiply_limit: int = 1800
) -> list[Expression]:
    """Return all possible mathematical combinations of two Expressions."""
    results = [expr_1.add(other=expr_2), expr_1.minus(other=expr_2)]

    # Attempt to multiply and divide the expressions, appending valid results
    if result := expr_1.multiply(other=expr_2, limit=multiply_limit):
        results.append(result)
    if result := expr_1.divide(other=expr_2):
        results.append(result)
    return results


def get_all_variations(expr: Expression, factorial_limit: int = 8) -> list[Expression]:
    """
    Returns all possible mathematical variations of an Expression:
    1. The expression itself.
    2. Its opposite if it's negative.
    3. Its factorial if it's valid.
    4. Its square root if it's a valid integer.
    """
    results = [expr]

    # Check if expression is negative
    if expr.value != 0 and expr.string.lstrip("(").startswith("-"):
        results.append(expr.opposite)

    # Append factorial and square root if they're valid
    if (result := expr.get_factorial(limit=factorial_limit)) is not None:
        results.append(result)
    if (result := expr.sqrt) is not None:
        results.append(result)
    return results


def get_all_expressions(
    digits: Sequence[int], factorial_limit: int = 8, multiply_limit: int = 1800
) -> list[Expression]:
    """
    Recursively generate all possible expressions for a given set of digits.
    """
    # Base case
    if len(digits) == 0:
        return []

    # Single digit case
    if len(digits) == 1:
        digit = digits[0]
        expr = Expression(value=digit, string=str(object=digit))
        return get_all_variations(expr=expr, factorial_limit=factorial_limit)

    # Recursion on combinations and variations
    all_combinations = itertools.chain(
        *[
            get_all_combinations(
                expr_1=expr_1, expr_2=expr_2, multiply_limit=multiply_limit
            )
            for expr_1 in get_all_expressions(digits=digits[:1])
            for expr_2 in get_all_expressions(digits=digits[1:])
        ]
    )
    all_variations = itertools.chain(
        *[
            get_all_variations(expr=expr, factorial_limit=factorial_limit)
            for expr in all_combinations
        ]
    )

    return list(all_variations)


def find_targets(
    digits: Sequence[int],
    target_range: int,
    multiply_limit: int = 1800,
    factorial_limit: int = 8,
) -> dict[int, str | None]:
    """Find and return expressions that can generate values in a given target range."""
    interval = range(target_range)
    results: dict[int, str | None] = {i: None for i in interval}
    all_expressions = get_all_expressions(
        digits=digits, multiply_limit=multiply_limit, factorial_limit=factorial_limit
    )

    for expr in all_expressions:
        if expr.value in interval and results[expr.value] is None:
            results[expr.value] = expr.string

    return results


def find_targets_for_permutations(
    digits: Sequence[int],
    target_range: int,
    factorial_limit: int = 8,
    multiply_limit: int = 1800,
) -> dict[int, str | None]:
    """Find expressions for all possible permutations of the digits that generate values in the target range."""
    results: dict[int, str | None] = {i: None for i in range(target_range)}
    found = False

    # Loop through all permutations of given digits
    for r in range(len(digits)):
        for perm in itertools.permutations(iterable=digits, r=r):
            targets = find_targets(
                digits=list(perm),
                target_range=target_range,
                factorial_limit=factorial_limit,
                multiply_limit=multiply_limit,
            )
            missing_targets = [
                target for target, value in results.items() if value is None
            ]

            if len(missing_targets) == 0:
                found = True
                break

            for target in missing_targets:
                results[target] = targets[target]

        if found:
            break

    return results


def main(
    digits: Sequence[int],
    target_range: int = 1000,
    factorial_limit: int = 8,
    multiply_limit: int = 1800,
) -> None:
    """
    Main function to determine how to achieve numbers in a given target range
    using mathematical operations on the provided set of digits.

    This is a solution to a game where the goal is to generate as many numbers
    in the target range as possible using the provided digits. Each digit can
    be used only once in a given expression, but not all digits need to be used.

    Parameters:
        - digits (Sequence[int]): A sequence of numbers available for creating expressions.
        - target_range (int): The range of numbers that we aim to express.
        - factorial_limit (int): The highest number for which factorial will be computed. Adjust to improve performance.
        - multiply_limit (int): The maximum allowed result for multiplication operations.

    The function prints out each number in the target range and the first found
    mathematical expression (using the provided digits) that results in that number,
    if such an expression exists.
    """
    results = find_targets_for_permutations(
        digits=digits,
        target_range=target_range,
        factorial_limit=factorial_limit,
        multiply_limit=multiply_limit,
    )

    for target, string in results.items():
        print(f"{target}: {string}")


if __name__ == "__main__":
    digits = [3, 4, 8, 7, 25, 50]
    target_range = 1000
    multply_limit = 1000
    factorial_limit = 5

    main(
        digits=digits,
        target_range=target_range,
        factorial_limit=factorial_limit,
        multiply_limit=multply_limit,
    )
