import pandas as pd, numpy as np

csv_path = r"C:\Users\weida\Desktop\酒店研究\data\flight_prices_real\db1b_2024q1\Origin_and_Destination_Survey_DB1BMarket_2024_1.csv"

# 分块读取全部 740 万行，并计算流式统计量
print("正在分块处理全部 740 万行数据……")

# 累加器
n = 0
sum_fare = 0.0; sum_fare2 = 0.0
sum_dist = 0.0; sum_dist2 = 0.0
sum_fpm = 0.0; sum_fpm2 = 0.0
min_fare = float('inf'); max_fare = 0
carrier_counts = {}
coupon_counts = {}
geo_counts = {}
route_stats = {}  # (origin,dest) -> [sum_fare, sum_fare2, n, carriers_set]

# 协方差计算
dist_fare_cov = 0.0

chunk_n = 0
for chunk in pd.read_csv(csv_path, chunksize=500000, low_memory=False):
    chunk_n += 1
    fares = chunk['MktFare'].values
    dists = chunk['MktMilesFlown'].values
    paxs = chunk['Passengers'].values
    carriers = chunk['RPCarrier'].values
    coupons = chunk['MktCoupons'].values
    geos = chunk['ItinGeoType'].values
    origins = chunk['Origin'].values
    dests = chunk['Dest'].values

    mask = ~np.isnan(fares) & ~np.isnan(dists) & (dists > 0)
    fares = fares[mask]; dists = dists[mask]; paxs = paxs[mask]

    m = len(fares)
    n += m
    sum_fare += fares.sum()
    sum_fare2 += (fares**2).sum()
    sum_dist += dists.sum()
    sum_dist2 += (dists**2).sum()

    fpm = fares / dists
    sum_fpm += fpm.sum()
    sum_fpm2 += (fpm**2).sum()

    min_fare = min(min_fare, fares.min())
    max_fare = max(max_fare, fares.max())

    # 航司计数
    for c in carriers[mask]:
        carrier_counts[c] = carrier_counts.get(c, 0) + 1

    # 航段数计数
    for c in coupons[mask]:
        coupon_counts[c] = coupon_counts.get(c, 0) + 1

    # 地理类型计数
    for g in geos[mask]:
        geo_counts[g] = geo_counts.get(g, 0) + 1

    # 航线统计（聚合）
    for i in range(m):
        key = (origins[i], dests[i])
        if key not in route_stats:
            route_stats[key] = {'sum_fare': 0.0, 'sum_fare2': 0.0, 'n': 0, 'carriers': set()}
        rs = route_stats[key]
        rs['sum_fare'] += fares[i]
        rs['sum_fare2'] += fares[i]**2
        rs['n'] += 1
        rs['carriers'].add(carriers[i])

    if chunk_n % 4 == 0:
        print(f"  已处理 {chunk_n*0.5:.0f} 百万行……")

print(f"\n合计有效行数：{n:,}")

# 计算最终统计量
mean_fare = sum_fare / n
var_fare = sum_fare2/n - mean_fare**2
std_fare = np.sqrt(var_fare)

mean_dist = sum_dist / n
var_dist = sum_dist2/n - mean_dist**2
std_dist = np.sqrt(var_dist)

mean_fpm = sum_fpm / n
var_fpm = sum_fpm2/n - mean_fpm**2
std_fpm = np.sqrt(var_fpm)

print(f"\n{'='*60}")
print(f"全数据集统计（{n:,} 行）")
print(f"{'='*60}")
print(f"票价：均值=${mean_fare:.2f}，标准差=${std_fare:.2f}，范围 ${min_fare:.2f}–${max_fare:.2f}")
print(f"  均值校验：均值=${mean_fare:.0f}（中位数需另行分块计算）")
print(f"距离：均值={mean_dist:.0f} 英里，标准差={std_dist:.0f} 英里")
print(f"单位距离票价：均值=${mean_fpm:.4f}，标准差=${std_fpm:.4f}")

# 航空公司
print(f"\n=== 全部航司（按运输量排序） ===")
total_rows = sum(carrier_counts.values())
for c, cnt in sorted(carrier_counts.items(), key=lambda x: -x[1]):
    pct = cnt/total_rows*100
    print(f"  {c:4s}: {cnt:>10,} ({pct:5.1f}%)")

# 航段数
print(f"\n=== 航段数 ===")
for c, cnt in sorted(coupon_counts.items()):
    print(f"  {c} segment(s): {cnt:>10,} ({cnt/n*100:.1f}%)")

# 地理类型
print(f"\n=== 地理类型 ===")
for g, cnt in sorted(geo_counts.items()):
    print(f"  Type {g}: {cnt:>10,} ({cnt/n*100:.1f}%)")

# 航线统计
print(f"\n=== 航线层面分析 ===")
total_routes = len(route_stats)
# 计算航线变异系数与竞争程度
route_cvs = []
route_competition = []
for key, rs in route_stats.items():
    if rs['n'] >= 5:
        mean_r = rs['sum_fare'] / rs['n']
        var_r = rs['sum_fare2']/rs['n'] - mean_r**2
        if var_r > 0 and mean_r > 0:
            cv = np.sqrt(var_r) / mean_r
            route_cvs.append(cv)
    if rs['n'] >= 1:
        route_competition.append(len(rs['carriers']))

print(f"起讫点对总数：{total_routes:,}")
print(f"观测数不少于 5 的航线：{len(route_cvs):,}")
if route_cvs:
    route_cvs = np.array(route_cvs)
    print(f"航线内变异系数分布：")
    print(f"  均值：{np.mean(route_cvs):.3f}，中位数：{np.median(route_cvs):.3f}")
    print(f"  P25: {np.percentile(route_cvs,25):.3f}, P75: {np.percentile(route_cvs,75):.3f}")
    print(f"  P10: {np.percentile(route_cvs,10):.3f}, P90: {np.percentile(route_cvs,90):.3f}")

if route_competition:
    rc = np.array(route_competition)
    for ncar in sorted(set(rc)):
        cnt = (rc == ncar).sum()
        print(f"  {ncar} 家航司：{cnt:,} 条航线（{cnt/len(rc)*100:.1f}%）")

# 竞争程度与票价离散度的关系
print(f"\n=== 竞争程度与票价离散度 ===")
comp_cv = {}
for key, rs in route_stats.items():
    ncar = len(rs['carriers'])
    if rs['n'] >= 5:
        mean_r = rs['sum_fare'] / rs['n']
        var_r = rs['sum_fare2']/rs['n'] - mean_r**2
        if var_r > 0 and mean_r > 0:
            cv = np.sqrt(var_r) / mean_r
            if ncar not in comp_cv:
                comp_cv[ncar] = []
            comp_cv[ncar].append(cv)

for ncar in sorted(comp_cv.keys()):
    cvs = np.array(comp_cv[ncar])
    print(f"  {ncar} 家航司：{len(cvs):,} 条航线，平均 CV={np.mean(cvs):.3f}，中位 CV={np.median(cvs):.3f}")
