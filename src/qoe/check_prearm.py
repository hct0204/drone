import asyncio
from mavsdk import System

# 在背景持續接收並印出飛控傳來的文字訊息
async def print_status_text(drone):
    try:
        async for status in drone.telemetry.status_text():
            # 標示出系統訊息，如果包含 PreArm 就用醒目提示
            if "PreArm" in status.text:
                print(f"\n🚨 找到解鎖阻擋原因 ➔ {status.text}\n")
            else:
                print(f"ℹ️ 飛控訊息: {status.text}")
    except asyncio.CancelledError:
        pass

async def run():
    drone = System()
    
    print("正在等待無人機連線...")
    await drone.connect(system_address="serial:///dev/ttyAMA0:57600")

    async for state in drone.core.connection_state():
        if state.is_connected:
            print("✅ 無人機連線成功！\n")
            break

    # 啟動監聽任務
    status_task = asyncio.create_task(print_status_text(drone))

    print("等待 2 秒讓系統同步...")
    await asyncio.sleep(2)

    print("正在送出解鎖指令 (Arm)，請觀察畫面輸出的錯誤訊息...")
    try:
        await drone.action.arm()
        print("✅ 解鎖竟然成功了！(立刻執行上鎖確保安全)")
        await drone.action.disarm()
    except Exception as e:
        print(f"❌ 解鎖被拒絕。")

    # 稍微等待一下，確保錯誤訊息有足夠時間從飛控傳送過來並印出
    await asyncio.sleep(2)
    status_task.cancel()

if __name__ == "__main__":
    asyncio.run(run())
