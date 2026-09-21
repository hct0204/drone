# 編輯: src/qoe/__init__.py
import asyncio
import argparse
import sys
import os
from mavsdk import System

async def run(plan_file):
    # 檢查檔案是否存在
    if not os.path.exists(plan_file):
        print(f"❌ 錯誤：找不到指定的任務檔案 '{plan_file}'")
        sys.exit(1)

    drone = System()
    
    print("正在等待無人機連線...")
    await drone.connect(system_address="serial:///dev/ttyAMA0:57600")

    async for state in drone.core.connection_state():
        if state.is_connected:
            print("✅ 無人機連線成功！")
            break

    # 1. 讀取並解析從參數傳入的任務檔案
    print(f"正在讀取任務檔案: {plan_file} ...")
    
    try:
        mission_import_data = await drone.mission_raw.import_qgroundcontrol_mission(plan_file)
        mission_items = mission_import_data.mission_items
        print(f"✅ 成功解析 {len(mission_items)} 個航點/指令。")

        # ======== 動態提取起飛高度 ========
        target_takeoff_alt = 2.0 # 給定一個預設安全值
        for item in mission_items:
            if item.command == 22: # 找到 MAV_CMD_NAV_TAKEOFF
                target_takeoff_alt = item.z
                break
            elif item.command == 16: # 如果沒起飛點，找第一個一般航點 MAV_CMD_NAV_WAYPOINT
                target_takeoff_alt = item.z
                break
                
        print(f"🔍 根據任務設定，將自動起飛高度設為: {target_takeoff_alt} 公尺")
        # ==================================

        print("正在上傳任務至無人機...")
        await drone.mission_raw.upload_mission(mission_items)
        print("✅ 任務上傳完成！")
    except Exception as e:
        print(f"❌ 任務處理失敗: {e}")
        return

    # 2. 等待 GPS 鎖定
    print("正在等待 GPS 3D 鎖定與感測器初始化...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            print("✅ GPS 定位完成，達到起飛標準！")
            break

    # 3. 安全倒數
    print("\n⚠️ 警告：無人機即將自動起飛！")
    for i in range(10, 0, -1):
        print(f"倒數 {i} 秒...")
        await asyncio.sleep(1)

    # 4. 解鎖無人機
    print("解鎖無人機 (Arming)...")
    try:
        await drone.action.arm()
    except Exception as e:
        print(f"❌ 解鎖失敗: {e}")
        return

    # 5. 使用提取到的高度執行強制起飛，隨後切換任務模式
    print(f"🚀 執行 Python 強制起飛 (目標高度: {target_takeoff_alt}m)...")
    try:
        await drone.action.set_takeoff_altitude(target_takeoff_alt)
        await drone.action.takeoff()
        
        # 依高度預留爬升時間 (每公尺約給予 3 秒寬限)
        sleep_time = max(5, int(target_takeoff_alt * 3))
        print(f"等待無人機升空 ({sleep_time} 秒)...")
        await asyncio.sleep(sleep_time) 

        print("👉 切換為自動任務模式以執行後續航點 (Start Mission)！")
        await drone.mission_raw.start_mission()
    except Exception as e:
        print(f"❌ 起飛或任務切換失敗: {e}")

    await asyncio.sleep(1)
    async for mode in drone.telemetry.flight_mode():
        print(f"✅ 目前飛控模式: {mode}")
        break

    # 6. 持續監控
    print("持續監控無人機狀態 (按 Ctrl+C 中止監控)...")
    async for position in drone.telemetry.position():
        print(f"目前相對高度: {position.relative_altitude_m:.2f} 公尺", end="\r")


def main():
    # 使用 argparse 處理命令列參數
    parser = argparse.ArgumentParser(description="上傳並執行 QGC 任務檔案")
    parser.add_argument(
        "plan_file", 
        help="QGC 任務檔案 (.plan) 的路徑"
    )
    args = parser.parse_args()

    # 將參數傳遞給非同步主函數
    asyncio.run(run(args.plan_file))

