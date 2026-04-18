from __future__ import annotations

from .nodes import (
    AssignmentNode,
    BinaryExprNode,
    BracketNode,
    BoxedNodeParams,
    BranchNode,
    BreakNode,
    CallNode,
    ContinueNode,
    DefNode,
    DictNode,
    ForNode,
    FunctionNode,
    ImportNode,
    LiteralNode,
    ListNode,
    NoOpNode,
    PassNode,
    ReturnNode,
    SequenceNode,
    SetNode,
    TupleNode,
    UnaryExprNode,
    ValueNode,
)
from .parse_exception import ParseException
from .program_model import Program
from ..runtime.py_values import PyNumber, PyString
from ..runtime.scope import Scope
from .token_stream import TokenStream
from .token_types import TokenType


def parse(stream: TokenStream) -> Program:
    global_vars: set[str] = set()
    imported_modules: set[str] = set()
    all_vars: set[str] = set()
    syntax_tree = _block(stream, -1, global_vars, global_vars, all_vars, is_global=True)
    if stream.current is not None:
        raise ParseException("error_code_after_block", stream.current_string_start_index, stream.current_string_end_index)
    return Program(syntax_tree, global_vars, all_vars, imported_modules)


def _block(stream: TokenStream, prev_indentation: int, vars_set: set[str], global_vars: set[str], all_vars: set[str], is_global: bool = False):
    if is_global and stream.current is None:
        return SequenceNode(BoxedNodeParams())
    if stream.current is None or stream.current.type != TokenType.NEW_LINE:
        raise ParseException("error_no_statements", stream.current_string_start_index, stream.current_string_end_index)
    indentation = _get_indentation(stream)
    if indentation <= prev_indentation:
        raise ParseException("error_not_enough_indentation", stream.current_string_start_index + 1, stream.current_string_end_index)
    statements = []
    current_indent = indentation
    while current_indent == indentation:
        stream.consume(TokenType.NEW_LINE)
        statements.append(_statement(stream, indentation, vars_set, global_vars, all_vars, is_global))
        if stream.current is None or stream.current.type != TokenType.NEW_LINE:
            break
        current_indent = _get_indentation(stream)
    if current_indent > indentation:
        raise ParseException("error_too_much_indentation", stream.current_string_start_index + 1, stream.current_string_end_index)
    node = SequenceNode(BoxedNodeParams())
    node.slots = statements
    return node


def _statement(stream: TokenStream, indentation: int, vars_set: set[str], global_vars: set[str], all_vars: set[str], is_global: bool = False):
    current = stream.current
    if current is None:
        raise ParseException("error_no_statements", stream.current_string_start_index, stream.current_string_end_index)
    if current.type == TokenType.DEF:
        return _function(stream, indentation, vars_set, global_vars, all_vars, is_global)
    if current.type == TokenType.IMPORT:
        return _import_statement(stream)
    if current.type == TokenType.FROM:
        return _from_import_statement(stream)
    if current.type == TokenType.PASS:
        token = stream.consume(TokenType.PASS)
        return PassNode(BoxedNodeParams(word_start=token.start_index, word_end=token.start_index + len(token.value)))
    if current.type == TokenType.GLOBAL:
        token = stream.consume(TokenType.GLOBAL)
        while stream.current is not None and stream.current.type == TokenType.IDENTIFIER:
            if stream.current.value not in global_vars:
                global_vars.add(stream.current.value)
            stream.consume(TokenType.IDENTIFIER)
            if stream.current is None or stream.current.type != TokenType.COMMA:
                break
            stream.consume(TokenType.COMMA)
        return NoOpNode(BoxedNodeParams(word_start=token.start_index, word_end=token.start_index + len(token.value)))
    if current.type == TokenType.BREAK:
        token = stream.consume(TokenType.BREAK)
        return BreakNode(BoxedNodeParams(word_start=token.start_index, word_end=token.start_index + len(token.value)))
    if current.type == TokenType.CONTINUE:
        token = stream.consume(TokenType.CONTINUE)
        return ContinueNode(BoxedNodeParams(word_start=token.start_index, word_end=token.start_index + len(token.value)))
    if current.type == TokenType.RETURN:
        token = stream.consume(TokenType.RETURN)
        node = ReturnNode(BoxedNodeParams(word_start=token.start_index, word_end=token.start_index + len(token.value)))
        if stream.current is not None and stream.current.type != TokenType.NEW_LINE:
            node.slots.append(_tuple_or_expression(stream))
        return node
    if current.type == TokenType.IF:
        return _if_statement(stream, indentation, vars_set, global_vars, all_vars)
    if current.type == TokenType.WHILE:
        return _while_statement(stream, indentation, vars_set, global_vars, all_vars)
    if current.type == TokenType.FOR:
        return _for_statement(stream, indentation, vars_set, global_vars, all_vars)
    node = _tuple_or_expression(stream, end_of_tuple_token=TokenType.ASSIGN, is_leftmost=True)
    if stream.current is not None and stream.current.type == TokenType.ASSIGN:
        token = stream.consume(TokenType.ASSIGN)
        rhs = _tuple_or_expression(stream)
        assign = AssignmentNode(token.value, BoxedNodeParams(word_start=token.start_index, word_end=token.start_index + len(token.value)))
        assign.slots = [node, rhs]
        _register_assignment_targets(node, vars_set, global_vars, all_vars)
        return assign
    return node


