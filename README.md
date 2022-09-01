# ATCF
ATCF parser

# 環境構築
Anaconda環境を作成し、依存ライブラリをインストールする
```
conda create -n atcf --python==3.10
conda activate atcf
pip install numpy pandas scipy xarray matplotlib
```

# 使用方法
* ATCFデータをオンラインからメモリに直接読み込む（b-deckの例）

    ```py
    from atcf import ATCF
    atcf = ATCF()
    sid = "al142021"
    atcf.download(sid, deck="b")
    ```

* ダウンロード済みのデータをロードする（b-deckの例）

    ```py
    from atcf import ATCF
    atcf = ATCF()
    atcf.load("sample_data/2021/bal142021.dat")
    ```

* ATCFデータのハンドリング

    上記を実行した結果として、`atcf.data` に `xarray.Dataset` 型に整形されたデータが格納されている。
    変数名一覧は
    ```py
    print(list(atcf.data.data_vars))
    >>> ['basin', 'cy', 'technum', 'tech', 'tau', 'lat', 'lon', 'vmax', 'mslp', 'ty', 'rad', 'windcode', 'r1', 'r2', 'r3', 'r4', 'pout', 'rout', 'rmw', 'gusts', 'eye', 'subbasin', 'maxseas', 'initials', 'storm_dir', 'storm_speed', 'name', 'depth', 'seas', 'seascode', 'seas1', 'seas2', 'seas3', 'seas4', 'USERDEFINE1', 'userdata1', 'USERDEFINE2', 'userdata2', 'USERDEFINE3', 'userdata3', 'USERDEFINE4', 'userdata4', 'USERDEFINE5', 'userdata5']
    ```
    で閲覧可能。例えば `vmax` であれば、`atcf.data["vmax"]` としてアクセス可能。単位などは適宜SI単位系などに変換されている。変数の説明や単位は `atcf.data["vmax"].attrs` に辞書形式で格納されている。
    例えば、
    ```py
    print(atcf.data["vmax"].attrs)
    >>> {'standard_name': 'vmax',
        'long_name': 'Maximum sustained wind speed',
        'units': 'ms-1',
        'parser': 'kt2ms',
        'description': 'Maximum sustained wind speed'}
    ```
    また、クイックルックには `xarray.Dataset` の描画関数を用いると良い。例えば
    ```py
    atcf.data["vmax"].plot()
    ```

* NetCDF 出力

    ロードしたATCFデータをNetCDF出力するには、`.to_netcdf` メソッドを用いる。
    ```py
    atcf.to_netcdf("mynetcdf.nc")
    ```

* 解析例

    解析においては `xarray` の[使用方法](https://docs.xarray.dev/en/stable/index.html)に慣れれば良いが、例えば f-deck において `type` が `"DVTS"` の行だけ取り出したい場合は、次のようにする：
    ```py
    DVTS_data = atcf.isel(t=atcf["type"]=="DVTS")
    ```
    複数の条件で絞りたい場合は、
    ```py
    DVTS_data = atcf.isel(t=(atcf["type"]=="DVTS")*(atcf["fixsite"]=="TAFB"))
    ```
    のようにする。

    そのほか、`rmw` が欠損じゃない時のみを取り出したければ、
    ```py
    rmw_data = atcf.isel(t=atcf["rmw"].notnull())
    ```
    などとする。