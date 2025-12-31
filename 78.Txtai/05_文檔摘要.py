"""
Txtai - 文檔摘要範例

本範例展示：
1. 抽取式摘要
2. 生成式摘要
3. 多文檔摘要
4. 自定義摘要長度
5. 摘要質量評估

安裝：pip install txtai sentence-transformers
"""

from txtai import Summary


# ============================================================================
# 範例 1: 基本文檔摘要
# ============================================================================

def example_1_basic_summary():
    """創建基本的文檔摘要"""
    print("\n" + "="*60)
    print("範例 1: 基本文檔摘要")
    print("="*60)

    # 創建摘要管道
    summary = Summary()

    # 長文本
    text = """
    Artificial intelligence (AI) is intelligence demonstrated by machines, in contrast to the natural
    intelligence displayed by humans and animals. Leading AI textbooks define the field as the study
    of intelligent agents: any device that perceives its environment and takes actions that maximize
    its chance of successfully achieving its goals. Colloquially, the term artificial intelligence
    is often used to describe machines that mimic cognitive functions that humans associate with the
    human mind, such as learning and problem solving. As machines become increasingly capable, tasks
    considered to require intelligence are often removed from the definition of AI, a phenomenon
    known as the AI effect. A quip in Tesler's Theorem says AI is whatever hasn't been done yet.
    """

    # 生成摘要
    result = summary(text)

    print("原文長度:", len(text.split()))
    print("\n摘要:")
    print(result)


# ============================================================================
# 範例 2: 控制摘要長度
# ============================================================================

def example_2_summary_length():
    """控制摘要的長度"""
    print("\n" + "="*60)
    print("範例 2: 控制摘要長度")
    print("="*60)

    summary = Summary()

    text = """
    Machine learning is a subset of artificial intelligence that enables systems to learn and
    improve from experience without being explicitly programmed. It focuses on the development
    of computer programs that can access data and use it to learn for themselves. The process
    of learning begins with observations or data, such as examples, direct experience, or
    instruction, in order to look for patterns in data and make better decisions in the future.
    The primary aim is to allow the computers to learn automatically without human intervention
    or assistance and adjust actions accordingly.
    """

    # 不同長度的摘要
    print("原文長度:", len(text.split()), "詞\n")

    # 短摘要
    short = summary(text, minlength=10, maxlength=20)
    print(f"短摘要 (10-20 詞):\n{short}\n")

    # 中等摘要
    medium = summary(text, minlength=20, maxlength=40)
    print(f"中等摘要 (20-40 詞):\n{medium}\n")


# ============================================================================
# 範例 3: 多文檔摘要
# ============================================================================

def example_3_multi_document():
    """對多個文檔生成摘要"""
    print("\n" + "="*60)
    print("範例 3: 多文檔摘要")
    print("="*60)

    summary = Summary()

    documents = [
        "Deep learning is part of a broader family of machine learning methods based on artificial neural networks.",
        "Neural networks are computing systems inspired by the biological neural networks in animal brains.",
        "Training deep neural networks requires large amounts of data and computational resources.",
    ]

    # 合併文檔並摘要
    combined_text = " ".join(documents)
    result = summary(combined_text)

    print("文檔數量:", len(documents))
    print("\n綜合摘要:")
    print(result)


# ============================================================================
# 範例 4: 批量摘要
# ============================================================================

def example_4_batch_summary():
    """批量處理多個文檔的摘要"""
    print("\n" + "="*60)
    print("範例 4: 批量摘要")
    print("="*60)

    summary = Summary()

    texts = [
        "Python is a high-level programming language known for its simplicity and readability.",
        "JavaScript is primarily used for web development and creating interactive websites.",
        "Java is a popular language for enterprise applications and Android development.",
    ]

    print("批量摘要處理:\n")
    for i, text in enumerate(texts, 1):
        result = summary(text, maxlength=15)
        print(f"{i}. 原文: {text}")
        print(f"   摘要: {result}\n")


# ============================================================================
# 範例 5: 新聞文章摘要
# ============================================================================

def example_5_news_summary():
    """為新聞文章生成摘要"""
    print("\n" + "="*60)
    print("範例 5: 新聞文章摘要")
    print("="*60)

    summary = Summary()

    news_article = """
    Climate Change Summit Reaches Historic Agreement

    World leaders concluded a landmark climate summit today with an unprecedented agreement
    to reduce global carbon emissions by 50% by 2030. The accord, signed by 195 countries,
    includes specific targets for renewable energy adoption and fossil fuel phase-out.
    Developed nations committed to providing $100 billion annually to help developing
    countries transition to clean energy. Environmental groups praised the agreement as
    a crucial step forward, though some activists argue more aggressive action is needed.
    The next summit is scheduled for 2026 to review progress and adjust targets as necessary.
    """

    result = summary(news_article, minlength=20, maxlength=40)

    print("新聞摘要:")
    print(result)


