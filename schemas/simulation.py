from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class simulation(BaseModel):
    title: str

class simulationResiter(simulation):
    #이건 너가 말했듯이 시뮬레이션 설정값을 받아와야 하는데 그거 어떻게 할지는 의논이 필요할거 같아서 ㅎㅎ
    data: int
    data2: int
    is_public: bool
    pass

class simulationResponse(BaseModel):
    simulationId: int