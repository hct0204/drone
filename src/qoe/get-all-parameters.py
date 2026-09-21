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

    # 給予飛控幾秒鐘的時間，將參數表同步到樹莓派
    print("等待參數同步 (3秒)...")
    await asyncio.sleep(3)

    try:
        print("正在取得完整參數表，並搜尋 'RTL' 相關設定...\n")
        all_params = await drone.param.get_all_params()
        
        print("=== 📌 整數型參數 (INT) ===")
        found_int = False
        for p in all_params.int_params:
            if "RTL" in p.name:
                print(f"名稱: {p.name} | 數值: {p.value}")
                found_int = True
        if not found_int: print("無相關參數")

        print("\n=== 📌 浮點數型參數 (FLOAT) ===")
        found_float = False
        for p in all_params.float_params:
            if "RTL" in p.name:
                print(f"名稱: {p.name} | 數值: {p.value}")
                found_float = True
        if not found_float: print("無相關參數")

    except Exception as e:
        print(f"❌ 讀取參數表失敗: {e}")

if __name__ == "__main__":
    asyncio.run(run())
