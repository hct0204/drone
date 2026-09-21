import asyncio
import argparse
from mavsdk import System

async def run(alt_max):
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
        # 1. 設定最高高度限制 (Float)
        print(f"正在將高度圍欄限制設定為: {alt_max} 公尺...")
        await drone.param.set_param_float("FENCE_ALT_MAX", float(alt_max))
        print("✅ FENCE_ALT_MAX 設定成功！")

        # 2. 檢查並啟用圍欄總開關 (Int)
        fence_enable = await drone.param.get_param_int("FENCE_ENABLE")
        if fence_enable == 0:
            print("⚠️ 偵測到地理圍欄尚未啟用，正在自動啟用 (FENCE_ENABLE = 1)...")
            await drone.param.set_param_int("FENCE_ENABLE", 1)
            print("✅ 圍欄總開關已啟用！")

        # 3. 檢查並疊加高度限制條件 (Int)
        fence_type = await drone.param.get_param_int("FENCE_TYPE")
        # 檢查二進位的第一位 (高度限制) 是否為 1
        if (fence_type & 1) == 0:
            new_type = fence_type | 1  # 透過 OR 運算加上高度限制，保留原有多邊形設定
            print(f"⚠️ 高度圍欄尚未包含在觸發條件中 (目前 FENCE_TYPE: {fence_type})")
            print(f"正在加入高度圍欄條件 (FENCE_TYPE 變更為: {new_type})...")
            await drone.param.set_param_int("FENCE_TYPE", new_type)
            print("✅ 高度圍欄條件已加入！")

        # 確認最終設定結果
        final_alt = await drone.param.get_param_float("FENCE_ALT_MAX")
        print(f"\n🎉 設定完成！目前絕對高度限制為: {final_alt} 公尺")

    except Exception as e:
        print(f"❌ 參數設定失敗: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="設定無人機高度圍欄")
    parser.add_argument("altitude", type=float, help="最高飛行高度限制 (公尺)")
    args = parser.parse_args()
    
    asyncio.run(run(args.altitude))