def _function(stream: TokenStream, indentation: int, vars_set: set[str], global_vars: set[str], all_vars: set[str], is_global: bool):
    token = stream.consume(TokenType.DEF)
    name_token = stream.consume(TokenType.IDENTIFIER)
    stream.consume(TokenType.BRACKET_OPEN)
    _line_breaks(stream)
    param_names: list[str] = []
    defaults: list = []
    if stream.current is not None and stream.current.type != TokenType.BRACKET_CLOSE:
        while True:
            param = stream.consume(TokenType.IDENTIFIER)
            param_names.append(param.value)
            all_vars.add(param.value)
            if stream.current is not None and stream.current.type == TokenType.ASSIGN:
                stream.consume(TokenType.ASSIGN)
                defaults.append(_expression(stream))
            _line_breaks(stream)
            if stream.current is None or stream.current.type != TokenType.COMMA:
                break
            stream.consume(TokenType.COMMA)
            _line_breaks(stream)
    stream.consume(TokenType.BRACKET_CLOSE)
    _consume_colon(stream)
    func_node = FunctionNode(param_names, name_token.value, BoxedNodeParams(word_start=token.start_index, word_end=name_token.start_index + len(name_token.value)))
    func_vars = set(param_names)
    func_node.slots.append(_block(stream, indentation, func_vars, set(), all_vars, is_global=False))
    func_node.slots.extend(defaults)
    func_node.vars = func_vars
    def_node = DefNode(name_token.value, True, BoxedNodeParams(word_start=token.start_index, word_end=token.start_index + len(token.value)))
    def_node.slots.append(func_node)
    if name_token.value not in global_vars:
        vars_set.add(name_token.value)
    all_vars.add(name_token.value)
    return def_node


def _if_statement(stream: TokenStream, indentation: int, vars_set: set[str], global_vars: set[str], all_vars: set[str]):
    token = stream.consume(TokenType.IF)
    node = BranchNode(BoxedNodeParams(word_start=token.start_index, word_end=token.start_index + len(token.value)), looping=False)
    node.slots.append(_expression(stream))
    _consume_colon(stream)
    node.slots.append(_block(stream, indentation, vars_set, global_vars, all_vars, is_global=False))
    if stream.current is not None and stream.current.type == TokenType.NEW_LINE and _indentation_value(stream.current.value) == indentation:
        if stream.look_ahead is not None and stream.look_ahead.type == TokenType.ELSE:
            stream.consume(TokenType.NEW_LINE)
            stream.consume(TokenType.ELSE)
            _consume_colon(stream)
            node.slots.append(_block(stream, indentation, vars_set, global_vars, all_vars, is_global=False))
        elif stream.look_ahead is not None and stream.look_ahead.type == TokenType.ELIF:
            stream.consume(TokenType.NEW_LINE)
            node.slots.append(_elif_statement(stream, indentation, vars_set, global_vars, all_vars))
    return node


