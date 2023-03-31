from fastapi import Form
from pydantic.dataclasses import dataclass


@dataclass
class AdditionalUserDataForm:
   name: str = Form(...)
   Amount: int = Form(...)

class OlapForm:
   queryn: int = Form(...)


