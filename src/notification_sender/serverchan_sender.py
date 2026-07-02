# -*- coding: utf-8 -*-
"""
Server酱发送提醒服务

职责：
1. 通过官方 serverchan-sdk 发送 Server酱消息
"""
import logging
from typing import Any, Dict, Optional

from src.config import Config


logger = logging.getLogger(__name__)


class ServerchanSender:
    def __init__(self, config: Config):
        """
        初始化 Server酱配置

        Args:
            config: 配置对象
        """
        self._sendkey = getattr(config, "serverchan_sendkey", None)
        self._channel = getattr(config, "serverchan_channel", None)
        self._openid = getattr(config, "serverchan_openid", None)
        self._short = getattr(config, "serverchan_short", None)
        self._tags = getattr(config, "serverchan_tags", None)
        self._noip = getattr(config, "serverchan_noip", False)

    def send_to_serverchan(
        self,
        content: str,
        title: Optional[str] = None,
        *,
        timeout_seconds: Optional[float] = None,
    ) -> bool:
        """
        推送消息到 Server酱。

        官方 SDK 会按 SendKey 自动适配 Server酱 Turbo 与 Server酱3。
        """
        if not self._sendkey:
            logger.warning("Server酱 SendKey 未配置，跳过推送")
            return False

        try:
            from serverchan_sdk import sc_send
        except ImportError:
            logger.error("serverchan-sdk 未安装，无法发送 Server酱通知")
            return False

        message_title = title or "股票分析报告"
        options = self._build_options()
        try:
            response = sc_send(self._sendkey, message_title, content, options)
        except Exception as exc:
            logger.error("发送 Server酱消息失败: %s", exc)
            return False

        if self._is_success_response(response):
            logger.info("Server酱消息发送成功")
            return True

        logger.error("Server酱返回错误: %s", response)
        return False

    def _build_options(self) -> Dict[str, Any]:
        """构造官方 SDK options 参数，只传递已配置项。"""
        options: Dict[str, Any] = {}
        if self._tags:
            options["tags"] = self._tags
        if self._short:
            options["short"] = self._short
        if self._channel:
            options["channel"] = self._channel
        if self._openid:
            options["openid"] = self._openid
        if self._noip:
            options["noip"] = 1
        return options

    @staticmethod
    def _is_success_response(response: Any) -> bool:
        """兼容 SDK 返回 dict 或对象两种形态，code 为 0 表示成功。"""
        if isinstance(response, dict):
            return response.get("code") == 0
        return getattr(response, "code", None) == 0
