import asyncio
import math
from mavsdk import System

# 暫存最新的遙測數據，新增 fix_type 欄位
telemetry_data = {
    "fix_type": "未連線", # GPS 定位狀態
    "satellites": 0,    # 鎖定的 GPS 衛星數量
    "lat": 0.0,
    "lon": 0.0,
    "alt_rel": 0.0, 
    "alt_abs": 0.0, 
    "speed": 0.0    
}

# 任務 1：持續監聽位置資料
async def update_position(drone):
    async for pos in drone.telemetry.position():
        telemetry_data["lat"] = pos.latitude_deg
        telemetry_data["lon"] = pos.longitude_deg
        telemetry_data["alt_rel"] = pos.relative_altitude_m
        telemetry_data["alt_abs"] = pos.absolute_altitude_m

# 任務 2：持續監聽速度資料
async def update_velocity(drone):
    async for vel in drone.telemetry.velocity_ned():
        ground_speed = math.sqrt(vel.north_m_s**2 + vel.east_m_s**2)
        telemetry_data["speed"] = ground_speed

# 任務 3：持續監聽 GPS 狀態 (包含衛星數量與定位類型)
async def update_gps_info(drone):
    async for gps_info in drone.telemetry.gps_info():
        telemetry_data["satellites"] = gps_info.num_satellites
        # gps_info.fix_type 是一個 Enum (例如 FixType.FIX_3D)，將其轉換為乾淨的字串
        telemetry_data["fix_type"] = str(gps_info.fix_type).replace("FixType.", "")

async def run():
    drone = System()
    
    print("正在等待無人機連線...")
    await drone.connect(system_address="serial:///dev/ttyAMA0:57600")

    async for state in drone.core.connection_state():
        if state.is_connected:
            print("✅ 無人機連線成功！\n")
            break

    # 在背景同時啟動 3 個監聽任務
    asyncio.create_task(update_position(drone))
    asyncio.create_task(update_velocity(drone))
    asyncio.create_task(update_gps_info(drone))

    print("🛰️  開始即時監控 GPS 與飛行資料 (按 Ctrl+C 結束)")
    print("-" * 100)
    
    try:
        # 主迴圈：每 0.5 秒更新一次畫面
        while True:
            await asyncio.sleep(0.5)
            # 將定位狀態 (fix_type) 加入到字串最前方顯示，使用 <20 確保對齊
            print(f"定位: {telemetry_data['fix_type']:<8} | "
                  f"衛星: {telemetry_data['satellites']:2d} 顆 | "
                  f"緯度: {telemetry_data['lat']:.6f}° | "
                  f"經度: {telemetry_data['lon']:.6f}° | "
                  f"高度: {telemetry_data['alt_rel']:.1f}m | "
                  f"速度: {telemetry_data['speed']:.2f} m/s   ", end="\r")
    except asyncio.CancelledError:
        pass

if __name__ == "__main__":
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("\n\n⏹️ 監控已安全結束。")
