"""
Handlers for opcode addressing modes.
Currently just stubs.
"""

class HandlerMetaclass(type):
    """
    This metaclass simplifies the specification of handler classes.

    When writing a handler class, a few values can be specified as class
    variables.  This metaclass turns them into instance variables, and generates
    various useful methods and properties for the handler class.
    """

    def __new__(metacls, clsname, bases, attr_dict):
        # Copy useful info from the class variables.
        operand_size = attr_dict["operand_size"]
        assert operand_size >= 0
        size = operand_size + 1

        # We now remove the class variables.
        del attr_dict["operand_size"]

        # Define an init method for the handler class.
        # This turns the (now removed) class variables into instance variables.
        def init(self):
            self.size = size
            self.operand_size = operand_size

        def operands_string(self):
            return "[{} operand bytes todo]".format(self.operand_size)

        # Add the new methods and properties to the handler class.
        attr_dict["__init__"] = init
        attr_dict["operands_string"] = property(operands_string)

        return super().__new__(metacls, clsname, bases, attr_dict)


class Implicit(metaclass=HandlerMetaclass):
    operand_size = 0

class DirectXIndirect(metaclass=HandlerMetaclass):
    operand_size = 1

class Illegal(metaclass=HandlerMetaclass):
    operand_size = 0

class Direct(metaclass=HandlerMetaclass):
    operand_size = 1

class Immediate(metaclass=HandlerMetaclass):
    operand_size = 1

class Accumulator(metaclass=HandlerMetaclass):
    operand_size = 0

class Absolute(metaclass=HandlerMetaclass):
    operand_size = 2

class Relative(metaclass=HandlerMetaclass):
    operand_size = 1

class DirectIndirectY(metaclass=HandlerMetaclass):
    operand_size = 1

class DirectX(metaclass=HandlerMetaclass):
    operand_size = 1

class AbsoluteY(metaclass=HandlerMetaclass):
    operand_size = 2

class AbsoluteX(metaclass=HandlerMetaclass):
    operand_size = 2

class Ret(metaclass=HandlerMetaclass):
    operand_size = 0

class JmpAbsolute(metaclass=HandlerMetaclass):
    operand_size = 2

class JmpAbsoluteIndirect(metaclass=HandlerMetaclass):
    operand_size = 2

class DirectY(metaclass=HandlerMetaclass):
    operand_size = 1
