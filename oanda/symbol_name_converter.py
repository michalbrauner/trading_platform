class SymbolNameConverter(object):
    def __init__(self):
        pass

    def convert_symbol_names_to_oanda_symbol_names(self, symbols: list) -> list:
        return list(map(lambda symbol: (symbol[0:3] + '_' + symbol[3:]).upper(), symbols))

    def convert_oanda_symbol_names_to_normalized_names(self, symbols: list) -> list:
        return list(map(lambda symbol: (symbol[0:3] + symbol[4:]).upper(), symbols))
