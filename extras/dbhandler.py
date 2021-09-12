from utils import logInfo, logException, logWarning, mongoDBClient, config
import asyncio
import schedule


async def handle_db_calls():
    while True:
        try:
            # for runtime data
            run_data = mongoDBClient.fetchRunTimeData()
            # logInfo(f"Making call to fetch runtime data")
            if run_data is not None:
                for item, value in run_data.items():
                    config.setExtraData(item, value)
            schedule.run_pending()
        except Exception as ex:
            logException(f"Error in handle_db_calls: {ex}", True)
        finally:
            if config.get("env") == "local":
                await asyncio.sleep(1 * 60)
            else:
                await asyncio.sleep(10 * 60)
