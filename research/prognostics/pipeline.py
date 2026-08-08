"""Reproducible NASA C-MAPSS FD001 research pipeline for TROJANS AeroFleetX.

Research only: no airworthiness, operational maintenance, or release-to-service authority.
"""
from __future__ import annotations
import hashlib, json, math, zipfile
from pathlib import Path
from typing import Iterable, Mapping, Sequence
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.model_selection import KFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

DATASET_ARCHIVE_SHA256="74bef434a34db25c7bf72e668ea4cd52afe5f2cf8e44367c55a82bfd91a5a34f"
MODEL_ID="cmapss-fd001-rf-phase5-v1"
APP_BASELINE_COMMIT="346d8db1a7e51cdd05ae5dc206e953ec6402fac2"
COLUMNS=["unit_id","cycle"]+[f"setting_{i}" for i in range(1,4)]+[f"sensor_{i}" for i in range(1,22)]
CANDIDATE_FEATURES=COLUMNS[2:]
OUTER_SEED=42
INNER_SEEDS=(4201,4202,4203,4204,4205)
MODEL_SEED=2026
BOOTSTRAP_SEED=4242
RIDGE_GRID=tuple({"alpha":v} for v in (0.1,1.0,10.0,100.0))
RF_GRID=tuple({"max_depth":d,"min_samples_leaf":l,"max_features":f} for d in (10,None) for l in (1,5) for f in (0.7,1.0))
HGB_GRID=tuple({"learning_rate":r,"max_leaf_nodes":n,"l2_regularization":l2} for r in (0.05,0.1) for n in (15,31) for l2 in (0.0,1.0))
FROZEN_RF_PARAMS={"n_estimators":100,"max_depth":10,"min_samples_leaf":5,"max_features":0.7,"random_state":MODEL_SEED}
EXPECTED={"train_rows":20631,"test_rows":13096,"train_engines":100,"test_engines":100,"test_rul":100}

def sha256_file(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""): h.update(block)
    return h.hexdigest()

def verify_dataset_archive(path,expected_sha256=DATASET_ARCHIVE_SHA256):
    actual=sha256_file(path)
    if actual!=expected_sha256: raise ValueError(f"Dataset SHA-256 mismatch: expected {expected_sha256}, got {actual}")
    with zipfile.ZipFile(path) as z:
        bad=z.testzip()
        if bad: raise ValueError(f"Corrupt ZIP member: {bad}")
        required={"train_FD001.txt","test_FD001.txt","RUL_FD001.txt","readme.txt"}
        missing=required.difference(z.namelist())
        if missing: raise ValueError(f"Missing required FD001 files: {sorted(missing)}")
    return actual

def _table(z,name,names):
    with z.open(name) as f: df=pd.read_csv(f,sep=r"\s+",header=None,names=names)
    if df.shape[1]!=len(names): raise ValueError(f"{name}: wrong column count")
    return df

def _validate(train,test,test_rul=None):
    for name,df in (("train",train),("test",test)):
        if list(df.columns)!=COLUMNS: raise ValueError(f"{name}: schema mismatch")
        if df.isna().any().any(): raise ValueError(f"{name}: missing values")
        if not np.isfinite(df.to_numpy(float)).all(): raise ValueError(f"{name}: non-finite values")
        if df.duplicated().any() or df.duplicated(["unit_id","cycle"]).any(): raise ValueError(f"{name}: duplicate records")
    if len(train)!=EXPECTED["train_rows"] or train.unit_id.nunique()!=EXPECTED["train_engines"]: raise ValueError("Unexpected FD001 training size")
    if len(test)!=EXPECTED["test_rows"] or test.unit_id.nunique()!=EXPECTED["test_engines"]: raise ValueError("Unexpected FD001 test size")
    if test_rul is not None and len(test_rul)!=EXPECTED["test_rul"]: raise ValueError("Unexpected official RUL count")

def load_fd001(archive_path,*,verify_hash=True,include_test_truth=False):
    """Return (train, test, test_rul). Official truth is opt-in and excluded by default."""
    if verify_hash: verify_dataset_archive(archive_path)
    with zipfile.ZipFile(archive_path) as z:
        train=_table(z,"train_FD001.txt",COLUMNS); test=_table(z,"test_FD001.txt",COLUMNS); truth=None
        if include_test_truth:
            with z.open("RUL_FD001.txt") as f: truth=pd.read_csv(f,sep=r"\s+",header=None).iloc[:,0].astype(float)
    _validate(train,test,truth)
    return train,test,truth

def add_linear_rul(train):
    out=train.copy()
    out["RUL"]=out.groupby("unit_id")["cycle"].transform("max")-out["cycle"]
    if (out.RUL<0).any(): raise ValueError("Negative generated RUL")
    return out

def zero_variance_features(train):
    return [c for c in CANDIDATE_FEATURES if train[c].nunique(dropna=False)<=1]

def snapshot_features(train):
    drop=set(zero_variance_features(train))
    return [c for c in CANDIDATE_FEATURES if c not in drop]

