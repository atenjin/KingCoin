#!/usr/bin/env python
# -*- coding: utf-8 -*-
import copy

from app.base import bignum
from enum import IntEnum

from app.base import serialize
from app.block.key import PyKey
from app.block.utils import cryptoutil
from app.block.utils import typeutil
from app.config import VERSION
from app import context as ctx


class SignType(IntEnum):
    SIGHASH_ALL = 1
    SIGHASH_NONE = 2
    SIGHASH_SINGLE = 3
    SIGHASH_ANYONECANPAY = 0x80
    SIGHASH_UNKNOWN = 0xFF


class OpCodeType(IntEnum):
    # reverse = None
    # @staticmethod
    # def look_up(value):
    #     if OpCodeType.reverse is None:
    #         reverse = dict((value, key) for key, value in OpCodeType.iteritems())
    #     return OpCodeType.reverse.get(value, None)

    # push value
    OP_0 = 0
    OP_FALSE = OP_0
    OP_PUSHDATA1 = 76
    OP_PUSHDATA2 = 77
    OP_PUSHDATA4 = 78
    OP_1NEGATE = 79
    OP_RESERVED = 80
    OP_1 = 81
    OP_TRUE = OP_1
    OP_2 = 82
    OP_3 = 83
    OP_4 = 84
    OP_5 = 85
    OP_6 = 86
    OP_7 = 87
    OP_8 = 88
    OP_9 = 89
    OP_10 = 90
    OP_11 = 91
    OP_12 = 92
    OP_13 = 93
    OP_14 = 94
    OP_15 = 95
    OP_16 = 96

    # control
    OP_NOP = 97
    OP_VER = 98
    OP_IF = 99
    OP_NOTIF = 100
    OP_VERIF = 101
    OP_VERNOTIF = 102
    OP_ELSE = 103
    OP_ENDIF = 104
    OP_VERIFY = 105
    OP_RETURN = 106

    # stack ops
    OP_TOALTSTACK = 107
    OP_FROMALTSTACK = 108
    OP_2DROP = 109
    OP_2DUP = 110
    OP_3DUP = 111
    OP_2OVER = 112
    OP_2ROT = 113
    OP_2SWAP = 114
    OP_IFDUP = 115
    OP_DEPTH = 116
    OP_DROP = 117
    OP_DUP = 118
    OP_NIP = 119
    OP_OVER = 120
    OP_PICK = 121
    OP_ROLL = 122
    OP_ROT = 123
    OP_SWAP = 124
    OP_TUCK = 125

    # splice ops
    OP_CAT = 126
    OP_SUBSTR = 127
    OP_LEFT = 128
    OP_RIGHT = 129
    OP_SIZE = 130

    # bit logic
    OP_INVERT = 131
    OP_AND = 132
    OP_OR = 133
    OP_XOR = 134
    OP_EQUAL = 135
    OP_EQUALVERIFY = 136
    OP_RESERVED1 = 137
    OP_RESERVED2 = 138

    # numeric
    OP_1ADD = 139
    OP_1SUB = 140
    OP_2MUL = 141
    OP_2DIV = 142
    OP_NEGATE = 143
    OP_ABS = 144
    OP_NOT = 145
    OP_0NOTEQUAL = 146

    OP_ADD = 147
    OP_SUB = 148
    OP_MUL = 149
    OP_DIV = 150
    OP_MOD = 151
    OP_LSHIFT = 152
    OP_RSHIFT = 153

    OP_BOOLAND = 154
    OP_BOOLOR = 155
    OP_NUMEQUAL = 156
    OP_NUMEQUALVERIFY = 157
    OP_NUMNOTEQUAL = 158
    OP_LESSTHAN = 159
    OP_GREATERTHAN = 160
    OP_LESSTHANOREQUAL = 161
    OP_GREATERTHANOREQUAL = 162
    OP_MIN = 163
    OP_MAX = 164

    OP_WITHIN = 165

    # crypto
    OP_RIPEMD160 = 166
    OP_SHA1 = 167
    OP_SHA256 = 168
    OP_HASH160 = 169
    OP_HASH256 = 170
    OP_CODESEPARATOR = 171
    OP_CHECKSIG = 172
    OP_CHECKSIGVERIFY = 173
    OP_CHECKMULTISIG = 174
    OP_CHECKMULTISIGVERIFY = 175

    # multi-byte opcodes
    OP_SINGLEBYTE_END = 0xF0
    OP_DOUBLEBYTE_BEGIN = 0xF000

    # template matching params
    OP_PUBKEY = 0xF001
    OP_PUBKEYHASH = 0xF002

    OP_INVALIDOPCODE = 0xFFFF
    pass


