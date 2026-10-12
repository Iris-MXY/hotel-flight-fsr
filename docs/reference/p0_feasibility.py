"""
P0 可行性预实验：酒店退出是否可从价格面板预测？

决定性问题：如果"平台退出"是随机噪声，那么基于面板特征的机器学习 PD 模型
这条路直接不成立，后续六个月排期全部作废。本脚本用最少的功夫回答它。

设计（严格无泄漏）：
    特征 - 仅取自队列所在月份（如 2024-03）的价格面板
    标签 - 队列月份 + 3 个月后是否仍出现在价格面板中（退出 = 1）

评估：
    1. 判别力 AUC / PR-AUC（正例率约 9%，PR-AUC 的随机基线 = 正例率）
    2. 概率校准 Brier（因为分层评级吃的是 PD 绝对值，不是排序）
    3. 多队列稳定性（3 月→6 月、3 月→5 月、4 月→6 月）
    4. 结构式模型的边际价值（把 Merton DD 作为额外特征是否提升）

判定标准：
    AUC > 0.65  -> 信号存在，方案成立
    AUC ~ 0.5   -> 退出是噪声，此路不通，止损

用法：
    python src/p0_feasibility.py
"""

import os
import sys
import warnings

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import CLEANED_PRICES_PATH, HOTEL_INFO_PATH

warnings.filterwarnings('ignore')

COHORTS = [
    ('2024-03', '2024-06'),
    ('2024-03', '2024-05'),
    ('2024-04', '2024-06'),
]
LEVELS = ['经济', '舒适', '高档', '豪华']


# ───────────────────────────── 特征工程（无泄漏） ─────────────────────────────

def _hotel_features(g):
    """单家酒店在某一月份内的价格面板特征"""
    p = g['price'].values.astype(float)
    n = len(p)
    lr = np.diff(np.log(p)) if n > 1 and (p > 0).all() else np.array([0.0])
    lr = lr[np.isfinite(lr)]

    mean = p.mean()
    trend = np.polyfit(np.arange(n), p, 1)[0] if n > 2 else 0.0

    days = g['date'].dt.day.nunique()
    span = (g['date'].max() - g['date'].min()).days

    return pd.Series({
        'n_records': n,
        'days_present': days,
        'span_days': span,
        'price_mean': mean,
        'price_median': np.median(p),
        'price_min': p.min(),
        'price_max': p.max(),
        'price_std': p.std(),
        'price_cv': p.std() / mean if mean else 0.0,
        'range_ratio': p.max() / p.min() if p.min() else 0.0,
        'logret_std': lr.std() if len(lr) else 0.0,
        'ann_vol': (lr.std() * np.sqrt(365)) if len(lr) else 0.0,
        'trend_norm': trend / mean if mean else 0.0,
        'first_last_ratio': p[-1] / p[0] if p[0] else 1.0,
    })


def build_dataset(prices, info, cohort_month, exit_month):
    """返回 (X, y, codes) —— 特征只来自 cohort_month，标签来自 exit_month"""
    present = prices.groupby(['hotelCode', 'ym']).size().unstack(fill_value=0)
    if cohort_month not in present.columns or exit_month not in present.columns:
        raise ValueError(f'面板缺少 {cohort_month} 或 {exit_month}')

    cohort = present.index[present[cohort_month] > 0]
    y = (present.loc[cohort, exit_month] == 0).astype(int)

    sub = prices[(prices['ym'] == cohort_month) & (prices['hotelCode'].isin(cohort))]
    X = sub.groupby('hotelCode').apply(_hotel_features)
    X = X.join(info.set_index('hotelCode')[['hotelLevel', 'lon经度', 'lat纬度']])
    for lv in LEVELS:
        X[f'lv_{lv}'] = (X['hotelLevel'] == lv).astype(int)
    X = X.drop(columns=['hotelLevel'])
    X['lon'] = X.pop('lon经度')
    X['lat'] = X.pop('lat纬度')

    X = X.loc[cohort].replace([np.inf, -np.inf], np.nan).fillna(0.0)
    return X, y.loc[cohort], cohort


# ─────────────────────────────── 评估 ───────────────────────────────