def engine_folds(engine_ids,*,n_splits,seed):
    ids=np.asarray(sorted({int(x) for x in engine_ids}),dtype=int)
    out=[]
    for tr,va in KFold(n_splits=n_splits,shuffle=True,random_state=seed).split(ids):
        a,b=ids[tr],ids[va]
        if set(a)&set(b): raise AssertionError("Engine leakage")
        out.append((a,b))
    return out

def outer_engine_folds(engine_ids): return engine_folds(engine_ids,n_splits=5,seed=OUTER_SEED)
def inner_engine_folds(engine_ids,fold):
    if fold not in range(1,6): raise ValueError("fold must be 1..5")
    return engine_folds(engine_ids,n_splits=3,seed=INNER_SEEDS[fold-1])

def macro_engine_metrics(frame,y_true,y_pred):
    tmp=pd.DataFrame({"unit_id":frame.unit_id.to_numpy(),"truth":np.asarray(y_true,float),"pred":np.asarray(y_pred,float)})
    rmses=[]; maes=[]
    for _,g in tmp.groupby("unit_id",sort=True):
        e=g.pred.to_numpy()-g.truth.to_numpy(); rmses.append(np.sqrt(np.mean(e**2))); maes.append(np.mean(np.abs(e)))
    e=tmp.pred.to_numpy()-tmp.truth.to_numpy()
    return {"macro_engine_rmse":float(np.mean(rmses)),"macro_engine_mae":float(np.mean(maes)),
            "pooled_rmse":float(np.sqrt(np.mean(e**2))),"pooled_mae":float(np.mean(np.abs(e)))}

def nasa_score(y_true,y_pred):
    e=np.asarray(y_pred,float)-np.asarray(y_true,float)
    return float(np.sum(np.where(e<0,np.exp(-e/13.0)-1.0,np.exp(e/10.0)-1.0)))

def map_rul_to_priority(value):
    try: rul=float(value)
    except (TypeError,ValueError): return "Unavailable","Unavailable"
    if not math.isfinite(rul) or rul<0: return "Unavailable","Unavailable"
    if rul<=10: return "High","0-10"
    if rul<=25: return "High","11-25"
    if rul<=60: return "Medium","26-60"
    if rul<=100: return "Medium","61-100"
    return "Low",">100"

def build_model(kind,params=None):
    p=dict(params or {})
    if kind=="age_linear": return LinearRegression()
    if kind=="ridge": return Pipeline([("scale",StandardScaler()),("model",Ridge(alpha=float(p["alpha"])))])
    if kind=="random_forest":
        return RandomForestRegressor(n_estimators=int(p.get("n_estimators",100)),max_depth=p["max_depth"],
            min_samples_leaf=int(p["min_samples_leaf"]),max_features=float(p["max_features"]),random_state=MODEL_SEED,n_jobs=-1)
    if kind=="hist_gradient_boosting":
        return HistGradientBoostingRegressor(max_iter=300,learning_rate=float(p["learning_rate"]),
            max_leaf_nodes=int(p["max_leaf_nodes"]),l2_regularization=float(p["l2_regularization"]),random_state=MODEL_SEED)
    raise ValueError(kind)

def fit_predict(kind,params,train,val):
    if kind=="mean": return np.clip(np.full(len(val),train.RUL.mean()),0,None)
    if kind=="age_linear":
        m=build_model(kind); m.fit(train[["cycle"]],train.RUL); return np.clip(m.predict(val[["cycle"]]),0,None)
    features=snapshot_features(train); m=build_model(kind,params); m.fit(train[features],train.RUL)
    return np.clip(m.predict(val[features]),0,None)

def _key(p): return json.dumps(dict(p),sort_keys=True,separators=(",",":"))

def tune_model(kind,grid,outer_train,fold):
    rows=[]
    for p in grid:
        scores=[]
        for tri,vai in inner_engine_folds(outer_train.unit_id.unique(),fold):
            tr=outer_train[outer_train.unit_id.isin(tri)]; va=outer_train[outer_train.unit_id.isin(vai)]
            pred=fit_predict(kind,p,tr,va); scores.append(macro_engine_metrics(va,va.RUL,pred)["macro_engine_rmse"])
        rows.append({"params":dict(p),"mean_inner_macro_engine_rmse":float(np.mean(scores)),"sd_inner_macro_engine_rmse":float(np.std(scores,ddof=1))})
    rows.sort(key=lambda r:(r["mean_inner_macro_engine_rmse"],_key(r["params"])))
    return dict(rows[0]["params"]),rows

