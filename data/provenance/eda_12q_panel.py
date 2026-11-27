"""
12 个季度 DB1B 面板探索性分析：竞争悖论验证。
在全部 13 个可用季度（2022Q1–2025Q1）上验证票价变异系数与航司数量的关系。
输出：各季度竞争悖论统计与汇总结果。
"""
import pandas as pd, numpy as np, os, glob, json

BASE = r"C:\Users\weida\Desktop\酒店研究\data\flight_prices_real"
OUTPUT = os.path.join(BASE, "panel_results")
os.makedirs(OUTPUT, exist_ok=True)

# 查找所有季度目录
quarters = sorted(glob.glob(os.path.join(BASE, "db1b_*")))
print(f"找到 {len(quarters)} 个季度目录：\n")
for q in quarters:
    print(f"  {os.path.basename(q)}")

results = []

for qdir in quarters:
    qname = os.path.basename(qdir)
    csv_files = glob.glob(os.path.join(qdir, "*.csv"))
    if not csv_files:
        print(f"\n[跳过] {qname}：未找到 CSV 文件", flush=True)
        continue

    csv_path = csv_files[0]
    print(f"\n{'='*60}")
    print(f"正在处理 {qname}（{os.path.basename(csv_path)}）")
    print(f"{'='*60}")

    # 分块读取，并在航线层面聚合
    route_data = {}  # (origin, dest) -> {fares: [], carriers: set, pax: 0}
    total_rows = 0
    chunk_n = 0

    try:
        for chunk in pd.read_csv(csv_path, chunksize=500000, low_memory=False):
            chunk_n += 1
            total_rows += len(chunk)

            mask = chunk['MktFare'].notna() & (chunk['MktMilesFlown'] > 0)
            chunk = chunk[mask]

            for _, row in chunk.iterrows():
                key = (row['Origin'], row['Dest'])
                if key not in route_data:
                    route_data[key] = {'fares': [], 'carriers': set(), 'pax': 0.0}
                route_data[key]['fares'].append(row['MktFare'])
                route_data[key]['carriers'].add(row['RPCarrier'])
                route_data[key]['pax'] += row['Passengers']

            if chunk_n % 5 == 0:
                print(f"  已处理 {chunk_n * 0.5:.0f} 百万行，{len(route_data):,} 条航线……", flush=True)

        print(f"  合计：{total_rows:,} 行，{len(route_data):,} 条航线")

        # 聚合：计算每条航线的变异系数
        route_stats = []
        for (orig, dest), data in route_data.items():
            fares = np.array(data['fares'])
            if len(fares) >= 10:  # 每条航线至少保留 10 个观测
                mean_f = np.mean(fares)
                std_f = np.std(fares)
                cv = std_f / mean_f if mean_f > 0 else np.nan
                route_stats.append({
                    'origin': orig, 'dest': dest,
                    'n_obs': len(fares),
                    'n_carriers': len(data['carriers']),
                    'total_pax': data['pax'],
                    'mean_fare': mean_f,
                    'median_fare': np.median(fares),
                    'std_fare': std_f,
                    'cv': cv,
                    'min_fare': np.min(fares),
                    'max_fare': np.max(fares),
                })

        df_routes = pd.DataFrame(route_stats).dropna(subset=['cv'])
        print(f"  观测数不少于 10 的航线：{len(df_routes):,}")

        # 检验竞争悖论：按航司数量分组统计变异系数
        cv_by_n = df_routes.groupby('n_carriers').agg(
            n_routes=('cv', 'count'),
            mean_cv=('cv', 'mean'),
            median_cv=('cv', 'median'),
            std_cv=('cv', 'std'),
            mean_fare=('mean_fare', 'mean'),
        ).reset_index()

        print(f"\n  竞争悖论（{qname}）：", flush=True)
        for _, row in cv_by_n.iterrows():
            print(f"    {int(row['n_carriers'])} 家航司：{int(row['n_routes']):,} 条航线，CV={row['mean_cv']:.3f}（中位数={row['median_cv']:.3f}）")

        # 普通最小二乘回归：CV ~ 航司数量
        from sklearn.linear_model import LinearRegression
        X = df_routes[['n_carriers']].values
        y = df_routes['cv'].values
        reg = LinearRegression().fit(X, y)

        # 同时估计对数航司数量模型
        X_log = np.log(df_routes[['n_carriers']].values)
        reg_log = LinearRegression().fit(X_log, y)

        results.append({
            'quarter': qname,
            'total_rows': total_rows,
            'n_routes': len(df_routes),
            'n_carriers_unique': df_routes['n_carriers'].nunique(),
            'mean_cv': df_routes['cv'].mean(),
            'median_cv': df_routes['cv'].median(),
            'cv_n1': cv_by_n[cv_by_n['n_carriers']==1]['mean_cv'].values[0] if 1 in cv_by_n['n_carriers'].values else np.nan,
            'cv_n4': cv_by_n[cv_by_n['n_carriers']==4]['mean_cv'].values[0] if 4 in cv_by_n['n_carriers'].values else np.nan,
            'cv_n8': cv_by_n[cv_by_n['n_carriers']==8]['mean_cv'].values[0] if 8 in cv_by_n['n_carriers'].values else np.nan,
            'cv_n_max': cv_by_n['mean_cv'].iloc[-1],
            'beta_linear': reg.coef_[0],
            'beta_log': reg_log.coef_[0],
            'r2_linear': reg.score(X, y),
            'r2_log': reg_log.score(X_log, y),
        })

        print(f"  线性模型 beta：{reg.coef_[0]:.6f}，R^2={reg.score(X,y):.4f}", flush=True)
        print(f"  对数模型 beta：{reg_log.coef_[0]:.6f}，R^2={reg_log.score(X_log,y):.4f}", flush=True)

    except Exception as e:
        print(f"  [错误] {qname}：{e}")
        results.append({'quarter': qname, 'error': str(e)})

