from fastapi import status
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
from decimal import Decimal
from datetime import datetime, date


def convert_decimals(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimals(item) for item in obj]
    else:
        return obj

def convert_non_serializable(obj):
    """
    Convierte tipos no JSON serializables a tipos serializables.
    """
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: convert_non_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_non_serializable(item) for item in obj]
    elif hasattr(obj, '__dict__'):
        # Para objetos que se pueden convertir a dict
        return convert_non_serializable(obj.__dict__)
    else:
        return obj


def success_response(data: Any, message: str, status_code: int = 200) -> JSONResponse:
    """
    Genera una respuesta JSON exitosa.
    """
    # Convierte todos los Decimal a float antes de serializar
    cleaned_data = convert_non_serializable(data)

    return JSONResponse(
        status_code=status_code,
        content={"success": True, "message": message, "data": cleaned_data},
    )


def error_response(message: str, status_code: int = 400) -> JSONResponse:
    """
    Genera una respuesta JSON de error.
    """
    return JSONResponse(
        status_code=status_code, content={"success": False, "message": message}
    )


def validation_error_response(errors: List[Dict[str, Any]]) -> JSONResponse:
    """
    Genera una respuesta de error de validación para parámetros faltantes o incorrectos.
    """
    detailed_errors = []

    for err in errors:
        field_name = (
            ".".join(str(loc) for loc in err["loc"][1:])
            if len(err["loc"]) > 1
            else str(err["loc"][-1])
        )
        error_type = err.get("type", "unknown")
        error_msg = err.get("msg", "Error de validación")

        # Crear mensaje más descriptivo según el tipo de error
        # Compatibilidad con Pydantic v1 y v2
        if error_type in ["missing", "value_error.missing"]:
            detailed_errors.append(f"El campo '{field_name}' es obligatorio")
        elif error_type in ["string_too_long", "value_error.str.max_length"]:
            ctx = err.get("ctx", {})
            max_length = ctx.get("max_length", ctx.get("limit_value", "N/A"))
            detailed_errors.append(
                f"El campo '{field_name}' excede la longitud máxima de {max_length} caracteres"
            )
        elif error_type in ["string_too_short", "value_error.str.min_length"]:
            ctx = err.get("ctx", {})
            min_length = ctx.get("min_length", ctx.get("limit_value", "N/A"))
            detailed_errors.append(
                f"El campo '{field_name}' debe tener al menos {min_length} caracteres"
            )
        elif error_type in [
            "greater_than",
            "value_error.number.not_gt",
            "value_error.number.not_ge",
        ]:
            ctx = err.get("ctx", {})
            limit = ctx.get("gt", ctx.get("ge", ctx.get("limit_value", "N/A")))
            detailed_errors.append(
                f"El campo '{field_name}' debe ser mayor que {limit}"
            )
        elif error_type in [
            "less_than",
            "value_error.number.not_lt",
            "value_error.number.not_le",
        ]:
            ctx = err.get("ctx", {})
            limit = ctx.get("lt", ctx.get("le", ctx.get("limit_value", "N/A")))
            detailed_errors.append(
                f"El campo '{field_name}' debe ser menor que {limit}"
            )
        elif error_type in ["int_type", "type_error.integer"]:
            detailed_errors.append(f"El campo '{field_name}' debe ser un número entero")
        elif error_type in ["float_type", "type_error.float"]:
            detailed_errors.append(
                f"El campo '{field_name}' debe ser un número decimal"
            )
        elif error_type in ["string_type", "type_error.str"]:
            detailed_errors.append(
                f"El campo '{field_name}' debe ser una cadena de texto"
            )
        elif error_type in ["bool_type", "type_error.bool"]:
            detailed_errors.append(
                f"El campo '{field_name}' debe ser verdadero o falso"
            )
        else:
            # Para otros tipos de error, usar el mensaje original
            detailed_errors.append(f"Campo '{field_name}': {error_msg}")

    # Crear mensaje principal
    if len(detailed_errors) == 1:
        main_message = "Error de validación"
    else:
        main_message = f"Se encontraron {len(detailed_errors)} errores de validación"

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": main_message,
            "errors": detailed_errors,
            # "details": errors,  # Incluir errores originales para debugging
        },
    )
