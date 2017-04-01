import pyparsing as pp


LPAR, RPAR = map(pp.Suppress, '()')
column = pp.Word(pp.alphas, pp.alphanums+"_")('column')
function = (
    pp.CaselessKeyword('COUNT')
)('function')
alias = column.copy()
alias_expr = pp.Suppress(pp.CaselessKeyword('AS')) + alias('alias')

function_call = function('function') + LPAR + pp.delimitedList(column)('arguments') + RPAR

expr = pp.Forward()('expr')
expr <<= (
    function_call('function_call') | column('column')
)

full_expr = pp.Group(expr)('expr') + pp.Optional(alias_expr)

exprs = pp.delimitedList(pp.Group(full_expr('full_expr')))

SOURCES = pp.oneOf('entries tags events')

source = pp.Suppress(pp.CaselessKeyword('FROM')) + SOURCES('source')

query = (
    pp.CaselessKeyword('SELECT')('statement') +
    exprs('exprs') +
    source
)
