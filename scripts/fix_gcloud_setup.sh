#!/bin/bash
# 修正 gcloud 設定腳本

echo "=========================================="
echo "修正 gcloud 設定"
echo "=========================================="

# 1. 將 gcloud 加入 PATH
echo ""
echo "1. 將 gcloud 加入 PATH..."
export PATH="/opt/homebrew/share/google-cloud-sdk/bin:$PATH"

# 2. 設定正確的 Python 路徑
echo "2. 設定 Python 路徑..."
export CLOUDSDK_PYTHON="/opt/homebrew/bin/python3"

# 3. 設定 gcloud 使用正確的 Python
echo "3. 設定 gcloud 使用正確的 Python..."
gcloud config set python /opt/homebrew/bin/python3 2>/dev/null || echo "   (如果失敗，稍後會自動處理)"

# 4. 驗證安裝
echo ""
echo "4. 驗證 gcloud 安裝..."
if gcloud --version > /dev/null 2>&1; then
    echo "✅ gcloud 可以正常使用！"
    gcloud --version
else
    echo "❌ gcloud 仍有問題，嘗試重新初始化..."
    gcloud init --skip-diagnostics
fi

# 5. 將設定加入 shell 設定檔
echo ""
echo "5. 將設定加入 ~/.zshrc..."
SHELL_CONFIG="$HOME/.zshrc"

if ! grep -q "google-cloud-sdk" "$SHELL_CONFIG" 2>/dev/null; then
    cat >> "$SHELL_CONFIG" << 'EOF'

# Google Cloud SDK
export PATH="/opt/homebrew/share/google-cloud-sdk/bin:$PATH"
export CLOUDSDK_PYTHON="/opt/homebrew/bin/python3"
EOF
    echo "✅ 已將設定加入 ~/.zshrc"
    echo "   請執行: source ~/.zshrc 或重新開啟終端機"
else
    echo "✅ 設定已存在於 ~/.zshrc"
fi

echo ""
echo "=========================================="
echo "✅ 設定完成！"
echo "=========================================="
echo ""
echo "現在您可以："
echo "1. 執行: source ~/.zshrc"
echo "2. 或重新開啟終端機"
echo "3. 然後執行: gcloud auth login"
echo ""

