
put my_mission.plan in the current folder

# 使用 sudo 確保有權限讀取 ttyAMA0 通訊埠，並執行程式
sudo nohup timeout 60 env PATH=$PATH uv run qoe mission2.plan > /home/pi/hct/qoe/mission.log 2>&1 &
