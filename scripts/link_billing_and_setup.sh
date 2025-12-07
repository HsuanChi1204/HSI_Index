#!/bin/bash
# 連結計費帳戶並完成設定

set -e

export PATH="/opt/homebrew/share/google-cloud-sdk/bin:$PATH"
export CLOUDSDK_PYTHON="/opt/homebrew/bin/python3"

echo "=========================================="
echo "連結計費帳戶並完成設定"
echo "=========================================="

PROJECT_ID=$(gcloud config get-value project)
echo "當前專案: $PROJECT_ID"
echo ""

# 檢查計費狀態
echo "步驟 1: 檢查計費狀態"
echo "----------------------------------------"
BILLING_INFO=$(gcloud billing projects describe $PROJECT_ID 2>&1)

if echo "$BILLING_INFO" | grep -q "billingAccountName"; then
    echo "✅ 計費帳戶已連結"
    BILLING_ACCOUNT=$(echo "$BILLING_INFO" | grep "billingAccountName" | cut -d'/' -f2)
    echo "   計費帳戶 ID: $BILLING_ACCOUNT"
else
    echo "⚠️  計費帳戶未連結"
    echo ""
    echo "可用的計費帳戶："
    gcloud billing accounts list
    
    echo ""
    read -p "請輸入計費帳戶 ID（或按 Enter 前往 GCP Console 連結）: " BILLING_ACCOUNT_ID
    
    if [ -n "$BILLING_ACCOUNT_ID" ]; then
        echo "正在連結計費帳戶..."
        gcloud billing projects link $PROJECT_ID --billing-account=$BILLING_ACCOUNT_ID
        echo "✅ 計費帳戶已連結"
    else
        echo ""
        echo "請前往 GCP Console 連結計費帳戶："
        echo "https://console.cloud.google.com/billing?project=$PROJECT_ID"
        echo ""
        echo "連結完成後，按 Enter 繼續..."
        read
    fi
fi

# 建立 bucket
echo ""
echo "步驟 2: 建立 Storage Bucket"
echo "----------------------------------------"
BUCKET_NAME="dc-crime-data-$(whoami)-$(date +%s)"
echo "建立 bucket: gs://$BUCKET_NAME"

if gcloud storage buckets create gs://$BUCKET_NAME --location=us-east1; then
    echo "✅ Bucket 建立成功"
    echo $BUCKET_NAME > .bucket_name.txt
else
    echo "❌ Bucket 建立失敗"
    exit 1
fi

# 設定認證
echo ""
echo "步驟 3: 設定認證"
echo "----------------------------------------"
echo "請在瀏覽器中完成認證..."
gcloud auth application-default login
echo "✅ 認證完成"

# 安裝 Python 套件
echo ""
echo "步驟 4: 安裝 Python 套件"
echo "----------------------------------------"
cd /Users/zhangxuanqi/Downloads/Adv_Spatial_HCI
source venv/bin/activate
pip install -q google-cloud-storage
echo "✅ google-cloud-storage 已安裝"

# 設定 CORS
echo ""
echo "步驟 5: 設定 CORS"
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

gcloud storage buckets update gs://$BUCKET_NAME --cors-file=cors.json
echo "✅ CORS 設定完成"

# 上傳檔案
echo ""
echo "步驟 6: 上傳 JSON 檔案"
echo "----------------------------------------"
if [ ! -f "dc_crime_zillow_combined.json" ]; then
    echo "❌ 找不到 JSON 檔案"
    exit 1
fi

echo "正在上傳..."
gcloud storage cp dc_crime_zillow_combined.json gs://$BUCKET_NAME/data/
echo "✅ 檔案上傳成功"

echo "設定檔案為公開讀取..."
gcloud storage objects update gs://$BUCKET_NAME/data/dc_crime_zillow_combined.json --acl-public
echo "✅ 檔案已設定為公開讀取"

# 驗證
echo ""
echo "步驟 7: 驗證上傳"
echo "----------------------------------------"
PUBLIC_URL="https://storage.googleapis.com/$BUCKET_NAME/data/dc_crime_zillow_combined.json"
echo "公開 URL: $PUBLIC_URL"
echo ""

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" $PUBLIC_URL)
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ 檔案可以正常存取 (HTTP $HTTP_CODE)"
else
    echo "⚠️  檔案存取可能有問題 (HTTP $HTTP_CODE)"
fi

# 儲存資訊
echo $PUBLIC_URL > .public_url.txt

echo ""
echo "=========================================="
echo "✅ 所有步驟完成！"
echo "=========================================="
echo ""
echo "📦 Bucket: gs://$BUCKET_NAME"
echo "🌐 公開 URL: $PUBLIC_URL"
echo ""
echo "前端使用方式："
echo "fetch('$PUBLIC_URL')"
echo "  .then(res => res.json())"
echo "  .then(data => console.log(data));"
echo ""

