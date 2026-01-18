from alarm_list import AlarmsMenager, AlarmType

def test_warning_not_duplicated():
    m = AlarmsMenager()
    for _ in range(1000):
        m.raise_alarm("Zbiornik 1", "Temperatura powyżej 90", AlarmType.WARNING)

    assert len(m.active_alarms()) == 1
