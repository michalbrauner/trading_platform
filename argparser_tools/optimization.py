def with_sl_and_tp(parser):
    # (argparse.ArgumentParser) -> argparse.ArgumentParser

    parser.add_argument('--sl_min', type=int, required=True)
    parser.add_argument('--sl_max', type=int, required=True)
    parser.add_argument('--sl_step', type=int, required=True)

    parser.add_argument('--tp_min', type=int, required=True)
    parser.add_argument('--tp_max', type=int, required=True)
    parser.add_argument('--tp_step', type=int, required=True)

    return parser


def with_sma_short_and_long(parser):
    # (argparse.ArgumentParser) -> argparse.ArgumentParser

    parser.add_argument('--short_window_min', type=int, required=True)
    parser.add_argument('--short_window_max', type=int, required=True)
    parser.add_argument('--short_window_step', type=int, required=True)

    parser.add_argument('--long_window_min', type=int, required=True)
    parser.add_argument('--long_window_max', type=int, required=True)
    parser.add_argument('--long_window_step', type=int, required=True)

    return parser
