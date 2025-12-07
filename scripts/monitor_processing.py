#!/usr/bin/env python3
"""
監控腳本處理進度，確保腳本持續運行直到完成
"""
import pandas as pd
import subprocess
import time
import sys
import os

def check_progress():
    """檢查處理進度"""
    try:
        df = pd.read_csv('DC_Crime_Incidents_2025_08_09_with_zipcode.csv')
        total = len(df)
        with_zip = df['ZIP_CODE'].notna().sum()
        pending = total - with_zip
        progress_pct = with_zip / total * 100
        return total, with_zip, pending, progress_pct
    except Exception as e:
        print(f"讀取檔案錯誤: {e}")
        return None, None, None, None

def is_script_running():
    """檢查腳本是否正在運行"""
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        return 'batch_process_zipcode.py' in result.stdout
    except:
        return False

def restart_script():
    """重新啟動處理腳本"""
    print("重新啟動處理腳本...")
    os.chdir('/Users/zhangxuanqi/Downloads/Adv_Spatial_HCI')
    subprocess.Popen(
        ['nohup', 'python3', 'batch_process_zipcode.py'],
        stdout=open('processing_output.log', 'a'),
        stderr=subprocess.STDOUT,
        cwd='/Users/zhangxuanqi/Downloads/Adv_Spatial_HCI'
    )
    time.sleep(5)

def main():
    print("開始監控處理進度...")
    print("=" * 60)
    
    while True:
        total, with_zip, pending, progress_pct = check_progress()
        
        if total is None:
            print("無法讀取進度，等待中...")
            time.sleep(10)
            continue
        
        # 檢查是否完成
        if pending == 0:
            print("=" * 60)
            print("✅ 所有記錄處理完成！")
            print(f"總記錄數: {total}")
            print(f"已處理: {with_zip} 筆 (100%)")
            print("=" * 60)
            break
        
        # 檢查腳本是否運行
        if not is_script_running():
            print(f"⚠️  腳本未運行，重新啟動中...")
            restart_script()
        
        # 顯示進度
        print(f"[{time.strftime('%H:%M:%S')}] 進度: {with_zip}/{total} ({progress_pct:.1f}%) - 剩餘: {pending} 筆")
        if pending > 0:
            estimated_time = pending * 0.05 / 60  # 預估剩餘時間（分鐘）
            print(f"    預估剩餘時間: {estimated_time:.1f} 分鐘")
        
        # 每 30 秒檢查一次
        time.sleep(30)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n監控已停止")
        sys.exit(0)

