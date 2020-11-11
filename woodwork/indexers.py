import pandas as pd

import woodwork as ww
from woodwork.utils import _new_dt_including


class _iLocIndexer:
    def __init__(self, ww_data):
        self.ww_data = ww_data
        if isinstance(ww_data, ww.DataTable):
            self.underlying_data = ww_data._dataframe
            if not isinstance(self.underlying_data, pd.DataFrame):
                raise TypeError("iloc is only supported for DataFrames coming from pandas")
        elif isinstance(ww_data, ww.DataColumn):
            self.underlying_data = ww_data._series
            if not isinstance(self.underlying_data, pd.Series):
                raise TypeError("iloc is only supported for DataColumns coming from pandas")

    def __getitem__(self, key):
        selection = self.underlying_data.iloc[key]
        if isinstance(selection, pd.Series):
            col_name = selection.name
            if isinstance(self.ww_data, ww.DataTable) and set(selection.index) == set(self.ww_data.columns):
                # return selection as series if series of one row.
                return selection
            if isinstance(self.ww_data, ww.DataTable):
                logical_type = self.ww_data.logical_types.get(col_name, None)
                semantic_tags = self.ww_data.semantic_tags.get(col_name, None)
            else:
                logical_type = self.ww_data.logical_type or None
                semantic_tags = self.ww_data.semantic_tags or None
            if semantic_tags is not None:
                semantic_tags = semantic_tags - {'index'} - {'time_index'}
            name = self.ww_data.name
            return ww.DataColumn(selection,
                                 logical_type=logical_type,
                                 semantic_tags=semantic_tags,
                                 use_standard_tags=self.ww_data.use_standard_tags,
                                 name=name)
        elif isinstance(selection, pd.DataFrame):
            return _new_dt_including(self.ww_data, selection)
        else:
            # singular value
            return selection
