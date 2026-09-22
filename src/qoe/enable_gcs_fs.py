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

    try:
        print("正在 turn on GCS Failsafe (地面站斷線保護)...")
        # 設定 FS_GCS_ENABLE 為 1 
        await drone.param.set_param_int("FS_GCS_ENABLE", 1)
        
        # 再次讀取確認
        check_val = await drone.param.get_param_int("FS_GCS_ENABLE")
        if check_val == 1:
            print("🎉 成功！地面站失控保護已 turn on。")
        else:
            print("⚠️ 設定可能未生效，請重試。")
            
    except Exception as e:
        print(f"❌ 參數設定失敗: {e}")

if __name__ == "__main__":
    asyncio.run(run())
