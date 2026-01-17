from enum import Enum
from datetime import datetime


class AlarmType(Enum):
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class Alarm:
    def __init__(self, source: str, message: str, alarm_type: AlarmType):
        self.time = datetime.now()
        self.source = source
        self.message = message
        self.alarm_type = alarm_type
        self.active = True


class AlarmsMenager:
    def __init__(self):
        self.alarms = []

    # ----------------------------
    # PODSTAWOWE OPERACJE
    # ----------------------------

    def raise_alarm(self, source: str, message: str, alarm_type: AlarmType):
        if not self._exists_active(source, message, alarm_type):
            self.alarms.append(Alarm(source, message, alarm_type))

    def clear_alarm(self, source: str, message: str, alarm_type: AlarmType):
        for alarm in reversed(self.alarms):
            if (
                alarm.active
                and alarm.source == source
                and alarm.message == message
                and alarm.alarm_type == alarm_type
            ):
                alarm.active = False
                return

    def clear_all(self):
        for alarm in self.alarms:
            alarm.active = False

    def active_alarms(self):
        return [alarm for alarm in self.alarms if alarm.active]

    # ----------------------------
    # POMOCNICZE
    # ----------------------------

    def _exists_active(self, source: str, message: str, alarm_type: AlarmType) -> bool:
        return any(
            alarm.active
            and alarm.source == source
            and alarm.message == message
            and alarm.alarm_type == alarm_type
            for alarm in self.alarms
        )
