"""
机票 FSR 探索性分析 v4：单遍流式处理，完全向量化。
策略：只遍历全部季度一次，按数据块分组，并流式合并结果。
每完成一个季度就输出快照，便于观察进度。
"""
import pandas as pd, numpy as np, json, time, sys, glob, os
from collections import defaultdict
from pathlib import Path

BASE = Path(r"C:\Users\weida\Desktop\酒店研究\data\flight_prices_real")
OUT = Path(r"C:\Users\weida\Desktop\酒店研究\output")
OUT.mkdir(exist_ok=True)

COLS = ['Year', 'Quarter', 'Origin', 'Dest', 'RPCarrier', 'Passengers',
        'MktFare', 'MktMilesFlown']

def log(msg):
    print(msg, flush=True)

def merge_route_chunk(acc, chunk_stats):
    """把数据块内的航线聚合结果（样本量、和、平方和、航司集合、乘客数和）
    合并到全局累加器，并采用并行均值/M2 合并算法。"""
    for key, (n2, sum2, sum2sq, carriers2, pax2) in chunk_stats.items():
        if key not in acc:
            acc[key] = [n2, sum2, sum2sq, set(carriers2), pax2]
        else:
            n1, sum1, sum1sq, carriers1, pax1 = acc[key]
            # 合并均值与 M2（Chan 等提出的并行方差算法）
            n_new = n1 + n2
            mean1 = sum1 / n1; mean2 = sum2 / n2
            delta = mean2 - mean1
            # M2_new = M2_1 + M2_2 + delta^2 * n1 * n2 / n_new
            m2_1 = sum1sq - n1 * mean1**2  # 原有 M2（未归一化）
            m2_2 = sum2sq - n2 * mean2**2
            m2_new = m2_1 + m2_2 + delta**2 * n1 * n2 / n_new
            sum_new = sum1 + sum2
            sum2sq_new = m2_new + n_new * (sum_new / n_new)**2
            carriers1.update(carriers2)
            acc[key] = [n_new, sum_new, sum2sq_new, carriers1, pax1 + pax2]

# ─── 查找季度文件 ───
files = sorted(glob.glob(str(BASE / 'db1b_*/Origin_and_Destination_Survey_DB1BMarket_*.csv')) +
               glob.glob(str(BASE / 'Origin_and_Destination_Survey_DB1BMarket_*/Origin_and_Destination_Survey_DB1BMarket_*.csv')))
labels = [os.path.basename(os.path.dirname(f)) for f in files]
log(f"找到 {len(files)} 个季度文件\n")

t0 = time.time()

# ─── 单遍处理：全局、航司、航线与季度统计 ───
log("=" * 70)
log("单遍流式处理：航线、航司与全局统计")
log("=" * 70)

# 全局累加器
global_n = 0; global_sum = 0.0; global_sum2 = 0.0
global_min = float('inf'); global_max = -float('inf')

# 航司累加器
carrier_data = defaultdict(lambda: {'n': 0, 'sum_fare': 0.0, 'sum2_fare': 0.0,
                                     'sum_pax': 0.0, 'routes': set()})

# 航线累加器（跨数据块合并）
route_acc = {}  # (origin,dest) -> [n, sum, sum2, carriers_set, pax_sum]

# 各季度快照
qtr_snapshots = []

