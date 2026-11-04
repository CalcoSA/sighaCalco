from decimal import Decimal, InvalidOperation
from datetime import date, datetime
from openpyxl import load_workbook
from unicodedata import normalize
from io import BytesIO
import re

class LoanImportExcelReader:

    HEADERS = {
        "documento": "employeeDocumentNumber",
        "nombre": "employeeFullName",
        "prestamo (si para prestamo, no para emolumento)": "isLoan",
        "concepto sinergy": "conceptCode",
        "plan deduccion": "IdDeductionPlan",
        "documento cruzado": "crossDocument",
        "valor de prestamo": "loanAmount",
        "valor de emolumento": "serviceValue",
        "numero de cuotas": "numberInstallments",
        "cuotas pagadas": "paidInstallments",
        "valor cuota": "installmentValue",
        "fecha inicio descuento": "startDiscountDate",
    }

    def read(self, content: bytes,) -> list[dict]:
        workbook = load_workbook(BytesIO(content), read_only=True, data_only=True,)
        worksheet = workbook.active
        headerRow, columns = self._findHeaders(worksheet)

        records: list[dict] = []

        for rowNumber in range(headerRow + 1, worksheet.max_row + 1,):

            rawValues = {
                key: worksheet.cell(
                    rowNumber,
                    columnNumber,
                ).value
                for key, columnNumber
                in columns.items()
            }

            if all(
                value is None
                or str(value).strip() == ""
                for value in rawValues.values()
            ):
                continue

            try:

                documentNumber = (self._normalizeDocument(rawValues[ "employeeDocumentNumber" ]))

                if not documentNumber:
                    raise ValueError("El Documento es obligatorio.")

                fullName = str(
                    rawValues[
                        "employeeFullName"
                    ]
                    or ""
                ).strip()

                if not fullName:
                    raise ValueError("El Nombre es obligatorio.")

                records.append(
                    {
                        "rowNumber": rowNumber,
                        "employeeDocumentNumber": documentNumber,
                        "employeeFullName": fullName,
                        "isLoan": self._parseBoolean(rawValues["isLoan"]),
                        "conceptCode": self._normalizeConceptCode(rawValues["conceptCode"]),
                        "IdDeductionPlan": self._parseInteger(rawValues["IdDeductionPlan"], required=True,),
                        "crossDocument": self._optionalText(rawValues["crossDocument"]),
                        "loanAmount": self._parseDecimal(rawValues["loanAmount"]),
                        "serviceValue": self._parseDecimal(rawValues["serviceValue"]),
                        "numberInstallments": self._parseInteger(rawValues["numberInstallments"]),
                        "paidInstallments": self._parseInteger(rawValues["paidInstallments"]),
                        "installmentValue": self._parseDecimal(rawValues["installmentValue"]),
                        "startDiscountDate": self._parseDate(rawValues["startDiscountDate"]),
                    }
                )

            except ValueError as exception:
                raise ValueError(f"Fila {rowNumber}: " f"{str(exception)}") from exception

        return records

    def _findHeaders(self, worksheet,):
        maxRows = min(worksheet.max_row, 10,)

        for rowNumber in range(1, maxRows + 1,):
            columns = {}

            for columnNumber in range(1, worksheet.max_column + 1,):

                value = worksheet.cell(rowNumber, columnNumber,).value
                header = self._normalizeHeader(value)
                fieldName = self.HEADERS.get(header)

                if fieldName:
                    columns[fieldName] = (columnNumber)

            requiredFields = set(self.HEADERS.values())

            if requiredFields.issubset(columns.keys()):
                return (rowNumber, columns,)

        raise ValueError("El archivo no contiene todas las columnas requeridas.")

    def _normalizeHeader(self, value,) -> str:

        if value is None:
            return ""

        value = (str(value).strip().lower())

        value = "".join(
            character
            for character in normalize(
                "NFD",
                value,
            )
            if ord(character) < 128
        )

        return re.sub(r"\s+", " ", value,)

    def _normalizeDocument(self, value,) -> str:

        if value is None:
            return ""

        if (isinstance(value, float) and value.is_integer()):
            value = int(value)

        return re.sub(r"\D", "", str(value),)

    def _normalizeConceptCode(self, value,) -> str:

        if value is None:
            raise ValueError("Concepto Sinergy es obligatorio.")

        if isinstance(value, (int, float, Decimal),):

            decimalValue = Decimal(str(value))

            if (decimalValue != decimalValue.to_integral_value()):
                raise ValueError("Concepto Sinergy no es válido.")

            return str(int(decimalValue)).zfill(4)

        value = str(value).strip()

        if not value:
            raise ValueError("Concepto Sinergy es obligatorio.")

        if value.isdigit():
            return value.zfill(4)

        return value

    def _parseBoolean(self, value,) -> bool:
        value = self._normalizeHeader(value)

        if value in {
            "si",
            "s",
            "1",
            "yes",
        }:
            return True

        if value in {
            "no",
            "n",
            "0",
        }:
            return False

        raise ValueError("Préstamo debe contener Si o No.")

    def _parseInteger(self, value, required: bool = False,) -> int | None:

        if (value is None or str(value).strip() == ""):

            if required:
                raise ValueError("El valor es obligatorio.")

            return None

        try:
            decimalValue = Decimal(str(value))

        except InvalidOperation:

            raise ValueError(f"Valor entero inválido: {value}.")

        if (decimalValue != decimalValue.to_integral_value()):
            raise ValueError(f"{value} debe ser un número entero.")

        return int(decimalValue)

    def _parseDecimal(self, value,) -> Decimal | None:

        if value is None:
            return None

        if str(value).strip() == "":
            return None

        if isinstance(value, (int, float, Decimal),):
            return Decimal(str(value)).quantize(Decimal("0.01"))

        value = (str(value).strip().replace("$", "").replace(" ", ""))

        if ("." in value and "," in value):
            if (value.rfind(",") > value.rfind(".")):
                value = (value.replace(".", "").replace(",", "."))
            else:
                value = value.replace(",", "",)
        elif "," in value:
            value = value.replace(",", ".",)

        try:
            return Decimal(value).quantize(Decimal("0.01"))

        except InvalidOperation:
            raise ValueError(f"Valor monetario inválido: {value}.")

    def _parseDate(self, value,) -> date:

        if isinstance(value, datetime,):
            return value.date()

        if isinstance(value, date,):
            return value

        if value is None:
            raise ValueError("Fecha Inicio descuento es obligatoria.")

        value = str(value).strip()

        for dateFormat in ("%d/%m/%Y", "%Y-%m-%d",):

            try:

                return datetime.strptime(value, dateFormat,).date()

            except ValueError:
                continue

        raise ValueError("Fecha Inicio descuento no tiene un formato válido.")

    def _optionalText(self, value,) -> str | None:

        if value is None:
            return None

        value = str(value).strip()

        return value or None