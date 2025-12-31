"""
Browserbase 代理輪換示例
========================

本模塊展示了如何使用 Browserbase 進行代理輪換和 IP 管理。
包括代理池管理、智能輪換、健康檢查、地理位置選擇等。

主要內容:
1. 代理配置和連接
2. 代理池管理
3. 智能代理輪換
4. 代理健康檢查
5. 地理位置選擇
6. 失敗重試機制

作者: Browserbase 示例團隊
日期: 2025-12-31
"""

import os
import time
import random
import asyncio
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict
from dotenv import load_dotenv


# 加載環境變量
load_dotenv()


class ProxyType(Enum):
    """代理類型"""
    HTTP = "http"
    HTTPS = "https"
    SOCKS5 = "socks5"


class ProxyProvider(Enum):
    """代理提供商"""
    RESIDENTIAL = "residential"  # 住宅代理
    DATACENTER = "datacenter"    # 數據中心代理
    MOBILE = "mobile"            # 移動代理


class ProxyStatus(Enum):
    """代理狀態"""
    AVAILABLE = "available"      # 可用
    IN_USE = "in_use"           # 使用中
    FAILED = "failed"           # 失敗
    BANNED = "banned"           # 被封禁
    CHECKING = "checking"       # 檢查中


@dataclass
class ProxyConfig:
    """代理配置"""
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    proxy_type: ProxyType = ProxyType.HTTP
    provider: ProxyProvider = ProxyProvider.DATACENTER
    country: Optional[str] = None
    city: Optional[str] = None
    isp: Optional[str] = None

    def get_url(self) -> str:
        """獲取代理 URL"""
        if self.username and self.password:
            return f"{self.proxy_type.value}://{self.username}:{self.password}@{self.host}:{self.port}"
        return f"{self.proxy_type.value}://{self.host}:{self.port}"

    def __repr__(self) -> str:
        location = f"{self.country}/{self.city}" if self.country else "Unknown"
        return f"<Proxy {self.host}:{self.port} ({location})>"


