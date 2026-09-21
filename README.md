> curl -LsSf https://astral.sh/uv/install.sh | sh
make 專案的根目錄 qoe
> mkdir qoe
> cd qoe
> uv init --python 3.13.5 
> uv add mavsdk
把以下的程式碼加入 src/qoe/__init__.py
把mission2.plan放在專案的根目錄 (有 pyproject.toml 的地方)
在專案的根目錄執行
> sudo nohup timeout 60 env PATH=$PATH uv run qoe mission2.plan > /home/pi/hct/qoe/mission.log 2>&1 &
指令拆解說明：
1. sudo：取得最高權限（讀取 UART 必備）。
2. nohup：讓程式忽略「掛斷 (HUP)」訊號，即使你的 SSH 視窗關閉，程式依然會繼續跑。
3. timeout 60：這是一個非常實用的 Linux 工具，它會啟動後面的指令，並在剛好 60 秒 時發送 SIGTERM 終止訊號，把後面的 Python 程式殺掉。
4. env PATH=$PATH uv run qoe mission2.plan：你原本的執行指令。
5. > /home/pi/hct/qoe/mission.log 2>&1：把原本會顯示在螢幕上的文字（包含正常的 print 與錯誤訊息）全部寫入 mission.log 檔案裡。你可以隨時輸入 cat mission.log 或是 tail -f mission.log 來查看進度。
6. &：將整個任務丟到背景執行，立刻還給你終端機的操控權。
