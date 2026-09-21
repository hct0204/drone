import asyncio
import math
from mavsdk import System

# 建立一個字典來暫存最新的遙測數據
telemetry_data = {
    "lat": 0.0,
    "lon": 0.0,
    "alt_rel": 0.0, # 相對起飛點高度
    "alt_abs": 0.0, # 海拔高度 (AMSL)
    "speed": 0.0    # 水平地速
}

# 任務 1：持續監聽位置資料 (經度、緯度、高度)
async def update_position(drone):
    async for pos in drone.telemetry.position():
        telemetry_data["lat"] = pos.latitude_deg
        telemetry_data["lon"] = pos.longitude_deg
        telemetry_data["alt_rel"] = pos.relative_altitude_m
        telemetry_data["alt_abs"] = pos.absolute_altitude_m

# 任務 2：持續監聽速度資料 (北向、東向、下向速度)
async def update_velocity(drone):
    async for vel in drone.telemetry.velocity_ned():
        # 透過北向 (North) 與東向 (East) 的向量，計算出實際的水平地速 (Ground Speed)
        ground_speed = math.sqrt(vel.north_m_s**2 + vel.east_m_s**2)
        telemetry_data["speed"] = ground_speed

async def run():
    drone = System()
    
    print("正在等待無人機連線...")
    await drone.connect(system_address="serial:///dev/ttyAMA0:57600")

    async for state in drone.core.connection_state():
        if state.is_connected:
            print("✅ 無人機連線成功！\n")
            break

    # 使用 asyncio.create_task 在背景啟動監聽任務
    asyncio.create_task(update_position(drone))
    asyncio.create_task(update_velocity(drone))

    print("🛰️  開始即時監控 GPS 與飛行資料 (按 Ctrl+C 結束)")
    print("-" * 75)
    
    try:
        # 主迴圈：每 0.5 秒將最新資料印在同一行
        while True:
            await asyncio.sleep(0.5)
            # 使用 \r 讓游標回到行首，覆蓋舊的輸出達成動態更新效果
            print(f"緯度: {telemetry_data['lat']:.6f}° | "
                  f"經度: {telemetry_data['lon']:.6f}° | "
                  f"高度: {telemetry_data['alt_rel']:.1f}m | "
                  f"速度: {telemetry_data['speed']:.2f} m/s", end="\r")
    except asyncio.CancelledError:
        pass

if __name__ == "__main__":
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        # 攔截 Ctrl+C 讓程式優雅退出，不會印出一大堆錯誤追蹤
        print("\n\n⏹️ 監控已安全結束。")