def _elif_statement(stream: TokenStream, indentation: int, vars_set: set[str], global_vars: set[str], all_vars: set[str]):
    token = stream.consume(TokenType.ELIF)
    node = BranchNode(BoxedNodeParams(word_start=token.start_index, word_end=token.start_index + len(token.value)), looping=False)
    node.slots.append(_expression(stream))
    _consume_colon(stream)
    node.slots.append(_block(stream, indentation, vars_set, global_vars, all_vars, is_global=False))
    if stream.current is not None and stream.current.type == TokenType.NEW_LINE and _indentation_value(stream.current.value) == indentation:
        if stream.look_ahead is not None and stream.look_ahead.type == TokenType.ELSE:
            stream.consume(TokenType.NEW_LINE)
            stream.consume(TokenType.ELSE)
            _consume_colon(stream)
            node.slots.append(_block(stream, indentation, vars_set, global_vars, all_vars, is_global=False))
        elif stream.look_ahead is not None and stream.look_ahead.type == TokenType.ELIF:
            stream.consume(TokenType.NEW_LINE)
            node.slots.append(_elif_statement(stream, indentation, vars_set, global_vars, all_vars))
    return node


def _while_statement(stream: TokenStream, indentation: int, vars_set: set[str], global_vars: set[str], all_vars: set[str]):
    token = stream.consume(TokenType.WHILE)
    node = BranchNode(BoxedNodeParams(word_start=token.start_index, word_end=token.start_index + len(token.value)), looping=True)
    node.slots.append(_expression(stream))
    _consume_colon(stream)
    node.slots.append(_block(stream, indentation, vars_set, global_vars, all_vars, is_global=False))
    return node


def _for_statement(stream: TokenStream, indentation: int, vars_set: set[str], global_vars: set[str], all_vars: set[str]):
    token = stream.consume(TokenType.FOR)
    pattern = _for_pattern(stream)
    stream.consume(TokenType.IN)
    node = ForNode(pattern, BoxedNodeParams(word_start=token.start_index, word_end=token.start_index + len(token.value)))
    node.slots.append(_expression(stream))
    _consume_colon(stream)
    node.slots.append(_block(stream, indentation, vars_set, global_vars, all_vars, is_global=False))
    return node


def _import_statement(stream: TokenStream):
    token = stream.consume(TokenType.IMPORT)
    module_names: list[str] = []
    while stream.current is not None and stream.current.type not in (TokenType.NEW_LINE,):
        module_names.append(stream.consume(TokenType.IDENTIFIER).value)
        if stream.current is None or stream.current.type != TokenType.COMMA:
            break
        stream.consume(TokenType.COMMA)
    return ImportNode(module_names, False, False, [], False, BoxedNodeParams(word_start=token.start_index, word_end=token.start_index + len(token.value)))


def _from_import_statement(stream: TokenStream):
    token = stream.consume(TokenType.FROM)
    module_name = stream.consume(TokenType.IDENTIFIER).value
    stream.consume(TokenType.IMPORT)
    if stream.current is not None and stream.current.type == TokenType.MULT:
        stream.consume(TokenType.MULT)
        return ImportNode([module_name], True, True, [], False, BoxedNodeParams(word_start=token.start_index, word_end=token.start_index + len(token.value)))
    vars_to_unpack: list[str] = []
    while stream.current is not None and stream.current.type not in (TokenType.NEW_LINE,):
        vars_to_unpack.append(stream.consume(TokenType.IDENTIFIER).value)
        if stream.current is None or stream.current.type != TokenType.COMMA:
            break
        stream.consume(TokenType.COMMA)
    return ImportNode([module_name], True, False, vars_to_unpack, False, BoxedNodeParams(word_start=token.start_index, word_end=token.start_index + len(token.value)))


def _expression(stream: TokenStream):
    return _or_expression(stream)


def _or_expression(stream: TokenStream):
    node = _and_expression(stream)
    while stream.current is not None and stream.current.type == TokenType.OR:
        token = stream.consume(TokenType.OR)
        _line_breaks(stream)
        rhs = _and_expression(stream)
        parent = BinaryExprNode(token.value, BoxedNodeParams(word_start=token.start_index, word_end=token.start_index + len(token.value)))
        parent.slots = [node, rhs]
        node = parent
    return node


def _and_expression(stream: TokenStream):
    node = _compare_expression(stream)
    while stream.current is not None and stream.current.type == TokenType.AND:
        token = stream.consume(TokenType.AND)
        _line_breaks(stream)
        rhs = _compare_expression(stream)
        parent = BinaryExprNode(token.value, BoxedNodeParams(word_start=token.start_index, word_end=token.start_index + len(token.value)))
        parent.slots = [node, rhs]
        node = parent
    return node


