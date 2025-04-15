from typing import List
from pydantic import BaseModel, Field


class ModelField(BaseModel):
    name: str = Field(description="Name of the field")
    description: str = Field(description="Description of the field")


class DataModel(BaseModel):
    name: str = Field(description="Name of the model")
    description: str = Field(description="Description of the model")
    fields: List[ModelField] = Field(description="List of fields in the model")


from typing import Any, Dict, Type, List as ListType, Optional, Union, get_type_hints
from pydantic import BaseModel, Field, create_model


def convert_to_dynamic_model(
        data_model: DataModel,
        as_list: bool = False
) -> Union[Type[BaseModel], Type[ListType[BaseModel]]]:
    """
    Convert a DataModel instance into a dynamically created Pydantic model.
    Optionally return a List type of the dynamic model.

    Args:
        data_model: An instance of DataModel containing model definition
        as_list: If True, returns a List type of the created model

    Returns:
        Either a new Pydantic model class or a List type of that model class
    """
    # Prepare field definitions for the dynamic model
    field_definitions: Dict[str, Any] = {}

    # Process each field from the DataModel
    for field in data_model.fields:
        # For each field, create a tuple of (type, field_info)
        field_info = Field(description=field.description)
        field_definitions[field.name] = (str, field_info)

    # Create the dynamic model using create_model
    dynamic_model = create_model(
        data_model.name,  # Use the name from DataModel as the class name
        __doc__=data_model.description,  # Set the model's docstring
        **field_definitions  # Unpack the field definitions
    )

    if as_list:
        # Create a list model type by annotating List[dynamic_model]
        # We're creating a type annotation, not a new model class
        return ListType[dynamic_model]
    else:
        return dynamic_model



def get_field_descriptions(
        model: Union[Type[BaseModel], Type[List[BaseModel]]],
        as_dict: bool = False,
        join_delimiter: str = ", "
) -> Union[str, Dict[str, str]]:
    """
    Extract field descriptions from a dynamically created Pydantic model.

    Args:
        model: A Pydantic model class or List[Model] type returned by convert_to_dynamic_model
        as_dict: If True, returns a dictionary mapping field names to descriptions
                 If False, returns a string with all descriptions joined by join_delimiter
        join_delimiter: The delimiter to use when joining descriptions (if as_dict=False)

    Returns:
        Either a string of joined field descriptions or a dictionary of field names to descriptions
    """
    # If we have a List type, extract the inner model
    if hasattr(model, "__origin__") and model.__origin__ is list:
        model = model.__args__[0]

    # Dictionary to store field descriptions
    descriptions: Dict[str, str] = {}

    # Extract descriptions from model fields
    for field_name, field_info in model.model_fields.items():
        if field_info.description:
            descriptions[field_name] = field_info.description

    # Return based on as_dict parameter
    if as_dict:
        return descriptions
    else:
        return join_delimiter.join(descriptions.values())