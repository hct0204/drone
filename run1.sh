echo "準備執行任務: $1"
# 1. 將程式丟入背景執行並導向輸出
sudo env PATH=$PATH uv run qoe "$1" 

