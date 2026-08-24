from typing import Optional
from pydantic import BaseModel


class AnaliseIAResponse(BaseModel):
    partida_id: int
    disponivel: bool
    texto: Optional[str] = None
    gerado_em: Optional[str] = None
