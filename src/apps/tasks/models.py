from piccolo.columns import Boolean, Serial, Text, Timestamp, Varchar
from piccolo.table import Table


class Task(Table):
    id: Serial
    name = Varchar(length=200)
    description = Text(null=True)
    completed = Boolean(default=False)
    created_at = Timestamp(auto_now_add=True)