__op_code = {
    # push value
    OpCodeType.OP_0: "0",
    OpCodeType.OP_PUSHDATA1: "OP_PUSHDATA1",
    OpCodeType.OP_PUSHDATA2: "OP_PUSHDATA2",
    OpCodeType.OP_PUSHDATA4: "OP_PUSHDATA4",
    OpCodeType.OP_1NEGATE: "-1",
    OpCodeType.OP_RESERVED: "OP_RESERVED",
    OpCodeType.OP_1: "1",
    OpCodeType.OP_2: "2",
    OpCodeType.OP_3: "3",
    OpCodeType.OP_4: "4",
    OpCodeType.OP_5: "5",
    OpCodeType.OP_6: "6",
    OpCodeType.OP_7: "7",
    OpCodeType.OP_8: "8",
    OpCodeType.OP_9: "9",
    OpCodeType.OP_10: "10",
    OpCodeType.OP_11: "11",
    OpCodeType.OP_12: "12",
    OpCodeType.OP_13: "13",
    OpCodeType.OP_14: "14",
    OpCodeType.OP_15: "15",
    OpCodeType.OP_16: "16",

    # control
    OpCodeType.OP_NOP: "OP_NOP",
    OpCodeType.OP_VER: "OP_VER",
    OpCodeType.OP_IF: "OP_IF",
    OpCodeType.OP_NOTIF: "OP_NOTIF",
    OpCodeType.OP_VERIF: "OP_VERIF",
    OpCodeType.OP_VERNOTIF: "OP_VERNOTIF",
    OpCodeType.OP_ELSE: "OP_ELSE",
    OpCodeType.OP_ENDIF: "OP_ENDIF",
    OpCodeType.OP_VERIFY: "OP_VERIFY",
    OpCodeType.OP_RETURN: "OP_RETURN",

    # stack ops
    OpCodeType.OP_TOALTSTACK: "OP_TOALTSTACK",
    OpCodeType.OP_FROMALTSTACK: "OP_FROMALTSTACK",
    OpCodeType.OP_2DROP: "OP_2DROP",
    OpCodeType.OP_2DUP: "OP_2DUP",
    OpCodeType.OP_3DUP: "OP_3DUP",
    OpCodeType.OP_2OVER: "OP_2OVER",
    OpCodeType.OP_2ROT: "OP_2ROT",
    OpCodeType.OP_2SWAP: "OP_2SWAP",
    OpCodeType.OP_IFDUP: "OP_IFDUP",
    OpCodeType.OP_DEPTH: "OP_DEPTH",
    OpCodeType.OP_DROP: "OP_DROP",
    OpCodeType.OP_DUP: "OP_DUP",
    OpCodeType.OP_NIP: "OP_NIP",
    OpCodeType.OP_OVER: "OP_OVER",
    OpCodeType.OP_PICK: "OP_PICK",
    OpCodeType.OP_ROLL: "OP_ROLL",
    OpCodeType.OP_ROT: "OP_ROT",
    OpCodeType.OP_SWAP: "OP_SWAP",
    OpCodeType.OP_TUCK: "OP_TUCK",

    # splice ops
    OpCodeType.OP_CAT: "OP_CAT",
    OpCodeType.OP_SUBSTR: "OP_SUBSTR",
    OpCodeType.OP_LEFT: "OP_LEFT",
    OpCodeType.OP_RIGHT: "OP_RIGHT",
    OpCodeType.OP_SIZE: "OP_SIZE",

    # bit logic
    OpCodeType.OP_INVERT: "OP_INVERT",
    OpCodeType.OP_AND: "OP_AND",
    OpCodeType.OP_OR: "OP_OR",
    OpCodeType.OP_XOR: "OP_XOR",
    OpCodeType.OP_EQUAL: "OP_EQUAL",
    OpCodeType.OP_EQUALVERIFY: "OP_EQUALVERIFY",
    OpCodeType.OP_RESERVED1: "OP_RESERVED1",
    OpCodeType.OP_RESERVED2: "OP_RESERVED2",

    # numeric
    OpCodeType.OP_1ADD: "OP_1ADD",
    OpCodeType.OP_1SUB: "OP_1SUB",
    OpCodeType.OP_2MUL: "OP_2MUL",
    OpCodeType.OP_2DIV: "OP_2DIV",
    OpCodeType.OP_NEGATE: "OP_NEGATE",
    OpCodeType.OP_ABS: "OP_ABS",
    OpCodeType.OP_NOT: "OP_NOT",
    OpCodeType.OP_0NOTEQUAL: "OP_0NOTEQUAL",
    OpCodeType.OP_ADD: "OP_ADD",
    OpCodeType.OP_SUB: "OP_SUB",
    OpCodeType.OP_MUL: "OP_MUL",
    OpCodeType.OP_DIV: "OP_DIV",
    OpCodeType.OP_MOD: "OP_MOD",
    OpCodeType.OP_LSHIFT: "OP_LSHIFT",
    OpCodeType.OP_RSHIFT: "OP_RSHIFT",
    OpCodeType.OP_BOOLAND: "OP_BOOLAND",
    OpCodeType.OP_BOOLOR: "OP_BOOLOR",
    OpCodeType.OP_NUMEQUAL: "OP_NUMEQUAL",
    OpCodeType.OP_NUMEQUALVERIFY: "OP_NUMEQUALVERIFY",
    OpCodeType.OP_NUMNOTEQUAL: "OP_NUMNOTEQUAL",
    OpCodeType.OP_LESSTHAN: "OP_LESSTHAN",
    OpCodeType.OP_GREATERTHAN: "OP_GREATERTHAN",
    OpCodeType.OP_LESSTHANOREQUAL: "OP_LESSTHANOREQUAL",
    OpCodeType.OP_GREATERTHANOREQUAL: "OP_GREATERTHANOREQUAL",
    OpCodeType.OP_MIN: "OP_MIN",
    OpCodeType.OP_MAX: "OP_MAX",
    OpCodeType.OP_WITHIN: "OP_WITHIN",

    # crypto
    OpCodeType.OP_RIPEMD160: "OP_RIPEMD160",
    OpCodeType.OP_SHA1: "OP_SHA1",
    OpCodeType.OP_SHA256: "OP_SHA256",
    OpCodeType.OP_HASH160: "OP_HASH160",
    OpCodeType.OP_HASH256: "OP_HASH256",
    OpCodeType.OP_CODESEPARATOR: "OP_CODESEPARATOR",
    OpCodeType.OP_CHECKSIG: "OP_CHECKSIG",
    OpCodeType.OP_CHECKSIGVERIFY: "OP_CHECKSIGVERIFY",
    OpCodeType.OP_CHECKMULTISIG: "OP_CHECKMULTISIG",
    OpCodeType.OP_CHECKMULTISIGVERIFY: "OP_CHECKMULTISIGVERIFY",

    # multi-byte opcodes
    OpCodeType.OP_SINGLEBYTE_END: "OP_SINGLEBYTE_END",
    OpCodeType.OP_DOUBLEBYTE_BEGIN: "OP_DOUBLEBYTE_BEGIN",
    OpCodeType.OP_PUBKEY: "OP_PUBKEY",
    OpCodeType.OP_PUBKEYHASH: "OP_PUBKEYHASH",
    OpCodeType.OP_INVALIDOPCODE: "OP_INVALIDOPCODE",
}


# @params_check(OpCodeType)
def get_op_name(op_code):
    if op_code in __op_code:
        return __op_code[op_code]
    return "UNKNOWN_OPCODE"


