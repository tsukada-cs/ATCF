#%%
from atcf import ATCF
atcf = ATCF()
sid = "al142021"
atcf.download(sid, deck="b")
atcf.data["vmax"].plot()
# %%
