#!/bin/bash
# 檢查處理進度的腳本

cd /Users/zhangxuanqi/Downloads/Adv_Spatial_HCI
source venv/bin/activate

python3 << 'EOF'
import pandas as pd
import json
import subprocess
from datetime import datetime

# 檢查進度
df = pd.read_csv('DC_Crime_Incidents_2025_08_09_with_zipcode.csv')
total = len(df)
with_zip = df['ZIP_CODE'].notna().sum()
pending = total - with_zip
progress_pct = with_zip / total * 100

print('=' * 60)
print(f'📊 處理進度報告 ({datetime.now().strftime("%Y-%m-%d %H:%M:%S")})')
print('=' * 60)
print(f'總記錄數: {total}')
print(f'已處理: {with_zip} 筆 ({progress_pct:.1f}%)')
print(f'剩餘: {pending} 筆')
if pending > 0:
    estimated_minutes = pending * 0.05 / 60
    print(f'預估剩餘時間: {estimated_minutes:.1f} 分鐘')
print('=' * 60)

# 檢查進度檔案
try:
    with open('processing_progress.json', 'r') as f:
        progress = json.load(f)
    print(f'累計成功: {progress.get("total_success", 0)}')
    print(f'累計失敗: {progress.get("total_failed", 0)}')
    if progress.get("last_updated"):
        print(f'最後更新: {progress["last_updated"]}')
except:
    pass

# 檢查進程
result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
if 'batch_process_zipcode.py' in result.stdout:
    print('✅ 腳本正在運行中')
else:
    print('⚠️  腳本未運行')

if pending == 0:
    print('\n🎉 所有記錄處理完成！')
EOF

