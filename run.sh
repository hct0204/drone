echo "準備執行任務: $1"
# 1. 將程式丟入背景執行並導向輸出
sudo nohup timeout 60 env PATH=$PATH uv run qoe "$1" > /home/pi/hct/qoe/mission.log 2>&1 &

# 2. 等待 1 秒確保 log 檔案已經建立
sleep 1 

# 3. 自動在前景開始監控日誌
tail -f /home/pi/hct/qoe/mission.log
