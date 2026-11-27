"""
提取真实航线统计量，用于构建机票 FSR 资产池。
读取一个代表性季度（2024 年第二季度），计算每条航线的统计量，
并输出可用于分层抽样的 CSV 文件。
"""
import pandas as pd, numpy as np, json, time, sys
from collections import defaultdict
from pathlib import Path

BASE = Path(r"C:\Users\weida\Desktop\酒店研究\data\flight_prices_real")
OUT = Path(r"C:\Users\weida\Desktop\酒店研究\output")

def log(msg):
    print(msg, flush=True)

log("正在提取用于 FSR 资产池构建的真实航线统计量……")
log("采用 2024 年第二季度作为代表性季度\n")

# 查找 2024 年第二季度文件
import glob
files = sorted(glob.glob(str(BASE / 'Origin_and_Destination_Survey_DB1BMarket_2024_2/Origin_and_Destination_Survey_DB1BMarket_2024_2.csv')))
if not files:
    log("错误：未找到 2024 年第二季度文件")
    sys.exit(1)

fpath = files[0]
log(f"数据源：{fpath}")

# 流式航线聚合
route_data = defaultdict(lambda: {'n': 0, 'sum_fare': 0.0, 'sum2_fare': 0.0,
                                    'sum_pax': 0.0, 'carriers': set(),
                                    'sum_dist': 0.0, 'sum_coupons': 0.0})

chunk_n = 0; t0 = time.time()
for chunk in pd.read_csv(fpath, chunksize=200000, low_memory=False,
                         usecols=['Origin', 'Dest', 'RPCarrier', 'MktFare',
                                  'Passengers', 'MktMilesFlown', 'MktCoupons']):
    chunk_n += 1
    valid = chunk[chunk['MktFare'].notna() & (chunk['MktMilesFlown'] > 0)]
    for _, row in valid.iterrows():
        key = (row['Origin'], row['Dest'])
        d = route_data[key]
        d['n'] += 1
        f = row['MktFare']
        d['sum_fare'] += f
        d['sum2_fare'] += f**2
        d['sum_pax'] += row['Passengers']
        d['carriers'].add(row['RPCarrier'])
        d['sum_dist'] += row['MktMilesFlown']
        d['sum_coupons'] += row['MktCoupons']
    if chunk_n % 10 == 0:
        log(f"  已处理 {chunk_n*200000/1e6:.1f} 百万行，{len(route_data):,} 条航线……")

log(f"\n  共提取 {len(route_data):,} 条航线（{time.time()-t0:.0f} 秒）")

# 汇总为 DataFrame
routes = []
for (origin, dest), d in route_data.items():
    if d['n'] < 20:  # 最小观测数
        continue
    mean_fare = d['sum_fare'] / d['n']
    var_fare = max(0, d['sum2_fare'] / d['n'] - mean_fare**2)
    cv = np.sqrt(var_fare) / mean_fare if mean_fare > 0 else 0
    n_carriers = len(d['carriers'])
    avg_dist = d['sum_dist'] / d['n']
    avg_coupons = d['sum_coupons'] / d['n']

    # 距离档
    if avg_dist <= 500:
        dist_band = 'short'
    elif avg_dist <= 1500:
        dist_band = 'medium'
    else:
        dist_band = 'long'

    routes.append({
        'origin': origin, 'dest': dest,
        'route': f'{origin}-{dest}',
        'n_obs': d['n'],
        'total_pax': d['sum_pax'],
        'mean_fare': round(mean_fare, 2),
        'std_fare': round(np.sqrt(max(0, var_fare)), 2),
        'fare_cv': round(cv, 4),
        'n_carriers': n_carriers,
        'avg_distance': round(avg_dist, 0),
        'avg_coupons': round(avg_coupons, 2),
        'dist_band': dist_band,
        'carriers_list': ','.join(sorted(d['carriers'])),
    })

df = pd.DataFrame(routes)
# 过滤极端变异系数
df = df[df['fare_cv'] < 1.5]
# 过滤异常低票价（疑似数据错误）
df = df[df['mean_fare'] >= 50]

# 保存
csv_path = OUT / 'flight_routes_real.csv'
df.to_csv(csv_path, index=False)

log(f"\n已将 {len(df):,} 条航线保存到 {csv_path}")
log(f"\n航线统计：")
log(f"  平均票价：${df['mean_fare'].mean():.0f}（中位数：${df['mean_fare'].median():.0f}）")
log(f"  票价 CV：均值={df['fare_cv'].mean():.3f}，中位数={df['fare_cv'].median():.3f}")
log(f"  航司数量：均值={df['n_carriers'].mean():.1f}")
log(f"  距离档：短程={(df['dist_band']=='short').sum():,}，"
    f"中程={(df['dist_band']=='medium').sum():,}，远程={(df['dist_band']=='long').sum():,}")
log(f"  乘客量前 5 条航线：")
for _, r in df.nlargest(5, 'total_pax').iterrows():
    log(f"    {r['route']}：{r['total_pax']:,.0f} 名乘客，${r['mean_fare']:.0f}，CV={r['fare_cv']:.3f}，{r['n_carriers']} 家航司")
log("处理完成。")