def _compare_expression(stream: TokenStream):
    node = _add_expression(stream)
    while stream.current is not None and stream.current.type in (TokenType.COMPARE, TokenType.IN):
        token = stream.consume(stream.current.type)
        _line_breaks(stream)
        rhs = _add_expression(stream)
        parent = BinaryExprNode(token.value, BoxedNodeParams(word_start=token.start_index, word_end=token.start_index + len(token.value)))
        parent.slots = [node, rhs]
        node = parent
    return node


def _add_expression(stream: TokenStream):
    node = _mult_expression(stream)
    while stream.current is not None and stream.current.type == TokenType.ADD:
        token = stream.consume(TokenType.ADD)
        _line_breaks(stream)
        rhs = _mult_expression(stream)
        parent = BinaryExprNode(token.value, BoxedNodeParams(word_start=token.start_index, word_end=token.start_index + len(token.value)))
        parent.slots = [node, rhs]
        node = parent
    return node


def _mult_expression(stream: TokenStream):
    node = _pow_expression(stream)
    while stream.current is not None and stream.current.type == TokenType.MULT:
        token = stream.consume(TokenType.MULT)
        _line_breaks(stream)
        rhs = _pow_expression(stream)
        parent = BinaryExprNode(token.value, BoxedNodeParams(word_start=token.start_index, word_end=token.start_index + len(token.value)))
        parent.slots = [node, rhs]
        node = parent
    return node


def _pow_expression(stream: TokenStream):
    node = _prefix_expression(stream)
    while stream.current is not None and stream.current.type == TokenType.EXP:
        token = stream.consume(TokenType.EXP)
        _line_breaks(stream)
        rhs = _prefix_expression(stream)
        parent = BinaryExprNode(token.value, BoxedNodeParams(word_start=token.start_index, word_end=token.start_index + len(token.value)))
        parent.slots = [node, rhs]
        node = parent
    return node


def _prefix_expression(stream: TokenStream):
    current = stream.current
    if current is not None and current.type in (TokenType.ADD, TokenType.NOT):
        token = stream.consume(current.type)
        _line_breaks(stream)
        node = UnaryExprNode(token.value, BoxedNodeParams(word_start=token.start_index, word_end=token.start_index + len(token.value)))
        node.slots = [_prefix_expression(stream)]
        return node
    return _postfix_expression(stream)


def _postfix_expression(stream: TokenStream):
    node = _atomic_expression(stream)
    while stream.current is not None and stream.current.type in (TokenType.BRACKET_OPEN, TokenType.SQUARE_BRACKET_OPEN, TokenType.DOT):
        if stream.current.type == TokenType.BRACKET_OPEN:
            token = stream.consume(TokenType.BRACKET_OPEN)
            args = SequenceNode(BoxedNodeParams(word_start=token.start_index, word_end=token.start_index + len(token.value)))
            _line_breaks(stream)
            if stream.current is not None and stream.current.type != TokenType.BRACKET_CLOSE:
                while True:
                    args.slots.append(_expression(stream))
                    _line_breaks(stream)
                    if stream.current is None or stream.current.type != TokenType.COMMA:
                        break
                    stream.consume(TokenType.COMMA)
                    _line_breaks(stream)
                    if stream.current is not None and stream.current.type == TokenType.BRACKET_CLOSE:
                        break
            stream.consume(TokenType.BRACKET_CLOSE)
            call = CallNode(BoxedNodeParams(word_start=token.start_index, word_end=token.start_index + 1))
            call.slots = [node, args]
            node = call
            continue
        if stream.current.type == TokenType.SQUARE_BRACKET_OPEN:
            token = stream.consume(TokenType.SQUARE_BRACKET_OPEN)
            seq = SequenceNode(BoxedNodeParams(word_start=token.start_index, word_end=token.start_index + 1))
            _line_breaks(stream)
            if stream.current is not None and stream.current.type != TokenType.SQUARE_BRACKET_CLOSE:
                if stream.current.type == TokenType.COLON:
                    stream.consume(TokenType.COLON)
                    if stream.current is not None and stream.current.type != TokenType.SQUARE_BRACKET_CLOSE:
                        seq.slots.append(_expression(stream))
                else:
                    seq.slots.append(_expression(stream))
                    if stream.current is not None and stream.current.type == TokenType.COLON:
                        stream.consume(TokenType.COLON)
                        if stream.current is not None and stream.current.type != TokenType.SQUARE_BRACKET_CLOSE:
                            seq.slots.append(_expression(stream))
            stream.consume(TokenType.SQUARE_BRACKET_CLOSE)
            index = BinaryExprNode("[]", BoxedNodeParams(word_start=token.start_index, word_end=token.start_index + 1))
            bracket = BracketNode(BoxedNodeParams(word_start=token.start_index, word_end=token.start_index + 1))
            bracket.slots = [seq]
            index.slots = [node, bracket]
            node = index
            continue
        token = stream.consume(TokenType.DOT)
        attr = stream.consume(TokenType.IDENTIFIER)
        dot = BinaryExprNode(".", BoxedNodeParams(word_start=token.start_index, word_end=attr.start_index + len(attr.value)))
        dot.slots = [node, ValueNode(attr.value, BoxedNodeParams(word_start=attr.start_index, word_end=attr.start_index + len(attr.value)))]
        node = dot
    return node


