import asyncio
from mavsdk import System

async def run():
    drone = System()
    
    print("正在等待無人機連線...")
    await drone.connect(system_address="serial:///dev/ttyAMA0:57600")

    async for state in drone.core.connection_state():
        if state.is_connected:
            print("✅ 無人機連線成功！")
            break

    # 等待一下確保參數同步
    await asyncio.sleep(2)

    # 讀取 RTL_ALT_M 參數 (浮點數)
    try:
        print("正在讀取 RTL 返航高度參數...")
        rtl_alt_m = await drone.param.get_param_float("RTL_ALT_M")
        
        print(f"📍 目前的 RTL 返航高度設定為: {rtl_alt_m} 公尺")
    except Exception as e:
        print(f"❌ 讀取參數失敗: {e}")

if __name__ == "__main__":
    asyncio.run(run())
