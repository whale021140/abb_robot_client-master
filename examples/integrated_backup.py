# 每隔十分钟备份一下，并查看日志中是否有编辑事件，有则记录时间到txt文档中，之后清空日志。
# API Address： https://developercenter.robotstudio.com/api/RWS
import abb_robot_client.rwsV2
import logging
import time
import os
import sys
from datetime import datetime
from abb_robot_client.rwsV2 import (
    RWSV2,
    SubscriptionResourceRequest,
    SubscriptionResourceType,
    SubscriptionResourcePriority,
)
from contextlib import closing

# 检查是否是单次备份模式
SINGLE_BACKUP_MODE = "--single-backup" in sys.argv

# 配置日志，用于输出日志(部分异步场景使用print不方便)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("backup.txt", mode="a", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

# 自定义print函数，同时输出到控制台和文件
def custom_print(*args, **kwargs):
    print_content = " ".join(str(arg) for arg in args)
    print(print_content, **kwargs)
    with open("backup.txt", "a", encoding="utf-8") as f:
        f.write(print_content + "\n")

def Subscriptionhandler(m):
    c = RWSV2()
    # 订阅PERS变量，但返回的消息没有值
    if isinstance(m, abb_robot_client.rwsV2.VariableValue):
        my_instance: abb_robot_client.rwsV2.VariableValue = m
        logging.info("VariableValue-----" + str(my_instance))

    # IO信号订阅，会返回新的值
    elif isinstance(m, abb_robot_client.rwsV2.IOSignal):
        my_instance: abb_robot_client.rwsV2.IOSignal = m
        logging.info("IOSignal-----" + str(my_instance))

    # 日志订阅 会返回日志编号，没有具体内容
    elif isinstance(m, abb_robot_client.rwsV2.EventLogEntryEvent):
        my_instance: abb_robot_client.rwsV2.EventLogEntryEvent = m
        logging.info("EventLogEntryEvent-----" + str(my_instance))
        json_list = c.get_elog_domain_MessagesV2(
            domain_number = str(0),
            lang = "en",
            resource = "title",
            order = "lifo",
            start = str(1),
            limit = str(10),
        )
        #遍历列表中的每个字典
        for item in json_list:
            sps = item["_title"].split("/")
            data2 = str(m.seqnum)
            data = str(sps[-1])
            if data == data2:
                #若有编辑事件则记录到txt文档中
                if item["code"] == "10063":
                    # print("jsonlist: ", json_list)
                    event_time = item["tstamp"]
                    custom_print(item["tstamp"] + " detect module edited~~~~~~~~~")
                    with open("C:/Users/CNLECHE25/Desktop/leyi/event_log.txt", "a") as file:
                        file.write(f"Event Code: 10063, Event Time: {event_time}\n")
                    logging.info(f"Event Code 10063 logged at {event_time}")

    # 操作模式订阅
    elif isinstance(m, abb_robot_client.rwsV2.OperationalMode):
        my_instance: abb_robot_client.rwsV2.OperationalMode = m
        logging.info("OperationalMode-----" + str(my_instance))

    # 控制器状态订阅
    elif isinstance(m, abb_robot_client.rwsV2.ControllerState):
        my_instance: abb_robot_client.rwsV2.ControllerState = m
        logging.info("ControllerState-----" + str(my_instance))

    # 速度状态订阅
    elif isinstance(m, abb_robot_client.rwsV2.SpeedRatioState):
        my_instance: abb_robot_client.rwsV2.SpeedRatioState = m
        logging.info("SpeedRatioState-----" + str(my_instance.speed))

def main():
    # 程序启动时添加分隔线
    separator = "="*50
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    custom_print(f"\n{separator}\n程序启动时间: {current_time}\n{separator}")
    
    # 真实机器人"http://192.168.125.1:80"
    c = RWSV2()
    variable22 = abb_robot_client.rwsV2.VariableValue("", "", "")

    ### 1.1 创建备份
    ### 获取此刻的时间用于命名备份文件
    current_time = datetime.now()
    time_str = current_time.strftime("%Y-%m-%d_%H-%M-%S")
    backup_path = "/fileservice/$Backup/" + time_str

    backup_result = c.try_create_backupV2(backup_path, False)
    custom_print(backup_result)

    ### 1.2 检查备份文件
    check_result = c.check_backup_restoreV2(
        backup_path, "all", "false", "false", "all"
    )
    custom_print(check_result)

    ### 1.3 恢复备份
    # 先检查不在手动模式，再恢复备份
    # operation_mode = c.get_operation_modeV2()
    # custom_print(f"当前操作模式: {operation_mode}")

    # if operation_mode != "MANR":
    #     custom_print(c.try_Mastership_requestV2())
    #     custom_print(
    #         c.try_backup_restoreV2(
    #             "/fileservice/$Backup/2025-02-08_10-28-01", "all", "false", "false", "false", "all"
    #         )
    #     )
    #     custom_print(c.try_Mastership_releaseV2())
    # else:
    #     custom_print("当前处于手动模式，跳过恢复备份操作。")

    # 如果是单次备份模式，则跳过订阅部分
    if SINGLE_BACKUP_MODE:
        custom_print("单次备份完成，程序退出。")
        return

    ### 2.1订阅机器人日志 实时打印出来
    sub = c.subscribeV2(
        [
            SubscriptionResourceRequest(
                    SubscriptionResourceType.ElogDomain,
                    SubscriptionResourcePriority.Medium,
                    "0",
                ),
            ],
            Subscriptionhandler,
        )
    # 继续运行30秒，等待事件
    custom_print("开始订阅，等待30秒...")
    time.sleep(30)
    custom_print("订阅运行结束，连接断开~")

    ### 清除日志
    clear_result = c.clear_ElogV2()
    custom_print(clear_result)


if __name__ == "__main__":
    # 确保backup.txt文件存在
    if not os.path.exists("backup.txt"):
        with open("backup.txt", "w", encoding="utf-8") as f:
            f.write("===== ABB机器人备份日志开始 =====\n")
    
    if SINGLE_BACKUP_MODE:
        # 单次备份模式，只执行一次
        try:
            main()
            custom_print("单次备份完成")
        except Exception as e:
            error_msg = f"备份过程中发生错误: {str(e)}"
            logging.error(error_msg)
            custom_print(error_msg)
            sys.exit(1)
    else:
        # 循环备份模式
        while True:
            try:
                main()
                custom_print("等待3分钟后再次执行...")
                time.sleep(180)  # 等待3分钟
            except Exception as e:
                error_msg = f"发生错误: {str(e)}"
                logging.error(error_msg)
                custom_print(error_msg)
                custom_print("5分钟后尝试重新执行...")
                time.sleep(300)  # 发生错误后等待5分钟再尝试