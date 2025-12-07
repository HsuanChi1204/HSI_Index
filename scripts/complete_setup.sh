#!/bin/bash
# 完成 GCP Storage 設定的剩餘步驟

set -e  # 遇到錯誤立即停止

export PATH="/opt/homebrew/share/google-cloud-sdk/bin:$PATH"
export CLOUDSDK_PYTHON="/opt/homebrew/bin/python3"

echo "=========================================="
echo "完成 GCP Storage 設定"
echo "=========================================="

# 取得 bucket 名稱
echo ""
echo "步驟 1: 確認 bucket 資訊"
echo "----------------------------------------"
BUCKETS=$(gcloud storage buckets list --format="value(name)")
if [ -z "$BUCKETS" ]; then
    echo "❌ 找不到 bucket，請先建立 bucket"
    echo ""
    echo "建立 bucket 命令："
    echo "  BUCKET_NAME=\"dc-crime-data-\$(date +%s)\""
    echo "  gcloud storage buckets create gs://\$BUCKET_NAME --location=us-east1"
    exit 1
fi

# 使用第一個 bucket（如果有多個）
BUCKET_NAME=$(echo "$BUCKETS" | head -1 | sed 's|gs://||')
echo "✅ 找到 bucket: gs://$BUCKET_NAME"

# 步驟 6: 設定認證
echo ""
echo "步驟 6: 設定認證"
echo "----------------------------------------"
echo "正在設定應用程式預設憑證..."
if gcloud auth application-default print-access-token > /dev/null 2>&1; then
    echo "✅ 認證已設定"
else
    echo "需要登入，請在瀏覽器中完成認證..."
    gcloud auth application-default login
    echo "✅ 認證完成"
fi

# 步驟 7: 安裝 Python 套件
echo ""
echo "步驟 7: 安裝 Python 套件"
echo "----------------------------------------"
cd /Users/zhangxuanqi/Downloads/Adv_Spatial_HCI
source venv/bin/activate

if pip show google-cloud-storage > /dev/null 2>&1; then
    echo "✅ google-cloud-storage 已安裝"
else
    echo "正在安裝 google-cloud-storage..."
    pip install google-cloud-storage
    echo "✅ 安裝完成"
fi

# 步驟 8: 設定 CORS
echo ""
echo "步驟 8: 設定 CORS"
echo "----------------------------------------"
cat > cors.json << 'EOF'
[
  {
    "origin": ["*"],
    "method": ["GET", "HEAD"],
    "responseHeader": ["Content-Type", "Access-Control-Allow-Origin"],
    "maxAgeSeconds": 3600
  }
]
EOF

echo "正在設定 CORS..."
gcloud storage buckets update gs://$BUCKET_NAME --cors-file=cors.json
echo "✅ CORS 設定完成"

# 步驟 9: 上傳 JSON 檔案
echo ""
echo "步驟 9: 上傳 JSON 檔案"
echo "----------------------------------------"
if [ ! -f "dc_crime_zillow_combined.json" ]; then
    echo "❌ 找不到 dc_crime_zillow_combined.json"
    echo "請先執行: python combine_data_to_json.py"
    exit 1
fi

echo "正在上傳檔案..."
gcloud storage cp dc_crime_zillow_combined.json gs://$BUCKET_NAME/data/
echo "✅ 檔案上傳成功"

# 設定檔案為公開讀取
echo "正在設定檔案為公開讀取..."
gcloud storage objects update gs://$BUCKET_NAME/data/dc_crime_zillow_combined.json --acl-public
echo "✅ 檔案已設定為公開讀取"

# 步驟 10: 驗證上傳
echo ""
echo "步驟 10: 驗證上傳"
echo "----------------------------------------"
PUBLIC_URL="https://storage.googleapis.com/$BUCKET_NAME/data/dc_crime_zillow_combined.json"
echo "公開 URL: $PUBLIC_URL"
echo ""

# 測試是否可以存取
echo "測試檔案存取..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" $PUBLIC_URL)
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ 檔案可以正常存取 (HTTP $HTTP_CODE)"
else
    echo "⚠️  檔案存取可能有問題 (HTTP $HTTP_CODE)"
fi

# 顯示結果
echo ""
echo "=========================================="
echo "✅ 設定完成！"
echo "=========================================="
echo ""
echo "📦 Bucket: gs://$BUCKET_NAME"
echo "🌐 公開 URL: $PUBLIC_URL"
echo ""
echo "前端可以使用以下程式碼讀取："
echo ""
echo "fetch('$PUBLIC_URL')"
echo "  .then(res => res.json())"
echo "  .then(data => console.log(data));"
echo ""
echo "=========================================="

