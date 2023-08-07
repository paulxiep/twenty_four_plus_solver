from dataclasses import dataclass
from math import sqrt, factorial


@dataclass
class Arithmetic:
    value: str
    repr: str
    '''
    Stores both value and repr, the representation.
    For Operators these are the same, 
    but for Numbers repr will be steps used to arrive at current value.
    
    right shift operator will be overridden for relevant subclasses
    the override is used to chain mathematical operations
    '''
    pass


@dataclass
class Number(Arithmetic):
    '''
    Class to represent the numbers.
    Not to be initialized directly, use get method.
    '''

    @staticmethod
    def get(value):
        return Number(value, str(value))

    def is_positive(self):
        if self.value >= 0:
            return True
        else:
            return False

    def integer_root(self):
        return sqrt(self.value * self.is_positive() - self.value * (not self.is_positive())).is_integer()

    def __rshift__(self, other):
        if isinstance(other, DuoOperator):
            return PartialOperation(self, other)
        elif isinstance(other, PostSingularOperator):
            assert self.value == int(self.value)
            return Number(factorial(int(self.value)), '(' + self.repr + '!)')
        else:
            raise NotImplementedError('Number can only be followed by PostSingularOperator or DuoOperator')


@dataclass
class Operator(Arithmetic):
    '''
    Base operator class.
    Not to be initialized directly, use get method.
    '''

    @staticmethod
    def get(value):
        if value == '!':
            return PostSingularOperator(value, value)
        elif value in ['sqrt', '-()']:
            return PreSingularOperator(value.rstrip('()'), value.rstrip('()'))
        elif value in ['+', '-', '*', '/']:
            return DuoOperator(value, value)
        else:
            raise NotImplementedError('Unidentified Operator')


@dataclass
class PreSingularOperator(Operator):
    '''
    For operators that operate on a single number and precede it.
    Currently only minus (-) and sqrt are defined.
    '''

    def __rshift__(self, other):
        if isinstance(other, Number):
            if self.value == 'sqrt':
                return Number(sqrt(other.value), 'sqrt(' + other.repr + ')')
            elif self.value == '-':
                return Number(-other.value, '(-' + other.repr + ')')
            elif self.value == '/':
                return Number(1 / other.value, '(1/' + other.repr + ')')
            else:
                raise NotImplementedError('Unknown Singular Operator, shouldn\'t be here')
        else:
            raise NotImplementedError('PreSingularOperator needs to be followed by Number')


@dataclass
class PostSingularOperator(Operator):
    '''
    for operators that operate on single number and follows it
    currently only factorial is defined

    Class type is required to chain with Number.
    '''
    pass


@dataclass
class DuoOperator(Operator):
    '''
    For operators that require 2 numbers

    Class type is required to chain with Number into PartialOperation instance.
    '''
    pass


@dataclass
class PartialOperation:
    number: Number
    next: DuoOperator
    '''
    As the attributes suggest, this is a partial merge between Number and following DuoOperator.
    It needs to be followed by Number to complete the operation.
    '''

    def __rshift__(self, other):
        if isinstance(other, Number):
            return Number(eval(f'{self.number.value} {self.next.value} {other.value}'),
                          '(' + self.number.repr + self.next.repr + other.repr + ')')
        else:
            raise NotImplementedError('PartialOperation can only be followed by Number')
