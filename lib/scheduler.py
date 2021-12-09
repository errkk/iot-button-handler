from datetime import datetime, timedelta
from os import environ

import boto3


ARN = environ["arn_rule"]


class Scheduler:
    boto_client = None
    rule_name = "sleep-timer"

    def get_boto_client(self):
        if not self.boto_client:
            self.boto_client = boto3.client("events", region_name="eu-west-2")
        return self.boto_client

    def enable(self, mins=15) -> datetime:
        dt = datetime.now() + timedelta(minutes=mins)
        schedule_expression = self.get_expression(dt)
        self.get_boto_client().put_rule(
            Name=self.rule_name, State="ENABLED", ScheduleExpression=schedule_expression
        )
        return dt

    def disable(self):
        res = self.get_boto_client().disable_rule(Name=self.rule_name)
        print(res)

    @classmethod
    def get_expression(cls, dt: datetime) -> str:
        return f"cron({dt.minute} {dt.hour} {dt.day} {dt.month} ? {dt.year})"
