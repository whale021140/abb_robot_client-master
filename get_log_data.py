#!/usr/bin/env python
# 提供ABB机器人日志数据的API接口
import json
import sys
import abb_robot_client.rwsV2
from abb_robot_client.rwsV2 import RWSV2

def get_robot_logs(limit=10):
    """获取机器人日志数据"""
    try:
        # 创建RWS客户端连接
        c = RWSV2()
        
        # 获取日志数据
        json_list = c.get_elog_domain_MessagesV2(
            domain_number=str(0),
            lang="en",
            resource="title",
            order="lifo",  # 最新的记录优先
            start=str(1),
            limit=str(limit),
        )
        
        # 返回日志列表
        return json_list
    except Exception as e:
        return [{"error": str(e), "code": "9999", "_title": "获取日志失败", "tstamp": ""}]

if __name__ == "__main__":
    # 从命令行参数获取请求的日志条数
    limit = 10
    if len(sys.argv) > 1:
        try:
            limit = int(sys.argv[1])
        except:
            pass
    
    # 获取日志并打印为JSON格式
    logs = get_robot_logs(limit)
    print(json.dumps(logs)) 