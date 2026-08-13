import re

import sqlglot
from sqlglot import exp

from core import log
from core.fetchxmlparser import FetchXmlParser
from core.exceptions import (
    SqlStatementFormat,
    IdentifierNotAllowedInSqlStatement,
    OperatorNotAllowedInSqlStatement,
    FunctionNotAllowedInSqlStatement,
    LiteralNotAllowedInJoinCondition,
)

logger=log.create_logger(__name__)

_IDENTIFIER_RE=re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')

_ALLOWED_JOIN_KINDS={"INNER", "LEFT", "RIGHT", "LEFT OUTER", "RIGHT OUTER", "CROSS"}

_COMPARISON_OPS={
    exp.EQ: "=",
    exp.NEQ: "<>",
    exp.GT: ">",
    exp.GTE: ">=",
    exp.LT: "<",
    exp.LTE: "<=",
    exp.Like: "LIKE",
}

_SELECT_FUNCTIONS={
    exp.Count: "COUNT",
    exp.Sum: "SUM",
    exp.Min: "MIN",
    exp.Max: "MAX",
    exp.Avg: "AVG",
    exp.Concat: "CONCAT",
}

"""
Decomposes an sql-like statement (via sqlglot) into the same internal
representation FetchXmlParser uses, so the inherited get_sql()/get_select()/
get_insert()/get_update()/get_delete() render the final, parameterized SQL.
Every table/alias reference is resolved through _validate_table_alias()
against api_table, so get_tables() is complete and accurate for the
table-level permission check in DatabaseServices.exec().
"""
class FetchSqlParser(FetchXmlParser):

    def __init__(self, sql_statement, context, page=0, page_size=0, dialect="mysql"):
        self._dialect=dialect
        super().__init__(sql_statement, context, page, page_size)

    def parse(self):
        self._init_properties()

        try:
            statements=sqlglot.parse(self._fetch_xml, read=self._dialect, error_level=sqlglot.ErrorLevel.RAISE)
        except sqlglot.errors.ParseError as err:
            raise SqlStatementFormat(str(err))

        statements=[s for s in statements if s is not None]
        if len(statements) != 1:
            raise SqlStatementFormat("Exactly one sql statement is required")

        ast=statements[0]

        if isinstance(ast, exp.Select):
            self._sql_type="select"
            self._parse_select(ast)
        elif isinstance(ast, exp.Insert):
            self._sql_type="insert"
            self._parse_insert(ast)
        elif isinstance(ast, exp.Update):
            self._sql_type="update"
            self._parse_update(ast)
        elif isinstance(ast, exp.Delete):
            self._sql_type="delete"
            self._parse_delete(ast)
        else:
            raise SqlStatementFormat(f"Statement type not allowed: {type(ast).__name__}")

    # ------------------------------------------------------------------
    # identifiers / tables
    # ------------------------------------------------------------------

    def _identifier(self, node):
        if isinstance(node, exp.Identifier):
            name=node.this
        elif isinstance(node, str):
            name=node
        else:
            raise IdentifierNotAllowedInSqlStatement(f"Expected identifier, got: {node}")

        if not _IDENTIFIER_RE.match(name):
            raise IdentifierNotAllowedInSqlStatement(f"Invalid identifier: {name}")

        return name

    def _resolve_table(self, table_expr):
        if not isinstance(table_expr, exp.Table):
            raise IdentifierNotAllowedInSqlStatement(f"Expected table reference, got: {table_expr}")

        if table_expr.args.get('db') or table_expr.args.get('catalog'):
            raise IdentifierNotAllowedInSqlStatement("Schema-qualified table names are not allowed")

        name=self._identifier(table_expr.this)
        table, table_id=self._validate_table_alias(self._context, name)

        alias=table
        alias_node=table_expr.args.get('alias')
        if alias_node is not None:
            alias=self._identifier(alias_node.this)

        return table, table_id, alias

    def _build_table_from_ast(self, table_expr):
        table, table_id, alias=self._resolve_table(table_expr)

        self._main_alias=table
        self._sql_table=table
        self._sql_table_alias=alias
        self._sql_table_id=table_id

        self._tables.append(table)
        self._append_alias(table, alias)

    def _build_joins_from_ast(self, joins):
        sql_parts=[]
        for join in joins:
            table, table_id, alias=self._resolve_table(join.this)

            kind_part=join.args.get('kind')
            side_part=join.args.get('side')
            if side_part:
                kind=f"{side_part} {kind_part}".strip() if kind_part else str(side_part)
            else:
                kind=str(kind_part) if kind_part else "INNER"
            kind=kind.upper()

            if kind not in _ALLOWED_JOIN_KINDS:
                raise OperatorNotAllowedInSqlStatement(f"Join type not allowed: {kind}")

            on_expr=join.args.get('on')
            if on_expr is None:
                raise SqlStatementFormat("JOIN without ON condition is not allowed")

            self._tables.append(table)
            self._append_alias(table, alias)

            join_params=[]
            condition_sql=self._render_condition(on_expr, join_params)
            if join_params:
                raise LiteralNotAllowedInJoinCondition("Literals are not allowed in JOIN conditions")

            sql_parts.append(f"{kind} JOIN {table} {alias} ON ({condition_sql}) ")

        self._sql_table_join=''.join(sql_parts)

    # ------------------------------------------------------------------
    # columns / literals
    # ------------------------------------------------------------------

    def _resolve_column_alias(self, node):
        table_node=node.args.get('table')
        if table_node is not None and str(table_node) != "":
            alias=self._identifier(table_node)
            if alias not in self._table_aliases:
                raise IdentifierNotAllowedInSqlStatement(f"Unknown table alias: {alias}")
            return alias

        return self.get_alias_by_table(self._main_alias)

    def _resolve_column(self, node):
        field=self._identifier(node.this)
        alias=self._resolve_column_alias(node)
        return f"{alias}.{field}"

    def _literal_value(self, node):
        if isinstance(node, exp.Literal):
            return node.this
        elif isinstance(node, exp.Null):
            return None
        elif isinstance(node, exp.Boolean):
            return -1 if node.this else 0
        else:
            raise OperatorNotAllowedInSqlStatement(f"Literal value expected, got: {type(node).__name__}")

    # ------------------------------------------------------------------
    # WHERE / ON condition rendering (shared)
    # ------------------------------------------------------------------

    def _render_side(self, node, params):
        if isinstance(node, exp.Column):
            return self._resolve_column(node)
        if isinstance(node, exp.Paren):
            return self._render_side(node.this, params)
        if isinstance(node, (exp.Literal, exp.Null, exp.Boolean)):
            params.append(self._literal_value(node))
            return "%s"
        if isinstance(node, exp.Neg) and isinstance(node.this, exp.Literal) and not node.this.is_string:
            params.append(f"-{node.this.this}")
            return "%s"

        raise IdentifierNotAllowedInSqlStatement(f"Expression not allowed here: {type(node).__name__}")

    def _render_condition(self, node, params):
        if isinstance(node, exp.Paren):
            return f"({self._render_condition(node.this, params)})"
        if isinstance(node, exp.And):
            return f"({self._render_condition(node.this, params)} AND {self._render_condition(node.expression, params)})"
        if isinstance(node, exp.Or):
            return f"({self._render_condition(node.this, params)} OR {self._render_condition(node.expression, params)})"
        if isinstance(node, exp.Not):
            inner=node.this
            if isinstance(inner, exp.Is) and isinstance(inner.expression, exp.Null):
                return f"{self._render_side(inner.this, params)} IS NOT NULL"
            return f"NOT ({self._render_condition(inner, params)})"
        if isinstance(node, exp.Is):
            left=self._render_side(node.this, params)
            if isinstance(node.expression, exp.Null):
                return f"{left} IS NULL"
            raise OperatorNotAllowedInSqlStatement("IS only supports NULL / NOT NULL")
        if isinstance(node, exp.Between):
            left=self._render_side(node.this, params)
            low=self._render_side(node.args.get('low'), params)
            high=self._render_side(node.args.get('high'), params)
            return f"{left} BETWEEN {low} AND {high}"
        if isinstance(node, exp.In):
            left=self._render_side(node.this, params)
            values=node.args.get('expressions')
            if not values:
                raise OperatorNotAllowedInSqlStatement("IN requires a literal list")
            rendered=[self._render_side(v, params) for v in values]
            return f"{left} IN ({', '.join(rendered)})"
        if type(node) in _COMPARISON_OPS:
            op=_COMPARISON_OPS[type(node)]
            left=self._render_side(node.this, params)
            right=self._render_side(node.expression, params)
            return f"{left} {op} {right}"

        raise OperatorNotAllowedInSqlStatement(f"Operator not allowed: {type(node).__name__}")

    def _build_where(self, where_expr):
        if where_expr is None:
            self._sql_where=""
            return

        condition=where_expr.this if isinstance(where_expr, exp.Where) else where_expr
        self._sql_where=self._render_condition(condition, self._sql_parameters_where)

    # ------------------------------------------------------------------
    # SELECT list / GROUP BY / ORDER BY
    # ------------------------------------------------------------------

    def _render_function(self, func_name, node):
        if func_name=="COUNT" and isinstance(node.this, exp.Star):
            return "COUNT(*)"

        if func_name=="CONCAT":
            args=[self._render_side(a, self._sql_parameters_select) for a in node.args.get('expressions', [])]
            return f"CONCAT({', '.join(args)})"

        inner=node.this
        if isinstance(inner, exp.Column):
            table_alias=self._resolve_column_alias(inner)
            field=self._identifier(inner.this)
            self._validate_field_permission(self._context, self._sql_type, table_alias, field)
            return f"{func_name}({table_alias}.{field})"

        raise FunctionNotAllowedInSqlStatement(f"Unsupported argument for {func_name}")

    def _render_date_format(self, node):
        inner=node.this
        if isinstance(inner, (exp.Cast, exp.TsOrDsToTimestamp)):
            inner=inner.this

        if not isinstance(inner, exp.Column):
            raise FunctionNotAllowedInSqlStatement("DATE_FORMAT requires a column argument")

        table_alias=self._resolve_column_alias(inner)
        field=self._identifier(inner.this)
        self._validate_field_permission(self._context, self._sql_type, table_alias, field)

        format_node=node.args.get('format')
        if not isinstance(format_node, exp.Literal) or not format_node.is_string:
            raise FunctionNotAllowedInSqlStatement("DATE_FORMAT requires a string format literal")

        self._sql_parameters_select.append(format_node.this)
        return f"DATE_FORMAT({table_alias}.{field}, %s)"

    def _render_select_expression(self, node):
        if isinstance(node, exp.Column):
            table_alias=self._resolve_column_alias(node)
            field=self._identifier(node.this)
            self._validate_field_permission(self._context, self._sql_type, table_alias, field)
            return table_alias, field, f"{table_alias}.{field}"

        if isinstance(node, exp.TimeToStr):
            return None, None, self._render_date_format(node)

        if type(node) in _SELECT_FUNCTIONS:
            func_name=_SELECT_FUNCTIONS[type(node)]
            return None, None, self._render_function(func_name, node)

        raise FunctionNotAllowedInSqlStatement(f"Expression not allowed in SELECT: {type(node).__name__}")

    def _build_select_from_ast(self, expressions):
        if len(expressions)==1 and isinstance(expressions[0], exp.Star):
            self._sql_select="*"
            return

        parts=[]
        for e in expressions:
            alias_name=""
            inner=e
            if isinstance(e, exp.Alias):
                alias_name=self._identifier(e.args.get('alias'))
                inner=e.this

            table_alias, field, field_sql=self._render_select_expression(inner)

            parts.append(f"{field_sql} {alias_name}" if alias_name else field_sql)

            if table_alias is not None:
                table_name=self._table_aliases[table_alias]['name']
            else:
                table_name=self._sql_table

            header=alias_name if alias_name else (field if field else "expr")
            column_alias=alias_name if alias_name else (field if field else "expr")
            column_desc={"table": table_name, "database_field": field if field else "", "label": header, "alias": column_alias, "formatter": None}
            self._columns_desc.append(column_desc)

        self._sql_select=', '.join(parts)

    def _build_group_by(self, group_expr):
        if group_expr is None:
            return

        parts=[]
        for g in group_expr.expressions:
            if not isinstance(g, exp.Column):
                raise FunctionNotAllowedInSqlStatement("GROUP BY only supports plain columns")

            table_alias=self._resolve_column_alias(g)
            field=self._identifier(g.this)
            self._validate_field_permission(self._context, self._sql_type, table_alias, field)
            parts.append(f"{table_alias}.{field}")

        self._sql_group_by=', '.join(parts)

    def _build_order_from_ast(self, order_expr):
        if order_expr is None:
            return

        parts=[]
        for o in order_expr.expressions:
            col=o.this
            if not isinstance(col, exp.Column):
                raise FunctionNotAllowedInSqlStatement("ORDER BY only supports plain columns")

            table_alias=self._resolve_column_alias(col)
            field=self._identifier(col.this)
            direction="DESC" if o.args.get('desc') else "ASC"
            parts.append(f"{table_alias}.{field} {direction}")

        self._sql_order=', '.join(parts)

    # ------------------------------------------------------------------
    # statement dispatch
    # ------------------------------------------------------------------

    def _parse_select(self, ast):
        if ast.args.get('with'):
            raise SqlStatementFormat("WITH / CTE is not allowed")

        if ast.args.get('limit') is not None or ast.args.get('offset') is not None:
            raise SqlStatementFormat("Inline LIMIT/OFFSET is not allowed, use the page/page_size parameters instead")

        from_expr=ast.args.get('from_')
        if from_expr is None or not isinstance(from_expr.this, exp.Table):
            raise SqlStatementFormat("SELECT requires a single table in FROM")

        self._build_table_from_ast(from_expr.this)
        self._build_joins_from_ast(ast.args.get('joins') or [])
        self._build_where(ast.args.get('where'))
        self._build_select_from_ast(ast.expressions)
        self._build_group_by(ast.args.get('group'))
        self._build_order_from_ast(ast.args.get('order'))

    def _parse_insert(self, ast):
        schema=ast.this
        if not isinstance(schema, exp.Schema) or not isinstance(schema.this, exp.Table):
            raise SqlStatementFormat("INSERT requires an explicit column list: INSERT INTO table (col1, col2) VALUES (...)")

        self._build_table_from_ast(schema.this)

        columns=[self._identifier(c) for c in schema.expressions]

        values_expr=ast.expression
        if not isinstance(values_expr, exp.Values) or len(values_expr.expressions) != 1:
            raise SqlStatementFormat("INSERT requires exactly one VALUES row")

        row=values_expr.expressions[0]
        value_nodes=row.expressions if isinstance(row, exp.Tuple) else [row]

        if len(value_nodes) != len(columns):
            raise SqlStatementFormat("Number of columns and values do not match")

        fields={}
        for name, value_node in zip(columns, value_nodes):
            fields[name]={"value": self._literal_value(value_node), "old_value": None}

        self._json_fields=fields

    def _parse_update(self, ast):
        table_expr=ast.this
        if not isinstance(table_expr, exp.Table):
            raise SqlStatementFormat("UPDATE requires a single table")

        self._build_table_from_ast(table_expr)

        where_expr=ast.args.get('where')
        if where_expr is None:
            raise SqlStatementFormat("UPDATE requires a WHERE clause")

        self._build_where(where_expr)

        fields={}
        for set_expr in ast.args.get('expressions', []):
            if not isinstance(set_expr, exp.EQ):
                raise SqlStatementFormat("SET clause must be column = value")

            column=set_expr.this
            if not isinstance(column, exp.Column):
                raise SqlStatementFormat("SET clause left side must be a plain column")

            table_alias=self._resolve_column_alias(column)
            if table_alias != self._sql_table_alias:
                raise IdentifierNotAllowedInSqlStatement("SET clause can only target the main table")

            field=self._identifier(column.this)
            fields[field]={"value": self._literal_value(set_expr.expression), "old_value": None}

        self._json_fields=fields

    def _parse_delete(self, ast):
        if ast.args.get('tables'):
            raise SqlStatementFormat("Multi-table DELETE is not allowed")

        table_expr=ast.this
        if not isinstance(table_expr, exp.Table):
            raise SqlStatementFormat("DELETE requires a single table")

        self._build_table_from_ast(table_expr)

        where_expr=ast.args.get('where')
        if where_expr is None:
            raise SqlStatementFormat("DELETE requires a WHERE clause")

        self._build_where(where_expr)