def _atomic_expression(stream: TokenStream):
    current = stream.current
    if current is None:
        raise ParseException("error_invalid_expression", stream.current_string_start_index, stream.current_string_end_index)
    if current.type == TokenType.NUM:
        token = stream.consume(TokenType.NUM)
        return LiteralNode(PyNumber(float(token.value)), BoxedNodeParams(word_start=token.start_index, word_end=token.start_index + len(token.value)))
    if current.type == TokenType.STRING:
        token = stream.consume(TokenType.STRING)
        return LiteralNode(PyString(token.value[1:-1]), BoxedNodeParams(word_start=token.start_index, word_end=token.start_index + len(token.value)))
    if current.type == TokenType.SQUARE_BRACKET_OPEN:
        token = stream.consume(TokenType.SQUARE_BRACKET_OPEN)
        seq = SequenceNode(BoxedNodeParams())
        _line_breaks(stream)
        if stream.current is not None and stream.current.type != TokenType.SQUARE_BRACKET_CLOSE:
            while True:
                seq.slots.append(_expression(stream))
                _line_breaks(stream)
                if stream.current is None or stream.current.type != TokenType.COMMA:
                    break
                stream.consume(TokenType.COMMA)
                _line_breaks(stream)
                if stream.current is not None and stream.current.type == TokenType.SQUARE_BRACKET_CLOSE:
                    break
        stream.consume(TokenType.SQUARE_BRACKET_CLOSE)
        node = ListNode(BoxedNodeParams(word_start=token.start_index, word_end=token.start_index + 1))
        node.slots = [seq]
        return node
    if current.type == TokenType.CURL_BRACE_OPEN:
        token = stream.consume(TokenType.CURL_BRACE_OPEN)
        seq = SequenceNode(BoxedNodeParams())
        key_value_pairs = True
        _line_breaks(stream)
        if stream.current is not None and stream.current.type != TokenType.CURL_BRACE_CLOSE:
            while True:
                key = _expression(stream)
                _line_breaks(stream)
                if stream.current is not None and stream.current.type == TokenType.COLON:
                    stream.consume(TokenType.COLON)
                    _line_breaks(stream)
                    value = _expression(stream)
                    seq.slots.append(key)
                    seq.slots.append(value)
                else:
                    key_value_pairs = False
                    seq.slots.append(key)
                _line_breaks(stream)
                if stream.current is None or stream.current.type != TokenType.COMMA:
                    break
                stream.consume(TokenType.COMMA)
                _line_breaks(stream)
                if stream.current is not None and stream.current.type == TokenType.CURL_BRACE_CLOSE:
                    break
        stream.consume(TokenType.CURL_BRACE_CLOSE)
        if key_value_pairs:
            node = DictNode(BoxedNodeParams(word_start=token.start_index, word_end=token.start_index + 1))
        else:
            node = SetNode(BoxedNodeParams(word_start=token.start_index, word_end=token.start_index + 1))
        node.slots = [seq]
        return node
    if current.type == TokenType.IDENTIFIER:
        token = stream.consume(TokenType.IDENTIFIER)
        constant = Scope.evaluate_constant(token.value)
        boxed = BoxedNodeParams(word_start=token.start_index, word_end=token.start_index + len(token.value))
        if constant is not None:
            return LiteralNode(constant, boxed)
        return ValueNode(token.value, boxed)
    if current.type == TokenType.BRACKET_OPEN:
        stream.consume(TokenType.BRACKET_OPEN)
        _line_breaks(stream)
        node = _tuple_or_expression(stream, end_of_tuple_token=TokenType.BRACKET_CLOSE)
        _line_breaks(stream)
        stream.consume(TokenType.BRACKET_CLOSE)
        bracket = BracketNode(BoxedNodeParams(word_start=current.start_index, word_end=current.start_index + len(current.value)))
        bracket.slots = [node]
        return bracket
    raise ParseException("error_invalid_expression", stream.current_string_start_index, stream.current_string_end_index)