def evaluate(X, y, label, seed=42, verbose=True):
    from sklearn.model_selection import StratifiedKFold, cross_val_predict
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    from sklearn.pipeline import make_pipeline
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss
    import lightgbm as lgb

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)
    models = {
        '逻辑回归': make_pipeline(StandardScaler(),
                              LogisticRegression(max_iter=2000, class_weight='balanced')),
        '随机森林': RandomForestClassifier(n_estimators=300, min_samples_leaf=5,
                                       class_weight='balanced', n_jobs=-1, random_state=seed),
        'LightGBM': lgb.LGBMClassifier(n_estimators=400, learning_rate=0.05,
                                       num_leaves=31, min_child_samples=30,
                                       subsample=0.8, colsample_bytree=0.8,
                                       class_weight='balanced', n_jobs=-1,
                                       random_state=seed, verbose=-1),
    }

    rows = []
    for name, mdl in models.items():
        prob = cross_val_predict(mdl, X, y, cv=cv, method='predict_proba')[:, 1]
        rows.append({
            '模型': name,
            'AUC': roc_auc_score(y, prob),
            'PR-AUC': average_precision_score(y, prob),
            'Brier': brier_score_loss(y, prob),
        })

    res = pd.DataFrame(rows)
    if verbose:
        print(f'\n--- {label}（N={len(y):,}，正例 {y.mean()*100:.2f}%）---')
        print(f"  随机基线: PR-AUC = {y.mean():.4f}   Brier(常数预测) = "
              f"{brier_score_loss(y, np.full(len(y), y.mean())):.4f}")
        print(f"  {'模型':<10}{'AUC':>9}{'PR-AUC':>10}{'Brier':>9}")
        for _, r in res.iterrows():
            print(f"  {r['模型']:<10}{r['AUC']:>9.4f}{r['PR-AUC']:>10.4f}{r['Brier']:>9.4f}")

        # 特征重要性
        rf = RandomForestClassifier(n_estimators=300, min_samples_leaf=5,
                                    class_weight='balanced', n_jobs=-1, random_state=seed)
        rf.fit(X, y)
        imp = pd.Series(rf.feature_importances_, index=X.columns).sort_values(ascending=False)
        print(f"  Top-8 特征: " + ', '.join(f'{k}({v:.3f})' for k, v in imp.head(8).items()))

    return res


def main():
    print('=' * 78)
    print('P0 可行性预实验：酒店退出是否可从价格面板预测？')
    print('=' * 78)

    prices = pd.read_csv(CLEANED_PRICES_PATH)
    prices['date'] = pd.to_datetime(prices['date'])
    prices['ym'] = prices['date'].dt.to_period('M').astype(str)
    info = pd.read_csv(HOTEL_INFO_PATH, encoding='utf-8-sig')
    print(f'面板: {len(prices):,} 条记录 / {prices["hotelCode"].nunique():,} 家酒店')

    # ---- 1. 主队列 ----
    X, y, _ = build_dataset(prices, info, *COHORTS[0])
    print(f'主队列 {COHORTS[0][0]} -> {COHORTS[0][1]}: {len(y):,} 家，'
          f'退出 {int(y.sum()):,} 家（{y.mean()*100:.2f}%）')
    main_res = evaluate(X, y, f'{COHORTS[0][0]} -> {COHORTS[0][1]}')

    # ---- 2. 多队列稳定性 ----
    print('\n' + '=' * 78)
    print('多队列稳定性（LightGBM 的 AUC）')
    print('=' * 78)
    import lightgbm as lgb
    from sklearn.model_selection import StratifiedKFold, cross_val_predict
    from sklearn.metrics import roc_auc_score, average_precision_score

    stability = []
    for cm, em in COHORTS:
        Xi, yi, _ = build_dataset(prices, info, cm, em)
        mdl = lgb.LGBMClassifier(n_estimators=400, learning_rate=0.05, num_leaves=31,
                                 min_child_samples=30, subsample=0.8, colsample_bytree=0.8,
                                 class_weight='balanced', n_jobs=-1, random_state=42, verbose=-1)
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        prob = cross_val_predict(mdl, Xi, yi, cv=cv, method='predict_proba')[:, 1]
        auc, ap = roc_auc_score(yi, prob), average_precision_score(yi, prob)
        stability.append((f'{cm} -> {em}', len(yi), yi.mean(), auc, ap))
        print(f'  {cm} -> {em}:  N={len(yi):>6,}  正例 {yi.mean()*100:>5.2f}%  '
              f'AUC={auc:.4f}  PR-AUC={ap:.4f}')

    # ---- 3. 判定 ----
    auc_main = main_res.loc[main_res['模型'] == 'LightGBM', 'AUC'].iloc[0]
    aucs = [s[3] for s in stability]
    print('\n' + '=' * 78)
    print('判定')
    print('=' * 78)
    print(f'  主队列 LightGBM AUC = {auc_main:.4f}')
    print(f'  三队列 AUC 范围 = [{min(aucs):.4f}, {max(aucs):.4f}]')
    if min(aucs) > 0.65:
        print('  >>> 结论：信号稳定存在，方案成立，可以启动 P1。')
    elif max(aucs) < 0.58:
        print('  >>> 结论：接近随机，退出基本是噪声，此路不通，建议止损。')
    else:
        print('  >>> 结论：信号偏弱或不稳定，需谨慎评估是否值得投入，'
              '并考虑补充更多月份数据。')


if __name__ == '__main__':
    main()
