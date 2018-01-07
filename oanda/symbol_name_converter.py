class SymbolNameConverter(object):
    def __init__(self):
        pass

    def convert_symbol_names_to_oanda_symbol_names(self, symbols):
        data = map(lambda symbol: (symbol[0:3] + '_' + symbol[3:]).upper(), symbols)

        return data