# === 跨季度汇总 ===
print(f"\n{'='*60}")
print("12 个季度横截面汇总")
print(f"{'='*60}")

valid = [r for r in results if 'beta_linear' in r]
print(f"\n有效季度数：{len(valid)}/{len(quarters)}")

if valid:
    betas = [r['beta_linear'] for r in valid]
    r2s = [r['r2_linear'] for r in valid]
    cv1s = [r['cv_n1'] for r in valid if not np.isnan(r['cv_n1'])]
    cv_maxs = [r['cv_n_max'] for r in valid]

    print(f"\n  beta（CV ~ 航司数量）：", flush=True)
    print(f"    均值：{np.mean(betas):.6f}，标准差：{np.std(betas):.6f}", flush=True)
    print(f"    最小值：{np.min(betas):.6f}（{valid[np.argmin(betas)]['quarter']}）", flush=True)
    print(f"    最大值：{np.max(betas):.6f}（{valid[np.argmax(betas)]['quarter']}）", flush=True)
    print(f"    所有 beta 均为正：{all(b > 0 for b in betas)}", flush=True)

    print(f"\n  R^2:", flush=True)
    print(f"    均值：{np.mean(r2s):.4f}，范围：[{np.min(r2s):.4f}, {np.max(r2s):.4f}]", flush=True)

    if cv1s and cv_maxs:
        print(f"\n  CV 范围：", flush=True)
        print(f"    垄断（航司数=1）：平均 CV = {np.mean(cv1s):.3f}", flush=True)
        print(f"    竞争最充分：平均 CV = {np.mean(cv_maxs):.3f}", flush=True)
        print(f"    CV 差值：{np.mean(cv_maxs) - np.mean(cv1s):.3f}", flush=True)

    # 保存完整结果
    df_results = pd.DataFrame(valid)
    csv_path = os.path.join(OUTPUT, "competition_paradox_12q.csv")
    df_results.to_csv(csv_path, index=False)
    print(f"\n结果已保存：{csv_path}", flush=True)

    # 各季度明细
    print(f"\n{'季度':<15} {'航线数':>10} {'线性 beta':>10} {'R^2':>8} {'CV(1家)':>10} {'CV(最大)':>10} {'beta>0':>8}", flush=True)
    print("-" * 73, flush=True)
    for r in valid:
        print(f"{r['quarter']:<15} {r['n_routes']:>10,} {r['beta_linear']:>10.6f} {r['r2_linear']:>8.4f} {r['cv_n1']:>10.3f} {r['cv_n_max']:>10.3f} {'是' if r['beta_linear'] > 0 else '否':>8}", flush=True)

print("\n处理完成。")