def _tuple_or_expression(stream: TokenStream, end_of_tuple_token: TokenType = TokenType.BRACKET_CLOSE, is_leftmost: bool = False):
    if stream.current is not None and stream.current.type == end_of_tuple_token:
        tuple_node = TupleNode(BoxedNodeParams())
        seq = SequenceNode(BoxedNodeParams())
        tuple_node.slots = [seq]
        return tuple_node
    first = _expression(stream)
    if stream.current is not None and stream.current.type == TokenType.COMMA:
        seq = SequenceNode(BoxedNodeParams())
        seq.slots = [first]
        while stream.current is not None and stream.current.type == TokenType.COMMA:
            stream.consume(TokenType.COMMA)
            if stream.current is None or stream.current.type == end_of_tuple_token:
                break
            seq.slots.append(_expression(stream))
        tuple_node = TupleNode(BoxedNodeParams())
        tuple_node.slots = [seq]
        return tuple_node
    return first


def _for_pattern(stream: TokenStream):
    first = stream.consume(TokenType.IDENTIFIER)
    first_node = ValueNode(first.value, BoxedNodeParams(word_start=first.start_index, word_end=first.start_index + len(first.value)))
    if stream.current is not None and stream.current.type == TokenType.COMMA:
        stream.consume(TokenType.COMMA)
        seq = SequenceNode(BoxedNodeParams())
        seq.slots = [first_node]
        while True:
            token = stream.consume(TokenType.IDENTIFIER)
            seq.slots.append(ValueNode(token.value, BoxedNodeParams(word_start=token.start_index, word_end=token.start_index + len(token.value))))
            if stream.current is None or stream.current.type != TokenType.COMMA:
                break
            stream.consume(TokenType.COMMA)
        tuple_node = TupleNode(BoxedNodeParams())
        tuple_node.slots = [seq]
        return tuple_node
    return first_node


def _register_assignment_targets(node, vars_set: set[str], global_vars: set[str], all_vars: set[str]):
    if isinstance(node, ValueNode):
        if node.value not in global_vars:
            vars_set.add(node.value)
        all_vars.add(node.value)
        return
    if isinstance(node, TupleNode):
        for slot in node.slots[0].slots:
            _register_assignment_targets(slot, vars_set, global_vars, all_vars)


def _get_indentation(stream: TokenStream) -> int:
    if stream.current is None or stream.current.type != TokenType.NEW_LINE:
        raise ParseException("error_new_line_expected", stream.current_string_start_index, stream.current_string_end_index)
    while stream.look_ahead is not None and stream.look_ahead.type == TokenType.NEW_LINE:
        stream.consume(TokenType.NEW_LINE)
    value = stream.current.value
    if "\t" in value and " " in value:
        raise ParseException("error_mixed_indentation", stream.current_string_start_index + 1, stream.current_string_end_index)
    return _indentation_value(value)


def _consume_colon(stream: TokenStream):
    if stream.current is not None and stream.current.type == TokenType.NEW_LINE:
        stream.consume(TokenType.COLON, "error_missing_colon", move_error_back=True)
    return stream.consume(TokenType.COLON)


def _indentation_value(newline_token_value: str) -> int:
    return newline_token_value.count(" ") + newline_token_value.count("\t") * 4


def _line_breaks(stream: TokenStream):
    while stream.current is not None and stream.current.type == TokenType.NEW_LINE:
        stream.consume(TokenType.NEW_LINE)
