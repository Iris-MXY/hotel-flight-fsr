"""
P0 支撑实验：特征消融、单特征基线、结构式模型基线

三个实验，用于给新论文的第 5、6 章提供证据：

  A. 特征组消融  —— 信号来自哪里？数据完整度是不是混淆项？
  B. 单特征基线  —— ML 相比"单个特征"到底强多少？
  C. 结构式基线  —— Merton / KMV 的 PD 单独预测能到什么水平？

2026-09-30 实测结论（成都 3月->6月队列，N=14,851，正例 7.84%）：

  A. 消融
       全部特征             AUC 0.8290   PR-AUC 0.3843
       去完整度             AUC 0.7930   PR-AUC 0.3071
       去完整度+地理        AUC 0.7808   PR-AUC 0.2776
       只留纯价格特征       AUC 0.7474   PR-AUC 0.2485
       只用完整度(对照)     AUC 0.7401   PR-AUC 0.2648
       只用地理(对照)       AUC 0.5813   PR-AUC 0.1034
     -> 完整度（n_records / days_present / span_days）是最强单组，
        是已知混淆项；但**纯价格特征仍有 0.747**，不依赖它。

  B. 单特征（双向最优）
       n_records / days_present  0.7433   <- 完整度（混淆项）
       span_days                 0.6934   <- 完整度
       price_mean                0.6522   <- 最佳"经济"单特征
       price_min / price_median  0.6488 / 0.6467
       ann_vol（年化波动率）      0.5076   <- 接近随机
       price_cv                  0.5038
     -> ML 价格特征 0.7808，比最佳经济单特征高 **+0.129**。

  C. 结构式基线（在"日记录>=50"的记录密集子样本上，N=2,000，正例 2.10%）
       Merton PD（单变量）        AUC 0.5644   PR-AUC 0.0253
       KMV PD（单变量）           AUC 0.6270   PR-AUC 0.0509
       单特征 ann_vol             AUC 0.6447
       ML 价格特征                AUC 0.6470
     -> Merton 2000 家里 957 家（48%）撞 50% 上限；其核心输入"波动率"
        在全队列上 AUC 仅 0.5076。**结构式模型失效的根因是输入变量无信息。**
     ⚠️ 子样本正例率只有 2.10%（全队列 7.84%），因为 Merton 要求足够长的
        价格历史，而记录稀疏的酒店恰恰最容易退出 —— 结构式模型的覆盖面
        系统性偏向安全酒店：**它在最需要它的地方是未定义的。**

用法：
    python src/p0_baselines.py           # 全部三个实验
    python src/p0_baselines.py --no-c    # 跳过耗时的结构式基线（C）
"""

import argparse
import os
import sys
import warnings

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import CLEANED_PRICES_PATH, HOTEL_INFO_PATH
from p0_feasibility import build_dataset, COHORTS

warnings.filterwarnings('ignore')

COMPLETENESS = ['n_records', 'days_present', 'span_days']
GEO = ['lon', 'lat']
LEVEL = ['lv_经济', 'lv_舒适', 'lv_高档', 'lv_豪华']


def _lgb():
    import lightgbm as lgb
    return lgb.LGBMClassifier(n_estimators=400, learning_rate=0.05, num_leaves=31,
                              min_child_samples=30, subsample=0.8, colsample_bytree=0.8,
                              n_jobs=-1, random_state=42, verbose=-1)


def _cv_auc(X, y, verbose=True):
    from sklearn.model_selection import StratifiedKFold, cross_val_predict
    from sklearn.metrics import roc_auc_score, average_precision_score
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    p = cross_val_predict(_lgb(), X, y, cv=cv, method='predict_proba')[:, 1]
    return roc_auc_score(y, p), average_precision_score(y, p)


def experiment_a_ablation(X, y):
    print('\n' + '=' * 96)
    print('A. 特征组消融')
    print('=' * 96)
    sets = [
        ('全部特征', list(X.columns)),
        ('去掉完整度特征', [c for c in X.columns if c not in COMPLETENESS]),
        ('去掉完整度 + 地理', [c for c in X.columns if c not in COMPLETENESS + GEO]),
        ('只留纯价格特征', [c for c in X.columns
                       if c not in COMPLETENESS + GEO + LEVEL]),
        ('只用完整度特征(对照)', COMPLETENESS),
        ('只用地理特征(对照)', GEO),
    ]
    print(f"{'特征集':<28}{'特征数':>8}{'AUC':>10}{'PR-AUC':>10}")
    out = []
    for name, cols in sets:
        a, ap = _cv_auc(X[cols], y)
        out.append((name, len(cols), a, ap))
        print(f'{name:<28}{len(cols):>8}{a:>10.4f}{ap:>10.4f}')
    return out