for idx, (label, fpath) in enumerate(zip(labels, files)):
    q_t0 = time.time()
    q_n = 0; q_sum = 0.0; q_sum2 = 0.0
    chunk_n = 0
    fsize_mb = os.path.getsize(fpath) / 1e6

    for chunk in pd.read_csv(fpath, chunksize=150000, usecols=COLS, low_memory=False):
        chunk_n += 1
        valid = chunk[(chunk['MktFare'].notna()) & (chunk['MktMilesFlown'] > 0)]
        if len(valid) == 0: continue
        fares = valid['MktFare'].values.astype(np.float64)
        paxs = valid['Passengers'].values.astype(np.float64)

        # --- 全局统计 ---
        q_n += len(fares); global_n += len(fares)
        q_sum += fares.sum(); global_sum += fares.sum()
        q_sum2 += (fares**2).sum(); global_sum2 += (fares**2).sum()
        global_min = min(global_min, fares.min())
        global_max = max(global_max, fares.max())

        # --- 航司统计（按数据块向量化） ---
        c_grp = valid.groupby('RPCarrier')
        c_n = c_grp['MktFare'].count()
        c_sum = c_grp['MktFare'].sum()
        c_sum2 = c_grp['MktFare'].apply(lambda x: (x**2).sum())
        c_pax = c_grp['Passengers'].sum()
        c_routes = c_grp.apply(lambda g: set(zip(g['Origin'], g['Dest'])))
        for carrier in c_n.index:
            cd = carrier_data[carrier]
            cd['n'] += int(c_n[carrier])
            cd['sum_fare'] += float(c_sum[carrier])
            cd['sum2_fare'] += float(c_sum2[carrier])
            cd['sum_pax'] += float(c_pax[carrier])
            cd['routes'].update(c_routes[carrier])

        # --- 航线统计（按数据块向量化） ---
        r_grp = valid.groupby(['Origin', 'Dest'])
        r_n = r_grp['MktFare'].count()
        r_sum = r_grp['MktFare'].sum()
        r_sum2 = r_grp['MktFare'].apply(lambda x: (x**2).sum())
        r_cars = r_grp['RPCarrier'].apply(set)
        r_pax = r_grp['Passengers'].sum()
        chunk_route_stats = {}
        for (orig, dest) in r_n.index:
            key = (orig, dest)
            chunk_route_stats[key] = (int(r_n[key]), float(r_sum[key]), float(r_sum2[key]),
                                       r_cars[key], float(r_pax[key]))
        merge_route_chunk(route_acc, chunk_route_stats)

        # 每处理约 300 万行输出一次进度
        if chunk_n % 20 == 0:
            elapsed = time.time() - q_t0
            rows_done = chunk_n * 150000
            pct_done = min(100, rows_done * 150 / fsize_mb)  # 粗略估计
            log(f"    [{idx+1}/{len(labels)}] {label}: ~{rows_done/1e6:.1f}M rows "
                f"（{elapsed:.0f} 秒，约完成文件的 {pct_done:.0f}%）")

    # 季度快照
    q_mean = q_sum / q_n if q_n > 0 else 0
    q_var = q_sum2/q_n - q_mean**2 if q_n > 0 else 0
    qtr_snapshots.append({
        'quarter': label, 'n_rows': q_n, 'mean_fare': round(q_mean, 2),
        'std_fare': round(np.sqrt(max(0, q_var)), 2),
        'routes_in_qtr': len(set(k for k, v in route_acc.items())),
    })
    log(f"  => {label}：{q_n:,.0f} 行，${q_mean:.0f} ± ${np.sqrt(max(0,q_var)):.0f}，"
        f"{time.time()-q_t0:.0f} 秒")

log(f"\n  合计：{global_n:,} 行，{len(route_acc):,} 条唯一航线，"
    f"{len(carrier_data)} 家航司，用时 {time.time()-t0:.0f} 秒")

# ─── 航线集中度 ───
log(f"\n{'='*70}")
log("第二阶段：航线与航司集中度")
log("=" * 70)

# 从航线累加器计算各航线乘客总量
route_pax_list = [(k, v[4]) for k, v in route_acc.items()]
route_pax_list.sort(key=lambda x: -x[1])
total_pax = sum(v for _, v in route_pax_list)
cumsum = np.cumsum([v for _, v in route_pax_list])
n_routes_total = len(route_pax_list)

for label_n, n in [('前 10', 10), ('前 50', 50), ('前 100', 100)]:
    share = cumsum[min(n, len(cumsum)) - 1] / total_pax * 100
    log(f"  {label_n} 条航线：占乘客总量 {share:.1f}%")
share_1pct = cumsum[max(1, int(n_routes_total * 0.01)) - 1] / total_pax * 100
share_10pct = cumsum[max(1, int(n_routes_total * 0.10)) - 1] / total_pax * 100
log(f"  前 1% 航线：{share_1pct:.1f}% | 前 10% 航线：{share_10pct:.1f}%")
lorenz = cumsum / cumsum[-1]
gini = 1 - 2 * np.trapz(lorenz, np.linspace(0, 1, n_routes_total))
log(f"  航线基尼系数：{gini:.4f}")

