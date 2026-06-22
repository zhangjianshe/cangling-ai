""" IMAGEBOT ENGINE

该模块提供了算法在工作流引擎中运行的标准环境封装。
通过 Engine 获取 Context，可以实现：
1. 节点与步骤的状态监控（开始、进度、结束）
2. 数据的输入读取与结果输出
3. 自动化的资源清理与结果持久化
"""
import atexit
import json
import os
import threading

from cangling.workflow.workflow import \
    NodeProgressMessage, StepBeginMessage, StepEndMessage, NodeEndMessage, NodeBeginMessage, StepProgressMessage, \
    StepMessage, Workflow


class Context:
    """
    算法运行时的上下文环境，负责与工作流引擎进行实时交互。

    生命周期建议：
    node_begin -> (step_begin -> step_progress -> step_end) -> node_end
    """
    _workflow: Workflow = None
    _output_values: dict = None
    _has_closed = False

    def __init__(self):
        """初始化上下文，建立工作流连接并注册退出钩子"""
        self._workflow = Workflow()
        self._output_values = {}
        # 注册进程退出时的自动清理逻辑
        atexit.register(self._close)

    def write(self, key: str, value: any):
        """
        向工作流输出一个变量值。
        该值会同步保存到本地缓冲区，并在 close() 时持久化到输出文件，同时通过消息实时发往引擎。

        :param key: 变量名
        :param value: 变量值（建议可 JSON 序列化）
        """
        self._output_values[key] = value
        self._workflow.write_output(**{key: value})

    def read(self, key: str, default_value: None | str = None) -> str:
        """
        从环境变量或配置中读取输入变量值。

        :param key: 变量名
        :param default_value: 默认值
        :return: 读取到的变量字符串
        """
        return self._workflow.read(key, default_value)

    def _close(self):
        """
        关闭上下文环境。
        该方法会将所有通过 write() 输出的变量写入到工作流指定的 output 路径，并断开与引擎的连接。
        """
        if self._has_closed:
            return

        file_path = self._workflow.get_output_file()
        if file_path:
            try:
                # 确保输出目录存在
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, 'w', encoding='utf-8') as f:
                    # 格式化持久化结果数据
                    json.dump(self._output_values, f, ensure_ascii=False, indent=4)

                print(f"[SUCCESS] 运行结果已成功保存至: {file_path}")
            except Exception as e:
                print(f"[ERROR] 写入输出文件失败: {e}")

        self._workflow.close()
        self._has_closed = True

    # --- 节点(Node)级别监控方法 ---

    def node_begin(self, title: str, step_count: int = 1) -> None:
        """
        标记算法节点正式开始运行。

        :param title: 节点名称（如：道路提取算法）
        :param step_count: 该节点下包含的总步骤数
        """
        begin_message = NodeBeginMessage(title, step_count)
        self._workflow.send_message(begin_message)

    def node_progress(self, progress: int = 1) -> None:
        """
        更新节点的总体进度。

        :param progress: 总体进度百分比 (0-100)
        """
        progress_message = NodeProgressMessage(progress)
        self._workflow.send_message(progress_message)

    def node_end(self, success: bool = True, msg: str = "") -> None:
        """
        标记算法节点运行结束。

        :param success: 是否成功结束
        :param msg: 结束时的说明消息（如错误原因）
        """
        end_message = NodeEndMessage(success, msg)
        self._workflow.send_message(end_message)

    # --- 步骤(Step)级别监控方法 ---

    def step_begin(self, title: str, step: int = 1) -> None:
        """
        开始一个具体的子步骤。

        :param title: 步骤标题（如：影像预处理）
        :param step: 当前步骤的序号（从1开始）
        """
        step_begin_message = StepBeginMessage(step, title)
        self._workflow.send_message(step_begin_message)

    def step_progress(self, step: int = 1, progress: int = 1, msg: str = "") -> None:
        """
        报告当前步骤的内部进度。

        :param step: 当前步骤序号
        :param progress: 当前步骤的进度百分比 (0-100)
        :param msg: 当前进度的详细描述
        """
        step_progress_message = StepProgressMessage(step, progress, msg)
        self._workflow.send_message(step_progress_message)

    def step_message(self, step: int = 1, msg: str = "") -> None:
        """
        在当前步骤下打印一条普通的文本消息。
        """
        step_message = StepMessage(step, msg)
        self._workflow.send_message(step_message)

    def step_end(self, step:int =1,success: bool = True, msg: str = "") -> None:
        """
        结束当前步骤。
        """
        step_end_message = StepEndMessage(step,success, msg)
        self._workflow.send_message(step_end_message)


class Engine:
    """
    ImageBot 引擎单例类。
    用于管理和获取算法运行环境的唯一入口。
    """
    _instance = None
    _lock = threading.Lock()
    context: Context = None

    def __new__(cls):
        """实现线程安全的单例模式"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(Engine, cls).__new__(cls)
        return cls._instance

    def context(self) -> Context:
        """
        获取当前算法的运行上下文。
        如果上下文不存在，则会自动创建一个新的实例。

        :return: RunningContext 实例
        """
        if self.context is None:
            self.context = Context()
        return self.context

    def close(self):
        pass