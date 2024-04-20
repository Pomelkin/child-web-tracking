from pydantic import BaseModel, ConfigDict
from multiprocessing.connection import Connection


class Worker(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    connection: Connection