@dataclass
class ProxyStats:
    """代理統計信息"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_bytes: int = 0
    avg_response_time: float = 0.0
    last_used: Optional[datetime] = None
    last_check: Optional[datetime] = None
    consecutive_failures: int = 0
    is_healthy: bool = True

    def get_success_rate(self) -> float:
        """獲取成功率"""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100

    def update_request(self, success: bool, response_time: float = 0.0, bytes_transferred: int = 0):
        """更新請求統計"""
        self.total_requests += 1
        self.last_used = datetime.now()

        if success:
            self.successful_requests += 1
            self.consecutive_failures = 0
            self.total_bytes += bytes_transferred

            # 更新平均響應時間
            if self.avg_response_time == 0:
                self.avg_response_time = response_time
            else:
                self.avg_response_time = (self.avg_response_time * 0.8) + (response_time * 0.2)
        else:
            self.failed_requests += 1
            self.consecutive_failures += 1

            # 連續失敗超過閾值，標記為不健康
            if self.consecutive_failures >= 3:
                self.is_healthy = False


class Proxy:
    """代理類"""

    def __init__(self, config: ProxyConfig):
        """
        初始化代理

        Args:
            config: 代理配置
        """
        self.config = config
        self.stats = ProxyStats()
        self.status = ProxyStatus.AVAILABLE
        self.id = f"{config.host}:{config.port}"

    def use(self) -> str:
        """
        使用代理

        Returns:
            代理 URL
        """
        self.status = ProxyStatus.IN_USE
        return self.config.get_url()

    def release(self):
        """釋放代理"""
        if self.status == ProxyStatus.IN_USE:
            self.status = ProxyStatus.AVAILABLE

    def mark_failed(self):
        """標記為失敗"""
        self.status = ProxyStatus.FAILED
        self.stats.update_request(success=False)

    def mark_success(self, response_time: float = 0.0, bytes_transferred: int = 0):
        """標記為成功"""
        self.status = ProxyStatus.AVAILABLE
        self.stats.update_request(
            success=True,
            response_time=response_time,
            bytes_transferred=bytes_transferred
        )

    def is_available(self) -> bool:
        """檢查是否可用"""
        return (
            self.status == ProxyStatus.AVAILABLE and
            self.stats.is_healthy and
            self.stats.consecutive_failures < 3
        )


class ProxyPool:
    """
    代理池

    管理一組代理，提供自動輪換、健康檢查等功能。
    """

    def __init__(
        self,
        proxies: List[ProxyConfig],
        rotation_strategy: str = "round_robin"
    ):
        """
        初始化代理池

        Args:
            proxies: 代理配置列表
            rotation_strategy: 輪換策略 (round_robin, random, least_used)
        """
        self.proxies: Dict[str, Proxy] = {
            f"{p.host}:{p.port}": Proxy(p) for p in proxies
        }
        self.rotation_strategy = rotation_strategy
        self.current_index = 0
        self.usage_stats = defaultdict(int)

        print(f"[ProxyPool] 初始化代理池: {len(self.proxies)} 個代理")
        print(f"[ProxyPool] 輪換策略: {rotation_strategy}")

    def get_next_proxy(self, country: Optional[str] = None) -> Optional[Proxy]:
        """
        獲取下一個可用代理

        Args:
            country: 指定國家（可選）

        Returns:
            代理對象
        """
        available_proxies = [
            p for p in self.proxies.values()
            if p.is_available() and (country is None or p.config.country == country)
        ]

        if not available_proxies:
            print("[ProxyPool] 警告: 沒有可用代理")
            return None

        # 根據策略選擇代理
        if self.rotation_strategy == "round_robin":
            proxy = available_proxies[self.current_index % len(available_proxies)]
            self.current_index += 1

        elif self.rotation_strategy == "random":
            proxy = random.choice(available_proxies)

        elif self.rotation_strategy == "least_used":
            proxy = min(available_proxies, key=lambda p: p.stats.total_requests)

        elif self.rotation_strategy == "best_performance":
            # 選擇成功率最高且響應時間最短的
            proxy = min(
                available_proxies,
                key=lambda p: (
                    -p.stats.get_success_rate(),
                    p.stats.avg_response_time or float('inf')
                )
            )

        else:
            proxy = available_proxies[0]

        self.usage_stats[proxy.id] += 1
        print(f"[ProxyPool] 分配代理: {proxy.config.host}:{proxy.config.port}")
        return proxy

    def release_proxy(self, proxy: Proxy):
        """
        釋放代理

        Args:
            proxy: 代理對象
        """
        proxy.release()
        print(f"[ProxyPool] 釋放代理: {proxy.config.host}:{proxy.config.port}")

    def mark_proxy_failed(self, proxy: Proxy):
        """
        標記代理失敗

        Args:
            proxy: 代理對象
        """
        proxy.mark_failed()
        print(f"[ProxyPool] 代理失敗: {proxy.config.host}:{proxy.config.port}")

    def get_pool_stats(self) -> Dict:
        """
        獲取代理池統計

        Returns:
            統計信息字典
        """
        total = len(self.proxies)
        available = sum(1 for p in self.proxies.values() if p.is_available())
        in_use = sum(1 for p in self.proxies.values() if p.status == ProxyStatus.IN_USE)
        failed = sum(1 for p in self.proxies.values() if p.status == ProxyStatus.FAILED)

        total_requests = sum(p.stats.total_requests for p in self.proxies.values())
        total_success = sum(p.stats.successful_requests for p in self.proxies.values())

        return {
            "total_proxies": total,
            "available": available,
            "in_use": in_use,
            "failed": failed,
            "total_requests": total_requests,
            "success_rate": (total_success / total_requests * 100) if total_requests > 0 else 0
        }

    def remove_unhealthy_proxies(self) -> int:
        """
        移除不健康的代理

        Returns:
            移除的代理數量
        """
        to_remove = [
            proxy_id for proxy_id, proxy in self.proxies.items()
            if not proxy.stats.is_healthy
        ]

        for proxy_id in to_remove:
            del self.proxies[proxy_id]
            print(f"[ProxyPool] 移除不健康代理: {proxy_id}")

        return len(to_remove)


class ProxyHealthChecker:
    """
    代理健康檢查器

    定期檢查代理的可用性和性能。
    """

    def __init__(self, proxy_pool: ProxyPool, check_interval: int = 60):
        """
        初始化健康檢查器

        Args:
            proxy_pool: 代理池
            check_interval: 檢查間隔（秒）
        """
        self.proxy_pool = proxy_pool
        self.check_interval = check_interval
        self.is_running = False
        print(f"[ProxyHealthChecker] 初始化 (檢查間隔: {check_interval}秒)")

    def check_proxy(self, proxy: Proxy) -> bool:
        """
        檢查單個代理

        Args:
            proxy: 代理對象

        Returns:
            是否健康
        """
        print(f"[ProxyHealthChecker] 檢查代理: {proxy.id}")

        # 模擬健康檢查（實際應該發送真實請求）
        start_time = time.time()

        # 70% 成功率
        is_healthy = random.random() > 0.3
        response_time = random.uniform(0.1, 2.0)

        elapsed = time.time() - start_time

        if is_healthy:
            proxy.stats.last_check = datetime.now()
            proxy.stats.is_healthy = True
            print(f"  ✓ 健康 (響應時間: {response_time:.2f}s)")
        else:
            proxy.stats.is_healthy = False
            print(f"  ✗ 不健康")

        return is_healthy

    def check_all(self):
        """檢查所有代理"""
        print(f"\n[ProxyHealthChecker] 開始健康檢查...")

        healthy_count = 0
        unhealthy_count = 0

        for proxy in self.proxy_pool.proxies.values():
            if self.check_proxy(proxy):
                healthy_count += 1
            else:
                unhealthy_count += 1

        print(f"[ProxyHealthChecker] 檢查完成: {healthy_count} 健康, {unhealthy_count} 不健康\n")

        # 移除不健康的代理
        removed = self.proxy_pool.remove_unhealthy_proxies()
        if removed > 0:
            print(f"[ProxyHealthChecker] 已移除 {removed} 個不健康代理\n")


class GeoProxySelector:
    """
    地理位置代理選擇器

    根據地理位置需求選擇合適的代理。
    """

    def __init__(self, proxy_pool: ProxyPool):
        """
        初始化地理選擇器

        Args:
            proxy_pool: 代理池
        """
        self.proxy_pool = proxy_pool
        self._build_geo_index()
        print("[GeoProxySelector] 初始化完成")

    def _build_geo_index(self):
        """構建地理位置索引"""
        self.country_index: Dict[str, List[Proxy]] = defaultdict(list)
        self.city_index: Dict[str, List[Proxy]] = defaultdict(list)

        for proxy in self.proxy_pool.proxies.values():
            if proxy.config.country:
                self.country_index[proxy.config.country].append(proxy)
            if proxy.config.city:
                self.city_index[proxy.config.city].append(proxy)

        print(f"[GeoProxySelector] 索引構建完成:")
        print(f"  - 國家數: {len(self.country_index)}")
        print(f"  - 城市數: {len(self.city_index)}")

    def get_proxy_by_country(self, country: str) -> Optional[Proxy]:
        """
        根據國家獲取代理

        Args:
            country: 國家代碼

        Returns:
            代理對象
        """
        available = [
            p for p in self.country_index.get(country, [])
            if p.is_available()
        ]

        if not available:
            print(f"[GeoProxySelector] 沒有可用的 {country} 代理")
            return None

        proxy = random.choice(available)
        print(f"[GeoProxySelector] 選擇 {country} 代理: {proxy.id}")
        return proxy

    def get_proxy_by_city(self, city: str) -> Optional[Proxy]:
        """
        根據城市獲取代理

        Args:
            city: 城市名稱

        Returns:
            代理對象
        """
        available = [
            p for p in self.city_index.get(city, [])
            if p.is_available()
        ]

        if not available:
            print(f"[GeoProxySelector] 沒有可用的 {city} 代理")
            return None

        proxy = random.choice(available)
        print(f"[GeoProxySelector] 選擇 {city} 代理: {proxy.id}")
        return proxy

    def get_available_locations(self) -> Dict[str, int]:
        """
        獲取可用的地理位置

        Returns:
            位置和代理數量的字典
        """
        locations = {}

        for country, proxies in self.country_index.items():
            available = sum(1 for p in proxies if p.is_available())
            if available > 0:
                locations[country] = available

        return locations


class RetryHandler:
    """
    重試處理器

    處理代理失敗時的重試邏輯。
    """

    def __init__(
        self,
        proxy_pool: ProxyPool,
        max_retries: int = 3,
        backoff_factor: float = 1.5
    ):
        """
        初始化重試處理器

        Args:
            proxy_pool: 代理池
            max_retries: 最大重試次數
            backoff_factor: 退避係數
        """
        self.proxy_pool = proxy_pool
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        print(f"[RetryHandler] 初始化 (最大重試: {max_retries})")

    def execute_with_retry(
        self,
        func,
        *args,
        **kwargs
    ) -> Optional[any]:
        """
        執行函數並在失敗時重試

        Args:
            func: 要執行的函數
            *args: 位置參數
            **kwargs: 關鍵字參數

        Returns:
            函數執行結果
        """
        last_exception = None

        for attempt in range(self.max_retries):
            try:
                # 獲取新代理
                proxy = self.proxy_pool.get_next_proxy()
                if not proxy:
                    print(f"[RetryHandler] 嘗試 {attempt + 1}: 無可用代理")
                    time.sleep(self.backoff_factor ** attempt)
                    continue

                print(f"[RetryHandler] 嘗試 {attempt + 1}/{self.max_retries} 使用代理: {proxy.id}")

                # 執行函數
                result = func(proxy, *args, **kwargs)

                # 標記成功
                proxy.mark_success()
                self.proxy_pool.release_proxy(proxy)

                print(f"[RetryHandler] 成功！")
                return result

            except Exception as e:
                last_exception = e
                print(f"[RetryHandler] 嘗試 {attempt + 1} 失敗: {str(e)}")

                # 標記代理失敗
                if proxy:
                    self.proxy_pool.mark_proxy_failed(proxy)

                # 退避等待
                if attempt < self.max_retries - 1:
                    wait_time = self.backoff_factor ** attempt
                    print(f"[RetryHandler] 等待 {wait_time:.1f}秒後重試...")
                    time.sleep(wait_time)

        print(f"[RetryHandler] 所有重試均失敗")
        if last_exception:
            raise last_exception

        return None


def example_proxy_pool_basic():
    """示例1: 基礎代理池使用"""
    print("\n" + "=" * 60)
    print("示例1: 基礎代理池使用")
    print("=" * 60 + "\n")

    # 創建代理配置
    proxies = [
        ProxyConfig("proxy1.example.com", 8080, "user1", "pass1", country="US", city="New York"),
        ProxyConfig("proxy2.example.com", 8080, "user2", "pass2", country="UK", city="London"),
        ProxyConfig("proxy3.example.com", 8080, "user3", "pass3", country="JP", city="Tokyo"),
        ProxyConfig("proxy4.example.com", 8080, "user4", "pass4", country="US", city="Los Angeles"),
    ]

    # 創建代理池
    pool = ProxyPool(proxies, rotation_strategy="round_robin")

    # 獲取並使用代理
    print("\n使用代理:")
    for i in range(6):
        proxy = pool.get_next_proxy()
        if proxy:
            url = proxy.use()
            print(f"  請求 {i + 1}: 使用 {proxy.config}")

            # 模擬請求
            time.sleep(0.1)

            # 標記成功並釋放
            proxy.mark_success(response_time=random.uniform(0.1, 0.5))
            pool.release_proxy(proxy)

    # 查看統計
    print("\n代理池統計:")
    stats = pool.get_pool_stats()
    for key, value in stats.items():
        print(f"  - {key}: {value}")


def example_rotation_strategies():
    """示例2: 不同的輪換策略"""
    print("\n" + "=" * 60)
    print("示例2: 輪換策略對比")
    print("=" * 60 + "\n")

    proxies = [
        ProxyConfig(f"proxy{i}.example.com", 8080, country="US")
        for i in range(1, 5)
    ]

    strategies = ["round_robin", "random", "least_used"]

    for strategy in strategies:
        print(f"\n策略: {strategy}")
        print("-" * 40)

        pool = ProxyPool(proxies, rotation_strategy=strategy)

        # 獲取5個代理
        for i in range(5):
            proxy = pool.get_next_proxy()
            if proxy:
                print(f"  {i + 1}. {proxy.id}")
                pool.release_proxy(proxy)


def example_health_check():
    """示例3: 健康檢查"""
    print("\n" + "=" * 60)
    print("示例3: 代理健康檢查")
    print("=" * 60 + "\n")

    proxies = [
        ProxyConfig(f"proxy{i}.example.com", 8080)
        for i in range(1, 6)
    ]

    pool = ProxyPool(proxies)
    checker = ProxyHealthChecker(pool, check_interval=60)

    # 執行健康檢查
    checker.check_all()

    # 查看池狀態
    stats = pool.get_pool_stats()
    print("健康檢查後的池狀態:")
    for key, value in stats.items():
        print(f"  - {key}: {value}")


def example_geo_selection():
    """示例4: 地理位置選擇"""
    print("\n" + "=" * 60)
    print("示例4: 地理位置代理選擇")
    print("=" * 60 + "\n")

    proxies = [
        ProxyConfig("us-proxy1.com", 8080, country="US", city="New York"),
        ProxyConfig("us-proxy2.com", 8080, country="US", city="Los Angeles"),
        ProxyConfig("uk-proxy1.com", 8080, country="UK", city="London"),
        ProxyConfig("jp-proxy1.com", 8080, country="JP", city="Tokyo"),
    ]

    pool = ProxyPool(proxies)
    geo_selector = GeoProxySelector(pool)

    # 查看可用位置
    print("可用地理位置:")
    locations = geo_selector.get_available_locations()
    for location, count in locations.items():
        print(f"  - {location}: {count} 個代理")

    # 按國家選擇
    print("\n按國家選擇代理:")
    for country in ["US", "UK", "JP"]:
        proxy = geo_selector.get_proxy_by_country(country)
        if proxy:
            print(f"  {country}: {proxy.config}")


def example_retry_mechanism():
    """示例5: 重試機制"""
    print("\n" + "=" * 60)
    print("示例5: 失敗重試機制")
    print("=" * 60 + "\n")

    proxies = [
        ProxyConfig(f"proxy{i}.example.com", 8080)
        for i in range(1, 4)
    ]

    pool = ProxyPool(proxies)
    retry_handler = RetryHandler(pool, max_retries=3)

    # 定義一個可能失敗的函數
    def simulate_request(proxy: Proxy) -> str:
        """模擬請求（可能失敗）"""
        print(f"  執行請求...")

        # 60% 成功率
        if random.random() < 0.6:
            return f"成功響應 from {proxy.id}"
        else:
            raise Exception("請求失敗")

    # 使用重試機制執行
    try:
        result = retry_handler.execute_with_retry(simulate_request)
        print(f"\n最終結果: {result}")
    except Exception as e:
        print(f"\n最終失敗: {str(e)}")


def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("Browserbase 代理輪換示例")
    print("=" * 60)

    # 運行所有示例
    example_proxy_pool_basic()
    example_rotation_strategies()
    example_health_check()
    example_geo_selection()
    example_retry_mechanism()

    print("\n" + "=" * 60)
    print("所有示例完成！")
    print("=" * 60 + "\n")

    print("最佳實踐:")
    print("- 使用住宅代理可以提高成功率")
    print("- 定期進行健康檢查")
    print("- 根據目標網站選擇合適的地理位置")
    print("- 實現合理的重試和退避策略")
    print("- 監控代理使用統計，及時更換不良代理")


if __name__ == "__main__":
    main()