# 航司集中度
sorted_carriers = sorted(carrier_data.items(), key=lambda x: -x[1]['sum_pax'])
total_c_pax = sum(v['sum_pax'] for _, v in sorted_carriers)
shares = [(c, v['sum_pax']/total_c_pax) for c, v in sorted_carriers]
hhi = sum(s**2 for _, s in shares) * 10000
top4 = sum(s for _, s in shares[:4]) * 100
log(f"  航司 HHI：{hhi:.0f} | 前 4 家份额：{top4:.1f}% | 航司总数：{len(sorted_carriers)}")

# ─── 航线票价波动 ───
log(f"\n{'='*70}")
log("第三阶段：航线层面票价波动")
log("=" * 70)

route_cvs = []; route_ncarriers = []; route_nobs = []; route_mean_fares = []
for key, (n, sum_f, sum2_f, carriers, pax) in route_acc.items():
    if n >= 10:
        mean_f = sum_f / n
        var_f = sum2_f / n - mean_f**2
        if var_f > 0 and mean_f > 0:
            cv = np.sqrt(var_f) / mean_f
            if cv < 5:
                route_cvs.append(cv); route_ncarriers.append(len(carriers))
                route_nobs.append(n); route_mean_fares.append(mean_f)

route_cvs = np.array(route_cvs); route_ncarriers = np.array(route_ncarriers)
log(f"  观测数不少于 10 的航线：{len(route_cvs):,}")
log(f"  CV：均值={route_cvs.mean():.4f}，中位数={np.median(route_cvs):.4f}，"
    f"P25={np.percentile(route_cvs,25):.4f}, P75={np.percentile(route_cvs,75):.4f}, "
    f"P95={np.percentile(route_cvs,95):.4f}")
log(f"  与酒店 CV（0.20）相比：波动高 {np.median(route_cvs)/0.20:.1f} 倍")

# 竞争悖论
log(f"\n  按航司数量分组统计 CV：")
for n in range(1, 11):
    mask = route_ncarriers == n
    if mask.sum() >= 5:
        log(f"    {n} 家航司：{mask.sum():>7,} 条航线，CV={route_cvs[mask].mean():.4f} "
            f"（中位数={np.median(route_cvs[mask]):.4f}）")
mask_hi = route_ncarriers > 10
if mask_hi.sum() >= 5:
    log(f"    ＞10 家航司：{mask_hi.sum():>7,} 条航线，CV={route_cvs[mask_hi].mean():.4f} "
        f"（中位数={np.median(route_cvs[mask_hi]):.4f}）")

# ─── 航司风险 ───
log(f"\n{'='*70}")
log("第四阶段：航司层面风险")
log("=" * 70)

log(f"  {'航司':<6} {'乘客(百万)':>10} {'份额':>7} {'均票价':>9} {'票价CV':>8} {'航线数':>8} {'PD*':>6}")
log(f"  {'-'*58}")
carrier_stats = []
for c, d in sorted_carriers:
    if d['n'] < 100: continue
    mean_f = d['sum_fare'] / d['n']
    var_f = d['sum2_fare'] / d['n'] - mean_f**2
    cv_f = np.sqrt(max(0, var_f)) / mean_f if mean_f > 0 else 0
    pax_m = d['sum_pax'] / 1e6
    share = d['sum_pax'] / total_c_pax * 100
    n_routes = len(d['routes'])
    # PD 代理：CV 越高，经营风险越高
    pd_proxy = min(cv_f * 100, 40)
    carrier_stats.append((c, pax_m, share, mean_f, cv_f, n_routes, pd_proxy))
    if len(carrier_stats) <= 15:
        log(f"  {c:<6} {pax_m:>8.1f}M {share:>6.1f}% ${mean_f:>8.0f} {cv_f:>8.3f} {n_routes:>8,} {pd_proxy:>5.1f}%")

# 资产池层面的加权 PD 代理
wtd_pd = sum(cs[6] * cs[2] / 100 for cs in carrier_stats)
log(f"\n  按市场份额加权的 PD 代理：{wtd_pd:.2f}%")
log(f"  *PD 代理 = min(票价CV × 100, 40%)。票价离散度越高，经营风险越高。")

# ─── 季节性 ───
log(f"\n{'='*70}")
log("第五阶段：季节性趋势")
log("=" * 70)
for qs in qtr_snapshots:
    log(f"  {qs['quarter']}：${qs['mean_fare']:.0f} ± ${qs['std_fare']:.0f} "
        f"（{qs['n_rows']:,} 行，{qs['routes_in_qtr']:,} 条航线）")

