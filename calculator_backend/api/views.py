from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import CalculationHistory
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi as yasg_openapi

# PUBLIC_INTERFACE
@api_view(['GET'])
def health(request):
    """Simple healthcheck endpoint."""
    return Response({"message": "Server is up!"})

# Schema for calculation input
calculation_input_schema = yasg_openapi.Schema(
    type=yasg_openapi.TYPE_OBJECT,
    required=["operand1", "operator", "operand2"],
    properties={
        "operand1": yasg_openapi.Schema(type=yasg_openapi.TYPE_NUMBER, description="First operand"),
        "operator": yasg_openapi.Schema(type=yasg_openapi.TYPE_STRING, enum=["+", "-", "*", "/"], description="Operator"),
        "operand2": yasg_openapi.Schema(type=yasg_openapi.TYPE_NUMBER, description="Second operand"),
    },
    description="Input fields for calculator operation"
)

calculation_output_schema = yasg_openapi.Schema(
    type=yasg_openapi.TYPE_OBJECT,
    properties={
        "result": yasg_openapi.Schema(type=yasg_openapi.TYPE_NUMBER, description="Result of calculation"),
        "operation": yasg_openapi.Schema(type=yasg_openapi.TYPE_STRING, description="Human readable operation"),
    },
    description="Result of calculation"
)

# PUBLIC_INTERFACE
@swagger_auto_schema(
    method='post',
    operation_summary="Perform a calculation",
    operation_description="Accepts two numbers and an operator, performs the calculation, returns the result, and saves the operation to calculation history.",
    request_body=calculation_input_schema,
    responses={200: calculation_output_schema, 400: "Invalid request."},
    tags=['calculator'],
)
@api_view(['POST'])
def calculate(request):
    """
    Performs the arithmetic calculation and stores the history.
    Required POST data: operand1, operator, operand2.
    Returns: result.
    """
    data = request.data
    # Input validation
    operand1 = data.get("operand1")
    operand2 = data.get("operand2")
    operator = data.get("operator")

    # Validate input types and content
    if operand1 is None or operand2 is None or operator not in {"+", "-", "*", "/"}:
        return Response(
            {"detail": "Invalid input. Must include operand1, operand2, and operator (+, -, *, /)."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Perform calculation
    try:
        operand1 = float(operand1)
        operand2 = float(operand2)
    except Exception:
        return Response(
            {"detail": "Operands must be numbers."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        if operator == "+":
            result = operand1 + operand2
        elif operator == "-":
            result = operand1 - operand2
        elif operator == "*":
            result = operand1 * operand2
        elif operator == "/":
            if operand2 == 0:
                return Response({"detail": "Division by zero."}, status=status.HTTP_400_BAD_REQUEST)
            result = operand1 / operand2
        else:
            return Response({"detail": "Operator must be one of +, -, *, /."}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as exc:
        return Response({"detail": f"Error performing calculation: {str(exc)}"}, status=status.HTTP_400_BAD_REQUEST)

    # Save the operation to history
    CalculationHistory.objects.create(
        operand1=operand1, operand2=operand2, operator=operator, result=result
    )

    return Response(
        {
            "result": result,
            "operation": f"{operand1} {operator} {operand2} = {result}"
        }
    )

# PUBLIC_INTERFACE
@swagger_auto_schema(
    method='get',
    operation_summary="Get calculation history",
    operation_description="Returns the most recent calculations performed by all users. Supports optional limit query parameter.",
    manual_parameters=[
        yasg_openapi.Parameter(
            "limit", yasg_openapi.IN_QUERY, description="Maximum number of history records (most recent first)", type=yasg_openapi.TYPE_INTEGER
        ),
    ],
    responses={
        200: yasg_openapi.Response(
            "List of previous calculations",
            yasg_openapi.Schema(
                type=yasg_openapi.TYPE_ARRAY,
                items=yasg_openapi.Schema(
                    type=yasg_openapi.TYPE_OBJECT,
                    properties={
                        "id": yasg_openapi.Schema(type=yasg_openapi.TYPE_INTEGER),
                        "operand1": yasg_openapi.Schema(type=yasg_openapi.TYPE_NUMBER),
                        "operator": yasg_openapi.Schema(type=yasg_openapi.TYPE_STRING),
                        "operand2": yasg_openapi.Schema(type=yasg_openapi.TYPE_NUMBER),
                        "result": yasg_openapi.Schema(type=yasg_openapi.TYPE_NUMBER),
                        "created_at": yasg_openapi.Schema(type=yasg_openapi.FORMAT_DATETIME),
                    }
                )
            )
        )
    },
    tags=['calculator'],
)
@api_view(['GET'])
def history(request):
    """
    Returns the list of previous calculation history.
    Optional query param: limit (default 20)
    """
    limit = request.query_params.get('limit', 20)
    try:
        limit = int(limit)
    except Exception:
        limit = 20
    records = CalculationHistory.objects.order_by('-created_at')[:limit]
    data = [
        {
            "id": rec.id,
            "operand1": rec.operand1,
            "operator": rec.operator,
            "operand2": rec.operand2,
            "result": rec.result,
            "created_at": rec.created_at,
        }
        for rec in records
    ]
    return Response(data)
