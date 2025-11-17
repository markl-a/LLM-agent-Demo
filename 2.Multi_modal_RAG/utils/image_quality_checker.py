"""
圖像質量評估工具

功能：
1. 檢查圖像質量（解析度、清晰度、大小）
2. 分類圖像類型（圖表、流程圖、照片等）
3. 評估圖像對 RAG 的價值
4. 提供優化建議
"""

import os
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import argparse
import json

try:
    from PIL import Image
    import numpy as np
    import cv2
except ImportError:
    print("請安裝依賴：pip install Pillow numpy opencv-python")
    raise


class ImageType(Enum):
    """圖像類型"""
    CHART = "chart"           # 圖表
    DIAGRAM = "diagram"       # 示意圖
    FLOWCHART = "flowchart"   # 流程圖
    TABLE = "table"           # 表格圖像
    PHOTO = "photo"           # 照片
    SCREENSHOT = "screenshot" # 截圖
    DECORATIVE = "decorative" # 裝飾性圖片
    UNKNOWN = "unknown"


class QualityLevel(Enum):
    """質量等級"""
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"
    UNUSABLE = "unusable"


@dataclass
class ImageQualityReport:
    """圖像質量報告"""
    file_path: str
    width: int
    height: int
    file_size: int  # 字節
    image_type: ImageType
    quality_level: QualityLevel
    sharpness_score: float  # 0-1
    text_density: float     # 0-1
    color_variance: float   # 0-1
    rag_value: float        # 對 RAG 的價值評分 0-1
    recommendations: List[str]
    issues: List[str]


