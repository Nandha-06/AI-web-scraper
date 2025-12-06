from pydantic import BaseModel, Field
from typing import Optional

class BusinessData(BaseModel):
    name: str = Field(..., description="The name of the business.")
    rating_score: Optional[str] = Field(None, description="The rating score (e.g., 4.5).")
    address: str = Field(..., description="The address/location of the business.")
    years_in_business: Optional[str] = Field(None, description="Years of experience or 'Years in Business/Healthcare'.")
    categories: Optional[str] = Field(None, description="Business categories or services offered.")
    phone_number: Optional[str] = Field(None, description="The phone number of the business.")