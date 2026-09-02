import httpx
import os

class BukEmployeeClient:

    def __init__(self):
        self.baseUrl = os.getenv("BUK_API_BASE_URL")
        self.token = os.getenv("BUK_API_TOKEN")

        if not self.baseUrl:
            raise ValueError("La variable BUK_API_BASE_URL no está configurada.")

        if not self.token:
            raise ValueError("La variable BUK_API_TOKEN no está configurada.")

    async def getEmployeeByDocument(self, documentNumber: str) -> dict | None:
        documentNumber = documentNumber.strip()

        if not documentNumber:
            raise ValueError("El número de documento es obligatorio.")

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(f"{self.baseUrl}/employees", params={ "document_number": documentNumber }, headers={ "Accept": "application/json", "auth_token": self.token, },)

        response.raise_for_status()
        payload = response.json()
        employees = []

        if isinstance(payload, dict):
            employees = payload.get("data") or []
        elif isinstance(payload, list):
            employees = payload

        if not employees:
            return None

        employee = employees[0]
        currentJob = employee.get("current_job") or {}
        role = currentJob.get("role") or {}
        area = currentJob.get("area") or {}
        customAttributes = currentJob.get("custom_attributes") or {}
        costCenterName = (customAttributes.get("Centro costo") or customAttributes.get("Centro de costo") or customAttributes.get("Centro Costo"))

        return {
            "documentNumber": employee.get("document_number"),
            "firstName": employee.get("first_name"),
            "surname": employee.get("surname"),
            "secondSurname": employee.get("second_surname"),
            "fullName": employee.get("full_name"),
            "status": employee.get("status"),
            "roleName": role.get("name"),
            "roleCode": role.get("code"),
            "areaId": currentJob.get("area_id"),
            "areaName": area.get("name") if isinstance(area, dict) else None,
            "costCenter": currentJob.get("cost_center"),
            "costCenterName": costCenterName,
        }