class ImageQualityChecker:
    """圖像質量檢查器"""

    def __init__(self):
        """初始化檢查器"""
        pass

    def check_image(self, image_path: str) -> ImageQualityReport:
        """
        檢查單個圖像

        Args:
            image_path: 圖像文件路徑

        Returns:
            ImageQualityReport: 質量報告
        """
        # 加載圖像
        pil_image = Image.open(image_path)
        cv_image = cv2.imread(image_path)

        # 基本資訊
        width, height = pil_image.size
        file_size = os.path.getsize(image_path)

        # 質量評估
        sharpness = self._calculate_sharpness(cv_image)
        text_density = self._estimate_text_density(cv_image)
        color_variance = self._calculate_color_variance(cv_image)

        # 圖像類型分類
        image_type = self._classify_image_type(
            pil_image, sharpness, text_density, color_variance
        )

        # 質量等級
        quality_level = self._determine_quality_level(
            width, height, sharpness, file_size
        )

        # RAG 價值評分
        rag_value = self._calculate_rag_value(
            image_type, quality_level, text_density
        )

        # 問題和建議
        issues = self._identify_issues(
            width, height, file_size, sharpness, quality_level
        )
        recommendations = self._generate_recommendations(
            issues, image_type, quality_level
        )

        return ImageQualityReport(
            file_path=image_path,
            width=width,
            height=height,
            file_size=file_size,
            image_type=image_type,
            quality_level=quality_level,
            sharpness_score=sharpness,
            text_density=text_density,
            color_variance=color_variance,
            rag_value=rag_value,
            recommendations=recommendations,
            issues=issues
        )

    def check_directory(self, directory: str) -> List[ImageQualityReport]:
        """
        檢查目錄中的所有圖像

        Args:
            directory: 目錄路徑

        Returns:
            List[ImageQualityReport]: 質量報告列表
        """
        reports = []

        # 支持的圖像格式
        supported_formats = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}

        # 遍歷目錄
        for file_path in Path(directory).rglob('*'):
            if file_path.suffix.lower() in supported_formats:
                try:
                    report = self.check_image(str(file_path))
                    reports.append(report)
                    print(f"✓ {file_path.name}: {report.quality_level.value}")
                except Exception as e:
                    print(f"✗ {file_path.name}: 處理失敗 - {str(e)}")

        return reports

    def _calculate_sharpness(self, image: np.ndarray) -> float:
        """
        計算圖像清晰度（使用 Laplacian 方差）

        Args:
            image: OpenCV 圖像

        Returns:
            float: 清晰度評分 (0-1)
        """
        # 轉換為灰度圖
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # 計算 Laplacian 方差
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()

        # 歸一化到 0-1
        # 通常 > 100 被認為是清晰的
        normalized = min(laplacian_var / 500, 1.0)

        return normalized

    def _estimate_text_density(self, image: np.ndarray) -> float:
        """
        估計圖像中的文本密度

        Args:
            image: OpenCV 圖像

        Returns:
            float: 文本密度 (0-1)
        """
        # 轉換為灰度圖
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # 邊緣檢測
        edges = cv2.Canny(gray, 50, 150)

        # 計算邊緣密度（文本通常有很多邊緣）
        edge_density = np.sum(edges > 0) / edges.size

        return min(edge_density * 5, 1.0)  # 放大並限制到 0-1

    def _calculate_color_variance(self, image: np.ndarray) -> float:
        """
        計算顏色方差（用於判斷圖像複雜度）

        Args:
            image: OpenCV 圖像

        Returns:
            float: 顏色方差 (0-1)
        """
        # 計算每個顏色通道的標準差
        std_b = np.std(image[:, :, 0])
        std_g = np.std(image[:, :, 1])
        std_r = np.std(image[:, :, 2])

        avg_std = (std_b + std_g + std_r) / 3

        # 歸一化（標準差通常在 0-128 範圍）
        normalized = min(avg_std / 128, 1.0)

        return normalized

    def _classify_image_type(
        self,
        image: Image.Image,
        sharpness: float,
        text_density: float,
        color_variance: float
    ) -> ImageType:
        """
        分類圖像類型

        Args:
            image: PIL 圖像
            sharpness: 清晰度
            text_density: 文本密度
            color_variance: 顏色方差

        Returns:
            ImageType: 圖像類型
        """
        # 基於啟發式規則分類

        # 裝飾性圖片：顏色方差高，文本密度低
        if color_variance > 0.7 and text_density < 0.2:
            return ImageType.DECORATIVE

        # 圖表：文本密度中等，顏色方差低（通常是簡單顏色）
        if 0.2 < text_density < 0.5 and color_variance < 0.5:
            return ImageType.CHART

        # 流程圖/示意圖：文本密度高，清晰
        if text_density > 0.4 and sharpness > 0.5:
            return ImageType.DIAGRAM

        # 截圖：清晰度高，文本密度高
        if sharpness > 0.7 and text_density > 0.5:
            return ImageType.SCREENSHOT

        # 照片：顏色方差高，文本密度低
        if color_variance > 0.6:
            return ImageType.PHOTO

        return ImageType.UNKNOWN

    def _determine_quality_level(
        self,
        width: int,
        height: int,
        sharpness: float,
        file_size: int
    ) -> QualityLevel:
        """
        判斷質量等級

        Args:
            width: 寬度
            height: 高度
            sharpness: 清晰度
            file_size: 文件大小

        Returns:
            QualityLevel: 質量等級
        """
        # 計算總像素
        total_pixels = width * height

        # 評分規則
        score = 0

        # 解析度評分
        if total_pixels >= 1920 * 1080:  # Full HD+
            score += 3
        elif total_pixels >= 1280 * 720:  # HD
            score += 2
        elif total_pixels >= 640 * 480:   # VGA
            score += 1

        # 清晰度評分
        if sharpness >= 0.7:
            score += 3
        elif sharpness >= 0.5:
            score += 2
        elif sharpness >= 0.3:
            score += 1

        # 文件大小評分（太小可能過度壓縮）
        if file_size >= 100 * 1024:  # > 100KB
            score += 1

        # 判定等級
        if score >= 6:
            return QualityLevel.EXCELLENT
        elif score >= 4:
            return QualityLevel.GOOD
        elif score >= 2:
            return QualityLevel.ACCEPTABLE
        elif score >= 1:
            return QualityLevel.POOR
        else:
            return QualityLevel.UNUSABLE

    def _calculate_rag_value(
        self,
        image_type: ImageType,
        quality_level: QualityLevel,
        text_density: float
    ) -> float:
        """
        計算圖像對 RAG 的價值

        Args:
            image_type: 圖像類型
            quality_level: 質量等級
            text_density: 文本密度

        Returns:
            float: 價值評分 (0-1)
        """
        # 基礎評分（根據圖像類型）
        type_scores = {
            ImageType.CHART: 0.9,
            ImageType.DIAGRAM: 0.8,
            ImageType.FLOWCHART: 0.8,
            ImageType.TABLE: 0.9,
            ImageType.SCREENSHOT: 0.6,
            ImageType.PHOTO: 0.3,
            ImageType.DECORATIVE: 0.1,
            ImageType.UNKNOWN: 0.5,
        }

        base_score = type_scores.get(image_type, 0.5)

        # 質量調整
        quality_multipliers = {
            QualityLevel.EXCELLENT: 1.0,
            QualityLevel.GOOD: 0.9,
            QualityLevel.ACCEPTABLE: 0.7,
            QualityLevel.POOR: 0.4,
            QualityLevel.UNUSABLE: 0.1,
        }

        quality_mult = quality_multipliers.get(quality_level, 0.5)

        # 文本密度調整（更多文本通常意味著更多資訊）
        text_mult = 0.7 + (text_density * 0.3)

        # 最終評分
        final_score = base_score * quality_mult * text_mult

        return min(final_score, 1.0)

    def _identify_issues(
        self,
        width: int,
        height: int,
        file_size: int,
        sharpness: float,
        quality_level: QualityLevel
    ) -> List[str]:
        """識別圖像問題"""
        issues = []

        # 解析度問題
        if width < 400 or height < 300:
            issues.append("解析度過低（< 400x300）")

        # 清晰度問題
        if sharpness < 0.3:
            issues.append("圖像模糊")

        # 文件大小問題
        if file_size < 10 * 1024:
            issues.append("文件過小，可能過度壓縮")
        elif file_size > 5 * 1024 * 1024:
            issues.append("文件過大（> 5MB），會增加處理成本")

        # 寬高比問題
        aspect_ratio = width / height if height > 0 else 0
        if aspect_ratio > 5 or aspect_ratio < 0.2:
            issues.append("寬高比異常")

        return issues

    def _generate_recommendations(
        self,
        issues: List[str],
        image_type: ImageType,
        quality_level: QualityLevel
    ) -> List[str]:
        """生成優化建議"""
        recommendations = []

        # 基於問題的建議
        if "解析度過低" in issues:
            recommendations.append("使用更高解析度的原始圖像")

        if "圖像模糊" in issues:
            recommendations.append("使用清晰度更高的圖像源")

        if "文件過小" in issues:
            recommendations.append("減少壓縮，使用更高質量的導出設置")

        if "文件過大" in issues:
            recommendations.append("適當壓縮圖像（推薦 1024x1024 以下）")

        # 基於類型的建議
        if image_type == ImageType.DECORATIVE:
            recommendations.append("考慮跳過此圖像以節省成本（裝飾性）")

        elif image_type == ImageType.CHART:
            recommendations.append("確保圖表清晰，文字可讀")
            recommendations.append("考慮提取圖表數據為結構化格式")

        elif image_type == ImageType.PHOTO:
            recommendations.append("評估照片是否必要，照片的 RAG 價值較低")

        # 基於質量的建議
        if quality_level in [QualityLevel.POOR, QualityLevel.UNUSABLE]:
            recommendations.append("⚠️ 圖像質量太差，建議重新獲取高質量版本")

        return recommendations

    def generate_summary_report(
        self,
        reports: List[ImageQualityReport],
        output_file: Optional[str] = None
    ) -> Dict:
        """
        生成總結報告

        Args:
            reports: 質量報告列表
            output_file: 輸出文件路徑（可選）

        Returns:
            Dict: 總結報告
        """
        total = len(reports)

        # 統計質量等級分佈
        quality_dist = {}
        for level in QualityLevel:
            count = sum(1 for r in reports if r.quality_level == level)
            quality_dist[level.value] = {
                "count": count,
                "percentage": f"{count/total*100:.1f}%" if total > 0 else "0%"
            }

        # 統計圖像類型分佈
        type_dist = {}
        for img_type in ImageType:
            count = sum(1 for r in reports if r.image_type == img_type)
            type_dist[img_type.value] = {
                "count": count,
                "percentage": f"{count/total*100:.1f}%" if total > 0 else "0%"
            }

        # RAG 價值統計
        high_value = sum(1 for r in reports if r.rag_value >= 0.7)
        medium_value = sum(1 for r in reports if 0.4 <= r.rag_value < 0.7)
        low_value = sum(1 for r in reports if r.rag_value < 0.4)

        # 常見問題
        all_issues = []
        for r in reports:
            all_issues.extend(r.issues)

        from collections import Counter
        issue_counts = Counter(all_issues)

        summary = {
            "total_images": total,
            "quality_distribution": quality_dist,
            "type_distribution": type_dist,
            "rag_value_distribution": {
                "high_value": {"count": high_value, "percentage": f"{high_value/total*100:.1f}%"},
                "medium_value": {"count": medium_value, "percentage": f"{medium_value/total*100:.1f}%"},
                "low_value": {"count": low_value, "percentage": f"{low_value/total*100:.1f}%"},
            },
            "common_issues": [
                {"issue": issue, "count": count}
                for issue, count in issue_counts.most_common(5)
            ],
            "recommendations": self._generate_overall_recommendations(reports)
        }

        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)

        return summary

    def _generate_overall_recommendations(
        self,
        reports: List[ImageQualityReport]
    ) -> List[str]:
        """生成整體建議"""
        recommendations = []

        # 低質量圖像比例
        poor_quality = sum(
            1 for r in reports
            if r.quality_level in [QualityLevel.POOR, QualityLevel.UNUSABLE]
        )
        if poor_quality / len(reports) > 0.2:
            recommendations.append(
                f"⚠️ {poor_quality/len(reports)*100:.0f}% 的圖像質量較差，"
                "建議檢查圖像源"
            )

        # 裝飾性圖像比例
        decorative = sum(1 for r in reports if r.image_type == ImageType.DECORATIVE)
        if decorative / len(reports) > 0.3:
            recommendations.append(
                f"建議跳過 {decorative} 個裝飾性圖像以節省成本"
            )

        # 文件大小問題
        large_files = sum(1 for r in reports if r.file_size > 5 * 1024 * 1024)
        if large_files > 0:
            recommendations.append(
                f"{large_files} 個圖像文件過大，建議壓縮"
            )

        return recommendations


