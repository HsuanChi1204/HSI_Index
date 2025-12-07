#!/bin/bash
# GCP Cloud Storage 快速設定腳本

set -e  # 遇到錯誤立即停止

echo "=========================================="
echo "GCP Cloud Storage 快速設定"
echo "=========================================="

# 顏色定義
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 檢查 gcloud 是否安裝
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ gcloud CLI 未安裝${NC}"
    echo "請前往 https://cloud.google.com/sdk/docs/install 安裝"
    exit 1
fi

echo -e "${GREEN}✅ gcloud CLI 已安裝${NC}"

# 檢查是否已登入
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo -e "${YELLOW}⚠️  尚未登入，正在登入...${NC}"
    gcloud auth login
fi

echo -e "${GREEN}✅ 已登入 GCP${NC}"

# 取得或建立專案
read -p "請輸入 GCP 專案 ID（或按 Enter 使用現有專案）: " PROJECT_ID

if [ -z "$PROJECT_ID" ]; then
    PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
    if [ -z "$PROJECT_ID" ]; then
        echo -e "${RED}❌ 沒有設定專案，請先建立或選擇專案${NC}"
        exit 1
    fi
    echo -e "${GREEN}使用現有專案: $PROJECT_ID${NC}"
else
    gcloud config set project $PROJECT_ID
    echo -e "${GREEN}✅ 已設定專案: $PROJECT_ID${NC}"
fi

# 啟用 Cloud Storage API
echo -e "\n${YELLOW}正在啟用 Cloud Storage API...${NC}"
gcloud services enable storage-component.googleapis.com --project=$PROJECT_ID
echo -e "${GREEN}✅ Cloud Storage API 已啟用${NC}"

# 建立 bucket
read -p "請輸入 bucket 名稱（必須全球唯一，建議使用: dc-crime-data-您的名字）: " BUCKET_NAME

if [ -z "$BUCKET_NAME" ]; then
    BUCKET_NAME="dc-crime-data-$(date +%s)"
    echo -e "${YELLOW}使用自動生成名稱: $BUCKET_NAME${NC}"
fi

# 選擇區域
echo -e "\n可用的區域:"
echo "1. us-central1 (Iowa)"
echo "2. us-east1 (South Carolina)"
echo "3. us-west1 (Oregon)"
echo "4. asia-east1 (Taiwan)"
read -p "請選擇區域 (1-4，預設 1): " REGION_CHOICE

case $REGION_CHOICE in
    2) REGION="us-east1" ;;
    3) REGION="us-west1" ;;
    4) REGION="asia-east1" ;;
    *) REGION="us-central1" ;;
esac

echo -e "\n${YELLOW}正在建立 bucket: gs://$BUCKET_NAME${NC}"
if gcloud storage buckets create gs://$BUCKET_NAME --location=$REGION --project=$PROJECT_ID 2>/dev/null; then
    echo -e "${GREEN}✅ Bucket 建立成功${NC}"
else
    echo -e "${YELLOW}⚠️  Bucket 可能已存在，繼續...${NC}"
fi

# 設定認證
echo -e "\n${YELLOW}設定應用程式預設憑證...${NC}"
gcloud auth application-default login
echo -e "${GREEN}✅ 認證設定完成${NC}"

# 建立 CORS 設定
echo -e "\n${YELLOW}設定 CORS...${NC}"
cat > cors.json << EOF
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
echo -e "${GREEN}✅ CORS 設定完成${NC}"

# 檢查 JSON 檔案是否存在
if [ ! -f "dc_crime_zillow_combined.json" ]; then
    echo -e "${RED}❌ 找不到 dc_crime_zillow_combined.json${NC}"
    echo "請先執行: python combine_data_to_json.py"
    exit 1
fi

# 上傳檔案
echo -e "\n${YELLOW}正在上傳 JSON 檔案...${NC}"
gcloud storage cp dc_crime_zillow_combined.json gs://$BUCKET_NAME/data/
echo -e "${GREEN}✅ 檔案上傳成功${NC}"

# 設定公開讀取
echo -e "\n${YELLOW}設定檔案為公開讀取...${NC}"
gcloud storage objects update gs://$BUCKET_NAME/data/dc_crime_zillow_combined.json --acl-public
echo -e "${GREEN}✅ 檔案已設定為公開讀取${NC}"

# 顯示結果
PUBLIC_URL="https://storage.googleapis.com/$BUCKET_NAME/data/dc_crime_zillow_combined.json"

echo -e "\n${GREEN}=========================================="
echo "✅ 設定完成！"
echo "==========================================${NC}"
echo ""
echo "📦 Bucket: gs://$BUCKET_NAME"
echo "🌐 公開 URL: $PUBLIC_URL"
echo ""
echo "前端可以使用以下程式碼讀取:"
echo ""
echo "fetch('$PUBLIC_URL')"
echo "  .then(res => res.json())"
echo "  .then(data => console.log(data));"
echo ""
echo -e "${YELLOW}⚠️  請將 URL 儲存下來，前端會需要用到${NC}"

