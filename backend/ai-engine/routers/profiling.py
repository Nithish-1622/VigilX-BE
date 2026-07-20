from fastapi import APIRouter, HTTPException
from schemas.common import StandardResponse
from utils.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/ai/profiling", tags=["Offender Profiling"])

@router.get("/story/{accused_id}", response_model=StandardResponse)
async def generate_offender_story(accused_id: str):
    """
    6.9 Offender 'Story' Generation (LLM Narrative Profile)
    Generates a readable investigative brief of an offender using LLM.
    """
    try:
        from llm.client import LLMClient
        from services.prompt_service import PromptService
        from pathlib import Path
        
        # In a real scenario, we would fetch the Accused details and Graph profile here.
        # For demonstration, we'll mock the profile data.
        profile_data = f"Suspect {accused_id} is a repeat offender with 3 prior burglary convictions, operating primarily in the North District, utilizing lock picking tools."
        
        # We would use PromptService here with `offender_profile_v1.txt`
        llm = LLMClient()
        prompt = f"Write a professional, concise CJIS-compliant investigative summary for the following suspect profile data:\n{profile_data}"
        
        story = await llm.generate(prompt)
        
        return StandardResponse(
            success=True,
            message="Story generated successfully",
            data={"accused_id": accused_id, "narrative_profile": story},
            metadata={}
        )
    except Exception as e:
        logger.error(f"Failed to generate story: {e}")
        raise HTTPException(status_code=500, detail=str(e))