#####
##   CScript:
##   vector<unsigned char> containing built-in little scripting-language script
##   (opcodes and arguments to do crypto stuff)
class PyScript(bytearray):
    def __init__(self, in_val=None, val_type=None):  # val_type is uint160 or uint 256
        """
        可以使用 num, OpCodeType，str|bytearray|PyScrip，hash 初始化PyScript。\n
        * 使用 hash 的时候要填写 val_type (uint160|uint256)  \n
        * 使用 str|bytearray|PyScrip 的时候不做任何修改直接填充  \n
        :param in_val:
        :type in_val int | long | str | bytearray | PyScript
        :param val_type: uint160|uint256
        """
        super(PyScript, self).__init__()
        if in_val is not None:
            self.__append(in_val, val_type)
        pass

    def get_str(self):
        return super(PyScript, self).__str__()

    def append_num(self, num):
        if num == -1 or (1 <= num <= 16):
            super(PyScript, self).append(serialize.ser_char(num + (OpCodeType.OP_1 - 1)))
        else:
            self.extend(bignum.PyBigNum(num).getvch())
        return self

    def append_op(self, opcode):
        if opcode <= OpCodeType.OP_SINGLEBYTE_END:
            super(PyScript, self).append(opcode)
        else:
            # OP_DOUBLEBYTE_BEGIN 0xF000  这里就是说超过1B 的操作符号 以大端存储的方式拆成2B存下来
            assert opcode >= OpCodeType.OP_DOUBLEBYTE_BEGIN
            super(PyScript, self).append((opcode >> 8) & 0xFF)  # 先存高位
            super(PyScript, self).append(opcode & 0xFF)  # 后存低位
            # bytes('高8位', '低8位')， 大端存储
        return self

    def append_hash(self, u, hash_bytes):
        if hash_bytes == 20:
            super(PyScript, self).append(hash_bytes)
            super(PyScript, self).extend(serialize.ser_uint160(u))
        elif hash_bytes == 32:
            super(PyScript, self).append(hash_bytes)
            super(PyScript, self).extend(serialize.ser_uint256(u))
        else:
            raise RuntimeError("bytes of param is 20(uint160) or 32(uint256)")
        return self

    def op_init(self, l_op):
        assert isinstance(l_op, list), 'l_op is list for op'
        del self[:]
        ret = [True if i <= OpCodeType.OP_SINGLEBYTE_END or i >= OpCodeType.OP_DOUBLEBYTE_BEGIN else False
               for i in l_op]
        assert ret, "list element must use OpType, wrong for:" + str(ret)
        [self.append(i) for i in l_op]
        return self

    def __append(self, in_var, val_type):
        if isinstance(in_var, OpCodeType):
            self.append_op(in_var)
        elif isinstance(in_var, int) or isinstance(in_var, long):
            if in_var <= 0x00FFFFFFFFFFFFFFFF:  # int64 and uint64
                self.append_num(in_var)
            else:
                if val_type == 'uint160':
                    self.append_hash(in_var, 20)
                elif val_type == 'uint256':
                    self.append_hash(in_var, 32)
                else:
                    raise RuntimeError(
                        "param larger than uint64 or int64 is unsupported or use hash must point hash bytes`")
        elif isinstance(in_var, str) or isinstance(in_var, bytearray):
            # equal to init with raw
            super(PyScript, self).extend(in_var)
        else:
            raise RuntimeError("Unknown type to init PyScript")
        return self

    def append(self, p_var, var_type=None):
        """
        将num，OpCodeType，hash(num) 序列化成 script，当操作的是hash的时候一定要填写var_type (uint160|uint256)\n
        注：不能append str|bytearray|PyScript，若使用，其长度必须为1 \n
        :param p_var:
        :type p_var int | long | str | bytearray | PyScript
        :param var_type: uint160|uint256
        :return:
        """
        if isinstance(p_var, str) or isinstance(p_var, bytearray) and len(p_var) != 1:
            raise RuntimeError("when append str or bytearray, the length must be 1")
        return self.__append(p_var, var_type)

    def extend(self, iterable_var, raw=False):
        """
        使用 str | bytearray 扩充PyScript. 当使用 PyScript 的时候不做任何修改直接附加到Script末尾\n
        当使用 raw=True 时同样不会修改 \n
        :param iterable_var: str | bytearray | PyScript
        :param raw:
        :return:
        """
        # 这里我可以支持 extend PyScript 而不是像源代码那样禁止
        if type(iterable_var) is PyScript:
            raw = True
        if raw:
            super(PyScript, self).extend(iterable_var)
            return self

        size = len(iterable_var)
        if size < OpCodeType.OP_PUSHDATA1:  # 76(0x4c)
            super(PyScript, self).append(size)
        elif size <= 0xff:  # 1B
            super(PyScript, self).append(OpCodeType.OP_PUSHDATA1)
            super(PyScript, self).append(size)
        else:
            super(PyScript, self).append(OpCodeType.OP_PUSHDATA2)
            # l_len large than one byte
            # l_len is unsigned short
            super(PyScript, self).extend(typeutil.str_from_ushort(size))
        super(PyScript, self).extend(iterable_var)
        return self

    def get_op(self, index):
        opcode_ret = OpCodeType.OP_INVALIDOPCODE
        ret = None
        # read instruction
        bytes_size = len(self)
        if index >= bytes_size:
            return None
        opcode = self[index]
        index += 1
        # 如果当前的操作数是一个超过1B的op,那么就把下一B也取出来组合出完整的op
        if opcode >= OpCodeType.OP_SINGLEBYTE_END:
            if index + 1 > bytes_size:
                return None
            opcode <<= 8
            opcode |= self[index]  # 这里对应 append_op 中的 大端
            index += 1
        # Immediate operand
        if opcode <= OpCodeType.OP_PUSHDATA4:  # 1B, OP_PUSHDATA4 = 78(0x4E)
            size = opcode
            if opcode == OpCodeType.OP_PUSHDATA1:
                if index + 1 > bytes_size:
                    return None
                size = self[index]
                index += 1
            elif opcode == OpCodeType.OP_PUSHDATA2:
                if index + 2 > bytes_size:
                    return None
                size = typeutil.ushort_from_str(bytes(self[index:index + 2]))
                index += 2
            elif opcode == OpCodeType.OP_PUSHDATA4:  # 貌似目前是走不到这里的
                if index + 4 > bytes_size:
                    return None
                size = typeutil.uint_from_str(bytes(self[index:index + 4]))
                index += 4

            if (index + size) > bytes_size:  # 就是小于 0x4e长度的
                return None
            ret = self[index: index + size]
            index += size
        opcode_ret = opcode
        return index, opcode_ret, ret

    def find_and_delete(self, script):
        assert isinstance(script, PyScript), "parameter must be PyScript"
        index = 0
        bytes_size = len(self)
        find_bytes_size = len(script)
        # opcode = 0
        count = 0
        # l_ret = bytearray()
        while True:
            while (bytes_size - index >= find_bytes_size
                   and self[index:index + find_bytes_size] == script):
                del self[index:index + find_bytes_size]
                count += 1

            op_ret = self.get_op(index)
            # return index, opcode_ret, ret
            if op_ret is None:
                break
            index = op_ret[0]
            # opcode = op_ret[1]
            # l_ret = op_ret[2]
        return count

    def print_hex(self, in_var=None):
        return ':'.join(['%02x' % i for i in (in_var if in_var else self)])

    def __deepcopy__(self, memodict={}):
        s = PyScript()
        s.extend(self)
        return s

    def __add__(self, other):
        new_script = PyScript()
        new_script.extend(self)
        super(PyScript, new_script).extend(other)
        return new_script

    def __radd__(self, other):
        if type(other) is bytearray or type(other) is str:
            other = PyScript().extend(other)  # change str to PyScript
        return other.__add__(self)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        index = 0
        ret_str_list = []
        while True:
            op_ret = self.get_op(index)
            if op_ret is None:
                break
            index = op_ret[0]
            opcode = op_ret[1]
            l_ret = op_ret[2]

            if opcode <= OpCodeType.OP_PUSHDATA4:
                ret_str_list.append(self.print_hex(l_ret))
            else:
                ret_str_list.append(get_op_name(opcode))

        return 'pyscript: ' + ' '.join(ret_str_list)

    pass


TEMPLATES = [
    # Standard tx, sender provides pubkey, receiver adds signature
    PyScript().op_init([OpCodeType.OP_PUBKEY, OpCodeType.OP_CHECKSIG]),
    # Short account number tx, sender provides hash of pubkey, receiver provides signature and pubkey
    PyScript().op_init([OpCodeType.OP_DUP, OpCodeType.OP_HASH160, OpCodeType.OP_PUBKEYHASH,
                        OpCodeType.OP_EQUALVERIFY, OpCodeType.OP_CHECKSIG])
]


