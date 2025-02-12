from datetime import date
from io import StringIO

import numpy as np
import pandas as pd
import pytest

from pvoutput import pvoutput


def test_date_to_pvoutput_str():
    VALID_DATE_STR = "20190101"
    assert pvoutput.date_to_pvoutput_str(VALID_DATE_STR) == VALID_DATE_STR
    ts = pd.Timestamp(VALID_DATE_STR)
    assert pvoutput.date_to_pvoutput_str(ts) == VALID_DATE_STR


def test_check_date():
    assert pvoutput._check_date("20190101") is None
    with pytest.raises(ValueError):
        pvoutput._check_date("2010")
    with pytest.raises(ValueError):
        pvoutput._check_date("2010-01-02")


def test_check_pv_system_status():
    def _make_timeseries(start, end):
        index = pd.date_range(start, end, freq="5T")
        n = len(index)
        timeseries = pd.DataFrame(np.zeros(n), index=index)
        return timeseries

    DATE = date(2019, 1, 1)
    good_timeseries = _make_timeseries("2019-01-01 00:00", "2019-01-02 00:00")
    pvoutput.check_pv_system_status(good_timeseries, DATE)

    bad_timeseries = _make_timeseries("2019-01-01 00:00", "2019-01-03 00:00")
    with pytest.raises(ValueError):
        pvoutput.check_pv_system_status(bad_timeseries, DATE)

    bad_timeseries2 = _make_timeseries("2019-01-02 00:00", "2019-01-03 00:00")
    with pytest.raises(ValueError):
        pvoutput.check_pv_system_status(bad_timeseries2, DATE)


def test_process_batch_status():
    # Response text copied from
    # https://pvoutput.org/help.html#dataservice-getbatchstatus
    response_text = """
20140330;07:35,2,24;07:40,4,24;07:45,6,24;07:50,8,24;07:55,13,60;08:00,24,132
20140329;07:35,2,24;07:40,4,24;07:45,6,24;07:50,8,24;07:55,13,60;08:00,24,132
20140328;07:35,2,24;07:40,4,24;07:45,6,24;07:50,8,24;07:55,13,60;08:00,24,132"""

    correct_interpretation_csv = """
datetime,cumulative_energy_gen_Wh,instantaneous_power_gen_W,temperature_C,voltage
2014-03-28 07:35:00,2.0,24.0,,
2014-03-28 07:40:00,4.0,24.0,,
2014-03-28 07:45:00,6.0,24.0,,
2014-03-28 07:50:00,8.0,24.0,,
2014-03-28 07:55:00,13.0,60.0,,
2014-03-28 08:00:00,24.0,132.0,,
2014-03-29 07:35:00,2.0,24.0,,
2014-03-29 07:40:00,4.0,24.0,,
2014-03-29 07:45:00,6.0,24.0,,
2014-03-29 07:50:00,8.0,24.0,,
2014-03-29 07:55:00,13.0,60.0,,
2014-03-29 08:00:00,24.0,132.0,,
2014-03-30 07:35:00,2.0,24.0,,
2014-03-30 07:40:00,4.0,24.0,,
2014-03-30 07:45:00,6.0,24.0,,
2014-03-30 07:50:00,8.0,24.0,,
2014-03-30 07:55:00,13.0,60.0,,
2014-03-30 08:00:00,24.0,132.0,,"""

    df = pvoutput._process_batch_status(response_text)
    correct_df = pd.read_csv(
        StringIO(correct_interpretation_csv), parse_dates=["datetime"], index_col="datetime"
    )
    pd.testing.assert_frame_equal(df, correct_df)

    empty_df = pvoutput._process_batch_status("")
    assert empty_df.empty, "DataFrame should be empty but it was:\n{}\n".format(empty_df)

    with pytest.raises(NotImplementedError):
        pvoutput._process_batch_status("20140330;07:35,2,24,2,24,23.1,230.3")
