# API Address： https://developercenter.robotstudio.com/api/RWS
import abb_robot_client.rwsV2
import logging
import time
from datetime import datetime
from abb_robot_client.rwsV2 import (
    RWSV2,
    SubscriptionResourceRequest,
    SubscriptionResourceType,
    SubscriptionResourcePriority,
)
from contextlib import closing


# 配置日志，用于输出日志(部分异步场景使用print不方便)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

### 1. 1.1 读写变量 / 1.2 读写信号
### 2. 2.1 创建备份 / 2.2 检查备份文件 / 2.3 备份恢复，恢复后控制器会自动重启
### 3. 读写机器人控制器状态
### 4. 读写机器人操作模式
### 5. 读取机器人日志  /  读取指定序号日志内容
### 6. 订阅机器人：控制器状态变化、操作模式变化、指定变量变化、指定信号变化、新增日志内容、速度比例变化.
### 7. 7.1 PPToMain / 7.2 启动程序 / 7.3 停止程序
### 8. 读取机器人当前jointtarget/robtarget  读写speedratio"

FuncNum = 3 # 根据FuncNum值执行不同示例 1-8，示例介绍如上


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
                if item["code"] == "10063":
                    print(item["tstamp"] + " detect module edited~~~~~~~~~")

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
    # "http://127.0.0.1:80"
    c = RWSV2()
    variable22 = abb_robot_client.rwsV2.VariableValue("", "", "")

    #以下都是示例，
    if FuncNum == 1:

        ### 1.1 读写PERS变量,根据实际情况修改参数,参数里需要有module名
        print(c.get_rapid_variableV2("mainPro/targetPosition"))

        ### 写变量之前要请求Mastership
        print(c.try_Mastership_requestV2())
        print(
            c.set_rapid_variableV2(
                "mainPro/targetPosition",
                "[[1316,124.0,869.0],[0.531997,0.0805023,0.837865,0.0920889],[0,-2,2,0],[9E+9,9E+9,9E+9,9E+9,9E+9,9E+9]]",
            )
        )
        print(c.try_Mastership_releaseV2())
        ### 再读一次
        print(c.get_rapid_variableV2("mainPro/targetPosition"))

        ## 1.2 读写信号 对于模拟、数字和组信号都有效，但赋值时注意值是否合法
        print(c.get_io_signalV2(network="virtual", signal="vdotest01"))

        # ### 写变量之前要请求Mastership
        print(c.try_Mastership_requestV2())
        print(c.set_io_signalV2(network="virtual", signal="vdotest01", value=False))
        print(c.try_Mastership_releaseV2())
        # ### 再读一次
        print(c.get_io_signalV2(network="virtual", signal="vdotest01"))

    elif FuncNum == 2:
        ### 2.1 创建备份
        ### 获取此刻的时间用于命名备份文件
        current_time = datetime.now()
        time_str = current_time.strftime("%Y-%m-%d_%H-%M-%S")
        backup_path = "/fileservice/$Backup/" + time_str

        print(c.try_create_backupV2(backup_path, False))

        ### 2.2 检查备份文件
        print(
            c.check_backup_restoreV2(
                backup_path, "all", "false", "false", "all"
            )
        )

        ## 2.3 备份恢复，恢复后控制器会自动重启
        print(c.try_Mastership_requestV2())
        print(
            c.try_backup_restoreV2(
                "/fileservice/$Backup/2025-02-08_10-28-01", "all", "false", "false", "false", "all"
            )
        )
        print(c.try_Mastership_releaseV2())

    elif FuncNum == 3:
        ### 3.1 读取机器人控制器状态
        #print(c.get_controller_stateV2())

        ### 3.2 设置机器人控制器状态
        print(c.set_controller_stateV2("motoron"))

    elif FuncNum == 4:
        ### 4.1 读取机器人操作模式
        print(c.get_operation_modeV2())

        ### 4.2 设置机器人操作模式
        # print(c.try_Mastership_requestV2())
        # print(c.set_operation_stateV2("man"))
        # print(c.try_Mastership_releaseV2())

    elif FuncNum == 5:
        ### 5.读取机器人日志，通过分页机制循环读取所有已有日志

        ### 设置每页日志数量   !!!当数量大于50时，服务器返回数量可能会只按50计算,会导致计算页数小于实际页数
        pagesize = 80
        ### 设置日志类别 domain-number
        domain_num = 0

        ### 获取domain日志总数量
        info = c.get_elog_domain_MessagesV2(
            domain_number=str(domain_num), lang="en", resource="info"
        )
        print("当前domain日志数量" + info[0]["numevts"])
        ### 计算domain日志页数
        pagenum = int(info[0]["numevts"]) // int(pagesize)
        if int(info[0]["numevts"]) % pagesize != 0:
            pagenum += 1
        ### 遍历分页,获取每页日志信息,并打印出来
        if pagenum < 1:
            exit()
        else:
            print("当前domain日志页数" + str(pagenum))
            idx = 0
            for i in range(1, pagenum + 1):
                json_list = c.get_elog_domain_MessagesV2(
                    domain_number=str(domain_num),
                    lang="en",
                    resource="title",
                    order="fifo",
                    start=str(i),
                    limit=str(pagesize),
                )
                # 遍历列表中的每个字典
                for item in json_list:
                    idx += 1
                    print(str(idx))
                    # 如果事件代码为10063（即编辑module），则把事件时间保存到本地txt文档中
                    if item["code"] == '10063':
                        event_time = item["tstamp"]
                        with open("C:/Users/CNLECHE25/Desktop/leyi/event_log.txt", "a") as file: # 打开文件失败
                            file.write(f"Event Code: 10063, Event Time: {event_time}\n")
                        logging.info(f"Event Code 10063 logged at {event_time}")
                    for key, value in item.items():
                        print(f"{key}: {value}")
                    print("-" * 30)  # 打印分隔线以便区分不同项
        print("-" * 30)

    elif FuncNum == 6:
        # ### 6.1订阅机器人日志 实时打印出来
        #   由于API2.0 订阅种类增加到41种，每种类型订阅还需要做相应的正则表达式匹配处理，
        #   用于从返回的html消息中提取需要的信息,详见RWS2Subscription类的init和onMessage方法

        # 目前只支持以下类型订阅：控制器状态、操作模式、指定变量、指定信号、新增日志、速度比例. 20250124
        sub = c.subscribeV2(
            [
                # SubscriptionResourceRequest(
                #     SubscriptionResourceType.SubscribeControllerState,
                #     SubscriptionResourcePriority.Medium,
                # ),
                # SubscriptionResourceRequest(
                #     SubscriptionResourceType.SubscribeControllerOperationMode,
                #     SubscriptionResourcePriority.Medium,
                # ),
                # SubscriptionResourceRequest(
                #     SubscriptionResourceType.SubscribeRAPIDPersistentVariable,
                #     SubscriptionResourcePriority.Medium,
                #     "RAPID/T_ROB1/user/tool01",
                # ),
                # SubscriptionResourceRequest(
                #     SubscriptionResourceType.SubscribeRAPIDExecution,
                #     SubscriptionResourcePriority.Medium,
                # ),
                # SubscriptionResourceRequest(
                #     SubscriptionResourceType.IOSignal,
                #     SubscriptionResourcePriority.Medium,
                #     "test01",
                # ),
                SubscriptionResourceRequest(
                    SubscriptionResourceType.ElogDomain,
                    SubscriptionResourcePriority.Medium,
                    "0",
                ),
                # SubscriptionResourceRequest(
                #     SubscriptionResourceType.SubscribeSpeedRatio,
                #     SubscriptionResourcePriority.Medium,
                # ),
            ],
            Subscriptionhandler,
        )

        # 继续运行60秒，等待事件
        time.sleep(600)
        print("运行结束，连接断开~")

        # ###6.2 读取指定序号的日志信息
        # log = c.read_event_logV2(666)
        # print(log[0].code)

    elif FuncNum == 7:
        time.sleep(0.5)

        ### 7.1 PPToMain
        print(c.try_Mastership_requestV2())
        print(c.resetppV2())
        print(c.try_Mastership_releaseV2())

        time.sleep(3)

        ### 7.2 启动程序
        print(c.try_Mastership_requestV2(domian_name="edit"))
        print(c.startV2())
        print(c.try_Mastership_releaseV2(domian_name="edit"))

        time.sleep(3)

        ### 7.3 启动程序
        print(c.try_Mastership_requestV2())
        print(c.stopV2())
        print(c.try_Mastership_releaseV2())

    elif FuncNum == 8:

        ### 读取机器人当前jointtarget/robtarget
        print(c.get_jointtargetV2())
        print(c.get_robtargetV2())

        ### 读写speedratio
        print("当前速度: " + str(c.get_speedratioV2()))
        print(c.try_Mastership_requestV2())
        c.set_speedratioV2(50)
        print(c.try_Mastership_releaseV2())

    elif FuncNum == 9:
        # 请求后可以在munual模式下修改PERS变量
        # 需要机器人在munual模式下执行，否则会报错；执行后要及时在示教器点确认，否则超时也会报错；
        c.request_rmmpV2()
        print(c.try_Mastership_requestV2())
        print(
            c.set_rapid_variableV2(
                "mainPro/targetPosition",
                "[[1316,124.0,869.0],[0.531997,0.0805023,0.837865,0.0920889],[0,-2,2,0],[9E+9,9E+9,9E+9,9E+9,9E+9,9E+9]]",
            )
        )
        print(c.try_Mastership_releaseV2())
    
    else:
        print("Done")


if __name__ == "__main__":
    main()