#
# Script is a stack machine (like Forth) that evaluates a predicate
# returning a bool indicating valid or not.  There are no loops.
#
# script is scirpt_sig + op.sep + script_pubkey
def eval_scrip(script, tx_to, nin, hash_type=0, endian='small'):
    pc = 0
    pend = len(script)
    p_begin_code_hash = 0
    exec_ret = list()
    stack = list()
    altstack = list()
    while pc < pend:
        exec_r = not exec_ret.count(False)
        # read instruction
        ret = script.get_op(pc)  # return index, opcode_ret, ret
        if ret is None:
            return False
        pc = ret[0]
        opcode = ret[1]
        push_value = ret[2]
        if push_value is not None:
            push_value = str(push_value)

        if exec_r and opcode <= OpCodeType.OP_PUSHDATA4:
            stack.append(push_value)
        elif exec_r or (OpCodeType.OP_IF <= opcode <= OpCodeType.OP_ENDIF):
            # Push value
            if OpCodeType.OP_1NEGATE == opcode or \
                    (OpCodeType.OP_1 <= opcode <= OpCodeType.OP_16):
                # ( -- value)
                # CBigNum bn((int)opcode - (int)(OP_1 - 1)); (和 pyscript 的 append时候<16 + op_1 相对应)
                bn = bignum.PyBigNum(opcode - (OpCodeType.OP_1 - 1))
                stack.append(bn.getvch())
            # Control  控制流程
            elif opcode == OpCodeType.OP_NOP:
                pass
            elif opcode == OpCodeType.OP_VER:
                stack.append(bignum.PyBigNum(VERSION).getvch())

            # if 控制部分
            elif OpCodeType.OP_IF <= opcode <= OpCodeType.OP_VERNOTIF:
                # OP_IF OP_NOTIF OP_VERIF OP_VERNOTIF
                # <expression> if [statements] [else [statements]] endif
                value_r = False
                if exec_r:
                    if len(stack) < 1:
                        return False
                    v = stack[-1]  # stacktop(-1);
                    if opcode == OpCodeType.OP_VERIF or opcode == OpCodeType.OP_VERNOTIF:
                        # compare version
                        value_r = bignum.PyBigNum(VERSION) >= bignum.PyBigNum(v)
                    else:
                        value_r = typeutil.cast_to_bool(v)

                    if opcode == OpCodeType.OP_NOTIF or opcode == OpCodeType.OP_VERNOTIF:
                        value_r = not value_r
                    stack.pop()  # stack.pop_back(); 出栈
                exec_ret.append(value_r)
            # else 控制部分
            elif opcode == OpCodeType.OP_ELSE:
                if len(exec_ret) == 0:  # else 的判断数为空
                    return False
                exec_ret[-1] = not exec_ret[-1]  # 把判断数取反
            # end if
            elif opcode == OpCodeType.OP_ENDIF:
                if len(exec_ret) == 0:  # 走完控制流却没有结果
                    return False
                exec_ret.pop()  # vfExec.pop_back();
            # verify 部分
            elif opcode == OpCodeType.OP_VERIFY:
                # (true -- ) or
                # (false -- false) and return
                if len(stack) < 1:  # 执行栈空了
                    return False
                value_r = typeutil.cast_to_bool(stack[-1])
                if value_r:
                    stack.pop()
                else:
                    pc = pend  # verify 错误
            elif opcode == OpCodeType.OP_RETURN:
                pc = pend

            # Stack ops
            elif opcode == OpCodeType.OP_TOALTSTACK:
                if len(stack) < 1:
                    return False
                # altstack.push_back(stacktop(-1));
                # stack.pop_back();
                altstack.append(stack.pop())  # pop 出stack 进入 altstack
            elif opcode == OpCodeType.OP_FROMALTSTACK:
                if len(altstack) < 1:
                    return False
                # stack.push_back(altstacktop(-1));
                # altstack.pop_back();
                stack.append(altstack.pop())  # 从 altstack转移到stack
            elif opcode == OpCodeType.OP_2DROP:  # op_2drop -> 丢掉2个数
                # (x1 x2 -- )
                stack.pop()
                stack.pop()
            elif opcode == OpCodeType.OP_2DUP:  # op_2dup 复制栈顶2个数(按顺序)
                # (x1 x2 -- x1 x2 x1 x2)
                if len(stack) < 2:
                    return False
                v1 = stack[-2]
                v2 = stack[-1]
                stack.append(copy.deepcopy(v1))  # 防止 stack 的内容是 bytearray 时 append只添加一个引用
                stack.append(copy.deepcopy(v2))
            elif opcode == OpCodeType.OP_3DUP:  # op_3dup 复制栈顶3个数(按顺序)
                # (x1 x2 x3 -- x1 x2 x3 x1 x2 x3)
                if len(stack) < 3:
                    return False
                v1 = stack[-3]
                v2 = stack[-2]
                v3 = stack[-1]
                stack.append(copy.deepcopy(v1))
                stack.append(copy.deepcopy(v2))
                stack.append(copy.deepcopy(v3))
            elif opcode == OpCodeType.OP_2OVER:  # op_2over 跳过一个栈顶元素，复制栈顶下面的那个
                # (x1 x2 -- x1 x2 x1)
                if len(stack) < 2:
                    return False
                v = stack[-2]
                stack.append(copy.deepcopy(v))
            elif opcode == OpCodeType.OP_2ROT:  # op_2rot转移2个数据到栈顶
                # (x1 x2 x3 x4 x5 x6 -- x3 x4 x5 x6 x1 x2)
                if len(stack) < 6:
                    return False
                v1 = stack[-6]
                v2 = stack[-5]
                del stack[-6: -4]  # 左闭右开
                stack.append(v1)
                stack.append(v2)
            elif opcode == OpCodeType.OP_2SWAP:  # op_2swap 2个为一组交换
                # (x1 x2 x3 x4 -- x3 x4 x1 x2)
                if len(stack) < 4:
                    return False
                stack[-4], stack[-2] = stack[-2], stack[-4]
                stack[-3], stack[-1] = stack[-1], stack[-3]
            elif opcode == OpCodeType.OP_IFDUP:  # op_ifdup 如果栈顶元素有效就复制，否则不处理
                # // (x - 0 | x x)
                if len(stack) < 1:
                    return False
                v = stack[-1]
                if typeutil.cast_to_bool(v):
                    stack.append(v)
            elif opcode == OpCodeType.OP_DEPTH:  # 获取栈高，并把高度入栈
                # -- stacksize
                stack.append(bignum.PyBigNum(len(stack)).getvch())
            elif opcode == OpCodeType.OP_DROP:  # op_drop 丢弃栈顶元素
                # (x -- )
                if len(stack) < 1:
                    return False
                stack.pop()
            elif opcode == OpCodeType.OP_DUP:  # op_dup 复制栈顶
                # (x -- x x)
                if len(stack) < 1:
                    return False
                stack.append(copy.deepcopy(stack[-1]))
            elif opcode == OpCodeType.OP_NIP:  # op_nip 剔除倒数第2个
                # (x1 x2 -- x2)
                if len(stack) < 2:
                    return False
                del stack[-2]
            elif opcode == OpCodeType.OP_OVER:
                # (x1 x2 -- x1 x2 x1)
                if len(stack) < 2:
                    return False
                stack.append(copy.deepcopy(stack[-2]))
            elif opcode == OpCodeType.OP_PICK or \
                            opcode == OpCodeType.OP_ROLL:  # op_pick 找到从栈顶向下数第n个元素并复制到栈顶， op_roll 找到那个元素并移到栈顶
                # (xn ... x2 x1 x0 n - xn ... x2 x1 x0 xn)
                # (xn ... x2 x1 x0 n - ... x2 x1 x0 xn)
                if len(stack) < 2:
                    return False
                # int n = CBigNum(stacktop(-1)).getint();
                # stack.pop_back();
                n = int(bignum.PyBigNum(stack.pop()))
                if n < 0 or n > len(stack):
                    return False
                v = stack[-n - 1]  # 取出倒数第n个元素
                if opcode == OpCodeType.OP_ROLL:
                    del stack[-n - 1]  # 把倒数第n个元素剔除
                stack.append(copy.deepcopy(v))  # 把刚才找到的倒数第n个元素放在最上面
            elif opcode == OpCodeType.OP_ROT:  # op_rot 把从栈顶倒数第3个元素移动到栈顶(rotation?`)
                # (x1 x2 x3 -- x2 x3 x1)
                # x2 x1 x3  after first swap
                # x2 x3 x1  after second swap
                if len(stack) < 3:
                    return False
                stack[-3], stack[-2] = stack[-2], stack[-3]
                stack[-2], stack[-1] = stack[-1], stack[-2]
            elif opcode == OpCodeType.OP_SWAP:  # 交换栈顶2个元素
                # (x1 x2 -- x2 x1)
                if len(stack) < 2:
                    return False
                stack[-2], stack[-1] = stack[-1], stack[-2]
            elif opcode == OpCodeType.OP_TUCK:  # 把栈顶元素复制一份插入到原来栈顶向下的倒数第2个位置
                # x1 x2 -- x2 x1 x2)
                if len(stack) < 2:
                    return False
                v = stack[-1]
                stack.insert(-2, v)

            # Splice ops
            elif opcode == OpCodeType.OP_CAT:  # op_cat 把栈顶元素添加到倒数第2个元素的末尾并剔除栈顶元素
                # (x1 x2 -- out)  这个描述不太对？
                if len(stack) < 2:
                    return False
                v1 = stack[-2]
                v2 = stack[-1]
                stack[-2] = v1 + v2
                stack.pop()
            elif opcode == OpCodeType.OP_SUBSTR:  # 修改倒数第3个元素长度，从倒数第2个元素的位置开始剔除栈顶元素的长度
                # (in begin size -- out)
                if len(stack) < 3:
                    return False
                v = stack[-3]
                str_size = len(v)
                begin = bignum.PyBigNum(stack[-2]).getint()
                end = begin + bignum.PyBigNum(stack[-1]).getint()
                if begin < 0 or end < begin:
                    return False
                if begin > str_size:
                    begin = str_size
                if end > str_size:
                    end = str_size
                stack[-3] = v[:begin] + v[end:]
                stack.pop()
                stack.pop()
            elif opcode == OpCodeType.OP_LEFT or \
                            opcode == OpCodeType.OP_RIGHT:  # left 表示保留左边，right表示保留右边
                # (in size -- out)
                if len(stack) < 2:
                    return False
                v = stack[-2]
                str_size = len(v)
                size = bignum.PyBigNum(v).getint()
                if size < 0:
                    return False
                if size > str_size:
                    size = str_size
                if opcode == OpCodeType.OP_LEFT:
                    stack[-2] = v[:size]
                else:
                    stack[-2] = v[-size:]
                stack.pop()
            elif opcode == OpCodeType.OP_SIZE:  # op_size 获取栈顶元素的长度并把这个长度也入栈,注意是元素长度不是栈的长度
                # (in -- in size)
                if len(stack) < 1:
                    return False
                size = len(stack[-1])
                stack.append(bignum.PyBigNum(size).getvch())

            # Bitwise logic
            elif opcode == OpCodeType.OP_INVERT:  # op_invert 取反
                # (in - out)
                stack[-1] = bignum.invert_vch(stack[-1])
            elif opcode == OpCodeType.OP_AND or \
                            opcode == OpCodeType.OP_OR or \
                            opcode == OpCodeType.OP_XOR:  # op_and op_or op_xor 把栈顶和下一个元素进行每个字节的位运算
                # (x1 x2 - out)
                if len(stack) < 2:
                    return False
                v1 = stack[-2]
                v2 = stack[-1]
                if opcode == OpCodeType.OP_AND:
                    stack[-2] = bignum.and_vch(v1, v2)
                elif opcode == OpCodeType.OP_OR:
                    stack[-2] = bignum.or_vch(v1, v2)
                elif opcode == OpCodeType.OP_XOR:
                    stack[-2] = bignum.xor_vch(v1, v2)
                stack.pop()
            elif opcode == OpCodeType.OP_EQUAL or \
                            opcode == OpCodeType.OP_EQUALVERIFY:
                # (x1 x2 - bool)
                if len(stack) < 2:
                    return False
                # v1, v2 = stack[-2], stack[-1]
                v2, v1 = stack.pop(), stack.pop()  # v2 栈顶， v1倒数第2个
                equal_r = v1 == v2
                # OP_NOTEQUAL is disabled because it would be too easy to say
                # something like n != 1 and have some wiseguy pass in 1 with extra
                # zero bytes after it (numerically, 0x01 == 0x0001 == 0x000001)
                # if (opcode == OP_NOTEQUAL)
                #    fEqual = !fEqual;
                # 这段注释是说 这里保证的是 vector<unsigned int> 相等，不保证数字上的相等
                stack.append(bignum.vch_true if equal_r else bignum.vch_false)
                if opcode == OpCodeType.OP_EQUALVERIFY:
                    if equal_r:
                        stack.pop()
                    else:
                        pc = pend
            # Numeric
            elif OpCodeType.OP_1ADD <= opcode <= OpCodeType.OP_0NOTEQUAL:
                # OP_1ADD OP_1SUB OP_2MUL OP_2DIV OP_NEGATE OP_ABS OP_NOT OP_0NOTEQUAL
                if len(stack) < 1:
                    return False
                num = bignum.PyBigNum(stack.pop())
                if opcode == OpCodeType.OP_1ADD:
                    num += 1
                elif opcode == OpCodeType.OP_1SUB:
                    num -= 1
                elif opcode == OpCodeType.OP_2MUL:
                    num <<= 1
                elif opcode == OpCodeType.OP_2DIV:
                    num >>= 1
                elif opcode == OpCodeType.OP_NEGATE:
                    num = -num
                elif opcode == OpCodeType.OP_ABS:
                    num = abs(num)
                elif opcode == OpCodeType.OP_NOT:
                    num = (num == 0)
                elif opcode == OpCodeType.OP_0NOTEQUAL:
                    num = (num != 0)  # 这里保证是数字上等0
                    # num is long now
                stack.append(bignum.PyBigNum(num).getvch())
            elif OpCodeType.OP_ADD <= opcode <= OpCodeType.OP_MAX:
                # OP_ADD OP_SUB OP_MUL OP_DIV OP_MOD OP_LSHIFT OP_RSHIFT
                # OP_BOOLAND OP_BOOLOR OP_NUMEQUAL OP_NUMEQUALVERIFY OP_NUMNOTEQUAL
                # OP_LESSTHAN OP_GREATERTHAN OP_LESSTHANOREQUAL OP_GREATERTHANOREQUAL
                # OP_MIN OP_MAX
                # (x1 x2 -- out)  注意这里2个后一个数，所以对于-(/)来说，是栈顶倒数第2个数减去栈顶
                if len(stack) < 2:
                    return False
                # CBigNum bn1(stacktop(-2));
                # CBigNum bn2(stacktop(-1));
                num2 = bignum.PyBigNum(stack.pop())  # 栈顶
                num1 = bignum.PyBigNum(stack.pop())  # 栈顶倒数第2个
                num_ret = bignum.PyBigNum(0)
                if opcode == OpCodeType.OP_ADD:
                    num_ret = num1 + num2
                elif opcode == OpCodeType.OP_SUB:
                    num_ret = num1 - num2
                elif opcode == OpCodeType.OP_MUL:
                    num_ret = num1 * num2
                elif opcode == OpCodeType.OP_DIV:
                    if num2 == 0:
                        return False
                    num_ret = num1 / num2
                elif opcode == OpCodeType.OP_MOD:
                    if num2 == 0:
                        return False
                    num_ret = num1 % num2
                elif opcode == OpCodeType.OP_LSHIFT:
                    if num2 < 0:
                        return False
                    num_ret = num1 << num2
                elif opcode == OpCodeType.OP_RSHIFT:
                    if num2 < 0:
                        return False
                    num_ret = num1 >> num2
                elif opcode == OpCodeType.OP_BOOLAND:
                    num_ret = (num1 != 0 and num2 != 0)
                elif opcode == OpCodeType.OP_BOOLOR:
                    num_ret = (num1 != 0 or num2 != 0)
                elif opcode == OpCodeType.OP_NUMEQUAL:
                    num_ret = (num1 == num2)
                elif opcode == OpCodeType.OP_NUMEQUALVERIFY:
                    num_ret = (num1 == num2)
                elif opcode == OpCodeType.OP_NUMNOTEQUAL:
                    num_ret = (num1 != num2)
                elif opcode == OpCodeType.OP_LESSTHAN:
                    num_ret = (num1 < num2)
                elif opcode == OpCodeType.OP_GREATERTHAN:
                    num_ret = (num1 > num2)
                elif opcode == OpCodeType.OP_LESSTHANOREQUAL:
                    num_ret = (num1 <= num2)
                elif opcode == OpCodeType.OP_GREATERTHANOREQUAL:
                    num_ret = (num1 >= num2)
                elif opcode == OpCodeType.OP_MIN:
                    num_ret = min(num1, num2)
                elif opcode == OpCodeType.OP_MAX:
                    num_ret = max(num1, num2)
                    # num_ret is long now
                stack.append(bignum.PyBigNum(num_ret).getvch())
                if opcode == OpCodeType.OP_NUMEQUALVERIFY:
                    if typeutil.cast_to_bool(stack.pop()):
                        pass
                    else:
                        pc = pend
            elif opcode == OpCodeType.OP_WITHIN:  # op_within 判定范围
                # (x min max -- out)
                if len(stack) < 3:
                    return False
                # CBigNum bn1(stacktop(-3));
                # CBigNum bn2(stacktop(-2));
                # CBigNum bn3(stacktop(-1));
                num3 = bignum.PyBigNum(stack.pop())  # 栈顶
                num2 = bignum.PyBigNum(stack.pop())  # 倒数第2个
                num1 = bignum.PyBigNum(stack.pop())  # 倒数第3个
                r = (num2 <= num1 <= num3)
                stack.append(bignum.vch_true if r else  bignum.vch_false)
            # Crypto
            elif OpCodeType.OP_RIPEMD160 <= opcode <= OpCodeType.OP_HASH256:
                # OP_RIPEMD160 OP_SHA1 OP_SHA1 OP_HASH160 OP_HASH256
                # (in -- hash)
                if len(stack) < 1:
                    return False
                v = stack.pop()
                hash_ret = b''
                if opcode == OpCodeType.OP_RIPEMD160:
                    hash_ret = cryptoutil.Ripemd160(v, output_type='str')
                elif opcode == OpCodeType.OP_SHA1:
                    hash_ret = cryptoutil.Sha1(v, output_type='str')
                elif opcode == OpCodeType.OP_SHA256:
                    hash_ret = cryptoutil.Sha256(v, output_type='str')
                elif opcode == OpCodeType.OP_HASH160:
                    hash_ret = cryptoutil.Hash160(v, out_type='str')
                elif opcode == OpCodeType.OP_HASH256:
                    hash_ret = cryptoutil.Hash(v, out_type='str')
                stack.append(hash_ret)
            elif opcode == OpCodeType.OP_CODESEPARATOR:  # 分隔符
                # Hash starts after the code separator
                p_begin_code_hash = pc
            elif opcode == OpCodeType.OP_CHECKSIG or \
                            opcode == OpCodeType.OP_CHECKSIGVERIFY:
                # (sig pubkey -- bool)
                if len(stack) < 2:
                    return False
                # valtype& vchSig    = stacktop(-2);
                # valtype& vchPubKey = stacktop(-1);
                str_pubkey = stack.pop()  # 栈顶
                str_sig = stack.pop()  # 倒数第2个
                # debug  #TODO add log
                print (serialize.hexser_uint256(str_pubkey, in_type="str"))
                print (serialize.hexser_uint256(str_sig, in_type="str"))
                # Subset of script starting at the most recent codeseparator
                script_code = PyScript(script[p_begin_code_hash:pend])
                # Drop the signature, since there's no way for a signature to sign itself
                script_code.find_and_delete(PyScript(str_sig))

                success = check_sig(str_sig, str_pubkey, script_code, tx_to, nin, hash_type)
                stack.append(bignum.vch_true if success else bignum.vch_false)
                if opcode == OpCodeType.OP_CHECKSIGVERIFY:
                    if success:
                        stack.pop()
                    else:
                        pc = pend
            elif opcode == OpCodeType.OP_CHECKMULTISIG or \
                            opcode == OpCodeType.OP_CHECKMULTISIGVERIFY:
                # ([sig ...] num_of_signatures [pubkey ...] num_of_pubkeys -- bool)
                if len(stack) < 1:
                    return False
                i = 1
                keys_count = bignum.PyBigNum(stack[-i]).getint()  # num_of_pubkeys
                if keys_count < 0:
                    return False
                i += 1
                ikey = i
                i += keys_count
                if len(stack) < i:  # watch out!
                    return False
                sigs_count = bignum.PyBigNum(stack[-i]).getint()
                if sigs_count < 0 or sigs_count > keys_count:
                    return False
                i += 1
                isig = i
                i += sigs_count
                # watch out! ??? TODO sig <= pubkey, but if sigs_count = len(sigs) stack.size() will less than i
                # there must be a element add to end of sigs and not include to sigs_count,and it would be pop later
                if len(stack) < i:
                    return False
                # Subset of script starting at the most recent codeseparator
                script_code = PyScript(script[p_begin_code_hash:pend])
                # Drop the signatures, since there's no way for a signature to sign itself
                for i in range(sigs_count):
                    script_code.find_and_delete(PyScript(stack[-isig - i]))
                success = True
                while success and sigs_count > 0:
                    str_sig = stack[-isig]
                    str_pubkey = stack[-ikey]
                    if check_sig(str_sig, str_pubkey, script_code, tx_to, nin, hash_type):
                        isig += 1
                        sigs_count -= 1
                    ikey += 1
                    keys_count -= 1
                    # If there are more signatures left than keys left,
                    # then too many signatures have failed
                    if sigs_count > keys_count:
                        success = False
                # TODO 源码这里难道有Bug? 按照这样的逻辑会多Pop出一个？？
                # https://github.com/bitcoin/bitcoin/blob/v0.9.5rc2/src/script.cpp#L1014
                # https://github.com/bitcoin/bitcoin/blob/v0.10.0/src/script/interpreter.cpp#L890
                # 0.9.5 -> 0.10.0 改正了这个地方 确实是Bug
                # while True:
                #     if i <= 0:
                #         break
                #     i -= 1
                #     stack.pop()
                del stack[-i + 1:]  # 以修正的方式写
                stack.append(bignum.vch_true if success else bignum.vch_false)
                if opcode == OpCodeType.OP_CHECKMULTISIGVERIFY:
                    if success:
                        stack.pop()
                    else:
                        pc = pend
            # 没有捕获任何一个操作数
            else:
                return False

    if len(stack) == 0 or not typeutil.cast_to_bool(stack[-1]):
        return False
    return stack


