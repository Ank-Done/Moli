from pydantic import BaseModel

class Montacarga(BaseModel):
    IDMontacarga: int
    PorcentajeBateria: int
    EnUso: bool
    EnCarga: bool
