"""
添加缺失的数据库索引以优化查询性能
运行：python add_indexes.py
"""
from sqlalchemy import create_engine, text
from database import DATABASE_URL

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    # 检查 SQLite 版本
    version = conn.execute(text("SELECT sqlite_version()")).scalar()
    print(f"SQLite 版本: {version}")
    
    # 添加缺失的索引
    indexes = [
        ("idx_papers_journal_id", "papers", "journal_id"),
        ("idx_user_papers_user_id", "user_papers", "user_id"),
        ("idx_user_papers_paper_id", "user_papers", "paper_id"),
        ("idx_papers_fetched_at", "papers", "fetched_at"),
    ]
    
    for idx_name, table, column in indexes:
        try:
            conn.execute(text(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table}({column})"))
            print(f"✅ 已添加索引: {idx_name}")
        except Exception as e:
            print(f"❌ 添加索引失败 {idx_name}: {e}")
    
    conn.commit()
    
    # 更新统计信息（帮助查询优化器）
    conn.execute(text("ANALYZE"))
    print("\n✅ 已更新数据库统计信息 (ANALYZE)")
    
    # 显示所有索引
    print("\n=== 所有索引 ===")
    for table in ["journals", "papers", "user_papers", "users"]:
        try:
            result = conn.execute(text(f"PRAGMA index_list({table})"))
            print(f"\n{table}:")
            for row in result:
                print(f"  {row}")
        except:
            pass