# 这里就是生成stack
def solver2(script_pubkey):
    """
    根据 script_pubkey 脚本的要求生成初始指令数据栈 solution => list() -> tuple(op, data) \n
    :param script_pubkey:
    :type script_pubkey: PyScript
    :return: None 表示过程出错，生成正确为 一个元组的list list() -> tuple(op, data), 其中元组为 (操作数，操作数对应的数据)
    """
    l_solution = list()
    # scan templates:
    script1 = script_pubkey
    for script2 in TEMPLATES:
        # opcode1 = OpCodeType.OP_INVALIDOPCODE
        # opcode2 = OpCodeType.OP_INVALIDOPCODE
        # l_ret1 = None
        # l_ret2 = None
        index1 = 0  # for scrip1
        index2 = 0  # for scrip2(s)
        while True:
            r1 = script1.get_op(index1)
            r2 = script2.get_op(index2)  # index, opcode_ret, ret
            if r1 is None and r2 is None:  # 两边都是空
                return reversed(l_solution)
            elif (r1 is not None and r2 is None) or (r1 is None and r2 is not None):
                # 其中一个为空
                break
            # 两个都存在
            index1 = r1[0]
            index2 = r2[0]
            opcode1 = r1[1]
            l_ret1 = r1[2]
            opcode2 = r2[1]
            l_ret2 = r2[2]
            if opcode2 == OpCodeType.OP_PUBKEY:
                if l_ret1 is None or len(l_ret1) <= 32:  # uint256 size
                    break
                # stack 中加入公钥(公钥为33B或65B)
                l_solution.append((opcode2, l_ret1))
            elif opcode2 == OpCodeType.OP_PUBKEYHASH:
                if l_ret1 is None or len(l_ret1) != 20:  # uint160 size
                    break
                l_solution.append((opcode2, l_ret1))
            elif opcode1 != opcode2:
                break
    return None


