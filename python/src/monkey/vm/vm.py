from typing import Final, cast

from ..code import code
from ..compiler import compiler
from ..obj import obj

STACK_SIZE: Final[int] = 2048


class VirtualMachine:
    def __init__(self, bytecode: compiler.Bytecode) -> None:
        self.instructions: bytes = bytecode.instructions
        self.constants: list[obj.Object] = bytecode.constants
        self.stack: list[obj.Object] = [obj.NULL] * STACK_SIZE
        self.sp: int = 0

    @property
    def stack_top(self) -> obj.Object | None:
        if self.sp <= 0:
            return None
        else:
            return self.stack[self.sp - 1]

    @property
    def last_popped(self) -> obj.Object | None:
        return self.stack[self.sp]

    def push(self, o: obj.Object) -> None:
        if self.sp > STACK_SIZE:
            raise OverflowError("Stack overflow.")
        self.stack[self.sp] = o
        self.sp += 1

    def pop(self) -> obj.Object:
        if self.sp - 1 < 0:
            return obj.NULL
        o = self.stack[self.sp - 1]
        self.sp -= 1
        return o

    def run(self) -> None:
        ip = 0
        while ip < len(self.instructions):
            op = code.OpCode(self.instructions[ip].to_bytes(1, "big"))
            ip += 1
            match op:
                case code.OpCode.PConstant:
                    const_idx = int.from_bytes(self.instructions[ip : ip + 2], "big")
                    ip += 2
                    self.push(self.constants[const_idx])
                case code.OpCode.Add:
                    right = self.pop()
                    left = self.pop()
                    if isinstance(left, obj.Integer) and isinstance(right, obj.Integer):
                        result = left.value + right.value
                    self.push(obj.Integer(result))
                case code.OpCode.Sub:
                    right = self.pop()
                    left = self.pop()
                    result = left.value - right.value
                    self.push(obj.Integer(result))
                case code.OpCode.Mul:
                    right = self.pop()
                    left = self.pop()
                    result = left.value * right.value
                    self.push(obj.Integer(result))
                case code.OpCode.Div:
                    right = self.pop()
                    left = self.pop()
                    result = left.value // right.value
                    self.push(obj.Integer(result))
                case code.OpCode.PTrue:
                    self.push(obj.TRUE)
                case code.OpCode.PFalse:
                    self.push(obj.FALSE)
                case code.OpCode.Pop:
                    self.pop()
                case code.OpCode.Equal:
                    right = self.pop()
                    left = self.pop()
                    if isinstance(left, obj.Integer) and isinstance(right, obj.Integer):
                        result = obj.TRUE if left.value == right.value else obj.FALSE
                    else:
                        result = obj.TRUE if left == right else obj.FALSE
                    self.push(result)
                case code.OpCode.NotEqual:
                    right = self.pop()
                    left = self.pop()
                    if isinstance(left, obj.Integer) and isinstance(right, obj.Integer):
                        result = obj.TRUE if left.value != right.value else obj.FALSE
                    else:
                        result = obj.TRUE if left != right else obj.FALSE
                    self.push(result)
                case code.OpCode.GreaterThan:
                    right = self.pop()
                    left = self.pop()
                    result = obj.TRUE if left.value > right.value else obj.FALSE
                    self.push(result)
                case code.OpCode.Minus:
                    value = self.pop()
                    result = -value.value
                    self.push(obj.Integer(result))
                case code.OpCode.Bang:
                    value = self.pop()
                    result = obj.TRUE if not value.value else obj.FALSE
                    self.push(result)
                case code.OpCode.Jump:
                    const_idx = int.from_bytes(self.instructions[ip : ip + 2], "big")
                    ip = const_idx
                case code.OpCode.JumpNT:
                    const_idx = int.from_bytes(self.instructions[ip : ip + 2], "big")
                    ip += 2
                    condition = self.pop()
                    if condition is obj.FALSE:
                        ip = const_idx
                case code.OpCode.PNull:
                    self.push(obj.NULL)
                case _:
                    raise NotImplementedError("OpCode not yet supported")
