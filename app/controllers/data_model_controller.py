from fastapi import Request, APIRouter

from app.model.data_model import DataModel
from demos.extender import assistant

router = APIRouter()

@router.post("/")
async def get_response(request: Request):
    """
    This function is used to get a response from the assistant.
    :param request:
    :return:
    """
    body = await request.json()
    data_model = DataModel(**body.get("data_model"))
    query = body.get("query")
    response = await assistant(_query=query, _data_model=data_model)
    # unwrap the response
    model_output = response.data
    return model_output