def solver(script_pubkey, uint256_hash, hash_type):
    """
    生成对应pubkey_script的解密签名脚本 script_sig, \n
    如果传入的 hash == 0，那么就是用来验证pubkey_script的pubkey是否在本地(自身) \n
    :param script_pubkey:
    :type script_pubkey: PyScript
    :param uint256_hash:  是只包含 对应的 txin 其他 txin 都是空的 tx 的hash
    :param hash_type:
    :return: 返回 None 表示验证过程出错，返回scrip_pubkey 表示成功，注意在传入hash为0的时候，script_pubkey本身是空(len(s)=0)
    :rtype None | PyScript
    """
    script_sig = PyScript()
    if isinstance(script_pubkey, (str, bytearray)):  # TODO check this point
        script_pubkey = PyScript(script_pubkey)
    l_solution = solver2(script_pubkey)  # -> list()->(op,data)
    if l_solution is None:
        return None
    # Compile solution
    with ctx.dictKeysLock:
        # fir 是操作数， ser 是数据
        for fir, sec in l_solution:
            if fir == OpCodeType.OP_PUBKEY:
                # sign
                pubkey = str(sec)
                if not (pubkey in ctx.dictKeys):
                    return None
                if uint256_hash != 0:
                    if isinstance(uint256_hash, (long, int)):
                        uint256_hash = serialize.ser_uint256(uint256_hash)
                    sig = PyKey.static_sign(ctx.dictKeys[pubkey], uint256_hash)  # use prikey to sign !
                    # l_sig is str
                    if sig is None:
                        return None
                    # in source code, is int => (unsigned char) only choose one char
                    sig += serialize.ser_uchar(hash_type)
                    # l_sig length is 72B
                    # Sig is result of sign
                    script_sig.extend(sig)  # now script_sig is l_sig
            elif fir == OpCodeType.OP_PUBKEYHASH:
                pubkey = ctx.dictPubKeys.get(str(sec), None)
                if pubkey is None:
                    return None
                if uint256_hash != 0:
                    if isinstance(uint256_hash, (long, int)):
                        uint256_hash = serialize.ser_uint256(uint256_hash)
                    sig = PyKey.static_sign(ctx.dictKeys[pubkey], uint256_hash)  # use prikey to sign !
                    if sig is None:
                        return None
                    sig += serialize.ser_uchar(hash_type)
                    # l_sig length is 72B
                    script_sig.extend(sig)  # now script_sig is l_sig
                    # pubkey is 33B or 65B
                    script_sig.extend(pubkey)
            pass  # end loop for solution
    return script_sig