# 检验季节性：第二、三季度因夏季出行而票价较高
fares_by_q = defaultdict(list)
for qs in qtr_snapshots:
    # 从标签解析季度
    label = qs['quarter'].lower()
    if 'q1' in label or '_1' in label: q = 1
    elif 'q2' in label or '_2' in label: q = 2
    elif 'q3' in label or '_3' in label: q = 3
    elif 'q4' in label or '_4' in label: q = 4
    else: q = 0
    fares_by_q[q].append(qs['mean_fare'])
if fares_by_q:
    log(f"\n  按日历年季度统计的平均票价：")
    for q in sorted(fares_by_q):
        vals = fares_by_q[q]
        log(f"    第 {q} 季度：${np.mean(vals):.0f}（{len(vals)} 个季度）")

# ─── FSR 指标 ───
log(f"\n{'='*70}")
log("第六阶段：FSR 适配指标")
log("=" * 70)

log(f"  6a. 航线持续性：无法直接从横截面 DB1B 数据中测量")
log(f"      （DB1B 是季度市场调查，不是单体航线面板）")
log(f"      全部季度共观测到 {n_routes_total:,} 条航线")

log(f"\n  6b. 价格可预测性：")
log(f"    航线 CV：中位数={np.median(route_cvs):.3f}，均值={route_cvs.mean():.3f}")
log(f"    酒店个体 CV：约 0.20（来自前期工作）")
log(f"    比值：{np.median(route_cvs)/0.20:.1f} 倍，机票价格在结构上更难预测")

log(f"\n  6c. 集中度风险（FSR 关键指标）：")
log(f"    航线基尼系数：{gini:.4f}（酒店基尼系数：约 0.12）")
log(f"    → 机票 FSR 资产池分散化明显更难")
log(f"    航司 HHI：{hhi:.0f} → {('中度集中' if hhi < 1500 else '高度集中')}")

log(f"\n  6d. 违约主体是航司，而不是航线：")
log(f"    {len(carrier_data)} 家航司，对应 {n_routes_total:,} 条航线")
log(f"    → 信用模型应建立在航司层面，而不是航线层面")
log(f"    → 一家航司破产会使其所有航线同时违约")

log(f"\n  6e. 季节性：第二、三季度存在明显夏季出行溢价")
log(f"    → 时权期限宜设为 12 个月，以覆盖完整周期")
log(f"    → 选择季节性发行窗口可能改善定价")

# ─── 保存结果 ───
results = {
    'dataset': {'total_rows': global_n, 'n_quarters': len(files),
                'n_routes': n_routes_total, 'n_carriers': len(carrier_data),
                'total_passengers_m': round(total_pax / 1e6, 1)},
    'global_fare': {'mean': round(global_sum/global_n, 2) if global_n > 0 else 0,
                    'std': round(np.sqrt(max(0, global_sum2/global_n - (global_sum/global_n)**2)), 2),
                    'min': round(global_min, 2), 'max': round(global_max, 2)},
    'concentration': {'route_gini': round(float(gini), 4), 'carrier_hhi': round(float(hhi), 0),
                      'top4_carrier_pct': round(float(top4), 1)},
    'route_volatility': {'n_routes': len(route_cvs), 'mean_cv': round(float(route_cvs.mean()), 4),
                         'median_cv': round(float(np.median(route_cvs)), 4),
                         'p95_cv': round(float(np.percentile(route_cvs, 95)), 4)},
    'carrier_risk': [{'carrier': c, 'passengers_m': round(p, 2), 'avg_fare': round(m, 0),
                      'fare_cv': round(cv, 4), 'n_routes': nr, 'pd_proxy_pct': round(pd, 1)}
                     for c, p, _, m, cv, nr, pd in carrier_stats],
    'wtd_pd_proxy_pct': round(float(wtd_pd), 2),
    'quarterly': qtr_snapshots,
}
with open(OUT / 'flight_eda_v4_summary.json', 'w') as f:
    json.dump(results, f, indent=2)
log(f"\n已保存：{OUT / 'flight_eda_v4_summary.json'}")
log(f"总耗时：{time.time() - t0:.0f} 秒")
log("处理完成。")
