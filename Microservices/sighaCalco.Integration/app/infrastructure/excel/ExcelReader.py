from app.domain.dtos.GeneratedFileDto import GeneratedFileDto
from openpyxl.utils.datetime import from_excel
from datetime import date, datetime
from openpyxl import load_workbook
from dataclasses import dataclass
from typing import Any, Callable
from pathlib import Path
from io import BytesIO
import unicodedata

@dataclass
class FieldMapping:
    targetField: str
    sourceColumns: list[str]
    transform: Callable[[dict[str, Any]], Any]

class ExcelReader:

    INCOME_DATE_COLUMN = ["fecha de ingreso contrato", "trabajo - fecha ingreso compañía"]
    COMPANY_RUT_COLUMN = "Empresa - RUT Empresa"
    COMPANY_RUT_VALUE = "800.180.330-9"
    SALARY = "campos personalizados de trabajo - salario (obligatorio)"
    REST = "campos personalizados de trabajo - dia de descanso 2 (t)"

    def __init__(self):
        self.fieldMappings = self._buildFieldMappings()

    def generateTemplate(self, fileName: str, content: bytes, dateFrom: date, dateTo: date,) -> GeneratedFileDto:
        sourceWorkbook = load_workbook(BytesIO(content), data_only=True, keep_links=False)
        sourceWorksheet = sourceWorkbook.active
        headerRowNumber, sourceColumnMap = self._findSourceColumns(sourceWorksheet)
        sourceRows = self._getSourceRowsByDateRange(worksheet=sourceWorksheet, headerRowNumber=headerRowNumber, columnMap=sourceColumnMap, dateFrom=dateFrom, dateTo=dateTo,)
        templatePath = self._getTemplatePath()
        templateWorkbook = load_workbook(templatePath, keep_links=False)
        templateWorksheet = templateWorkbook["INGRESO DE PERSONAL"]
        campoRow, templateFieldMap = self._findTemplateFieldColumns(worksheet=templateWorksheet, valueToFind="CAMPO",)

        startRow = campoRow + 2

        self._writeTransformedRows(templateWorksheet=templateWorksheet, templateFieldMap=templateFieldMap, sourceRows=sourceRows, startRow=startRow,)
        self._writeBankAccountChangesSheet(templateWorkbook=templateWorkbook, sourceRows=sourceRows,)
        output = BytesIO()
        templateWorkbook.save(output)
        output.seek(0)
        generatedFileName = f"Sinergy_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        return GeneratedFileDto(fileName=generatedFileName, content=output.getvalue(), contentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",)

    def _buildFieldMappings(self) -> list[FieldMapping]:
        return [
            FieldMapping(
                targetField="campo",
                sourceColumns=[["apellidos y nombres", "colaborador - nombre completo"]],
                transform=lambda row: self._getCellText(row.get("apellidos y nombres") or row.get("colaborador - nombre completo")),
            ),
            FieldMapping(
                targetField="empleado",
                sourceColumns=[["cedula numero", "colaborador - número de documento"]],
                transform=lambda row: self._getCellText(row.get("cedula numero") or row.get("colaborador - número de documento")),
            ),
            FieldMapping(
                targetField="pnombre",
                sourceColumns=[["apellidos y nombres", "colaborador - nombre completo"]],
                transform=lambda row: self._splitFullName(self._getCellText(row.get("apellidos y nombres") or row.get("colaborador - nombre completo")))["pnombre"],
            ),
            FieldMapping(
                targetField="snombre",
                sourceColumns=[["apellidos y nombres", "colaborador - nombre completo"]],
                transform=lambda row: self._splitFullName(self._getCellText(row.get("apellidos y nombres") or row.get("colaborador - nombre completo")))["snombre"],
            ),
            FieldMapping(
                targetField="papellido",
                sourceColumns=[["apellidos y nombres", "colaborador - nombre completo"]],
                transform=lambda row: self._splitFullName(self._getCellText(row.get("apellidos y nombres") or row.get("colaborador - nombre completo")))["papellido"],
            ),
            FieldMapping(
                targetField="spellido",
                sourceColumns=[["apellidos y nombres", "colaborador - nombre completo"]],
                transform=lambda row: self._splitFullName(self._getCellText(row.get("apellidos y nombres") or row.get("colaborador - nombre completo")))["spellido"],
            ),
            FieldMapping(
                targetField="fecha_nacimiento",
                sourceColumns=[["fecha de nacimiento", "colaborador - fecha de nacimiento"]],
                transform=lambda row: self._formatDateAsText(row.get("fecha de nacimiento") or row.get("colaborador - fecha de nacimiento")),
            ),
            FieldMapping(
                targetField="tipo_doc_id",
                sourceColumns=[["tipo de identificacion", "colaborador - tipo de documento"]],
                transform=lambda row: self._mapDocumentTypeByCode(self._getCellText(row.get("tipo de identificacion") or row.get("colaborador - tipo de documento"))),
            ),
            FieldMapping(
                targetField="num_doc_id",
                sourceColumns=[["cedula numero", "colaborador - número de documento"]],
                transform=lambda row: self._getCellText(row.get("cedula numero") or row.get("colaborador - número de documento")),
            ),
            FieldMapping(
                targetField="ciudad_doc_id",
                sourceColumns=[["expedida en", "campos personalizados de colaborador - lugar de expedición- nmn"]],
                transform=lambda row: self._getCellText(row.get("expedida en") or row.get("campos personalizados de colaborador - lugar de expedición- nmn")),
            ),
            FieldMapping(
                targetField="sexo",
                sourceColumns=[["sexo", "colaborador - sexo"]],
                transform=lambda row: self._getCellText(row.get("sexo") or row.get("colaborador - sexo")),
            ),
            FieldMapping(
                targetField="fecha_ingreso",
                sourceColumns=[["fecha de ingreso contrato", "trabajo - fecha ingreso compañía"]],
                transform=lambda row: self._formatDateAsText(row.get("fecha de ingreso contrato") or row.get("trabajo - fecha ingreso compañía")),
            ),
            FieldMapping(
                targetField="salario",
                sourceColumns=[],
                transform=lambda row: (self._getCellText(row["campos personalizados de trabajo - salario (obligatorio)"])
                    if "campos personalizados de trabajo - salario (obligatorio)" in row
                    else ""
                ),
            ),
            FieldMapping(
                targetField="fecha_sueldo",
                sourceColumns=[["fecha de ingreso contrato", "trabajo - fecha ingreso compañía"]],
                transform=lambda row: self._formatDateAsText(row.get("fecha de ingreso contrato") or row.get("trabajo - fecha ingreso compañía")),
            ),
            FieldMapping(
                targetField="tipo_sueldo",
                sourceColumns=[["tipo de cargo", "campos personalizados de cargo - cargo general"]],
                transform=lambda row: self._mapSalaryType(self._getCellText(row.get("tipo de cargo") or row.get("campos personalizados de cargo - cargo general"))),
            ),
            FieldMapping(
                targetField="sucursal",
                sourceColumns=[],
                transform=lambda row: "002",
            ),
            #FieldMapping(
            #    targetField="centro_costos_1",
            #    sourceColumns=["centro de costo"],
            #    transform=lambda row: self._mapCostCenter1(self._getCellText(row["centro de costo"])),
            #),
            #FieldMapping(
            #    targetField="centro_costos_2",
            #    sourceColumns=["centro de costo"],
            #    transform=lambda row: self._getCellText(row["centro de costo"]),
            #),
            FieldMapping(
                targetField="centro_costos_3",
                sourceColumns=["trabajo - nombre sub-area asignada(o)"],
                transform=lambda row: self._mapCostCenter3(self._getCellText(row["trabajo - nombre sub-area asignada(o)"])),
            ),
            FieldMapping(
                targetField="centro_costos_4",
                sourceColumns=[],
                transform=lambda row: (self._getCellText(row["campos personalizados de trabajo - dia de descanso 2 (t)"])
                    if "campos personalizados de trabajo - dia de descanso 2 (t)" in row
                    else ""
                ),
            ),
            FieldMapping(
                targetField="tipo_empleado",
                sourceColumns=[],
                transform=lambda row: "002",
            ),
            FieldMapping(
                targetField="tipo_contrato",
                sourceColumns=[["trabajo - cargo", "tipo de cargo"]],
                transform=lambda row: (
                    self._mapContractType(
                        self._getCellText(row["tipo de cargo"]),
                        self._getCellText(row["centro de trabajo"]),
                    )
                    if "centro de trabajo" in row and self._getCellText(row["centro de trabajo"])
                    else self._mapContractType2(
                        self._getCellText(row["trabajo - cargo"])
                    )
                ),
            ),
            FieldMapping(
                targetField="fecha_terminacion",
                sourceColumns=[["fecha contrato hasta", "trabajo - fecha vencimiento contrato"]],
                transform=lambda row: self._formatDateAsText(row.get("fecha contrato hasta") or row.get("trabajo - fecha vencimiento contrato")),
            ),
            FieldMapping(
                targetField="regimen",
                sourceColumns=[],
                transform=lambda row: "2",
            ),
            FieldMapping(
                targetField="cargo",
                sourceColumns=[["tipo de cargo", "trabajo - cargo"]],
                transform=lambda row: self._mapTypeCharge(self._getCellText(row["tipo de cargo"])),
            ),
            FieldMapping(
                targetField="fondo_cesantias",
                sourceColumns=[["fondo de cesantias", "plan - fondo de cesantía"]],
                transform=lambda row: self._mapSeveranceFund(self._getCellText(row["fondo de cesantias"])),
            ),
            FieldMapping(
                targetField="fecha_cesantia",
                sourceColumns=[["fecha de ingreso contrato", "trabajo - fecha ingreso compañía"]],
                transform=lambda row: self._formatDateAsText(row.get("fecha de ingreso contrato") or row.get("trabajo - fecha ingreso compañía")),
            ),
            FieldMapping(
                targetField="entidad_pension",
                sourceColumns=["plan - fondo de pensiones"],
                transform=lambda row: (
                    "P000"
                    if self._normalize(self._getCellText(row["plan - fondo de pensiones"])) in {"", "no aplica"}
                    else self._getCellText(row["plan - fondo de pensiones"])
                ),
            ),
            FieldMapping(
                targetField="sucursal_pension",
                sourceColumns=[],
                transform=lambda row: "001",
            ),
            FieldMapping(
                targetField="fecha_pension",
                sourceColumns=[["fecha de ingreso contrato", "trabajo - fecha ingreso compañía"]],
                transform=lambda row: self._formatDateAsText(row.get("fecha de ingreso contrato") or row.get("trabajo - fecha ingreso compañía")),
            ),
            FieldMapping(
                targetField="entidad_salud",
                sourceColumns=[["e.p.s.", "plan - eps"]],
                transform=lambda row: self._mapEPS(self._getCellText(row["e.p.s."])),
            ),
            FieldMapping(
                targetField="sucursal_salud",
                sourceColumns=[],
                transform=lambda row: "001",
            ),
            FieldMapping(
                targetField="fecha_salud",
                sourceColumns=["fecha de ingreso contrato"],
                transform=lambda row: self._formatDateAsText(row["fecha de ingreso contrato"].value),
            ),
            FieldMapping(
                targetField="caja_compensacion",
                sourceColumns=[],
                transform=lambda row: "COMFAMA",
            ),
            FieldMapping(
                targetField="fecha_caja_compensacion",
                sourceColumns=[["fecha de ingreso contrato", "trabajo - fecha ingreso compañía"]],
                transform=lambda row: self._formatDateAsText(row.get("fecha de ingreso contrato") or row.get("trabajo - fecha ingreso compañía")),
            ),
            FieldMapping(
                targetField="corporacion",
                sourceColumns=[["codigo del banco", "colaborador - banco"]],
                transform=lambda row: self._mapBankCorporation(self._getCellText(row.get("codigo del banco") or row.get("colaborador - banco"))),
            ),
            FieldMapping(
                targetField="cuenta",
                sourceColumns=[["numero de cuenta", "colaborador - número de cuenta"]],
                transform=lambda row: self._getCellText(row.get("numero de cuenta") or row.get("colaborador - número de cuenta")),
            ),
            FieldMapping(
                targetField="tipo_cuenta",
                sourceColumns=[["tipo de cuenta", "colaborador - tipo de cuenta"]],
                transform=lambda row: self._getCellText(row.get("tipo de cuenta") or row.get("colaborador - tipo de cuenta")),
            ),
            FieldMapping(
                targetField="sucursal_bancaria",
                sourceColumns=[],
                transform=lambda row: "001",
            ),
            FieldMapping(
                targetField="tipo_pago",
                sourceColumns=[["forma de pago", "colaborador - forma de pago"]],
                transform=lambda row: self._mapPaymentType(self._getCellText(row["forma de pago"])),
            ),
            FieldMapping(
                targetField="auxilio_seguro",
                sourceColumns=[],
                transform=lambda row: "4",
            ),
            FieldMapping(
                targetField="porcentaje_seguro",
                sourceColumns=[],
                transform=lambda row: "100%",
            ),
            FieldMapping(
                targetField="indicador_retención",
                sourceColumns=[],
                transform=lambda row: "2",
            ),
            FieldMapping(
                targetField="estado",
                sourceColumns=[],
                transform=lambda row: "A",
            ),
            #FieldMapping(
            #    targetField="cuenta_gasto",
            #    sourceColumns=["centro de costo"],
            #    transform=lambda row: self._mapCostCenter1(self._getCellText(row["centro de costo"])),
            #),
            FieldMapping(
                targetField="entidad_riesgo",
                sourceColumns=[],
                transform=lambda row: "SURA",
            ),
            FieldMapping(
                targetField="sucur_Ent_riesgo",
                sourceColumns=[],
                transform=lambda row: "001",
            ),
            FieldMapping(
                targetField="fecha_riesgo",
                sourceColumns=[["fecha de ingreso contrato", "trabajo - fecha ingreso compañía"]],
                transform=lambda row: self._formatDateAsText(row.get("fecha de ingreso contrato") or row.get("trabajo - fecha ingreso compañía")),
            ),
            FieldMapping(
                targetField="centro_trabajo",
                sourceColumns=[["trabajo - cargo"]],
                transform=lambda row: self._mapNewDecreeCodeByCharge(self._getCellText(row["trabajo - cargo"])),
            ),
            FieldMapping(
                targetField="fecha_centro_trabajo",
                sourceColumns=[["fecha de ingreso contrato", "trabajo - fecha ingreso compañía"]],
                transform=lambda row: self._formatDateAsText(row.get("fecha de ingreso contrato") or row.get("trabajo - fecha ingreso compañía")),
            ),
            FieldMapping(
                targetField="ncontrato",
                sourceColumns=[],
                transform=lambda row: "1",
            ),
            FieldMapping(
                targetField="email",
                sourceColumns=[["correo electronico", "colaborador - email"]],
                transform=lambda row: self._getCellText(row.get("correo electronico") or row.get("colaborador - email")),
            ),
            FieldMapping(
                targetField="direccion",
                sourceColumns=[["direccion", "colaborador - dirección"]],
                transform=lambda row: self._getCellText(row.get("direccion") or row.get("colaborador - dirección")),
            ),
            FieldMapping(
                targetField="telefono",
                sourceColumns=[["fax", "colaborador - teléfono particular"]],
                transform=lambda row: self._getCellText(row.get("fax") or row.get("colaborador - teléfono particular")),
            ),
            FieldMapping(
                targetField="estado_civil",
                sourceColumns=["colaborador - estado civil"],
                transform=lambda row: self._mapMaritalStatus(self._getCellText(row["colaborador - estado civil"])),
            ),
            FieldMapping(
                targetField="fecha_cencos",
                sourceColumns=[["fecha de ingreso contrato", "trabajo - fecha ingreso compañía"]],
                transform=lambda row: self._formatDateAsText(row.get("fecha de ingreso contrato") or row.get("trabajo - fecha ingreso compañía")),
            ),
            FieldMapping(
                targetField="tipo_acumulado",
                sourceColumns=[],
                transform=lambda row: "N",
            ),
            FieldMapping(
                targetField="barrio",
                sourceColumns=[["barrio", "campos personalizados de colaborador - barrio"]],
                transform=lambda row: self._getCellText(row.get("barrio") or row.get("campos personalizados de colaborador - barrio")),
            ),
            FieldMapping(
                targetField="pais nacimiento",
                sourceColumns=["colaborador - nacionalidad"],
                transform=lambda row: self._getCellText(row["colaborador - nacionalidad"]),
            ),
            FieldMapping(
                targetField="departamento nacimiento",
                sourceColumns=["campos personalizados de colaborador - lugar de nacimiento"],
                transform=lambda row: self._mapBirthDepartment(self._getCellText(row["campos personalizados de colaborador - lugar de nacimiento"])),
            ),            
            FieldMapping(
                targetField="lugar_nacimiento",
                sourceColumns=["campos personalizados de colaborador - lugar de nacimiento"],
                transform=lambda row: self._getCellText(row["campos personalizados de colaborador - lugar de nacimiento"]),
            ),
            FieldMapping(
                targetField="tipo_sangre",
                sourceColumns=[],
                transform=lambda row: "000",
            ),
            FieldMapping(
                targetField="ojos",
                sourceColumns=[],
                transform=lambda row: "000",
            ),
            FieldMapping(
                targetField="piel",
                sourceColumns=[],
                transform=lambda row: "31",
            ),
            FieldMapping(
                targetField="cabello",
                sourceColumns=[],
                transform=lambda row: "000",
            ),
            FieldMapping(
                targetField="tipo_libreta_militar",
                sourceColumns=[],
                transform=lambda row: "N",
            ),
            FieldMapping(
                targetField="nivel_estudios",
                sourceColumns=["campos personalizados de colaborador - nivel academico"],
                transform=lambda row: self._mapAcademicLevel(self._getCellText(row["campos personalizados de colaborador - nivel academico"])),
            ),
            FieldMapping(
                targetField="empresa",
                sourceColumns=[],
                transform=lambda row: "000000000000002",
            ),

            FieldMapping(
                targetField="posicion",
                sourceColumns=["campos personalizados de cargo - cargo general"],
                transform=lambda row: self._getCellText(row["campos personalizados de cargo - cargo general"]),
            ),
            FieldMapping(
                targetField="tipo_cotizante",
                sourceColumns=["trabajo - cargo"],
                transform=lambda row: self._mapContributor(self._getCellText(row["trabajo - cargo"])),
            ),
            FieldMapping(
                targetField="subtipo_cotizante",
                sourceColumns=[],
                transform=lambda row: "0",
            ),
            FieldMapping(
                targetField="codigo_campo_dia_sabado",
                sourceColumns=[],
                transform=lambda row: "01",
            ),




            FieldMapping(
                targetField="trabaja_sabado",
                sourceColumns=[["trabajo - cargo", "tipo de cargo"]],
                transform=lambda row: self._mapSaturdayWorkByCharge(self._getCellText(row["trabajo - cargo"])),
            ),







            FieldMapping(
                targetField="fecha_cambio_sabado",
                sourceColumns=[["fecha de ingreso contrato", "trabajo - fecha ingreso compañía"]],
                transform=lambda row: self._formatDateAsText(row.get("fecha de ingreso contrato") or row.get("trabajo - fecha ingreso compañía")),
            ),
            FieldMapping(
                targetField="escalafon",
                sourceColumns=[],
                transform=lambda row: "220",
            ),
            FieldMapping(
                targetField="fecha_escalafon",
                sourceColumns=[["fecha de ingreso contrato", "trabajo - fecha ingreso compañía"]],
                transform=lambda row: self._formatDateAsText(row.get("fecha de ingreso contrato") or row.get("trabajo - fecha ingreso compañía")),
            ),
            FieldMapping(
                targetField="auxilio_pension",
                sourceColumns=[],
                transform=lambda row: "4",
            ),
            FieldMapping(
                targetField="porcentaje_pension",
                sourceColumns=[],
                transform=lambda row: "100%",
            ),
            FieldMapping(
                targetField="auxilio_solidaridad",
                sourceColumns=[],
                transform=lambda row: "4",
            ),
            FieldMapping(
                targetField="porcentaje_solidaridad",
                sourceColumns=[],
                transform=lambda row: "100%",
            ),
            FieldMapping(
                targetField="tipo_sueldo_empleado",
                sourceColumns=["trabajo - cargo"],
                transform=lambda row: self._mapEmployeeSalaryType(self._getCellText(row["trabajo - cargo"])),
            ),
            FieldMapping(
                targetField="depto_residencia",
                sourceColumns=["colaborador - departamento"],
                transform=lambda row: self._getCellText(row["colaborador - departamento"]),
            ),
            FieldMapping(
                targetField="municipio_resid",
                sourceColumns=["colaborador - municipio"],
                transform=lambda row: self._getCellText(row["colaborador - municipio"]),
            ),
            # 109
        ]

    def _findSourceColumns(self, worksheet):
        requiredColumns = self._getRequiredSourceColumns()
        optionalColumns = [
            self.COMPANY_RUT_COLUMN,
            self.SALARY,
            self.REST
        ]

        for row in worksheet.iter_rows(min_row=1, max_row=10):
            currentColumns = {}

            for cell in row:
                normalizedValue = self._normalize(cell.value)

                if not normalizedValue:
                    continue

                for requiredColumn in requiredColumns:

                    if isinstance(requiredColumn, list):
                        normalizedOptions = [
                            self._normalize(option)
                            for option in requiredColumn
                        ]

                        canonicalColumn = normalizedOptions[0]

                        if normalizedValue in normalizedOptions:
                            currentColumns[canonicalColumn] = cell.column

                    else:
                        normalizedRequiredColumn = self._normalize(requiredColumn)

                        if normalizedValue == normalizedRequiredColumn:
                            currentColumns[normalizedRequiredColumn] = cell.column

                for optionalColumn in optionalColumns:
                    normalizedOptionalColumn = self._normalize(optionalColumn)

                    if normalizedValue == normalizedOptionalColumn:
                        currentColumns[normalizedOptionalColumn] = cell.column

            if all(
                (
                    self._normalize(columnName[0]) in currentColumns
                    if isinstance(columnName, list)
                    else self._normalize(columnName) in currentColumns
                )
                for columnName in requiredColumns
            ):
                return row[0].row, currentColumns

        missingColumns = []

        for requiredColumn in requiredColumns:
            if isinstance(requiredColumn, list):
                missingColumns.append(" o ".join(requiredColumn))
            else:
                missingColumns.append(requiredColumn)

        missingColumnsText = ", ".join(missingColumns)

        raise ValueError(f"No se encontraron las columnas requeridas en el archivo origen: {missingColumnsText}.")

    def _getRequiredSourceColumns(self):
        requiredColumns = [self.INCOME_DATE_COLUMN]

        for mapping in self.fieldMappings:
            for sourceColumn in mapping.sourceColumns:
                requiredColumns.append(sourceColumn)

        return requiredColumns

    def _getSourceRowsByDateRange(self, worksheet, headerRowNumber: int, columnMap: dict, dateFrom: date, dateTo: date,) -> list[dict[str, Any]]:
        sourceRows = []
        incomeDateColumn = columnMap[self._normalize(self.INCOME_DATE_COLUMN[0])]
        companyRutColumn = columnMap.get(self._normalize(self.COMPANY_RUT_COLUMN))
        expectedCompanyRut = self._cleanRut(self.COMPANY_RUT_VALUE)

        for rowNumber in range(headerRowNumber + 1, worksheet.max_row + 1):
            incomeDateValue = worksheet.cell(row=rowNumber, column=incomeDateColumn).value
            incomeDate = self._parseDate(incomeDateValue)

            if not incomeDate:
                continue

            if incomeDate < dateFrom or incomeDate > dateTo:
                continue

            if companyRutColumn:
                companyRutValue = worksheet.cell(row=rowNumber, column=companyRutColumn).value
                currentCompanyRut = self._cleanRut(companyRutValue)

                if currentCompanyRut != expectedCompanyRut:
                    continue

            sourceRows.append(self._buildSourceRowContext(worksheet=worksheet, rowNumber=rowNumber, columnMap=columnMap,))

        return sourceRows

    def _buildSourceRowContext(self, worksheet, rowNumber: int, columnMap: dict,) -> dict[str, Any]:
        rowContext = {}

        for columnName, columnNumber in columnMap.items():
            rowContext[columnName] = worksheet.cell(row=rowNumber, column=columnNumber,)

        return rowContext

    def _findTemplateFieldColumns(self, worksheet, valueToFind: str):
        normalizedTarget = self._normalize(valueToFind)

        for row in worksheet.iter_rows():
            for cell in row:
                if self._normalize(cell.value) == normalizedTarget:
                    campoRow = cell.row
                    templateFieldMap = self._buildTemplateFieldMap(worksheet=worksheet, campoRow=campoRow,)

                    self._validateTemplateFields(templateFieldMap)

                    return campoRow, templateFieldMap

        raise ValueError(f"No se encontró la fila {valueToFind} en la plantilla.")

    def _buildTemplateFieldMap(self, worksheet, campoRow: int) -> dict[str, int]:
        templateFieldMap = {}

        for cell in worksheet[campoRow]:
            normalizedValue = self._normalize(cell.value)

            if normalizedValue:
                templateFieldMap[normalizedValue] = cell.column

        return templateFieldMap

    def _validateTemplateFields(self, templateFieldMap: dict[str, int]) -> None:
        missingFields = []

        for mapping in self.fieldMappings:
            targetField = self._normalize(mapping.targetField)

            if targetField not in templateFieldMap:
                missingFields.append(mapping.targetField)

        if missingFields:
            raise ValueError(f"No se encontraron estos campos en la plantilla: {', '.join(missingFields)}.")

    def _writeTransformedRows(self, templateWorksheet, templateFieldMap: dict[str, int], sourceRows: list[dict[str, Any]], startRow: int,) -> None:

        for index, sourceRow in enumerate(sourceRows):
            targetRow = startRow + index

            for mapping in self.fieldMappings:
                targetField = self._normalize(mapping.targetField)
                targetColumn = templateFieldMap[targetField]
                value = mapping.transform(sourceRow)

                cell = templateWorksheet.cell(row=targetRow, column=targetColumn, value=value,)

                if targetField in {
                    "empleado",
                    "num_doc_id",
                    "fecha_nacimiento",
                    "tipo_doc_id",
                    "ciudad_doc_id",
                    "sexo",
                    "fecha_ingreso",
                    "fecha_sueldo",
                    "sucursal",
                    "centro_costos_1",
                    "centro_costos_2",
                    "centro_costos_3",
                    "tipo_empleado",
                    "fecha_terminacion",
                    "regimen",
                    "fecha_cesantia",
                    "sucursal_pension",
                    "fecha_pension",
                    "sucursal_salud",
                    "fecha_salud",
                    "caja_compensacion",
                    "fecha_caja_compensacion",
                    "corporacion",
                    "cuenta",
                    "tipo_cuenta",
                    "sucursal_bancaria",
                    "tipo_pago",
                    "auxilio_seguro",
                    "porcentaje_seguro",
                    "indicador_retención",
                    "estado",
                    "cuenta_gasto",
                    "entidad_riesgo",
                    "sucur_Ent_riesgo",
                    "fecha_riesgo",
                    "fecha_centro_trabajo",
                    "ncontrato",
                    "email",
                    "direccion",
                    "telefono",
                    "estado_civil",
                    "fecha_cencos",
                    "tipo_acumulado",
                    "barrio",
                    "tipo_sangre",
                    "ojos",
                    "piel",
                    "cabello",
                    "tipo_libreta_militar",
                    "nivel_estudios",
                    "empresa",
                    "codigo_campo_dia_sabado",
                    "fecha_cambio_sabado",
                    "escalafon",
                    "fecha_escalafon",
                    "auxilio_pension",
                    "porcentaje_pension",
                    "auxilio_solidaridad",
                    "porcentaje_solidaridad",
                }:
                    cell.number_format = "@"

    def _splitFullName(self, fullName: str) -> dict[str, str]:
        value = " ".join(fullName.strip().split())

        if not value:
            return {
                "pnombre": "",
                "snombre": "",
                "papellido": "",
                "spellido": "",
            }

        parts = value.split(" ")

        if len(parts) >= 4:
            papellido = parts[0]
            spellido = parts[1]
            pnombre = parts[2]
            snombre = " ".join(parts[3:])
        elif len(parts) == 3:
            papellido = parts[0]
            spellido = parts[1]
            pnombre = parts[2]
            snombre = ""
        elif len(parts) == 2:
            papellido = parts[0]
            spellido = ""
            pnombre = parts[1]
            snombre = ""
        else:
            papellido = ""
            spellido = ""
            pnombre = parts[0]
            snombre = ""

        return {
            "pnombre": pnombre,
            "snombre": snombre,
            "papellido": papellido,
            "spellido": spellido,
        }

    def _getCellText(self, cell) -> str:
        value = cell.value

        if value is None:
            return ""

        if isinstance(value, str):
            return value.strip()

        if isinstance(value, int):
            return self._formatNumberAsText(value=value, numberFormat=cell.number_format)

        if isinstance(value, float):
            if value.is_integer():
                return self._formatNumberAsText(value=int(value), numberFormat=cell.number_format,)

            return str(value).strip()

        return str(value).strip()

    def _formatNumberAsText(self, value: int, numberFormat: str) -> str:
        normalizedFormat = str(numberFormat or "").strip()

        if normalizedFormat and set(normalizedFormat) == {"0"}:
            return str(value).zfill(len(normalizedFormat))

        return str(value)

    def _parseDate(self, value):
        if value is None:
            return None

        if isinstance(value, datetime):
            return value.date()

        if isinstance(value, date):
            return value

        if isinstance(value, (int, float)):
            try:
                return from_excel(value).date()
            except Exception:
                return None

        textValue = str(value).strip()

        for dateFormat in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
            try:
                return datetime.strptime(textValue, dateFormat).date()
            except ValueError:
                continue

        return None

    def _getProjectRoot(self) -> Path:
        return Path(__file__).resolve().parents[3]

    def _getTemplatePath(self) -> Path:
        templatePath = self._getProjectRoot() / "templates" / "Template_1.xlsx"

        if not templatePath.exists():
            raise ValueError(f"No se encontró la plantilla en la ruta: {templatePath}")

        return templatePath

    def _normalize(self, value) -> str:
        if value is None:
            return ""

        text = str(value).strip().lower()
        text = unicodedata.normalize("NFKD", text)
        text = "".join(character for character in text if not unicodedata.combining(character))
        text = " ".join(text.split())

        return text
    
    def _cleanRut(self, value) -> str:
        return "".join(character for character in str(value or "") if character.isdigit())
    
    def _formatDateAsText(self, value) -> str:
        if hasattr(value, "value"):
            value = value.value

        parsedDate = self._parseDate(value)

        if not parsedDate:
            return ""

        return parsedDate.strftime("%d/%m/%Y")

    def _mapDocumentTypeByCode(self, value: str) -> str:
        normalizedValue = self._normalize(value)

        if not normalizedValue:
            return ""

        normalizedValue = normalizedValue.replace(",", ".")

        try:
            documentTypeCode = int(float(normalizedValue))
        except ValueError:
            documentTypeCode = None

        if documentTypeCode == 1:
            return "C"

        if documentTypeCode == 4:
            return "T"

        if documentTypeCode == 3:
            return "E"

        if documentTypeCode == 5:
            return "U"

        if "ciudadania" in normalizedValue:
            return "C"

        if "tarjeta" in normalizedValue or normalizedValue in {"t.i", "ti"}:
            return "T"

        if "extranjeria" in normalizedValue:
            return "E"

        if "permiso" in normalizedValue:
            return "U"

        return ""
    
    def _mapCostCenter1(self, value: str) -> str:
        costCenter = str(value or "").strip()

        if not costCenter:
            return ""

        costCenter = costCenter.replace(".0", "")

        if costCenter.startswith("01"):
            return "51"

        if costCenter.startswith("02"):
            return "52"

        if costCenter.startswith("03") and costCenter.endswith("01"):
            return "73"

        if costCenter.startswith("03") and not costCenter.endswith("02"):
            return "72"

        return ""
    
    def _mapCostCenter3(self, value: str) -> str:
        subArea = self._normalize(value)

        if not subArea:
            return ""

        subArea = subArea.replace(".", " ")
        subArea = " ".join(subArea.split())

        restaurantCodes = {
            "museo de arte moderno": "R19",
            "amsterdam": "R25",
            "arkadia": "R21",
            "campestre": "R03",
            "cocina domicilios": "C01",
            "cocina occidente": "C02",
            "florida etapa 2": "R24",
            "florida parque comercial": "R15",
            "h florida parque comercial": "H05",
            "h molinos": "H04",
            "h santafe": "H02",
            "h tesoro": "H01",
            "h unicentro": "H06",
            "heladeria oviedo": "H08",
            "heladeria viva envigado": "H07",
            "laureles": "R07",
            "lemont": "R22",
            "llanogrande": "R10",
            "mayorca": "R09",
            "mayorca etapa dos": "R09",
            "molinos": "R08",
            "one plaza": "R18",
            "oviedo": "R06",
            "palma grande": "R16",
            "plaza fabricato": "R23",
            "poblado": "R01",
            "premium plaza": "R11",
            "puerta del norte": "R14",
            "san diego": "R05",
            "san nicolas": "R13",
            "santafe": "R12",
            "tesoro": "R04",
            "unicentro": "R02",
            "viva envigado": "R20",
        }

        administrativeAreas = {
            "diversidad funcional",
            "tesoreria",
            "vinculos y relaciones humanas",
            "calidad",
            "gerencia general",
            "sena",
            "seguridad y salud en el trabajo",
            "direccion operativa",
            "servicios administrativos",
            "comunicarte",
            "tecnologia",
            "direccion de calidad",
            "compras",
            "control y mejora continua",
            "costos",
            "direccion de alimentos",
            "contabilidad",
            "gestion ambiental",
            "nomina",
            "bienestar y cultura organizacional",
            "seleccion y contratacion",
            "direccion de logistica",
            "servicios generales",
            "analitica de datos",
            "gestion de activos fijos",
            "direccion administrativa",
            "direccion desarrollo humano",
        }

        code = restaurantCodes.get(subArea)

        if not code and subArea in administrativeAreas:
            code = "ADM"

        if not code:
            return ""

        return f"{code}-002"
    
    def _mapBankCorporation(self, value: str) -> str:
        originalValue = " ".join(str(value or "").strip().split())

        if not originalValue:
            return ""

        normalizedText = self._normalize(originalValue)

        if normalizedText in {"no aplica", "n/a", "na", "no"}:
            return ""

        bankCode = self._normalizeCode(originalValue, 2)

        bankCode = str(value or "").strip()

        if not bankCode:
            return ""

        bankCode = bankCode.replace(".0", "")

        if bankCode == "7":
            bankCode = "07"

        if bankCode == "07":
            return "BANCOLOMBIA"

        if bankCode == "51":
            return "DAVIVIENDA"

        return originalValue.upper()
    
    def _mapPaymentType(self, value: str) -> str:
        paymentType = " ".join(str(value or "").strip().split())

        if not paymentType:
            return ""

        normalizedPaymentType = self._normalize(paymentType)
        paymentTypeCode = self._normalizeCode(paymentType, 1)

        if normalizedPaymentType in {"no generar pago", "no aplica", "n/a", "na"}:
            return ""

        if paymentTypeCode == "2":
            return "CO"

        if paymentTypeCode == "1":
            return "CH"
        
        if paymentTypeCode == "0":
            return "EF"

        if "cheque" in normalizedPaymentType:
            return "CH"

        if "transferencia bancaria" in normalizedPaymentType:
            return "CO"

        if "transferencia" in normalizedPaymentType:
            return "CO"

        return ""

    def _mapMaritalStatus(self, value: str) -> str:
        maritalStatus = self._normalize(value)

        if not maritalStatus:
            return "000"

        if maritalStatus == "soltero":
            return "001"

        if maritalStatus == "casado":
            return "002"

        if maritalStatus == "union libre":
            return "003"

        if maritalStatus == "viudo":
            return "004"

        if maritalStatus == "divorciado":
            return "005"

        if maritalStatus == "separado":
            return "005"

        return "000"
    
    def _mapAcademicLevel(self, value: str) -> str:
        academicLevel = self._normalize(value)

        if not academicLevel:
            return "000"

        if academicLevel == "primaria":
            return "001"

        if academicLevel in {"bachiller", "bachiller - 002"}:
            return "002"

        if academicLevel in {"tecnico", "tecnico - 003"}:
            return "003"

        if academicLevel in {"tecnologo", "tecnologo - 004"}:
            return "004"

        if academicLevel in {"universitario", "universitario - 005", "profesional"}:
            return "005"

        if academicLevel in {"especialista", "especializacion"}:
            return "006"

        return "000"
    
    def _mapTypeCharge(self, value: str) -> str:
        originalValue = " ".join(str(value or "").strip().split())

        if not originalValue:
            return ""

        typeCharge = self._normalizeCode(originalValue, 4)

        if typeCharge == "0010":
            return "ADMINISTRADORA FIN DE SEMANA"
        
        if typeCharge == "0070":
            return "ADMINISTRADORA PUNTO DE VENTA"
        
        if typeCharge == "1124":
            return "ANALISTA DE LOGISTICA / DESCARGOS"
        
        if typeCharge == "1125":
            return "ANAL DE TESOR/VENTAS"
        
        if typeCharge == "2032":
            return "ANALISTA MOVIMIENTO INVENTARIO ALMACEN"
        
        if typeCharge == "1139":
            return "ANALISTA DE MOVIMIENTO INVENTARIO"
        
        if typeCharge == "2031":
            return "ANALISTA OPERACIONES JUNIOR"
        
        if typeCharge == "1143":
            return "ANALISTA SUPERNUMERARIA DE LOGISTICA"
        
        if typeCharge == "1116":
            return "ANALISTA DE TESORERIA SUPERNUMERARIA"
        
        if typeCharge == "1123":
            return "ANALISTA PRODUCCION"
        
        if typeCharge == "2005":
            return "ANALISTA DE PRESUPUESTO"
        
        if typeCharge == "181":
            return "ANALISTA DE BIENESTAR"
        
        if typeCharge == "1145":
            return "ANALISTA DE CONTRATACION"
        
        if typeCharge == "2029":
            return "ANALISTA CONTROL CAV"
        
        if typeCharge == "1184":
            return "ANALISTA CONTROL INTERNO"
        
        if typeCharge == "1188":
            return "ANALISTA CONTROL INTERNO"
        
        if typeCharge == "2027":
            return "ANALISTA DE ALMACEN"
        
        if typeCharge == "1134":
            return "ANALISTA DE CALIDAD"
        
        if typeCharge == "1110":
            return "ANALISTA DE COMPRAS"
        
        if typeCharge == "1162":
            return "ANALISTA DE COMUNICA"
        
        if typeCharge == "1207":
            return "ANALISTA DE CONTABILIDAD SUPERNUMERARIA"
        
        if typeCharge == "0161":
            return "ANALISTA DE CONTABILIDAD"
        
        if typeCharge == "0169":
            return "ANALISTA DE COSTOS"
        
        if typeCharge == "1141":
            return "ANALISTA DE INGRESOS"
        
        if typeCharge == "1171":
            return "ANALISTA DE MANTENIMIENTO"
        
        if typeCharge == "0020":
            return "ANALISTA DE NOMINA"
        
        if typeCharge == "1167":
            return "ANALISTA DE OPERACIONES"
        
        if typeCharge == "1161":
            return "ANALISTA DE PLANEACION"
        
        if typeCharge == "060":
            return "ANALISTA DE SALUD OCUPACIONAL"
        
        if typeCharge == "2204":
            return "ANALISTA DE SERVICIOS ADMINISTRATIVOS"
        
        if typeCharge == "1160":
            return "ANALISTA DE SOSTENIBILIDAD"
        
        if typeCharge == "149":
            return "ANALISTA DE DESPACHO PTO VTA 2"
        
        if typeCharge == "148":
            return "ANALISTA DE DESPACHO PTO DE VTA 1"
        
        if typeCharge == "0176":
            return "ANALISTA DE FACTURACION"
        
        if typeCharge == "1195":
            return "ANALISTA DE INGENIERIA DE IDI"
        
        if typeCharge == "2100":
            return "ANALISTA JUNIOR DE ACTIVOS FIJOS"
        
        if typeCharge == "2098":
            return "ANALISTA JUNIOR CENTRO DE SERVICIOS"
        
        if typeCharge == "2016":
            return "ANALISTA JUNIOR CONTROL INTERNO"
        
        if typeCharge == "2014":
            return "ANALISTA JUNIOR CONTABILIDAD"
        
        if typeCharge == "2002":
            return "ANALISTA JUNIOR DE NOMINA"
        
        if typeCharge == "2071":
            return "ANALAISTA JUNIOR TESORERIA"
        
        if typeCharge == "2021":
            return "ANALISTA JUNIOR SST"
        
        if typeCharge == "1163":
            return "ANALISTA JUNIOR TEGNOLOGIA E INFORMATICA"
        
        if typeCharge == "1175":
            return "ANALISTA DE MOVIMIENTOS DE INVENTARIOS"
        
        if typeCharge == "050":
            return "ANALISTA DE PRODUCCION"
        
        if typeCharge == "2019":
            return "ANALISTA SELECCION JUNIOR"
        
        if typeCharge == "0492":
            return "ANALISTA DE SELECCION"
        
        if typeCharge == "2009":
            return "ANALISTA SENIOR DE NOMINA"
        
        if typeCharge == "2043":
            return "ANALISTA SENIOR DE TESORERIA"
        
        if typeCharge == "2003":
            return "ANALISTA SENIOR TI Y COMUNICACIONES"
        
        if typeCharge == "2001":
            return "ANALISTA SENIOR TI Y COMUNICACIONES"
        
        if typeCharge == "158":
            return "ANALISTA DE SOPORTE TECNICO"
        
        if typeCharge == "1166":
            return "ANALISTA SST"
        
        if typeCharge == "0187":
            return "ANALISTA TECNOLOGIA E INFORMATICA"
        
        if typeCharge == "030":
            return "ANALISTA DE TESORERIA"
        
        if typeCharge == "0080":
            return "ANFITRIONA"
        
        if typeCharge == "2083":
            return "ANALISTA ANALITICA DE DATOS"
        
        if typeCharge == "2207":
            return "ANALISTA DESPACHO LOG"
        
        if typeCharge == "2108":
            return "ANL JR PLANEACION Y ANALISIS FINANCIERO"
        
        if typeCharge == "2111":
            return "ANALISTA JUNIOR DE TRANSFORMARTE"
        
        if typeCharge == "2055":
            return "ANALISTA JUNIOR DE COSTOS"
        
        if typeCharge == "2076":
            return "ANALISTA JUNIOR SERVICIOS ADMINISTRATIVO"
        
        if typeCharge == "2070":
            return "ANALISTA JUNIOR SUPERNUMERARIA TESORERIA"
        
        if typeCharge == "2081":
            return "ANALISTA SENIOR DE CALIDAD"
        
        if typeCharge == "2117":
            return "ANALISTA SENIOR DE CALIDAD"

        if typeCharge == "2044":
            return "ANALISTA SENIOR DE CONTROL INTERNO"
        
        if typeCharge == "2000":
            return "ANALISTA SENIOR CONTROL INTERNO"
        
        if typeCharge == "2110":
            return "ANALISTA SENIOR DE CONTABILIDAD"
        
        if typeCharge == "2092":
            return "ANALISTA SENIOR GESTION AMBIENTAL"
        
        if typeCharge == "2101":
            return "ANALISTA SENIOR DE IMPUESTOS"
        
        if typeCharge == "2112":
            return "ANALISTA SENIOR DE SELECCION"
        
        if typeCharge == "2109":
            return "ANALISTA SENIOR DE SERVICIOS ADMINISTRAT"
        
        if typeCharge == "2106":
            return "ANALISTA SENIOR DE SOSTENIBILIDAD"
        
        if typeCharge == "2119":
            return "ANALISTA SENIOR PLANEACION DE LA DEMANDA"
        
        if typeCharge == "2075":
            return "ANALISTA SUPERNUMERIA DE LOGISTICA"
        
        if typeCharge == "2086":
            return "ANALISTA DE VINCULOS Y RELACIONES HUMANA"
        
        if typeCharge == "0060":
            return "APRENDIZ"
        
        if typeCharge == "090":
            return "ASEO"
        
        if typeCharge == "0100":
            return "ACONDICIONAMIENTO POLLO"
        
        if typeCharge == "2066":
            return "ASEO Y LIMPIEZA"
        
        if typeCharge == "0120":
            return "ASEO Y PLATERO"
        
        if typeCharge == "0480":
            return "ASESORA DE SERVICIO AL CLIENTE"
        
        if typeCharge == "0157":
            return "ASIS DE GEST INOCUIDAD"
        
        if typeCharge == "1106":
            return "ASISTENTE DE GESTION DE CALIDAD"
        
        if typeCharge == "0186":
            return "ASISTENTE DE BIENESTAR LABORAL"
        
        if typeCharge == "0155":
            return "ASISTENTE DE CONTABILIDAD"
        
        if typeCharge == "0147":
            return "ASISTENTE DE COSTOS"
        
        if typeCharge == "0143":
            return "ASISTENTE DE DESARROLLO HUMANO"
        
        if typeCharge == "0149":
            return "ASISTENTE DE LOGISTICA"

        if typeCharge == "182":
            return "ASISTENTE DE NOMINA"
        
        if typeCharge == "0188":
            return "ASISTENTE DE SELECCION"
        
        if typeCharge == "0144":
            return "ASISTENTE DE TECNOLOGIA E INFORMATICA"
        
        if typeCharge == "0162":
            return "ASISTENTE DE TESORERIA"
        
        if typeCharge == "1153":
            return "AUXILAR ADMINISTRATIVA DE OPERACION"
        
        if typeCharge == "170":
            return "AUXILIAR ADMINISTRATIVO PRODUCCION"
        
        if typeCharge == "1178":
            return "AUXILIAR COMUNICARTE"
        
        if typeCharge == "2049":
            return "AUXILIAR CONTROL DE CAVAS"
        
        if typeCharge == "2205":
            return "AUXILIAR DE CONTROL INTERNO"
        
        if typeCharge == "0493":
            return "AUXILIAR DE SELECCION"
        
        if typeCharge == "1205":
            return "AUXILIAR DE SERVICIOS ADMINISTRATIVOS"
        
        if typeCharge == "2028":
            return "AUXILIAR EMPAQUE ALMACEN"
        
        if typeCharge == "0191":
            return "AUXILIAR DE GESTION AMBIENTAL"
        
        if typeCharge == "0177":
            return "AUX GESTION INOCUIDAD"
        
        if typeCharge == "1120":
            return "AUXILIAR LOGISTICO OPERATIVO"
        
        if typeCharge == "2091":
            return "AUXILIAR LOGISTICO ADMINISTRATIVO"
        
        if typeCharge == "1102":
            return "AUXILIAR DE MANTENIMIENTO"
        
        if typeCharge == "0201":
            return "AUXILIAR MOVIEMTO DE INVENTARIO"
        
        if typeCharge == "0491":
            return "AUXILIAR DE NOMINA"
        
        if typeCharge == "2008":
            return "AUXILIAR DE OPERACIONES PQRS"
        
        if typeCharge == "2024":
            return "AUXILIAR OPERATIVO MANTENIMIENTO"
        
        if typeCharge == "1197":
            return "AUXILIAR DE PLANEACION Y ANALISIS FINANC"
        
        if typeCharge == "1130":
            return "AUXILIAR DE PRODUCCION/FORMULACION MEZCL"
        
        if typeCharge == "0173":
            return "AUXILIAR DE SERVICIO AL CLIENTE"
        
        if typeCharge == "2054":
            return "AUXILIAR DE VENTA NO PRESENTE"
        
        if typeCharge == "2011":
            return "AUXILIAR ADMINISTRATIVO PRODUCCION"
        
        if typeCharge == "0158":
            return "AUXILIAR ADMINISTRATIVA"
        
        if typeCharge == "0496":
            return "AUXILIAR BIENESTAR"
        
        if typeCharge == "0620":
            return "SECRETARIA"
        
        if typeCharge == "0167":
            return "AUXILIAR CENTRO DE SERVICIOS"
        
        if typeCharge == "0154":
            return "AUXILIAR DE ALMACEN"
        
        if typeCharge == "0164":
            return "AUXILIAR DE ARCHIVO"
        
        if typeCharge == "0168":
            return "AUXILIAR DE AUDITORIA"
        
        if typeCharge == "0150":
            return "AUXILIAR DE BODEGA"
        
        if typeCharge == "0172":
            return "AUXILIAR DE CALIDAD"
        
        if typeCharge == "0170":
            return "AUXILIAR DE COCINA"
        
        if typeCharge == "0183":
            return "AUXILIAR DE COMPRAS"
        
        if typeCharge == "1203":
            return "AUXILIAR DE COMUNICACIONES"
        
        if typeCharge == "0180":
            return "AUXILIAR DE CONTABILIDAD"
        
        if typeCharge == "0184":
            return "AUXILIAR DE CONTRATACION"
        
        if typeCharge == "1113":
            return "AUXILIAR DE COSTOS"
        
        if typeCharge == "145":
            return "AUXILIAR DE COSTOS"

        if typeCharge == "146":
            return "AUXILIAR DE DESPACHOS"
        
        if typeCharge == "0160":
            return "AUXILIAR DE EGRESOS"
        
        if typeCharge == "1137":
            return "AUXILIAR DE FACTURACION LOGISTICA"
        
        if typeCharge == "1187":
            return "AUXILIAR DE FACTURACION"
        
        if typeCharge == "0190":
            return "AUXILIAR HELADOS"
        
        if typeCharge == "0195":
            return "AUXILIAR DE INGRESOS"
        
        if typeCharge == "1111":
            return "AUXILIAR DE INGRESOS"
        
        if typeCharge == "0200":
            return "AUXILIAR DE INVENTARIOS"
        
        if typeCharge == "0152":
            return "AUXILIAR DE LOGISTICA"
        
        if typeCharge == "0175":
            return "AUXILIAR DE PERSONAL"
        
        if typeCharge == "0182":
            return "AUXILIAR DE PRODUCCION"
        
        if typeCharge == "0490":
            return "AUXILIAR DE RESTAURANTE"
        
        if typeCharge == "2107":
            return "AUXILIAR DE SOSTENIBILIDAD"
        
        if typeCharge == "0185":
            return "AUXILIAR DESARROLLO HUMANO"
        
        if typeCharge == "2040":
            return "AUXILIAR IDI"
        
        if typeCharge == "0174":
            return "AUXILIAR SST"
        
        if typeCharge == "147":
            return "AUXILIAR DE TECNOLOGIA E INFORMATICA"
        
        if typeCharge == "0178":
            return "AUXILIAR TESORERIA"
        
        if typeCharge == "1196":
            return "AUXILIAR TRANSFORMARTE"
        
        if typeCharge == "0210":
            return "AXILIAR DE BODEGA"
        
        if typeCharge == "0220":
            return "BEBIDAS"
        
        if typeCharge == "0230":
            return "BODEGA"
        
        if typeCharge == "0240":
            return "CAJERA"
        
        if typeCharge == "0260":
            return "CELADOR"
        
        if typeCharge == "0270":
            return "COCINA"
        
        if typeCharge == "0290":
            return "COMPRAS"
        
        if typeCharge == "0300":
            return "CONDUCTOR"
        
        if typeCharge == "0650":
            return "CONTADOR ASISTENTE"
        
        if typeCharge == "2033":
            return "COORDINADOR ANALITICA DE DATOS"
        
        if typeCharge == "2012":
            return "COORDINADORA CENTRO DE SERVICIOS"
        
        if typeCharge == "0198":
            return "COORDINADOR DE LOGISTICA"
        
        if typeCharge == "2089":
            return "COORDINADOR DE PLANEACION DE LA DEMANDA"
        
        if typeCharge == "2048":
            return "COORDINADORA PLANTA DE PRODUCCION"
        
        if typeCharge == "159":
            return "COORD ALMACENAMIENTO"
        
        if typeCharge == "144":
            return "COORD DISTRIBUCION"
        
        if typeCharge == "2080":
            return "COORDINADDOR INFRAESTRUCTURA CLOUD"
        
        if typeCharge == "0165":
            return "COORDINADORA DE SERVICIO CLTE Y MERCADEO"
        
        if typeCharge == "2017":
            return "COORDINADORA SERVICIOS ADMINISTRATIVOS"
        
        if typeCharge == "2082":
            return "COORD VINCULOS Y RELACIONES HUMANAS"
        
        if typeCharge == "1142":
            return "COORDINADOR CONTABLE"
        
        if typeCharge == "0153":
            return "COORDINADOR DE ALMACEN"
        
        if typeCharge == "0196":
            return "COORDINADOR DE COMPRAS"
        
        if typeCharge == "2059":
            return "COORDINADOR DE COSTO"
        
        if typeCharge == "0166":
            return "COORDINADOR DE TECNOLOGIA E INFORMATICA"
        
        if typeCharge == "0151":
            return "COORDINADOR DESPACHO"
        
        if typeCharge == "155":
            return "COORDINADORA DE INFORMES Y AUDITORIA"
        
        if typeCharge == "2118":
            return "COORDINADOR DE TRANSFORMARTE"
        
        if typeCharge == "153":
            return "COORDINADORA DE BIENESTAR"
        
        if typeCharge == "152":
            return "COORDINADORA DE COSTOS"
        
        if typeCharge == "0030":
            return "COORDINADORA HELADERIA"
        
        if typeCharge == "156":
            return "COORDINADORA DE NOMINA"
        
        if typeCharge == "157":
            return "COORDINADORA DE SELECCION"
        
        if typeCharge == "0310":
            return "CREPERA"
        
        if typeCharge == "1156":
            return "DIRECTOR CONTABLE Y DE IMPUESTOS"
        
        if typeCharge == "2050":
            return "DIRECTORA DESARROLLO HUMANO"
        
        if typeCharge == "1107":
            return "DIRECTOR GESTION DE CALIDAD"
        
        if typeCharge == "070":
            return "DIREC GEST INOCUIDAD"
        
        if typeCharge == "0130":
            return "DIRECTORA ADMINISTRATIVA"
        
        if typeCharge == "0137":
            return "DIRECTOR OPERATIVO"
        
        if typeCharge == "2087":
            return "DIRECTORA DE COMPRAS"
        
        if typeCharge == "0136":
            return "DIRECTORA DE LINEAS"
        
        if typeCharge == "0135":
            return "DIRECTORA DE LOGISTICA"
        
        if typeCharge == "1135":
            return "DIRECTORA DE SER CLTE MERCADEO Y HELADER"
        
        if typeCharge == "160":
            return "DIRECTORA PRODUCCION"
        
        if typeCharge == "1177":
            return "DOMICILIARIA"
        
        if typeCharge == "0330":
            return "EMPAQUE"

        if typeCharge == "0340":
            return "ENSALADAS Y BEBIDAS"
        
        if typeCharge == "0350":
            return "ENSALADERA"
        
        if typeCharge == "1118":
            return "ESP TRANSPORTE/AUXILIAR CONDUCTOR"
        
        if typeCharge == "1117":
            return "ESPECIALISTA DE TRANSPORTE/AUXILIAR"
        
        if typeCharge == "1119":
            return "ESPECIALISTA TRANSPORTE/CONDUCTOR"
        
        if typeCharge == "1168":
            return "ESPECIALISTA EN GESTION DE CONOCIMIENTO"
        
        if typeCharge == "0148":
            return "ESPECIALISTA DE TRANSPORTE AUX CONDUCTOR"
        
        if typeCharge == "2041":
            return "FORMADORA"
        
        if typeCharge == "0360":
            return "GERENTE DE LOCAL"
        
        if typeCharge == "0380":
            return "GERENTE GENERAL"
        
        if typeCharge == "0390":
            return "GERENTE LOCAL"
        
        if typeCharge == "0370":
            return "GERENTE PUNTO DE VENTA"
        
        if typeCharge == "0371":
            return "GERENTE ROTANTE"
        
        if typeCharge == "2046":
            return "GESTOR INTEGRAL DE RESIDUOS"
        
        if typeCharge == "0400":
            return "GTE LOCAL FIN SEMANA"
        
        if typeCharge == "0410":
            return "HELADERA"
        
        if typeCharge == "0420":
            return "HELADOS"
        
        if typeCharge == "0430":
            return "HELADOS Y POSTRES"
        
        if typeCharge == "1122":
            return "INSTRUCTORA DE POSTRES Y HELADOS"
        
        if typeCharge == "1121":
            return "INSTRUCTORA DE PLANCHA"
        
        if typeCharge == "0193":
            return "INSTRUCTORA DE BEBIDAS"
        
        if typeCharge == "2067":
            return "INSTRUCTORA DE CAJA"
        
        if typeCharge == "2051":
            return "INSTRUCTORA DE COCINA"
        
        if typeCharge == "200":
            return "INSTRUCTORAS DE LINEAS"

        if typeCharge == "2052":
            return "INSTRUCTORA DE PITAS Y ENSALADA"
        
        if typeCharge == "0189":
            return "JEFE DE BIENESTAR"
        
        if typeCharge == "0280":
            return "JEFE DE COCINA"
        
        if typeCharge == "0146":
            return "JEFE DE COSTOS"
        
        if typeCharge == "0142":
            return "JEFE DE DESARROLLO HUMANO"
        
        if typeCharge == "1157":
            return "JEFE DE EXPERIENCIA DE MARCA"
        
        if typeCharge == "140":
            return "JEFE DE TECNOLOGIA E INFORMATICA"
        
        if typeCharge == "1172":
            return "JEFE DE INFRAESTRUCTURA"
        
        if typeCharge == "151":
            return "JEFE DE MANTENIMIENTO"
        
        if typeCharge == "141":
            return "JEFE DE NOMINA"
        
        if typeCharge == "1198":
            return "JEFE DE OPERACIONES"
        
        if typeCharge == "0140":
            return "JEFE DE PERSONAL"
        
        if typeCharge == "1133":
            return "JEFE DE SELECCION"
        
        if typeCharge == "0141":
            return "JEFE DE TESORERIA"
        
        if typeCharge == "1132":
            return "JEFE DE PLANEACION Y ANALISIS FINANCIERO"
        
        if typeCharge == "143":
            return "JEFE SST"
        
        if typeCharge == "0440":
            return "JUGOS Y BEBIDAS"
        
        if typeCharge == "2084":
            return "LIDER DE ALMACEN NO PERECEDERO"
        
        if typeCharge == "2079":
            return "LIDER DE BIENESTAR Y CULTURA ORGANIZACIO"
        
        if typeCharge == "2102":
            return "LIDER CARNES Y POLLO"
        
        if typeCharge == "2034":
            return "LIDER CAVA POLLO"
        
        if typeCharge == "2035":
            return "LIDER CAVA VERDURAS"
        
        if typeCharge == "2039":
            return "LIDER COCINA"
        
        if typeCharge == "1191":
            return "LIDER COCINA 1"
        
        if typeCharge == "1193":
            return "LIDER COCINA 3"
        
        if typeCharge == "2036":
            return "LIDER COCINA 4"
        
        if typeCharge == "2038":
            return "LIDER COCINA DE MASA"
        
        if typeCharge == "2113":
            return "LIDER COCINA PRINCIPAL PRODUCTO"
        
        if typeCharge == "1170":
            return "LIDER COMUNICARTE Y TRANSFORMARTE"
        
        if typeCharge == "2015":
            return "LIDER CONTROL INTERNO Y MEJORA CONTINUA"
        
        if typeCharge == "1179":
            return "LIDER CS TIC"
        
        if typeCharge == "2061":
            return "LIDER DE CALIDAD"
        
        if typeCharge == "1182":
            return "LIDER DE CALL CENTER"
        
        if typeCharge == "1189":
            return "LIDER DE CAVA DE CARNE"
        
        if typeCharge == "2115":
            return "LIDER DE COCINA 2"
        
        if typeCharge == "2065":
            return "LIDER DE COCINA 5"
        
        if typeCharge == "2103":
            return "LIDER DE COCINA 6 (MIX)"
        
        if typeCharge == "1185":
            return "LIDER DE COCINA FRIA"
        
        if typeCharge == "2013":
            return "LIDER DE CONTABILIDAD"
        
        if typeCharge == "1199":
            return "LIDER DE COSTOS"
        
        if typeCharge == "1201":
            return "LIDER DE LOGISTICA"
        
        if typeCharge == "1208":
            return "LIDER DE MANTENIMIENTO PDV"

        if typeCharge == "1209":
            return "LIDER DE MANTENIMIENTO DE PPP"
        
        if typeCharge == "1180":
            return "LIDER DE NOMINA"
        
        if typeCharge == "2099":
            return "LIDER DE OPERACIONES PUNTO DE"
        
        if typeCharge == "2104":
            return "LIDER DE PANADERIA"
        
        if typeCharge == "1194":
            return "LIDER DE PDV"
        
        if typeCharge == "2096":
            return "LIDER DE PRODUCTO"
        
        if typeCharge == "2105":
            return "LIDER DE SOSTENIBILIDAD"
        
        if typeCharge == "2020":
            return "LIDER DE SST"
        
        if typeCharge == "1183":
            return "LIDER DE TESORERIA"
        
        if typeCharge == "1174":
            return "LIDER DE TI"
        
        if typeCharge == "1186":
            return "LIDER DE VENTAS BB"
        
        if typeCharge == "1164":
            return "LIDER DE VERDURAS"
        
        if typeCharge == "2042":
            return "LIDER DE ZONA"
        
        if typeCharge == "1200":
            return "LIDER DE DESPACHOS Y DISTRIBUCION"

        if typeCharge == "1150":
            return "LIDER DULCES"
        
        if typeCharge == "1151":
            return "LIDER EMPAQUE ALMACENAMIENTO DE SALSAS"
        
        if typeCharge == "1148":
            return "LIDER FORMULACION LIQUIDOS"
        
        if typeCharge == "2068":
            return "LIDER DE GESTION ACTIVOS FIJOS"
        
        if typeCharge == "2088":
            return "LIDER LOGISTICA ALMACEN PERECEDERO"
        
        if typeCharge == "2037":
            return "LIDER PREALISTAMIENTO VERDURAS"
        
        if typeCharge == "1127":
            return "LIDER SEC DE HELADOS"
        
        if typeCharge == "2057":
            return "LIDER DE SERVICIOS ADMINISTRATIVOS"
        
        if typeCharge == "2030":
            return "LIDER DE VENTA NO PRESENTE"
        
        if typeCharge == "0450":
            return "MARISCOS"
        
        if typeCharge == "0460":
            return "MESAS"
        
        if typeCharge == "0470":
            return "MESAS FIN DE SEMANA"
        
        if typeCharge == "0110":
            return "ASEO PLATERO"
        
        if typeCharge == "0050":
            return "ADMINISTRADORA FIN S"
        
        if typeCharge == "0040":
            return "ADMINIST FIN SEMANA"
        
        if typeCharge == "0495":
            return "OFICIOS VARIOS"
        
        if typeCharge == "0500":
            return "PITAS Y ENSALADAS"
        
        if typeCharge == "0510":
            return "PLANCHA"
        
        if typeCharge == "0540":
            return "PLANCHA SAL"
        
        if typeCharge == "0550":
            return "PLATERO"
        
        if typeCharge == "0560":
            return "PLATERO Y ASEO"
        
        if typeCharge == "0570":
            return "POSTRES Y HELADOS"
        
        if typeCharge == "0163":
            return "AUXILIAR DE PRODUCCION"
        
        if typeCharge == "0701":
            return "PROFESIONAL EN GESTION AMBIENTAL"
        
        if typeCharge == "1104":
            return "PROFES MANTENIMIENTO"
        
        if typeCharge == "0192":
            return "PROGRAMADORA DE MANTENIMIENTO"
        
        if typeCharge == "0590":
            return "QUESOS CHOCOLATES"
        
        if typeCharge == "0610":
            return "REMPLAZO INCAPACIDAD"
        
        if typeCharge == "0630":
            return "SECRETARIA GERENCIA"
        
        if typeCharge == "650":
            return "SUPERNUMERARIA"
        
        if typeCharge == "1152":
            return "SUPERNUMERARIA"
        
        if typeCharge == "1192":
            return "SUPERNUMERARIO DE HELADOS"
        
        if typeCharge == "2114":
            return "SUPERVISOR DE RECIBO PERECEDERO"
        
        if typeCharge == "2116":
            return "SUPERVISOR ALMACEN"
        
        if typeCharge == "2025":
            return "SUPERVISORA PRODUCCION"
        
        if typeCharge == "2022":
            return "TECNICO LOCATIVO"
        
        if typeCharge == "1103":
            return "TECNICO MANTENIMIENTO"
        
        if typeCharge == "2023":
            return "TECNICO MANTENIMIENTO EQUIPOS"
        
        if typeCharge == "2078":
            return "TOSTADORA"

        return originalValue.upper()
    
    def _mapSeveranceFund(self, value: str) -> str:
        originalValue = " ".join(str(value or "").strip().split())

        if not originalValue:
            return "000"

        normalizedText = self._normalize(originalValue)

        if normalizedText in {"no aplica", "n/a", "na", "no"}:
            return "000"

        severanceFund = self._normalizeCode(originalValue, 2)

        if not severanceFund:
            return "000"

        if severanceFund == "04":
            return "COLFONDOS"
        
        if severanceFund == "03":
            return "COLPATRIA"
        
        if severanceFund == "08":
            return "FONDO NACIONAL DEL AHORRO"
        
        if severanceFund == "01":
            return "HORIZONTE"
        
        if severanceFund == "02":
            return "PORVENIR"
        
        if severanceFund == "05":
            return "PROTECCION"
        
        if severanceFund == "06":
            return "SANTANDER"
        
        if severanceFund == "07":
            return "SKANDIA"
        
        if severanceFund == "99":
            return "VARIOS"

        return originalValue.upper()
    
    def _mapPensionFund(self, value: str, typeChargeValue: str, workCenterValue: str) -> str:
        pensionFund = str(value or "").strip()
        typeCharge = self._normalizeCode(typeChargeValue, 4)
        workCenter = self._normalizeCode(workCenterValue, 2)

        if typeCharge == "0060" and workCenter.startswith("03"):
            return "P000"

        if pensionFund == "09":
            return "COLFONDOS PENSIONES Y CESANTIAS"
        
        if pensionFund == "01":
            return "COLPENSIONES"
        
        if pensionFund == "08":
            return "COOPERATIVA DE SALUD Y DESARROLLO INTEGR"
        
        if pensionFund == "02":
            return "HORIZONTE"
        
        if pensionFund == "06":
            return "NUEVA EPS"
        
        if pensionFund == "12":
            return "PENSION APRENDICES"
        
        if pensionFund == "03":
            return "PORVENIR"
        
        if pensionFund == "04":
            return "PROTECCION"
        
        if pensionFund == "10":
            return "SANTANDER"

        if pensionFund == "16":
            return "SKANDIA"
        
        if pensionFund == "99":
            return "VARIOS"

        return ""
    
    def _mapEPS(self, value: str) -> str:
        originalValue = " ".join(str(value or "").strip().split())

        if not originalValue:
            return "000"

        normalizedText = self._normalize(originalValue)

        if normalizedText in {"no aplica", "n/a", "na", "no"}:
            return "000"

        eps = self._normalizeCode(originalValue, 2)

        if not eps:
            return "S000"

        if eps == "79":
            return "ADMINISTRADORA DE LOS RECURSOS DEL SISTE"
        
        if eps == "53":
            return "ALIANSALUD"
        
        if eps == "70":
            return "ASOCIACION MUTUAL EMPRESA SOLIDARIA EMSS"
        
        if eps == "69":
            return "ASOCIACION MUTUAL LA ESPERANZA ASMET ESS"
        
        if eps == "75":
            return "ASOCIACION MUTUAL SER EMPRESA SOLIDARIA"
        
        if eps == "56":
            return "CAFESALUD"
        
        if eps == "73":
            return "CAJA DE COMPENSACION FAMILIAR CAJACOPI A"
        
        if eps == "74":
            return "CAJA DE COMPENSACION FAMILIAR DEL CHOCO"
        
        if eps == "71":
            return "CAPITAL SALUD ENTIDAD PROMOTORA DE SALUD"

        if eps == "59":
            return "COLPATRIA SALUD"
        
        if eps == "54":
            return "COMFENALCO"
        
        if eps == "78":
            return "COMPENSAR"
        
        if eps == "65":
            return "CONSORCIO SYAP 2011"
        
        if eps == "52":
            return "COOMEVA"
        
        if eps == "67":
            return "COOPERATIVA DE SALUD COMUNITARIA COMPART"
        
        if eps == "08":
            return "COOPERATIVA DE SALUD Y DESARROLLO INTEGR"
        
        if eps == "80":
            return "COOSALUD ENTIDAD PROMOTORA DE SALUD S A"
        
        if eps == "55":
            return "CRUZ BLANCA"
        
        if eps == "51":
            return "E.P.S. SANITAS"
        
        if eps == "66":
            return "ENTIDAD COOPERATIVA SOLIDARIA DE SALUD E"

        if eps == "50":
            return "EPS SURA"
        
        if eps == "62":
            return "FAMISANAR"
    
        if eps == "77":
            return "MEDIMAS EPS SAS"
        
        if eps == "76":
            return "NUEVA EMPRESA PROMOTRORA DE SALUD"
        
        if eps == "06":
            return "NUEVA EPS"
        
        if eps == "58":
            return "SALUD TOTAL"
        
        if eps == "60":
            return "SALUD VIDA"
        
        if eps == "57":
            return "SALUDCOOP"

        if eps == "07":
            return "SAVIA SALUD"
        
        if eps == "61":
            return "SERVICIO OCCIDENTAL DE SALUD"
        
        if eps == "99":
            return "VARIOS"

        return originalValue.upper()
    
    def _mapSalaryType(self, value: str) -> str:
        salaryType = str(value or "").strip()

        if not salaryType:
            return "000"

        normalizedSalaryType = self._normalize(salaryType)
        normalizedCode = self._normalizeCode(salaryType, 4)

        if normalizedCode == "0060":
            return "003"

        if "aprendiz" in normalizedSalaryType:
            return "003"

        return "001"

    def _mapEmployeeSalaryType(self, value: str) -> str:
        contributor = self._normalize(value)

        if not contributor:
            return "F"

        if "aprendiz" in contributor and "lectiva" in contributor:
            return "V"

        return "F"

    def _mapContributor(self, value: str) -> str:
        contributor = self._normalize(value)

        if not contributor:
            return "1"

        if "aprendiz" in contributor and "lectiva" in contributor:
            return "12"

        if "aprendiz" in contributor and "productiva" in contributor:
            return "19"

        return "1"

    def _mapContractType(self, typeChargeValue: str, workCenterValue: str) -> str:
        
        print(f"[DEBUG] tipoCargo={typeChargeValue}")
        print(f"[DEBUG] centroTrabajo={workCenterValue}")

        typeCharge = self._normalizeCode(typeChargeValue, 4)
        workCenter = self._normalizeCode(workCenterValue, 2)

        if typeCharge == "0060" and workCenter.startswith("03"):
            return "4"

        if typeCharge == "0060" and workCenter.startswith("01"):
            return "5"

        return "2"
    
    def _mapContractType2(self, typeChargeValue: str) -> str:
        typeCharge = self._normalize(typeChargeValue)

        if not typeCharge:
            return "2"

        if "aprendiz" in typeCharge and "lectiva" in typeCharge:
            return "4"

        if "aprendiz" in typeCharge and "productiva" in typeCharge:
            return "5"

        return "2"
    
    def _normalizeCode(self, value: str, width: int) -> str:
        text = str(value or "").strip()

        if not text:
            return ""

        text = text.replace(",", ".")

        try:
            numericValue = float(text)

            if numericValue.is_integer():
                text = str(int(numericValue))
        except ValueError:
            pass

        if text.isdigit():
            return text.zfill(width)

        return text
    
    def _mapBirthCity(self, value: str) -> str:
        birthCity = str(value or "").strip()

        if not birthCity:
            return ""

        birthCity = birthCity.replace(",", ".")

        try:
            numericValue = float(birthCity)

            if numericValue.is_integer():
                birthCity = str(int(numericValue))
        except ValueError:
            pass

        birthCity = "".join(character for character in birthCity if character.isdigit())

        birthCities = {
            "00000000": "CIUDAD DE NACIMIENTO NO EXISTE",
            "04701001": "CURACAO",
            "16925001": "BOGOTA",
            "19601001": "SAN JOSE",
            "23901001": "QUITO",
            "24904001": "NEW YORK",
            "34202001": "AALSMEER",
            "50002001": "OVALLE",
            "58902001": "LIMA",
            "61101001": "SAN JUAN",
            "77005001": "MEDELLIN",
            "77005002": "ABEJORRAL",
            "77005004": "ABRIAQUI",
            "77005021": "ALEJANDRIA",
            "77005030": "AMAGA",
            "77005031": "AMALFI",
            "77005034": "ANDES",
            "77005036": "ANGELOPOLIS",
            "77005038": "ANGOSTURA",
            "77005040": "ANORI",
            "77005042": "ANTIOQUIA",
            "77005044": "ANZA",
            "77005045": "APARTADO",
            "77005051": "ARBOLETES",
            "77005055": "ARGELIA",
            "77005059": "ARMENIA",
            "77005079": "BARBOSA",
            "77005086": "BELMIRA",
            "77005088": "BELLO",
            "77005091": "BETANIA",
            "77005093": "BETULIA",
            "77005101": "BOLIVAR",
            "77005107": "BRICE#O",
            "77005113": "BURITICA",
            "77005120": "CACERES",
            "77005125": "CAICEDO",
            "77005129": "CALDAS",
            "77005134": "CAMPAMENTO",
            "77005138": "CA#ASGORDAS",
            "77005142": "CARACOLI",
            "77005145": "CARAMANTA",
            "77005147": "CAREPA",
            "77005148": "CARMEN DE VIBORAL",
            "77005150": "CAROLINA",
            "77005154": "CAUCASIA",
            "77005172": "CHIGORODO",
            "77005190": "CISNEROS",
            "77005197": "COCORNA",
            "77005206": "CONCEPCION",
            "77005209": "CONCORDIA",
            "77005212": "COPACABANA",
            "77005234": "DABEIBA",
            "77005237": "DON MATIAS",
            "77005240": "EBEJICO",
            "77005250": "EL BAGRE",
            "77005264": "ENTRERRIOS",
            "77005266": "ENVIGADO",
            "77005282": "FREDONIA",
            "77005284": "FRONTINO",
            "77005306": "GIRALDO",
            "77005308": "GIRARDOTA",
            "77005310": "GOMEZ PLATA",
            "77005313": "GRANADA",
            "77005315": "GUADALUPE",
            "77005318": "GUARNE",
            "77005321": "GUATAPE",
            "77005347": "HELICONIA",
            "77005360": "ITAGUI",
            "77005361": "ITUANGO",
            "77005364": "JARDIN",
            "77005368": "JERICO",
            "77005376": "LA CEJA",
            "77005380": "LA ESTRELLA",
            "77005400": "LA UNION",
            "77005411": "LIBORINA",
            "77005425": "MACEO",
            "77005440": "MARINILLA",
            "77005467": "MONTEBELLO",
            "77005475": "MURINDO",
            "77005480": "MUTATA",
            "77005483": "NARI#O",
            "77005490": "NECOCLI",
            "77005495": "NECHI",
            "77005501": "OLAYA",
            "77005541": "PE#OL",
            "77005543": "PEQUE",
            "77005576": "PUEBLORRICO",
            "77005579": "PUERTO BERRIO",
            "77005585": "PTO NARE(LAMAGDALENA)",
            "77005591": "PUERTO TRIUNFO",
            "77005604": "REMEDIOS",
            "77005607": "RETIRO",
            "77005615": "RIONEGRO",
            "77005628": "SABANALARGA",
            "77005631": "SABANETA",
            "77005642": "SALGAR",
            "77005647": "SAN ANDRES",
            "77005649": "SAN CARLOS",
            "77005652": "SAN FRANCISCO",
            "77005656": "SAN JERONIMO",
            "77005659": "SAN JUAN DE URABA",
            "77005660": "SAN LUIS",
            "77005664": "SAN PEDRO",
            "77005665": "SAN PEDRO DE URABA",
            "77005667": "SAN RAFAEL",
            "77005670": "SAN ROQUE",
            "77005674": "SAN VICENTE",
            "77005679": "SANTA BARBARA",
            "77005686": "SANTA ROSA DE OSOS",
            "77005690": "SANTO DOMINGO",
            "77005697": "SANTUARIO",
            "77005736": "SEGOVIA",
            "77005756": "SONSON",
            "77005761": "SOPETRAN",
            "77005789": "TAMESIS",
            "77005790": "TARAZA",
            "77005792": "TARSO",
            "77005809": "TITIRIBI",
            "77005819": "TOLEDO",
            "77005837": "TURBO",
            "77005842": "URAMITA",
            "77005847": "URRAO",
            "77005854": "VALDIVIA",
            "77005856": "VALPARAISO",
            "77005858": "VEGACHI",
            "77005861": "VENECIA",
            "77005873": "VIGIA DEL FUERTE",
            "77005885": "YALI",
            "77005887": "YARUMAL",
            "77005890": "YOLOMBO",
            "77005893": "YONDO",
            "77005895": "ZARAGOZA",
            "77008001": "BARRANQUILLA",
            "77008137": "CAMPO D LA CRUZ",
            "77008141": "CANDELARIA",
            "77008296": "GALAPA",
            "77008421": "LURUACO",
            "77008433": "MALAMBO",
            "77008436": "MANATI",
            "77008606": "REPELON",
            "77008634": "SABANAGRANDE",
            "77008675": "SANTA LUCIA",
            "77008685": "SANTO TOMAS",
            "77008758": "SOLEDAD",
            "77013001": "CARTAGENA",
            "77013006": "ACHI",
            "77013052": "ARJONA",
            "77013140": "CALAMAR",
            "77013212": "CORDOBA",
            "77013244": "EL CARMEN DE BOLIVAR",
            "77013430": "MAGANGUE",
            "77013440": "MARGARITA",
            "77013442": "MARIA LA BAJA",
            "77013468": "MOMPOS",
            "77013473": "MORALES",
            "77013549": "PINILLOS",
            "77013647": "SAN ESTANISLAO",
            "77013650": "SAN FERNANDO",
            "77013654": "SAN JACINTO",
            "77013667": "SAN MARTIN DE LOBA",
            "77013670": "SAN PABLO",
            "77013673": "SANTA CATALINA",
            "77013683": "SANTA ROSA",
            "77013688": "SANTA ROSA DEL SUR",
            "77013744": "SIMITI",
            "77013760": "SOPLAVIENTO",
            "77013836": "TURBACO",
            "77013873": "VILLANUEVA",
            "77015001": "TUNJA",
            "77015104": "BOYACA",
            "77015106": "BRICENO",
            "77015109": "BUENAVISTA",
            "77015176": "CHIQUINQUIRA",
            "77015183": "CHITA",
            "77015238": "DUITAMA",
            "77015469": "MONIQUIRA",
            "77015514": "PAEZ",
            "77015516": "PAIPA",
            "77015572": "PUERTO BOYACA",
            "77015580": "QUIPAMA",
            "77015646": "SAMACA",
            "77015667": "SAN LUIS DE GACENO",
            "77015690": "SANTA MARIA",
            "77015753": "SOATA",
            "77017001": "MANIZALES",
            "77017013": "AGUADAS",
            "77017042": "ANSERMA",
            "77017088": "BELALCAZAR",
            "77017174": "CHINCHINA",
            "77017272": "FILADELFIA",
            "77017380": "LA DORADA",
            "77017444": "MARQUETALIA",
            "77017486": "NEIRA",
            "77017513": "PACORA",
            "77017541": "PENSILVANIA",
            "77017614": "RIOSUCIO",
            "77017616": "RISARALDA",
            "77017653": "SALAMINA",
            "77017662": "SAMANA",
            "77017777": "SUPIA",
            "77017877": "VITERBO",
            "77018001": "FLORENCIA",
            "77018029": "ALBANIA",
            "77018610": "SAN JOSE DE FRAGUA",
            "77018753": "SAN VICENTE DEL CAGUAN",
            "77019001": "POPAYAN",
            "77019075": "BALBOA",
            "77019142": "CALOTO",
            "77019256": "EL TAMBO",
            "77019318": "GUAPI",
            "77019364": "JAMBALO",
            "77019392": "LA SIERRA",
            "77019397": "LA VEGA",
            "77019418": "LOPEZ",
            "77019450": "MERCADERES",
            "77019455": "MIRANDA",
            "77019573": "PUERTO TEJADA",
            "77019698": "SANTANDER DE QUILICHAO",
            "77019809": "TIMBIQUI",
            "77020001": "VALLEDUPAR",
            "77020011": "AGUACHICA",
            "77020013": "AGUSTIN CODAZZI",
            "77020032": "ASTREA",
            "77020045": "BECERRIL",
            "77020060": "BOSCONIA",
            "77020175": "CHIMICHAGUA",
            "77020250": "EL PASO",
            "77020383": "LA GLORIA",
            "77020443": "MANAURE BALCON DL CESAR",
            "77020517": "PAILITAS",
            "77020621": "LA PAZ",
            "77020710": "SAN ALBERTO",
            "77020787": "TAMALAMEQUE",
            "77023001": "MONTERIA",
            "77023068": "AYAPEL",
            "77023090": "CANALETE",
            "77023162": "CERETE",
            "77023168": "CHIMA",
            "77023182": "CHINU",
            "77023189": "CIENAGA DE ORO",
            "77023417": "LORICA",
            "77023419": "LOS CORDOBAS",
            "77023466": "MONTELIBANO",
            "77023555": "PLANETA RICA",
            "77023570": "PUEBLO NUEVO",
            "77023574": "PUERTO ESCONDIDO",
            "77023580": "PUERTO LIBERTADOR",
            "77023660": "SAHAGUN",
            "77023670": "SAN ANDRES SOTAVENTO",
            "77023672": "SAN ANTERO",
            "77023675": "SAN BERNARDO DEL VIENTO",
            "77023686": "SAN PELAYO",
            "77023807": "TIERRALTA",
            "77023855": "VALENCIA",
            "77025099": "BOJACA",
            "77025126": "CAJICA",
            "77025175": "CHIA",
            "77025183": "CHOCONTA",
            "77025269": "FACATATIVA",
            "77025281": "FOSCA",
            "77025290": "FUSAGASUGA",
            "77025307": "GIRARDOT",
            "77025320": "GUADUAS",
            "77025322": "GUASCA",
            "77025377": "LA CALERA",
            "77025386": "LA MESA",
            "77025426": "MACHETA",
            "77025430": "MADRID",
            "77025436": "MANTA",
            "77025513": "PACHO",
            "77025518": "PAIME",
            "77025572": "PUERTO SALGAR",
            "77025649": "SAN BERNARDO",
            "77025740": "SIBATE",
            "77025754": "SOACHA",
            "77025817": "TOCANCIPA",
            "77025843": "UBATE",
            "77025875": "VILLETA",
            "77027001": "QUIBDO",
            "77027006": "ACANDI",
            "77027025": "ALTO BAUDO",
            "77027073": "BAGADO",
            "77027075": "BAHIA SOLANO",
            "77027077": "BAJO BAUDO",
            "77027099": "BOJAYA",
            "77027205": "CONDOTO",
            "77027245": "EL CARMEN",
            "77027361": "ITSMINA",
            "77027413": "LLORO",
            "77027491": "NOVITA",
            "77027495": "NUQUI",
            "77027660": "SAN JOSE DEL PALMAR",
            "77027745": "SIPI",
            "77027787": "TADO",
            "77027800": "UNGUIA",
            "77041001": "NEIVA",
            "77041016": "AIPE",
            "77041206": "COLOMBIA",
            "77041551": "PITALITO",
            "77041770": "SUAZA",
            "77044001": "RIOHACHA",
            "77044078": "BARRANCAS",
            "77044279": "FONSECA",
            "77044430": "MAICAO",
            "77044650": "SAN JUAN DEL CESAR",
            "77044847": "URIBIA",
            "77047001": "SANTA MARTA",
            "77047058": "ARIGUANI",
            "77047161": "CERRO SAN ANTONIO",
            "77047170": "CHIVOLO",
            "77047189": "CIENAGA",
            "77047245": "EL BANCO",
            "77047288": "FUNDACION",
            "77047318": "GUAMAL",
            "77047541": "PEDRAZA",
            "77047555": "PLATO",
            "77047707": "SANTA ANA",
            "77047798": "TENERIFE",
            "77050001": "VILLAVICENCIO",
            "77050573": "PUERTO LOPEZ",
            "77050606": "RESTREPO",
            "77050711": "VISTA HERMOSA",
            "77052001": "PASTO",
            "77052079": "BARBACOAS",
            "77052110": "BUESACO",
            "77052250": "EL CHARCO",
            "77052356": "IPIALES",
            "77052381": "LA FLORIDA",
            "77052490": "OLAYA HERRERA",
            "77052565": "PROVIDENCIA",
            "77052683": "SANDONA",
            "77052835": "TUMACO",
            "77052838": "TUQUERRES",
            "77054001": "CUCUTA",
            "77054003": "ABREGO",
            "77054172": "CHINACOTA",
            "77054344": "HACARI",
            "77054405": "LOS PATIOS",
            "77054498": "OCA#A",
            "77054518": "PAMPLONA",
            "77054599": "RAGONVALIA",
            "77054800": "TEORAMA",
            "77054810": "TIBU",
            "77054874": "VILLA DEL ROSARIO",
            "77063130": "CALARCA",
            "77063272": "FILANDIA",
            "77063302": "GENOVA",
            "77063401": "LA TEBAIDA",
            "77063470": "MONTENEGRO",
            "77063548": "PIJAO",
            "77063690": "SALENTO",
            "77066001": "PEREIRA",
            "77066088": "BELEN DE UMBRIA",
            "77066170": "DOS QUEBRADAS",
            "77066318": "GUATICA",
            "77066400": "LA VIRGINIA",
            "77066440": "MARSELLA",
            "77066572": "PUEBLO RICO",
            "77066594": "QUINCHIA",
            "77066682": "SANTA ROSA DE CABAL",
            "77068001": "BUCARAMANGA",
            "77068013": "AGUADA",
            "77068051": "ARATOCA",
            "77068081": "BARRANCABERMEJA",
            "77068152": "CARCASI",
            "77068167": "CHARALA",
            "77068190": "CIMITARRA",
            "77068250": "EL PE#ON",
            "77068276": "FLORIDABLANCA",
            "77068368": "JESUS MARIA",
            "77068573": "PUERTO PARRA",
            "77068655": "SABANA DE TORRES",
            "77068673": "SAN BENITO",
            "77068679": "SAN GIL",
            "77068689": "SAN VICENTE DE CHUCURI",
            "77068755": "SOCORRO",
            "77068770": "SUAITA",
            "77068773": "SUCRE",
            "77070001": "SINCELEJO",
            "77070124": "CAIMITO",
            "77070204": "COLOSO",
            "77070215": "COROZAL",
            "77070265": "GUARANDA",
            "77070429": "MAJAGUAL",
            "77070473": "MORROA",
            "77070508": "OVEJAS",
            "77070523": "PALMITO",
            "77070670": "SAMPUES",
            "77070678": "SAN BENITO ABAD",
            "77070702": "SAN JUAN DE BETULIA",
            "77070708": "SAN MARCOS",
            "77070713": "SAN ONOFRE",
            "77070742": "SINCE",
            "77070820": "TOLU",
            "77070823": "TOLUVIEJO",
            "77073001": "IBAGUE",
            "77073026": "ALVARADO",
            "77073055": "ARMERO",
            "77073152": "CASABIANCA",
            "77073268": "ESPINAL",
            "77073283": "FRESNO",
            "77073319": "GUAMO",
            "77073349": "HONDA",
            "77073411": "LIBANO",
            "77073449": "MELGAR",
            "77073555": "PLANADAS",
            "77073616": "RIOBLANCO",
            "77073675": "SAN ANTONIO",
            "77076001": "CALI",
            "77076109": "BUENAVENTURA",
            "77076111": "BUGA",
            "77076113": "BUGALAGRANDE",
            "77076122": "CAICEDONIA",
            "77076147": "CARTAGO",
            "77076246": "EL CAIRO",
            "77076248": "EL CERRITO",
            "77076250": "EL DOVIO",
            "77076275": "FLORIDA",
            "77076364": "JAMUNDI",
            "77076497": "OBANDO",
            "77076520": "PALMIRA",
            "77076616": "RIOFRIO",
            "77076736": "SEVILLA",
            "77076823": "TORO",
            "77076828": "TRUJILLO",
            "77076834": "TULUA",
            "77076892": "YUMBO",
            "77081001": "ARAUCA",
            "77081736": "SARAVENA",
            "77081794": "TAME",
            "77085001": "YOPAL",
            "77085410": "TAURAMENA",
            "77086001": "MOCOA",
            "77086568": "PUERTO ASIS",
            "77091001": "LETICIA",
            "77091540": "PUERTO NARI#O",
            "77095001": "SAN JOSE DEL GUAVIARE",
            "77095025": "EL RETORNO",
            "77099001": "PUERTO CARRENO",
            "77101001": "CARACAS",
            "85002001": "SAN ANTONIO DEL TACHIRA",
        }

        return birthCities.get(birthCity, "")
    
    def _mapBirthCountryName(self, value: str) -> str:
        birthCity = self._cleanNumericCode(value)

        if not birthCity or birthCity == "00000000":
            return "000"

        if birthCity.startswith("770"):
            return "COLOMBIANO"

        if birthCity.startswith("771") or birthCity.startswith("850"):
            return "VENEZOLANO"

        return "EXTRANJERO"


    def _mapBirthDepartmentName(self, value: str) -> str:
        birthCity = self._cleanNumericCode(value)

        if not birthCity or birthCity == "00000000":
            return "000"

        if birthCity.startswith("771") or birthCity.startswith("850"):
            return self._mapBirthCity(birthCity)

        if not birthCity.startswith("770"):
            return self._mapBirthCity(birthCity)

        departmentCode = birthCity[3:5]

        departments = {
            "05": "ANTIOQUIA",
            "08": "ATLANTICO",
            "11": "BOGOTA",
            "13": "BOLIVAR",
            "15": "BOYACA",
            "17": "CALDAS",
            "18": "CAQUETA",
            "19": "CAUCA",
            "20": "CESAR",
            "23": "CORDOBA",
            "25": "CUNDINAMARCA",
            "27": "CHOCO",
            "41": "HUILA",
            "44": "LA GUAJIRA",
            "47": "MAGDALENA",
            "50": "META",
            "52": "NARIÑO",
            "54": "NORTE DE SANTANDER",
            "63": "QUINDIO",
            "66": "RISARALDA",
            "68": "SANTANDER",
            "70": "SUCRE",
            "73": "TOLIMA",
            "76": "VALLE DEL CAUCA",
            "81": "ARAUCA",
            "85": "CASANARE",
            "86": "PUTUMAYO",
            "91": "AMAZONAS",
            "95": "GUAVIARE",
            "99": "VICHADA",
        }

        return departments.get(departmentCode, "000")
    
    def _mapBirthDepartment(self, value: str) -> str:
        place = self._normalize(value)

        if not place:
            return ""

        place = (
            place.replace(".", " ")
            .replace(",", " ")
            .replace("-", " ")
            .replace("/", " ")
        )

        place = " ".join(place.split())

        if not place:
            return ""

        foreignPlaces = [
            "venezuela",
            "caracas",
            "maracaibo",
            "merida",
            "tachira",
            "zulia",
            "aragua",
            "guarico",
            "lara",
            "ecuador",
            "suiza",
        ]

        if any(foreignPlace in place for foreignPlace in foreignPlaces):
            return ""

        departmentKeywords = {
            "valle del cauca": "VALLE DEL CAUCA",
            "norte de santander": "NORTE DE SANTANDER",
            "cundinamarca": "CUNDINAMARCA",
            "antioquia": "ANTIOQUIA",
            "atlantico": "ATLANTICO",
            "bolivar": "BOLIVAR",
            "boyaca": "BOYACA",
            "caldas": "CALDAS",
            "caqueta": "CAQUETA",
            "cauca": "CAUCA",
            "cesar": "CESAR",
            "choco": "CHOCO",
            "cordoba": "CORDOBA",
            "guajira": "LA GUAJIRA",
            "huila": "HUILA",
            "magdalena": "MAGDALENA",
            "meta": "META",
            "narino": "NARIÑO",
            "putumayo": "PUTUMAYO",
            "quindio": "QUINDIO",
            "risaralda": "RISARALDA",
            "santander": "SANTANDER",
            "sucre": "SUCRE",
            "tolima": "TOLIMA",
        }

        for keyword, department in departmentKeywords.items():
            if keyword in place:
                return department

        placesByDepartment = {
            "BOGOTA D.C.": [
                "bogota", "bogota dc", "bogota d c", "suba", "bosa", "kennedy",
                "usme", "engativa", "fontibon", "tunjuelito", "chapinero",
                "puente aranda", "ciudad bolivar", "rafael uribe", "antonio narino",
                "usaquen", "san cristobal sur",
            ],
            "ANTIOQUIA": [
                "medellin", "bello", "itagui", "envigado", "rionegro", "apartado",
                "turbo", "carepa", "chigorodo", "dabeiba", "vigia del fuerte",
                "ituango", "el bagre", "taraza", "caucasia", "yarumal", "urrao",
                "frontino", "sonson", "san roque", "arboletes", "necocli", "mutata",
                "canasgordas", "salgar", "concordia", "santa barbara", "jardin",
                "jerico", "tamesis", "marinilla", "la ceja", "retiro", "girardota",
                "copacabana", "barbosa", "amaga", "andes", "abejorral", "uramita",
                "puerto berrio", "liborina", "valdivia", "vegachi", "san francisco",
                "cocorna", "amalfi", "segovia", "titiribi", "betulia", "campamento",
                "yolombo", "san rafael", "alejandria", "peque", "san jeronimo",
                "san carlos", "caldas",
            ],
            "CHOCO": [
                "quibdo", "tado", "istmina", "condoto", "unguia", "riosucio",
                "bojaya", "alto baudo", "bajo baudo", "novita", "nuqui", "bagado",
                "bahia solano", "acandi", "lloro", "rio quito", "pizarro",
            ],
            "CORDOBA": [
                "monteria", "lorica", "ayapel", "montelibano", "tierralta",
                "sahagun", "chinu", "san pelayo", "planeta rica", "cerete",
                "puerto escondido", "canalete", "buenavista", "monitos",
                "pueblo nuevo", "valencia", "san bernardo del viento",
            ],
            "BOLIVAR": [
                "cartagena", "cartagena de indias", "magangue", "mompox", "mompos",
                "san jacinto", "san martin de loba", "achi", "maria la baja",
                "arjona", "turbaco", "san fernando", "mahates", "santa catalina",
                "san estanislao", "simiti", "arenal", "zambrano",
            ],
            "ATLANTICO": [
                "barranquilla", "soledad", "malambo", "luruaco", "baranoa",
                "puerto colombia", "santo tomas", "sabanalarga", "suan",
            ],
            "CESAR": [
                "valledupar", "bosconia", "agustin codazzi", "curumani",
                "chimichagua", "la paz", "astrea",
            ],
            "MAGDALENA": [
                "santa marta", "cienaga", "fundacion", "plato", "ariguani",
                "pivijay", "guamal", "zona bananera", "el banco", "santa ana",
                "pueblo viejo", "nueva granada",
            ],
            "SUCRE": [
                "sincelejo", "corozal", "san marcos", "san onofre", "morroa",
                "ovejas", "majagual", "san benito abad", "since", "guaranda",
                "caimito", "los palmitos", "tolu", "tolu viejo",
            ],
            "LA GUAJIRA": [
                "riohacha", "maicao", "uribia", "fonseca",
            ],
            "SANTANDER": [
                "bucaramanga", "barrancabermeja", "socorro", "charala",
                "barbosa santander", "rionegro santander", "malaga", "ocamonte",
                "floridablanca", "piedecuesta", "sabana de torres", "mogotes",
                "puente nacional", "landazuri", "cimitarra",
            ],
            "NORTE DE SANTANDER": [
                "cucuta", "chinacota", "pamplona", "villa del rosario", "tibu",
            ],
            "BOYACA": [
                "tunja", "duitama", "sogamoso", "paipa", "moniquira",
                "chiquinquira", "ramiriqui", "turmeque", "guateque", "sotaquira",
                "mongui", "chitaraque", "saboya", "iza", "gameza", "tibana",
                "muzo", "toca", "otanche", "quipama",
            ],
            "CUNDINAMARCA": [
                "soacha", "facatativa", "fusagasuga", "girardot", "chia",
                "zipaquira", "guasca", "cachipay", "choachi", "lenguazaque",
                "arbelaez", "la mesa", "viota", "sopo", "pasca", "junin",
                "yacopi", "ubala", "gacheta", "madrid", "choconta", "fuquene",
                "paime", "la pena",
            ],
            "VALLE DEL CAUCA": [
                "cali", "palmira", "buenaventura", "yumbo", "zarzal", "tulua",
                "buga", "cartago", "florida", "jamundi", "ansermanuevo",
                "cerrito", "trujillo", "obando",
            ],
            "CAUCA": [
                "popayan", "el tambo", "patia", "el bordo", "santander de quilichao",
                "guapi", "timbiqui", "rosas", "miranda", "balboa", "paez",
                "inza", "caloto", "mercaderes", "la sierra",
            ],
            "NARIÑO": [
                "tumaco", "pasto", "ipiales", "barbacoas", "barbacoa",
                "magui", "el charco", "olaya herrera", "satinga",
            ],
            "RISARALDA": [
                "pereira", "dosquebradas", "santa rosa de cabal", "marsella",
                "quinchia", "belen de umbria", "guatica",
            ],
            "CALDAS": [
                "manizales", "viterbo", "filadelfia", "supia", "palestina",
                "aranzazu", "chinchina", "samana", "la dorada", "aguadas",
                "anserma",
            ],
            "TOLIMA": [
                "ibague", "melgar", "fresno", "planadas", "chaparral", "mariquita",
                "coyaima", "icononzo", "ortega", "purificacion", "honda",
                "alpujarra", "libano", "espinal", "flandes",
            ],
            "HUILA": [
                "neiva", "garzon", "pitalito", "la plata", "algeciras",
                "campoalegre", "la argentina", "tarqui",
            ],
            "META": [
                "villavicencio", "puerto lopez", "vista hermosa", "vistahermosa",
                "acacias", "granada", "san juan de arama", "lejanias",
                "mapiripan", "el castillo",
            ],
            "CAQUETA": [
                "florencia", "san jose del fragua", "san vicente del caguan",
                "cartagena del chaira",
            ],
            "PUTUMAYO": [
                "mocoa", "orito",
            ],
            "ARAUCA": [
                "arauca", "tame",
            ],
            "CASANARE": [
                "yopal", "tauramena", "villanueva casanare",
            ],
            "QUINDIO": [
                "armenia", "montenegro", "calarca",
            ],
            "GUAVIARE": [
                "san jose del guaviare",
            ],
            "AMAZONAS": [
                "puerto narino",
            ],
        }

        paddedPlace = f" {place} "

        for department, places in placesByDepartment.items():
            for knownPlace in places:
                if f" {knownPlace} " in paddedPlace:
                    return department

        return ""
    
    def _mapNewDecreeCodeByCharge(self, value: str) -> str:
        originalValue = " ".join(str(value or "").strip().split())

        if not originalValue:
            return ""

        charge = self._normalize(originalValue)
        chargeCode = self._normalizeCode(originalValue, 4)

        if chargeCode.isdigit():
            mappedCharge = self._mapTypeCharge(originalValue)
            charge = self._normalize(mappedCharge)

        if not charge:
            return ""
        
        if "teletrabajo" in charge:
            return "1829902"

        maintenanceKeywords = [
            "mantenimiento",
            "tecnico mantenimiento",
            "tecnico locativo",
            "refrigeracion",
            "mecanico",
            "obras",
        ]

        if any(keyword in charge for keyword in maintenanceKeywords):
            return "3331201"

        transportKeywords = [
            "transporte",
            "conductor",
            "auxiliar conductor",
            "mensajero",
            "domiciliario",
        ]

        if any(keyword in charge for keyword in transportKeywords):
            return "4492201"

        logisticsKeywords = [
            "logistica",
            "logistico",
            "almacen",
            "bodega",
            "inventario",
            "inventarios",
            "despacho",
            "despachos",
            "distribucion",
            "abastecimiento",
            "recibo",
            "cava",
        ]

        if any(keyword in charge for keyword in logisticsKeywords):
            return "2521001"

        productionKeywords = [
            "produccion",
            "planta",
            "cocina principal",
            "heladeria principal",
            "operario",
            "alistamiento",
            "empaque",
            "empacador",
            "enfriamiento",
            "reposteria",
            "quesos",
            "ensambles",
            "conos",
            "tostadora",
            "chef cocina principal",
        ]

        if any(keyword in charge for keyword in productionKeywords):
            return "2108901"

        administrativeKeywords = [
            "aprendiz lectiva",
            "aprendiz productiva",
            "aprendiz",
            "administrativo",
            "administrativa",
            "analista",
            "coordinador",
            "coordinadora",
            "director",
            "directora",
            "gerente general",
            "jefe",
            "lider",
            "tesoreria",
            "contabilidad",
            "nomina",
            "compras",
            "desarrollo humano",
            "tecnologia",
            "informatica",
            "calidad",
            "sst",
            "seguridad y salud",
            "facturacion",
            "costos",
            "bienestar",
            "legal",
            "financiero",
            "financiera",
            "impuestos",
            "mercadeo",
            "call center",
            "centro de experiencia",
        ]

        if any(keyword in charge for keyword in administrativeKeywords):
            return "1701001"

        pointSaleKeywords = [
            "punto de venta",
            "restaurante",
            "mesera",
            "mesero",
            "mesas",
            "auxiliar mesas",
            "camarero",
            "office",
            "cocinero",
            "cocina",
            "ayudante de cocina",
            "plancha",
            "plancha sal",
            "bebidas",
            "heladera",
            "postres",
            "pitas",
            "ensaladas",
            "crepera",
            "cajera",
            "cajero",
            "cajera comedor",
            "cajera helados",
            "steward",
            "platero",
            "capitana",
            "anfitrion",
            "saloneras",
            "aseo",
            "servicios generales",
        ]

        if any(keyword in charge for keyword in pointSaleKeywords):
            return "3561101"

        return "3561101"
    
    def _mapSaturdayWorkByCharge(self, value: str) -> str:
        originalValue = " ".join(str(value or "").strip().split())

        if not originalValue:
            return "S"

        charge = self._normalize(originalValue)
        chargeCode = self._normalizeCode(originalValue, 4)

        # Si viene como código de cargo, lo convierte primero al nombre del cargo
        if chargeCode.isdigit():
            mappedCharge = self._mapTypeCharge(originalValue)
            charge = self._normalize(mappedCharge)

        if not charge:
            return "S"

        administrativeKeywords = [
            "aprendiz lectiva",
            "aprendiz productiva",
            "aprendiz",
            "administrativo",
            "administrativa",
            "analista",
            "auxiliar administrativo",
            "auxiliar administrativa",
            "coordinador",
            "coordinadora",
            "director",
            "directora",
            "gerente",
            "jefe",
            "lider",
            "tesoreria",
            "contabilidad",
            "contable",
            "nomina",
            "compras",
            "desarrollo humano",
            "tecnologia",
            "informatica",
            "calidad",
            "sst",
            "seguridad y salud",
            "facturacion",
            "costos",
            "bienestar",
            "legal",
            "financiero",
            "financiera",
            "impuestos",
            "mercadeo",
            "call center",
            "centro de experiencia",
        ]

        if any(keyword in charge for keyword in administrativeKeywords):
            return "N"

        return "S"

    def _cleanNumericCode(self, value: str) -> str:
        code = str(value or "").strip()

        if not code:
            return ""

        code = code.replace(",", ".")

        try:
            numericValue = float(code)

            if numericValue.is_integer():
                code = str(int(numericValue))
        except ValueError:
            pass

        return "".join(character for character in code if character.isdigit())

    def _writeBankAccountChangesSheet(self, templateWorkbook, sourceRows: list[dict[str, Any]]) -> None:
        sheetName = "CAMBIOS CUENTAS"

        if sheetName not in templateWorkbook.sheetnames:
            raise ValueError(f"No se encontró la hoja {sheetName} en la plantilla.")

        worksheet = templateWorkbook[sheetName]

        startRow = 5
        currentRow = startRow

        self._clearBankAccountChangesSheet(worksheet=worksheet, startRow=startRow)

        expectedCompanyRut = self._cleanRut(self.COMPANY_RUT_VALUE)

        for sourceRow in sourceRows:
            companyRut = self._cleanRut(self._getCellText(sourceRow.get(self._normalize(self.COMPANY_RUT_COLUMN))))

            if companyRut != expectedCompanyRut:
                continue

            birthCountry = self._normalize(
                self._getCellText(sourceRow.get(self._normalize("colaborador - nacionalidad")))
            )

            if birthCountry in {"", "colombiana", "colombiano", "colombia"}:
                continue

            employeeDocument = self._getCellText(
                sourceRow.get(self._normalize("colaborador - número de documento"))
                or sourceRow.get(self._normalize("cedula numero"))
            )

            employeeName = self._getCellText(
                sourceRow.get(self._normalize("colaborador - nombre completo"))
                or sourceRow.get(self._normalize("apellidos y nombres"))
            )

            bankName = self._getCellText(
                sourceRow.get(self._normalize("colaborador - banco"))
                or sourceRow.get(self._normalize("codigo del banco"))
            )

            accountNumber = self._getCellText(
                sourceRow.get(self._normalize("colaborador - número de cuenta"))
                or sourceRow.get(self._normalize("numero de cuenta"))
            )

            accountType = self._getCellText(
                sourceRow.get(self._normalize("colaborador - tipo de cuenta"))
                or sourceRow.get(self._normalize("tipo de cuenta"))
            )

            worksheet.cell(row=currentRow, column=1, value=employeeDocument)
            worksheet.cell(row=currentRow, column=2, value=employeeDocument)
            worksheet.cell(row=currentRow, column=3, value=employeeName)
            worksheet.cell(row=currentRow, column=4, value=bankName)
            worksheet.cell(row=currentRow, column=5, value=accountNumber)
            worksheet.cell(row=currentRow, column=6, value=accountType)

            for column in range(1, 7):
                worksheet.cell(row=currentRow, column=column).number_format = "@"

            currentRow += 1

    def _clearBankAccountChangesSheet(self, worksheet, startRow: int) -> None:
        for rowNumber in range(startRow, worksheet.max_row + 1):
            for columnNumber in range(1, 9):  # A hasta H
                cell = worksheet.cell(row=rowNumber, column=columnNumber)
                cell.value = None
                cell.number_format = "@"