def print_summary_report(summary: Dict):
    """打印總結報告"""
    print("\n" + "=" * 60)
    print("圖像質量總結報告")
    print("=" * 60)

    print(f"\n總圖像數：{summary['total_images']}")

    print("\n質量分佈：")
    for level, data in summary['quality_distribution'].items():
        print(f"  {level}: {data['count']} ({data['percentage']})")

    print("\n類型分佈：")
    for img_type, data in summary['type_distribution'].items():
        print(f"  {img_type}: {data['count']} ({data['percentage']})")

    print("\nRAG 價值分佈：")
    for level, data in summary['rag_value_distribution'].items():
        print(f"  {level}: {data['count']} ({data['percentage']})")

    print("\n常見問題：")
    for item in summary['common_issues']:
        print(f"  {item['issue']}: {item['count']} 次")

    print("\n整體建議：")
    for rec in summary['recommendations']:
        print(f"  • {rec}")

    print("\n" + "=" * 60)


def main():
    """命令行工具"""
    parser = argparse.ArgumentParser(description="圖像質量評估工具")
    parser.add_argument("input", help="圖像文件或目錄路徑")
    parser.add_argument("--output", help="輸出報告文件路徑")
    parser.add_argument("--detailed", action="store_true", help="顯示詳細報告")

    args = parser.parse_args()

    checker = ImageQualityChecker()

    # 檢查輸入
    input_path = Path(args.input)

    if input_path.is_file():
        # 單個文件
        report = checker.check_image(str(input_path))
        print(f"\n圖像：{input_path.name}")
        print(f"類型：{report.image_type.value}")
        print(f"質量：{report.quality_level.value}")
        print(f"RAG 價值：{report.rag_value:.2f}")
        print(f"解析度：{report.width}x{report.height}")
        print(f"清晰度：{report.sharpness_score:.2f}")

        if report.issues:
            print("\n問題：")
            for issue in report.issues:
                print(f"  • {issue}")

        if report.recommendations:
            print("\n建議：")
            for rec in report.recommendations:
                print(f"  • {rec}")

    elif input_path.is_dir():
        # 目錄
        reports = checker.check_directory(str(input_path))

        if reports:
            summary = checker.generate_summary_report(reports, args.output)
            print_summary_report(summary)

            if args.detailed:
                print("\n詳細報告：")
                for report in reports:
                    print(f"\n{report.file_path}:")
                    print(f"  類型：{report.image_type.value}")
                    print(f"  質量：{report.quality_level.value}")
                    print(f"  RAG 價值：{report.rag_value:.2f}")
    else:
        print(f"錯誤：{input_path} 不存在")


if __name__ == "__main__":
    main()
