import asyncio
import argparse
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

        # 2. 檢查並啟用圍欄總開關 (Int)
        fence_enable = await drone.param.get_param_int("FENCE_ENABLE")
        if fence_enable == 0:
            print("⚠️ 偵測到地理圍欄尚未啟用 ...")
            print("✅ turn on ！")
            await drone.param.set_param_int("FENCE_ENABLE", 1)
        else:
            print("✅ 圍欄總開關已啟用！")
            #print("✅ turn off ！")
            #await drone.param.set_param_int("FENCE_ENABLE", 0)
        fence_enable = await drone.param.get_param_int("FENCE_ENABLE")
        if fence_enable == 0:
            print("⚠️ 偵測到地理圍欄尚未啟用 ...")
        else:
            print("✅ 圍欄總開關已啟用！")

        final_alt = await drone.param.get_param_float("FENCE_ALT_MAX")
        print(f"\n🎉 設定完成！目前絕對高度限制為: {final_alt} 公尺")

    except Exception as e:
        print(f"❌ 參數設定失敗: {e}")

if __name__ == "__main__":
    
    asyncio.run(run())