def is_mine(script_pubkey):
    """
    判定传入的 script_pubkey 说含有的pubkey 是否在本地，来判断这个out是否是指向自己的地址
    :param script_pubkey:
    :return:
    """
    script_sig = solver(script_pubkey, 0, 0)  # hash ==0 表示不使用hash产生作用，相当于只是验证script_pubkey是否合理
    return True if script_sig is not None else False


def signature_hash(script_code, tx_to, nin, hash_type, out_type='str'):
    if nin >= len(tx_to.l_in):
        # TODO add log
        print ("ERROR: SignatureHash() : nIn=%d out of range" % nin)
        return 1
    tx_tmp = copy.deepcopy(tx_to)
    # In case concatenating two scripts ends up with two codeseparators,
    # or an extra one at the end, this prevents all those possible incompatibilities.
    script_code.find_and_delete(PyScript(OpCodeType.OP_CODESEPARATOR))
    # Blank out other inputs' signatures
    for txin in tx_tmp.l_in:
        txin.script_sig = PyScript()  # reinit for script_sig
    tx_tmp.l_in[nin].script_sig = script_code  # set out.script_pubkey(script_code) to script_sig
    # Blank out some of the outputs
    and_ret = hash_type & 0x1F  # SignType.SIGHASH_ANYONECANPAY is 0x80
    if and_ret == SignType.SIGHASH_NONE:
        # Wildcard payee  任意收款人(不指定收款方 撒钱？完成脚本规定的某个任务)
        tx_tmp.l_out = list()
        # Let the others update at will
        for i in range(len(tx_tmp.l_in)):
            if i != nin:  # 把 非指定的 in 的 seq 全部改成0
                tx_tmp.l_in[i].sequence = 0
    elif and_ret == SignType.SIGHASH_SINGLE:
        # Only lockin the txout payee at same index as txin
        nout = nin  # nin 是当前在计算第几个 in
        if nout >= len(tx_tmp.l_out):
            print ("ERROR: SignatureHash() : nOut=%d out of range" % nout)
            return 1
        for i in range(nout):  # 把 nin 对应的 out(按顺序) 之前的都置空
            tx_tmp.l_out[i].set_null()
        # Let the others update at will
        for i in range(len(tx_tmp.l_in)):
            if i != nin:  # 把 非指定的 in 的 seq 全部改成0
                tx_tmp.l_in[i].sequence = 0

    # Blank out other inputs completely, not recommended for open transactions
    if hash_type & SignType.SIGHASH_ANYONECANPAY:
        tx_tmp.l_in[0] = tx_tmp.l_in[nin]
        del tx_tmp[1:]  # txTmp.vin.resize(1);

    # // Serialize and hash
    # CDataStream ss(SER_GETHASH);
    # ss << txTmp << nHashType;
    # ret = tx_tmp.serialize() + typeutil.str_from_int(hash_type)
    ss = serialize.PyDataStream(nType=serialize.SerType.SER_GETHASH)
    ss.stream_in(tx_tmp)
    ss.stream_in(hash_type, "int")
    return cryptoutil.Hash(str(ss), out_type=out_type)