def experiment_b_single_feature(X, y):
    from sklearn.metrics import roc_auc_score, average_precision_score
    print('\n' + '=' * 96)
    print('B. 单特征基线（取双向最优）')
    print('=' * 96)
    rows = []
    for c in X.columns:
        v = X[c].values
        a = roc_auc_score(y, v)
        if a < 0.5:
            v, a = -v, 1 - a
        rows.append((c, a, average_precision_score(y, v)))
    rows.sort(key=lambda r: -r[1])
    print(f"{'特征':<26}{'AUC':>10}{'PR-AUC':>10}")
    for c, a, ap in rows:
        print(f'{c:<26}{a:>10.4f}{ap:>10.4f}')
    best = rows[0]
    print(f'\n最佳单特征: {best[0]}  AUC={best[1]:.4f}')
    return rows


def experiment_c_structural(X, y, codes, prices, info, n_sub=2000, seed=42):
    from credit_model import HotelCreditModel
    from robustness_checks import KMVCreditModel
    from sklearn.metrics import roc_auc_score, average_precision_score

    print('\n' + '=' * 96)
    print('C. 结构式模型基线 (Merton / KMV)')
    print('=' * 96)

    rc = prices.groupby('hotelCode').size()
    eligible = [c for c in codes if rc.get(c, 0) >= 50]
    rng = np.random.default_rng(seed)
    sub = list(rng.choice(eligible, size=min(n_sub, len(eligible)), replace=False))
    print(f'队列 {len(codes):,} -> 日记录>=50 的 {len(eligible):,} -> 子样本 {len(sub)}')

    # 只喂子样本价格表：把每次查找的扫描量从全表降到子集（否则极慢）
    psub = prices[prices['hotelCode'].isin(sub)].copy()

    mert = HotelCreditModel(psub, info).compute_hotel_credit_metrics_for_codes(
        sub, min_records=8)   # 注意：该参数与"周收益率个数"比较，引擎亦传 8
    kmvd = KMVCreditModel(psub, info).compute_all(sub, min_records=30)

    cap = int((mert['pd'] == 0.5).sum())
    print(f"  Merton {len(mert)} 家有值, PD 范围 [{mert['pd'].min():.4f},"
          f"{mert['pd'].max():.4f}], 撞顶(=0.5) {cap} ({cap/len(mert)*100:.0f}%)")
    print(f"  KMV    {len(kmvd)} 家有值, PD 范围 [{kmvd['kmv_pd'].min():.4f},"
          f"{kmvd['kmv_pd'].max():.4f}]")

    common = [c for c in sub
              if c in set(mert['hotelCode']) and c in set(kmvd['hotelCode'])]
    yc = y.loc[common]
    print(f'\n共有 {len(common)} 家, 正例 {yc.mean()*100:.2f}%'
          f'   <- 注意低于全队列 {y.mean()*100:.2f}%（选择效应）')

    mpd = mert.set_index('hotelCode')['pd'].reindex(common).values
    kpd = kmvd.set_index('hotelCode')['kmv_pd'].reindex(common).values
    price_cols = [c for c in X.columns if c not in COMPLETENESS + GEO]

    print(f"\n{'预测器':<34}{'AUC':>10}{'PR-AUC':>10}")
    for label, s in [('结构式 Merton PD (单变量)', mpd),
                     ('结构式 KMV PD (单变量)', kpd),
                     ('单特征: 年化波动率', X.loc[common, 'ann_vol'].values)]:
        print(f'{label:<34}{roc_auc_score(yc,s):>10.4f}'
              f'{average_precision_score(yc,s):>10.4f}')
    a, ap = _cv_auc(X.loc[common, price_cols], yc)
    print(f"{'ML: 价格特征 LightGBM':<34}{a:>10.4f}{ap:>10.4f}")


def main():
    ap = argparse.ArgumentParser(description='P0 支撑实验：消融 / 单特征 / 结构式基线')
    ap.add_argument('--cohort', nargs=2, default=COHORTS[0],
                    help='队列月份，默认 2024-03 2024-06')
    ap.add_argument('--no-c', action='store_true', help='跳过实验 C（较慢）')
    ap.add_argument('--n-sub', type=int, default=2000, help='实验 C 的子样本规模')
    a = ap.parse_args()

    prices = pd.read_csv(CLEANED_PRICES_PATH)
    prices['date'] = pd.to_datetime(prices['date'])
    prices['ym'] = prices['date'].dt.to_period('M').astype(str)
    info = pd.read_csv(HOTEL_INFO_PATH, encoding='utf-8-sig')

    X, y, codes = build_dataset(prices, info, a.cohort[0], a.cohort[1])
    print(f'队列 {a.cohort[0]} -> {a.cohort[1]}: N={len(y):,}, '
          f'正例 {y.mean()*100:.2f}%')

    experiment_a_ablation(X, y)
    experiment_b_single_feature(X, y)
    if not a.no_c:
        experiment_c_structural(X, y, codes, prices, info, n_sub=a.n_sub)


if __name__ == '__main__':
    main()
