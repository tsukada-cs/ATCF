import os
import toml

import numpy as np
import pandas as pd
import xarray as xr


class ATCF:
    home = "https://ftp.nhc.noaa.gov/atcf/"
    subdir = {"a":"fst/", "b":"btk/", "e":"gpce/", "f":"fix/"}
    def __init__(self):
        pass
    
    def date_parse_YmdH(self, string):
        return pd.to_datetime(string, format="%Y%m%d%H")

    def date_parse_YmdHM(self, string):
        return pd.to_datetime(string, format="%Y%m%d%H%M")

    def parse_latNS(self, string):
        if string == "" or isinstance(string, float):
            return np.nan
        lat = float(string[:-1])
        if string[-1] == "S":
            lat = -lat
        return lat

    def parse_lonEW(self, string):
        if string == "" or isinstance(string, float):
            return np.nan
        lon = float(string[:-1])
        if string[-1] == "W":
            lon = -lon
        return lon

    def parse_01latNS(self, string):
        return 0.1 * self.parse_latNS(string)

    def parse_01lonEW(self, string):
        return 0.1 * self.parse_lonEW(string)

    def parse_001latNS(self, string):
        return 0.01 * self.parse_latNS(string)

    def parse_001lonEW(self, string):
        return 0.01 * self.parse_lonEW(string)

    def inch001_to_mm(self, string):
        if string == "" or isinstance(string, float):
            return np.nan
        return 0.01 * 25.4 * float(string)

    def kt2ms(self, kt):
        if kt == "":
            return np.nan
        return 0.514444 * float(kt)

    def nm2km(self, nm):
        if nm == "":
            return np.nan
        return 1.852 * float(nm)

    def feet100_to_km(self, feet):
        return  100 * self.feet2km(feet)

    def feet2km(self, feet):
        if feet == "":
            return np.nan
        return  1e-3 * 0.3048 * float(feet)

    def feet2m(self, feet):
        if feet == "":
            return np.nan
        return  0.3048 * float(feet)

    def m2km(self, m):
        if m == "":
            return np.nan
        return float(m) * 1e-3

    def str_upper(self, m):
        return str(m).upper()

    def str_lower(self, m):
        return str(m).lower()
    
    def load(self, csv, deck=None):
        if deck is None:
            deck = os.path.basename(csv)[0]
        if deck not in ("a", "b", "e", "f"):
            raise ValueError("`deck` must be in ('a', 'b', 'e', 'f')")

        atcf_set = toml.load(os.path.dirname(__file__) + "/atcf.toml")
        deckinfo = atcf_set[deck]
        
        common_cols = deckinfo["common_cols"]
        total_cols = deckinfo["total_cols"]
        format_specifier = deckinfo["format_specifier"]
        subcolumn_devider = deckinfo["subcolumn_devider"]
        common_columns = list(deckinfo.keys())[4:4+common_cols]

        self.dtypes = {}
        self.converters = {}
        self.timevars = []
        for column in common_columns:
            parser = deckinfo[column]["parser"]
            if parser == "":
                continue
            if parser in ("str", "int", "float", "bool", "dict", "list", "tuple"):
                self.dtypes[column] = eval(parser)
            else:
                self.converters[column] = eval("self." + parser)
                if parser in ("date_parse_YmdH", "date_parse_YmdHM"):
                    self.timevars.append(column)

        unfix_columns = "__"+pd.Series(np.arange(total_cols-common_cols)).astype(str)
        read_columns = np.r_[common_columns, unfix_columns.values]

        read_options = {
            "index_col": False,
            "header": None,
            "skipinitialspace": True,
            "names": read_columns,
            "dtype": self.dtypes,
            "converters": self.converters,
            "na_values": "",
        }
        self.df = pd.read_csv(csv, **read_options)

        self.data = xr.Dataset.from_dataframe(self.df.iloc[:,:common_cols])
        for commonkey in common_columns:
            self.data[commonkey].attrs = deckinfo[commonkey]
        if subcolumn_devider == "":
            self.data = self.data.swap_dims({"index":"t"})
            return
    
        formats = []
        for key, val in deckinfo.items():
            if type(val) is dict:
                formats.append(key)
        for fmt in formats: # ex) fmt = "f.30"
            subinfo = deckinfo[fmt]
            # trim and rename
            sub_df = self.df[self.df[format_specifier]==fmt].iloc[:, common_cols:common_cols+len(subinfo.keys())]
            sub_df = sub_df.rename(columns=dict(zip(unfix_columns, subinfo.keys())))
            # convert subinfos
            for subinfo_key in subinfo.keys(): # ex) subinfo_key = f.30.rmw
                parser = subinfo[subinfo_key]["parser"]
                if parser in ("str", "int", "float", "bool", "dict", "list", "tuple"):
                    sub_df[subinfo_key] = sub_df[subinfo_key].astype(eval(parser))
                    if parser == "str":
                        sub_df[subinfo_key] = sub_df[subinfo_key].where(~(sub_df[subinfo_key]=="nan"), np.nan)
                else:
                    sub_df[subinfo_key] = sub_df[subinfo_key].apply(eval("self."+parser))
            
            divcolumn = self.data[subcolumn_devider].loc[sub_df.index]
            divcolumn[divcolumn.isnull()] = "UNKN"
            divcolumn[divcolumn=="nan"] = "UNKN"
            #** to xr.Dataset
            for subcol_name in sorted(list(set(divcolumn.values))):
                ds = xr.Dataset.from_dataframe(sub_df.iloc[(divcolumn==subcol_name).values,:])
                for subinfo_key in subinfo.keys(): # ex) subinfo_key = f.30.rmw
                    attrs = deckinfo[fmt][subinfo_key]
                    attrs["standard_name"] = subcol_name.lower()+"_"+attrs["standard_name"]
                    ds[subinfo_key].attrs = attrs
                ds = ds.rename(dict(zip(subinfo.keys(), subcol_name.lower()+"_"+pd.Series(subinfo.keys()))))
                self.data = xr.merge([self.data, ds])

        self.data = self.data.swap_dims({"index":"t"})
        for varname, dtype in self.dtypes.items():
            if dtype == str:
                dtype = "unicode"
            self.data[varname] = self.data[varname].astype(dtype)
        return

    def download(self, sid, deck="b"):
        url = self.compose_url(sid, deck)
        return self.load(url, deck)
    
    def _parse_sid(self, sid):
        return {"sid": sid, "basin": sid[:2], "number": sid[2:4], "year": sid[4:8]}

    def compose_url(self, sid, deck):
        """
        Parameters
        ----------
        sid : str
            Storm ID, `bbnnyyyy` format.
            * bb: basin
            * nn: number
            * yyyy: year
        deck : str
            deck specifier.
            * a: contains the forecast "aids", or model and official forecasts
            * b: contains the best tracks, or the official (re-)analysis of final storm position and intensity at synoptic times (00, 06, 12, 18 UTC) and landfall times
            * e: contains ensemble and probabilistic information (genesis, RI, etc.: 20% chance of genesis)
            * f: contains "fixes" from observations (e.g. Dvorak fixes, aircraft reconnaissance fixes, etc.)
        """
        if deck not in ("a", "b", "e", "f"):
            raise ValueError("deck must be in ('a', 'b', 'e', 'f')")
        sid = self._parse_sid(sid)
        fname = deck + sid["sid"]
        if int(sid["year"]) == pd.Timestamp.now().year:
            data_dir = self.home + self.subdir[deck]
            suffix = ".dat"
        else:
            data_dir = self.home + f'archive/{sid["year"]}/'
            suffix = ".dat.gz"
        url = data_dir + fname + suffix
        return url
    
    def to_netcdf(self, oname):
        data = self.data.copy(True)
        for timevars in self.timevars:
            if data[timevars].isnull().all():
                continue
            t0 = data[timevars][data[timevars].notnull()][0]
            data = data.assign_coords({timevars: data[timevars]})
            data[timevars] = pd.to_timedelta(data[timevars]-t0).total_seconds()
            data[timevars].attrs.update({"units": f'seconds since {t0.dt.strftime("%F %H:%M:%S").item()} UTC'})
        encoding = {}
        for varname in self.data:
            encode_opt = {varname: {"complevel": 3, "zlib": True}}
            encoding.update(encode_opt)
        data.to_netcdf(oname, encoding=encoding)