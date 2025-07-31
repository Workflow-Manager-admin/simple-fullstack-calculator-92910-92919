from django.db import models

# PUBLIC_INTERFACE
class CalculationHistory(models.Model):
    """
    Stores each calculation performed by a user, including operands, operator, result, and timestamp.
    """
    operand1 = models.FloatField(help_text="First operand")
    operand2 = models.FloatField(help_text="Second operand")
    operator = models.CharField(max_length=5, help_text="Arithmetic operator (+, -, *, /)")
    result = models.FloatField(help_text="Calculation result")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Calculation timestamp")

    def __str__(self):
        return f"{self.operand1} {self.operator} {self.operand2} = {self.result}"
