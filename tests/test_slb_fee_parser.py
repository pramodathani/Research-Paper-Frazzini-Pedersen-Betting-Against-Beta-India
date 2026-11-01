"""Tests of the SLB fee parser."""

import pandas as pd
import pytest

from frazzini_pedersen_betting_against_beta_india.data.slb_fee_parser import (
    SlbFeeParser,
)

LINE = (
    'TATA STEEL LIMITED            ,TATASTEEL ,03,03-MAR-2011,N,0000004.25,'
    '0000005.00,0000008.50,0000004.51,0000008.50,    ,         85500,'
    '         431650.00,0000008.50,0000001.50,25-JAN-2011,    32\n'
)


def test_a_contract_line_is_read(tmp_path):
    path = tmp_path / 'SLBM_BC_25012011.DAT'
    path.write_text(LINE)
    table = SlbFeeParser().parse_file(path)
    assert table['symbol'].iloc[0] == 'TATASTEEL'
    assert table['close_fee'].iloc[0] == pytest.approx(8.5)
    assert table['days_to_expiry'].iloc[0] == 37
    assert table['date'].iloc[0] == pd.Timestamp('2011-01-25')
    assert table['quantity'].iloc[0] == 85500
