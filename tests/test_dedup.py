from datetime import datetime, timezone

from app.services.jobs import make_dedup_key


def test_dedup_key_buckets_by_window():
    t0 = datetime(2026, 9, 16, 12, 0, tzinfo=timezone.utc)
    t1 = datetime(2026, 9, 16, 12, 4, tzinfo=timezone.utc)
    t2 = datetime(2026, 9, 16, 12, 6, tzinfo=timezone.utc)
    k0 = make_dedup_key("cam-1", "MH12AB1234", "Helmet", t0, 300)
    k1 = make_dedup_key("cam-1", "MH12AB1234", "Helmet", t1, 300)
    k2 = make_dedup_key("cam-1", "MH12AB1234", "Helmet", t2, 300)
    assert k0 == k1
    assert k0 != k2
