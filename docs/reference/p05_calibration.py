"""
P0.5 论点验证：判别力 vs 概率校准

验证论文第三条贡献是否成立：
    "判别力（AUC）容易获得，概率校准才是难点；而分层评级吃的是 PD 绝对值。"

设计：在同一份数据、同一套交叉验证下对比 7 个配置，观察
    - 判别力指标 AUC / PR-AUC 变动幅度
    - 校准指标 Brier / ECE / 平均预测概率 变动幅度

关键对照（最有冲击力）：
    随机森林 balanced vs 无权重 —— AUC 几乎相同，ECE 差约 14 倍。

结论（2026-09-30 实测，成都 3月->6月队列 N=14,851，正例 7.84%）：
    AUC 极差 0.0355，ECE 极差 0.3050（50 倍）。
    `class_weight='balanced'` 几乎不改善判别力，却普遍破坏概率校准
    （逻辑回归平均预测 PD 被放大 5.0 倍）。
    加 isotonic 校准可恢复（ECE 0.0943 -> 0.0100），且不伤 AUC。

用法：
    python src/p05_calibration.py
"""

import os
import sys
import warnings

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import CLEANED_PRICES_PATH, HOTEL_INFO_PATH
from p0_feasibility import build_dataset, COHORTS

warnings.filterwarnings('ignore')


def expected_calibration_error(y, p, n_bins=10):
    """ECE：按预测概率分箱，取 |平均预测 - 实际频率| 的样本加权平均"""
    edges = np.linspace(0, 1, n_bins + 1)
    idx = np.digitize(p, edges[1:-1])
    err = 0.0
    for b in range(n_bins):
        m = idx == b
        if m.sum() == 0:
            continue
        err += m.mean() * abs(p[m].mean() - y[m].mean())
    return err


def build_models():
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    from sklearn.pipeline import make_pipeline
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.calibration import CalibratedClassifierCV
    import lightgbm as lgb

    lgb_base = dict(n_estimators=400, learning_rate=0.05, num_leaves=31,
                    min_child_samples=30, subsample=0.8, colsample_bytree=0.8,
                    n_jobs=-1, random_state=42, verbose=-1)

    return {
        '逻辑回归 (无权重)': make_pipeline(
            StandardScaler(), LogisticRegression(max_iter=2000)),
        '逻辑回归 (balanced)': make_pipeline(
            StandardScaler(), LogisticRegression(max_iter=2000, class_weight='balanced')),
        '随机森林 (无权重)': RandomForestClassifier(
            n_estimators=300, min_samples_leaf=5, n_jobs=-1, random_state=42),
        '随机森林 (balanced)': RandomForestClassifier(
            n_estimators=300, min_samples_leaf=5, class_weight='balanced',
            n_jobs=-1, random_state=42),
        'LightGBM (无权重)': lgb.LGBMClassifier(**lgb_base),
        'LightGBM (balanced)': lgb.LGBMClassifier(class_weight='balanced', **lgb_base),
        'LightGBM balanced + isotonic': CalibratedClassifierCV(
            lgb.LGBMClassifier(class_weight='balanced', **lgb_base),
            method='isotonic', cv=3),
    }


def main():
    from sklearn.model_selection import StratifiedKFold, cross_val_predict
    from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss

    prices = pd.read_csv(CLEANED_PRICES_PATH)
    prices['date'] = pd.to_datetime(prices['date'])
    prices['ym'] = prices['date'].dt.to_period('M').astype(str)
    info = pd.read_csv(HOTEL_INFO_PATH, encoding='utf-8-sig')
    X, y, _ = build_dataset(prices, info, *COHORTS[0])

    base = y.mean()
    print('=' * 96)
    print('P0.5  判别力 vs 概率校准')
    print('=' * 96)
    print(f'N={len(y):,}  真实正例率={base*100:.2f}%  '
          f'(完美校准的模型：平均预测概率应≈{base:.4f})')

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    print(f"\n{'模型':<32}{'AUC':>8}{'PR-AUC':>9}{'Brier':>9}{'ECE':>8}"
          f"{'平均预测PD':>12}{'放大倍数':>10}")
    print('-' * 96)

    rows = []
    for name, mdl in build_models().items():
        p = cross_val_predict(mdl, X, y, cv=cv, method='predict_proba')[:, 1]
        rows.append({
            'model': name,
            'auc': roc_auc_score(y, p),
            'pr_auc': average_precision_score(y, p),
            'brier': brier_score_loss(y, p),
            'ece': expected_calibration_error(y, p),
            'mean_pd': p.mean(),
        })
        r = rows[-1]
        print(f"{name:<32}{r['auc']:>8.4f}{r['pr_auc']:>9.4f}{r['brier']:>9.4f}"
              f"{r['ece']:>8.4f}{r['mean_pd']:>12.4f}{r['mean_pd']/base:>9.1f}x")

    print('-' * 96)
    auc_spread = max(r['auc'] for r in rows) - min(r['auc'] for r in rows)
    ece_spread = max(r['ece'] for r in rows) - min(r['ece'] for r in rows)
    print(f"判别力 AUC 极差 = {auc_spread:.4f}")
    print(f"校准   ECE 极差 = {ece_spread:.4f}   (相差 {ece_spread/min(r['ece'] for r in rows):.0f} 倍以上)")
    print(f"平均预测PD 范围 = {min(r['mean_pd'] for r in rows):.4f} ~ "
          f"{max(r['mean_pd'] for r in rows):.4f}   (真实 {base:.4f})")
    print('\n结论：判别力在一个很宽的模型选择空间里几乎不变，而校准相差一个数量级；'
          '加 isotonic 校准可恢复校准且不伤 AUC。')

    return pd.DataFrame(rows)


if __name__ == '__main__':
    main()
