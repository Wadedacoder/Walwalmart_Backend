from fastapi import Form
from pydantic.dataclasses import dataclass


@dataclass
class AdditionalUserDataForm:
   display_name: str = Form(...)
   Amount: int = Form(...)


