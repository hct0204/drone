import asyncio
from mavsdk import System

async def check_battery():
    drone = System()
    
    print("正在等待無人機連線...")
    await drone.connect(system_address="serial:///dev/ttyAMA0:57600")

    async for state in drone.core.connection_state():
        if state.is_connected:
            print("✅ 無人機連線成功！\n")
            break

    # 讀取電池遙測資料
    print("🔋 正在讀取電池狀態...")
    async for battery in drone.telemetry.battery():
        # remaining_percent 預設是 0.0 到 1.0 的浮點數，乘以 100 轉為百分比
        percent = battery.remaining_percent * 100
        voltage = battery.voltage_v
        
        print(f"目前電量: {percent:.0f}% | 電壓: {voltage:.2f}V")
        
        # 如果只想讀取一次就結束，可以取消下面這行的註解
        # break

if __name__ == "__main__":
    asyncio.run(check_battery())
