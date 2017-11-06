from app import db
from app.models import Symbol

symbols = "AAPL,AMZN,BABA,FB,MU,MSFT,INTC,NVDA,TSLA,GE,GOOGL,QCOM,GOOG,BAC,SHOP,CELG,CHTR,T,MA,NFLX,MRK,V,JPM,AMD,AGN,BIDU,EXPE,C,AVGO,CVX,UNH,PFE,WFC,CMCSA,K,AABA,WBA,PCLN,AET,VZ,MDLZ,ORCL,BA,TWX,ROK,JNJ,XOM,IBM,MYL,GILD,EMR,GS,ABBV,PG,X,ALXN,WYNN,GM,TWTR,MCK,EA,UAA,AAAP,DIS,NKE,PM,PYPL,CAT,JD,FSLR,F,SLB,CRM,LEN,CMI,WDC,MCD,OHI,WMT,CVS,HD,AMGN,PEP,BMY,SQ,MS,CSCO,MO,MMM,ATVI,TEVA,ADBE,AKS,SBUX,LYB,CTSH,CAA,SPGI,UA,TMUS,AMT,LOW,ABT,FIS,DWDP,REGN,AMAT,COST,ETN,BP,UTX,KHC,MDT,PXD,ICE,MAT,EXAS,ADM,TGT,CMG,VRTX,LRCX,SPG,CSX,STZ,TXN,SBAC,CREE,HON,CAH,BIIB,APC,OXY,EOG,LLY,MPC,UNP,KO,CL,COP,CTL,SWKS,OA,CB,ACN,TAL,SHPG,KLAC,CBS,USB,SNE,CGNX,UAL,TMO,GSK,CTRP,MOS,AXP,CLX,PCG,HCA,BDX,NVS,SCHW,FLT,HAL,RTN,IR,NXPI,UPS,TRU,CCI,ANTM,ECL,CZR,EL,LVS,IPGP,ISRG,COG,GIS,M,TJX,WCG,TRIP,CI,OLED,BBT,INCY,HUN,VLO,ABC,VNTV,GGP,BSX,ALGN,DNKN,VST,SPX,^GSPC,FORD,FWP,FOSL,FMI,FOXF,FRAN,FELE,FRED,RAIL,FEIM,FRPT,FTEO,FTR,FTRPR,FRPH,FSBW,FSBC,FTD,FTEK,FCEL,FLGT,FORK,FLL,FULT,FSNN,FTFT,FFHL,WILC,GTHX,FOANC,GAIA,GLPG,GALT,GALE,GLMD,GLPI,GPIC,GRMN,GARS,GDS,GEMP,GENC,GNCMA,GFN,GFNCP,GENE,GNUS,GNMK,GNCA,GHDX,GNTX,THRM,GEOS,GABC,GERN,GEVO,ROCK,GIGM,GIII,GILT,GBCI,GLAD,GLADN,GOOD,GOODM,GOODO,GOODP,GAIN,GAINM,GAINN,GAINO,LAND,LANDP,GLBZ,GBT,GLBR,ENT,GBLI,GBLIZ,GPAC,SELF,GWRS,KRMA,FINX,BFIT,SNSR,LNGR,MILN,EFAS,QQQC,BOTZ,CATH,SOCL,ALTY,SRET,YLCO,GLBS,AAON,MNST,BUD,BREW"

# 301 Symbols

for s in symbols.split(","):
    try:
        sym = Symbol()
        sym.name = s
        db.session.add(sym)
        db.session.commit()
    except:
        db.session.rollback()
        continue