# 从栈中获得的 sig 和 pubkey 以及正在验证的 script_code, 一直在用的tx_to nin hash_type
def check_sig(str_sig, str_pubkey, script_code, tx_to, nin, hash_type):
    if len(str_sig) == 0:
        return False
    pykey = PyKey()
    if not pykey.set_pubkey(str_pubkey):
        return False
    # Hash type is one byte tacked on to the end of the signature
    try:
        sig_hash_type = ord(str_sig[-1])
    except Exception, e:
        sig_hash_type = SignType.SIGHASH_UNKNOWN

    if hash_type == 0:
        hash_type = sig_hash_type  # one byte
    elif hash_type != sig_hash_type:
        return False

    str_sig = str_sig[:-1]  # pop for hash_type   vchSig.pop_back()
    if pykey.verify(signature_hash(script_code, tx_to, nin, hash_type), str_sig):
        return True
    return False


def sign_signature(tx_from, tx_to, nin, hash_type=SignType.SIGHASH_ALL, script_prereq=None):
    """
    使用tx_from的out为tx_to的in进行签名,此时的tx_to的l_in应该是已经填充好的，这个l_in<PyTxin>\n
    中的PyTxIn缺少 script_sig，但是已经持有PyOutPoint，指向tx_from相对应的out \n
    :param tx_from: 为 tx_to 提供 被用来作为 in 的 PyTxOut, 提供 script_pubkey
    :param nin: 指明目前操作的是 是 tx_to 的第n个 TxIn
    :param tx_to: 需要签名 TxIn 的 Tx
    :param hash_type: 签名类型
    :param script_prereq: 附加在 script_pubkey 的前置条件脚本
    :return:
    """
    if script_prereq is None:
        script_prereq = PyScript()
    assert nin < len(tx_to.l_in), "PyTx TO -> l_in must larger than 'in', 'in' means which tx_in for TXTO"
    tx_in = tx_to.l_in[nin]
    assert tx_in.prev_out.index < len(tx_from.l_out), \
        "pre_out.index (PyOutPoint) of TxTO.txin[nin] should less than size of out of Tx FROM"
    tx_out = tx_from.l_out[tx_in.prev_out.index]
    # Leave out the signature from the hash, since a signature can't sign itself.
    # The checksig op will also drop the signatures from its hash.
    uint256_hash = signature_hash(script_prereq + tx_out.script_pubkey, tx_to, nin, hash_type, out_type='num')
    sig = solver(tx_out.script_pubkey, uint256_hash, hash_type)
    if sig is None:
        return False
    tx_in.script_sig = script_prereq + sig

    # test solution
    if len(script_prereq) == 0:
        script = PyScript(tx_in.script_sig)
        script.append(OpCodeType.OP_CODESEPARATOR)
        script.extend(tx_out.script_pubkey)

        ret = eval_scrip(script, tx_to, nin)
        if ret is False:
            return False
    return True


# PyTx, PyTx, uint , int
def verify_signature(tx_from, tx_to, nin, hash_type=0):
    """

    :param tx_from: 要验证 out script 的 tx (提供 pubkey scrip)
    :type tx_from: PyTransaction
    :param nin: 当前要验证的是 tx_to 的第几个 in
    :type nin: int
    :param tx_to: 要验证 in script 的 tx 对应于 tx_from 的相对应的 out  (提供sig script)
    :type tx_to: PyTransaction
    :param hash_type:
    :type hash_type: int | SignType
    :return:
    """
    assert nin < len(tx_to.l_in), "PyTx TO -> l_in must larger than 'in', 'in' means which tx_in for TXTO"
    tx_in = tx_to.l_in[nin]
    if tx_in.prev_out.index >= len(tx_from.l_out):
        return False
    tx_out = tx_from.l_out[tx_in.prev_out.index]
    if tx_in.prev_out.hash_tx != tx_from.get_hash():
        return False

    script = PyScript(tx_in.script_sig)
    script.append(OpCodeType.OP_CODESEPARATOR)
    script.extend(tx_out.script_pubkey)
    # ret = eval_scrip(tx_in.script_sig + PyScript(OpCodeType.OP_CODESEPARATOR) + tx_out.script_pubkey, tx_to, nin,
    #                  hash_type)
    ret = eval_scrip(script, tx_to, nin, hash_type)

    return True if ret is not False else False


def extract_pubkey(script_pubkey, mine_only):
    """
    从 pubkey_script中提取出公钥, 当设置了 mine_only 的时候会检查script持有的pubkey在不在mapKeys中
    :param script_pubkey:
    :param mine_only:
    :return: None表示失败，成功返回 script 的 str
    """
    pubkey = None
    solution = solver2(script_pubkey)
    if solution is None:
        return None
    with ctx.dictKeysLock:
        for fir, sec in solution:
            if fir == OpCodeType.OP_PUBKEY:
                pubkey = str(sec)
            elif fir == OpCodeType.OP_PUBKEYHASH:
                pubkey = ctx.dictPubKeys.get(str(sec), None)
                if pubkey is None:
                    continue

            if not mine_only or pubkey in ctx.dictKeys:  # mine_only的情况下一定会检查 mapKeys
                return pubkey
    return None


def extract_hash160(script_pubkey, out_type='str'):
    solution = solver2(script_pubkey)
    if solution is None:
        return None
    for op, data in solution:
        if op == OpCodeType.OP_PUBKEYHASH:
            if out_type == 'str':
                return data
            return serialize.ser_uint160(data)
    return None


def main():
    # ret = PyScript(1)
    # print repr(ret)
    # ret.extend(bytearray("\x12\x03"))
    # print repr(ret)
    # del ret[:]
    # print repr(ret)
    for i in TEMPLATES:
        print repr(i)
    s = PyScript(OpCodeType.OP_CODESEPARATOR)
    s = bytes(s)
    # print (type(s))
    ret = b'\x11' + PyScript(OpCodeType.OP_CODESEPARATOR) + b'\x01' + TEMPLATES[1]
    print (repr(ret))
    print ("==============")
    s2 = PyScript(OpCodeType.OP_CODESEPARATOR)
    print (str(s2))
    print (id(s2))
    s_tmp = s + s2
    print (type(s_tmp))
    print (id(s_tmp))
    print (str(s_tmp))
    print (id(s))
    s += s2
    print (id(s))

    print (repr(s2.get_str()))

    s_tmp.extend("\x12\x34")
    print str(s_tmp)
    s_tmp.find_and_delete(s2)
    print s_tmp
    # ret = PyScript(1)
    # # ret = PyScript(0x10 + 1)
    # # ret = PyScript(-1)
    # # ret = PyScript(0xFFFFFFFFF)
    # print repr(ret)
    # class Animal(IntEnum):
    #     ant = 1
    #     bee = 2
    #     cat = 3
    #     dog = 4

    # print Animal.ant + 1
    # print Animal.look_up(2)
    pass


if __name__ == '__main__':
    main()