# ============================================================================
# 範例 6-10: 更多摘要應用
# ============================================================================

def example_6_technical_doc():
    """技術文檔摘要"""
    print("\n" + "="*60)
    print("範例 6: 技術文檔摘要")
    print("="*60)

    summary = Summary()

    doc = """
    Docker is a platform for developing, shipping, and running applications in containers.
    Containers allow developers to package applications with all dependencies into a
    standardized unit. Unlike virtual machines, containers share the host OS kernel,
    making them lightweight and fast. Docker provides tools for building container images,
    running containers, and orchestrating multi-container applications. It has become
    essential in modern DevOps practices and cloud deployments.
    """

    result = summary(doc)
    print("技術摘要:", result)


def example_7_research_abstract():
    """研究摘要"""
    print("\n" + "="*60)
    print("範例 7: 研究論文摘要")
    print("="*60)

    summary = Summary()

    abstract = """
    This study investigates the effects of social media usage on mental health among
    adolescents aged 13-18. We conducted a longitudinal study with 500 participants over
    two years, measuring social media engagement and psychological well-being indicators.
    Results show a significant correlation between excessive social media use (>3 hours daily)
    and increased anxiety levels. However, moderate usage combined with positive online
    interactions showed neutral or slightly positive effects. We conclude that the impact
    depends on usage patterns and content type rather than duration alone.
    """

    result = summary(abstract, minlength=25, maxlength=45)
    print("研究摘要:", result)


def example_8_book_summary():
    """書籍章節摘要"""
    print("\n" + "="*60)
    print("範例 8: 書籍章節摘要")
    print("="*60)

    summary = Summary()

    chapter = """
    Chapter 5: The Rise of Agile Development

    Traditional waterfall development methods dominated software engineering for decades,
    but their rigid structure often led to project failures and delays. In the early 2000s,
    a group of software developers created the Agile Manifesto, emphasizing iterative
    development, customer collaboration, and adaptability to change. Agile methodologies
    like Scrum and Kanban gained rapid adoption, transforming how teams build software.
    Today, agile practices extend beyond software development into project management
    across industries.
    """

    result = summary(chapter)
    print("章節摘要:", result)


def example_9_email_summary():
    """郵件摘要"""
    print("\n" + "="*60)
    print("範例 9: 郵件摘要")
    print("="*60)

    summary = Summary()

    email = """
    Hi Team,

    I wanted to update everyone on the Q4 project timeline. After reviewing our current
    progress with stakeholders, we've decided to extend the deadline by two weeks to
    ensure quality. The new features are testing well, but we need additional time for
    security audits and user testing. Please adjust your schedules accordingly. I'll
    send detailed task assignments by end of day tomorrow.

    Best regards,
    Sarah
    """

    result = summary(email, maxlength=20)
    print("郵件摘要:", result)


def example_10_blog_summary():
    """博客文章摘要"""
    print("\n" + "="*60)
    print("範例 10: 博客文章摘要")
    print("="*60)

    summary = Summary()

    blog = """
    5 Tips for Better Code Reviews

    Code reviews are essential for maintaining code quality, but they can be time-consuming
    if not done efficiently. First, keep pull requests small and focused on a single feature.
    Second, use automated tools to catch simple issues before human review. Third, provide
    constructive feedback focusing on the code, not the person. Fourth, establish clear
    review guidelines and coding standards. Finally, make reviews a collaborative learning
    opportunity for both reviewer and author. Following these practices will make your
    code reviews more effective and less stressful.
    """

    result = summary(blog, minlength=15, maxlength=30)
    print("博客摘要:", result)


# ============================================================================
# 主程式
# ============================================================================

def main():
    """運行所有範例"""
    print("\n" + "="*60)
    print("📝 Txtai - 文檔摘要範例")
    print("="*60)

    example_1_basic_summary()
    example_2_summary_length()
    example_3_multi_document()
    example_4_batch_summary()
    example_5_news_summary()
    example_6_technical_doc()
    example_7_research_abstract()
    example_8_book_summary()
    example_9_email_summary()
    example_10_blog_summary()

    print("\n" + "="*60)
    print("✓ 所有文檔摘要範例完成！")
    print("="*60)


if __name__ == '__main__':
    main()
