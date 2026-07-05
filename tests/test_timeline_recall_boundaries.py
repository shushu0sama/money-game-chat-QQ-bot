from datetime import datetime
from pathlib import Path
from tempfile import NamedTemporaryFile
from unittest.mock import Mock

import nonebot_plugin_personal_companion as companion_plugin
from nonebot_plugin_personal_companion.memory import BEIJING_TZ, MemoryStore
from nonebot_plugin_personal_companion.proactive import ProactiveChat


def make_store():
    tmp = NamedTemporaryFile(suffix=".db", delete=False)
    db_path = tmp.name
    tmp.close()
    return MemoryStore(db_path=db_path), db_path


def cleanup_store(store, db_path):
    del store
    for ext in ("", "-wal", "-shm"):
        path = Path(db_path + ext) if ext else Path(db_path)
        try:
            path.unlink()
        except OSError:
            pass


def test_keyword_timeline_retrieval_excludes_completed_history_by_default():
    store, db_path = make_store()
    try:
        store.add_timeline_entry(1, "2026-04-22", "用户宣布自己已经拥有幸福了", tags=["名场面"], status="done")
        store.add_timeline_entry(1, "2026-07-01", "用户准备作品集", tags=["作品集"], status="planned")

        default = store.retrieve_timeline_entries(["幸福", "作品集"], user_id=1, limit=5)
        explicit_history = store.retrieve_timeline_entries(["幸福"], user_id=1, limit=5, include_history=True)

        assert [item["content"] for item in default] == ["用户准备作品集"]
        assert [item["content"] for item in explicit_history] == ["用户宣布自己已经拥有幸福了"]
    finally:
        cleanup_store(store, db_path)


def test_recent_timeline_entries_exclude_old_completed_events():
    store, db_path = make_store()
    try:
        store.add_timeline_entry(1, "2026-04-22", "用户宣布自己已经拥有幸福了", tags=["名场面"], status="done")
        store.add_timeline_entry(1, datetime.now(BEIJING_TZ).strftime("%Y-%m-%d"), "用户今天准备作品集", tags=["作品集"], status="planned")

        entries = store.get_recent_timeline_entries(1, limit=5)

        assert [item["content"] for item in entries] == ["用户今天准备作品集"]
    finally:
        cleanup_store(store, db_path)


def test_turn_timeline_retrieval_only_includes_history_for_explicit_date_query():
    store, db_path = make_store()
    old_store = companion_plugin.memory_store
    try:
        companion_plugin.memory_store = store
        store.add_timeline_entry(1, "2026-04-22", "用户宣布自己已经拥有幸福了", tags=["名场面"], status="done")

        implicit = companion_plugin._retrieve_timeline_for_turn("幸福名场面", ["幸福"], user_id=1)
        explicit = companion_plugin._retrieve_timeline_for_turn("4月22日发生了什么", ["幸福"], user_id=1)

        assert implicit == []
        assert [item["content"] for item in explicit] == ["用户宣布自己已经拥有幸福了"]
    finally:
        companion_plugin.memory_store = old_store
        cleanup_store(store, db_path)


def test_proactive_prompt_excludes_old_completed_timeline_events():
    store, db_path = make_store()
    try:
        store.add_timeline_entry(1, "2026-04-22", "用户宣布自己已经拥有幸福了", event_time="17:14", status="done")
        config = Mock()
        chat = ProactiveChat(store, Mock(), config, kb=None)

        prompt = chat._build_proactive_prompt(user_id=1)

        assert "用户宣布自己已经拥有幸福了" not in prompt
    finally:
        cleanup_store(store, db_path)
