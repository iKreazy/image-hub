from django.db import models


class CommandExecution(models.Model):
    command_name = models.CharField(max_length=255, unique=True)
    executed_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.command_name} - {self.executed_at}"