def run_development_cv(train):
    """Locked nested-CV development experiment. Official test truth is not accepted."""
    data=add_linear_rul(train); outer=[]; tuning=[]
    grids={"ridge":RIDGE_GRID,"random_forest":RF_GRID,"hist_gradient_boosting":HGB_GRID}
    labels={"mean":"Mean RUL","age_linear":"Age-only Linear","ridge":"Ridge","random_forest":"RandomForest","hist_gradient_boosting":"HistGradientBoosting"}
    for fold,(tri,vai) in enumerate(outer_engine_folds(data.unit_id.unique()),1):
        tr=data[data.unit_id.isin(tri)].copy(); va=data[data.unit_id.isin(vai)].copy()
        for kind in ("mean","age_linear"):
            pred=fit_predict(kind,{},tr,va); outer.append({"outer_fold":fold,"model":labels[kind],"params":"fixed",**macro_engine_metrics(va,va.RUL,pred)})
        for kind in ("ridge","random_forest","hist_gradient_boosting"):
            best,rows=tune_model(kind,grids[kind],tr,fold)
            tuning += [{"outer_fold":fold,"model":labels[kind],"params":_key(r["params"]),
                        "mean_inner_macro_engine_rmse":r["mean_inner_macro_engine_rmse"],
                        "sd_inner_macro_engine_rmse":r["sd_inner_macro_engine_rmse"]} for r in rows]
            pred=fit_predict(kind,best,tr,va); outer.append({"outer_fold":fold,"model":labels[kind],"params":_key(best),**macro_engine_metrics(va,va.RUL,pred)})
    return pd.DataFrame(outer),pd.DataFrame(tuning)

def summarize_development(outer):
    return outer.groupby("model",as_index=False).agg(
        mean_macro_engine_rmse=("macro_engine_rmse","mean"),sd_macro_engine_rmse=("macro_engine_rmse","std"),
        mean_macro_engine_mae=("macro_engine_mae","mean"),sd_macro_engine_mae=("macro_engine_mae","std"),
        mean_pooled_rmse=("pooled_rmse","mean"),mean_pooled_mae=("pooled_mae","mean")).sort_values("mean_macro_engine_rmse").reset_index(drop=True)

def frozen_random_forest(train):
    data=train if "RUL" in train.columns else add_linear_rul(train); features=snapshot_features(data)
    m=RandomForestRegressor(**FROZEN_RF_PARAMS,n_jobs=-1); m.fit(data[features],data.RUL)
    return m,features

def official_last_cycle_predictions(model,features,test):
    last=test.sort_values(["unit_id","cycle"]).groupby("unit_id",as_index=False).tail(1).copy()
    pred=np.clip(model.predict(last[list(features)]),0,None)
    return pd.DataFrame({"unit_id":last.unit_id.to_numpy(int),"last_observed_cycle":last.cycle.to_numpy(int),"predicted_RUL":pred}).sort_values("unit_id").reset_index(drop=True)

def evaluate_official_test(predictions,test_rul):
    truth=np.asarray(test_rul,float); pred=predictions.sort_values("unit_id").predicted_RUL.to_numpy(float)
    if len(truth)!=len(pred): raise ValueError("Prediction/truth length mismatch")
    e=pred-truth
    return {"RMSE":float(np.sqrt(np.mean(e**2))),"MAE":float(np.mean(np.abs(e))),"NASA_score":nasa_score(truth,pred),
            "mean_error_pred_minus_true":float(np.mean(e)),"median_absolute_error":float(np.median(np.abs(e)))}

def heldout_permutation_importance(train,repeats=10):
    """Development-only permutation importance; official test truth is not accepted."""
    data=add_linear_rul(train); rows=[]
    for fold,(tri,vai) in enumerate(outer_engine_folds(data.unit_id.unique()),1):
        tr=data[data.unit_id.isin(tri)].copy(); va=data[data.unit_id.isin(vai)].copy()
        m,features=frozen_random_forest(tr); base=np.clip(m.predict(va[features]),0,None)
        baseline=macro_engine_metrics(va,va.RUL,base)["macro_engine_rmse"]; rng=np.random.default_rng(6060+fold)
        for feature in features:
            original=va[feature].to_numpy(copy=True)
            for repeat in range(1,repeats+1):
                x=va[features].copy(); shuffled=original.copy(); rng.shuffle(shuffled); x[feature]=shuffled
                score=macro_engine_metrics(va,va.RUL,np.clip(m.predict(x),0,None))["macro_engine_rmse"]
                rows.append({"outer_fold":fold,"repeat":repeat,"feature":feature,"baseline_macro_engine_rmse":baseline,
                             "permuted_macro_engine_rmse":score,"importance_delta_rmse":score-baseline})
    return pd.DataFrame(rows)

def bootstrap_metric_ci(y_true,y_pred,metric,samples=10000,seed=BOOTSTRAP_SEED):
    truth=np.asarray(y_true,float); pred=np.asarray(y_pred,float)
    if len(truth)!=len(pred): raise ValueError("Prediction/truth length mismatch")
    rng=np.random.default_rng(seed); stats=np.empty(samples)
    for i in range(samples):
        idx=rng.integers(0,len(truth),len(truth)); e=pred[idx]-truth[idx]
        stats[i]=np.sqrt(np.mean(e**2)) if metric=="RMSE" else np.mean(np.abs(e)) if metric=="MAE" else np.nan
    if metric not in ("RMSE","MAE"): raise ValueError("metric must be RMSE or MAE")
    return tuple(float(x) for x in np.quantile(stats,[0.025,0.975]))
