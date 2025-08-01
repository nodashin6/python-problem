"""
Enhanced Judge System API Router
Enhanced judge endpoints with frontend integration support
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from ...domain.value_objects.execution_status import ExecutionStatus, ProgrammingLanguage
from ...usecase.api_submission_usecase import ApiSubmissionUseCase
from ...usecase.code_execution_use_case import CodeExecutionUseCase

judge_router = APIRouter(prefix="/api/judge", tags=["judge"])

# Request/Response Models for Frontend
class SubmissionRequest(BaseModel):
    """Submission request for frontend"""
    problem_id: str
    language: str = Field(..., description="Programming language (python, java, cpp, etc.)")
    source_code: str = Field(..., description="Source code to submit")


class ExecutionRequest(BaseModel):
    """Code execution request for frontend"""
    language: str = Field(..., description="Programming language") 
    source_code: str = Field(..., description="Source code to execute")
    input_data: str = Field(default="", description="Input data for execution")
    time_limit_ms: int = Field(default=5000, description="Time limit in milliseconds")
    memory_limit_mb: int = Field(default=256, description="Memory limit in MB")


class SubmissionResponse(BaseModel):
    """Submission response for frontend"""
    id: str
    problem_id: str
    user_id: str
    language: str
    source_code: str
    status: str
    result: str
    score: int = 0
    max_score: int = 100
    execution_time_ms: int = 0
    memory_usage_kb: int = 0
    test_cases_passed: int = 0
    test_cases_total: int = 0
    error_message: str = ""
    created_at: str
    completed_at: str | None = None


class ExecutionResponse(BaseModel):
    """Execution response for frontend"""
    id: str
    language: str
    status: str
    output: str = ""
    error_message: str = ""
    execution_time_ms: int = 0
    memory_usage_kb: int = 0
    exit_code: int = 0
    created_at: str
    completed_at: str | None = None


class TestCaseResult(BaseModel):
    """Test case result for frontend"""
    case_number: int
    status: str  # "AC", "WA", "TLE", "MLE", "RE", etc.
    execution_time_ms: int = 0
    memory_usage_kb: int = 0
    input_preview: str = ""
    expected_output_preview: str = ""
    actual_output_preview: str = ""
    error_message: str = ""


class SubmissionDetailResponse(SubmissionResponse):
    """Detailed submission response for frontend"""
    test_cases: List[TestCaseResult] = Field(default_factory=list)
    compile_output: str = ""
    judge_log: str = ""


class SubmissionListResponse(BaseModel):
    """Submission list response for frontend"""
    submissions: List[SubmissionResponse]
    total_count: int
    page: int
    page_size: int
    has_next: bool


# Submission Endpoints
@judge_router.post("/submit", response_model=SubmissionResponse)
async def submit_solution(
    request: SubmissionRequest,
    user_id: str = Query(..., description="User ID from authentication"),
    submission_usecase: ApiSubmissionUseCase = Depends(),
) -> SubmissionResponse:
    """Submit a solution to a problem"""
    try:
        # Validate language
        try:
            language = ProgrammingLanguage(request.language.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported language: {request.language}"
            )

        # Create submission through use case
        result = await submission_usecase.submit_solution(
            problem_id=UUID(request.problem_id),
            user_id=UUID(user_id),
            language=language,
            source_code=request.source_code
        )

        return SubmissionResponse(
            id=str(result.submission_id),
            problem_id=request.problem_id,
            user_id=user_id,
            language=request.language,
            source_code=request.source_code,
            status=result.status.value,
            result=result.result.value if result.result else "PENDING",
            score=result.score,
            max_score=result.max_score,
            execution_time_ms=result.execution_time_ms,
            memory_usage_kb=result.memory_usage_kb,
            test_cases_passed=result.test_cases_passed,
            test_cases_total=result.test_cases_total,
            error_message=result.error_message or "",
            created_at=result.created_at.isoformat(),
            completed_at=result.completed_at.isoformat() if result.completed_at else None,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid ID format: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit solution: {str(e)}"
        )


@judge_router.get("/submissions/{submission_id}", response_model=SubmissionDetailResponse)
async def get_submission(
    submission_id: str,
    user_id: str = Query(..., description="User ID from authentication"),
    submission_usecase: ApiSubmissionUseCase = Depends(),
) -> SubmissionDetailResponse:
    """Get submission details"""
    try:
        result = await submission_usecase.get_submission_detail(
            submission_id=UUID(submission_id),
            user_id=UUID(user_id)
        )

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Submission not found"
            )

        test_cases = [
            TestCaseResult(
                case_number=tc.case_number,
                status=tc.status.value,
                execution_time_ms=tc.execution_time_ms,
                memory_usage_kb=tc.memory_usage_kb,
                input_preview=tc.input_preview,
                expected_output_preview=tc.expected_output_preview,
                actual_output_preview=tc.actual_output_preview,
                error_message=tc.error_message or "",
            )
            for tc in result.test_cases
        ]

        return SubmissionDetailResponse(
            id=str(result.submission_id),
            problem_id=str(result.problem_id),
            user_id=str(result.user_id),
            language=result.language.value,
            source_code=result.source_code,
            status=result.status.value,
            result=result.result.value if result.result else "PENDING",
            score=result.score,
            max_score=result.max_score,
            execution_time_ms=result.execution_time_ms,
            memory_usage_kb=result.memory_usage_kb,
            test_cases_passed=result.test_cases_passed,
            test_cases_total=result.test_cases_total,
            error_message=result.error_message or "",
            created_at=result.created_at.isoformat(),
            completed_at=result.completed_at.isoformat() if result.completed_at else None,
            test_cases=test_cases,
            compile_output=result.compile_output or "",
            judge_log=result.judge_log or "",
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid ID format: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get submission: {str(e)}"
        )


@judge_router.get("/submissions", response_model=SubmissionListResponse)
async def get_submissions(
    user_id: str = Query(..., description="User ID from authentication"),
    problem_id: Optional[str] = Query(None, description="Filter by problem ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    submission_usecase: ApiSubmissionUseCase = Depends(),
) -> SubmissionListResponse:
    """Get user submissions with pagination"""
    try:
        offset = (page - 1) * page_size
        
        result = await submission_usecase.get_user_submissions(
            user_id=UUID(user_id),
            problem_id=UUID(problem_id) if problem_id else None,
            status=ExecutionStatus(status) if status else None,
            limit=page_size,
            offset=offset
        )

        submissions = [
            SubmissionResponse(
                id=str(sub.submission_id),
                problem_id=str(sub.problem_id),
                user_id=str(sub.user_id),
                language=sub.language.value,
                source_code=sub.source_code,
                status=sub.status.value,
                result=sub.result.value if sub.result else "PENDING",
                score=sub.score,
                max_score=sub.max_score,
                execution_time_ms=sub.execution_time_ms,
                memory_usage_kb=sub.memory_usage_kb,
                test_cases_passed=sub.test_cases_passed,
                test_cases_total=sub.test_cases_total,
                error_message=sub.error_message or "",
                created_at=sub.created_at.isoformat(),
                completed_at=sub.completed_at.isoformat() if sub.completed_at else None,
            )
            for sub in result.submissions
        ]

        return SubmissionListResponse(
            submissions=submissions,
            total_count=result.total_count,
            page=page,
            page_size=page_size,
            has_next=len(submissions) == page_size,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid parameter: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get submissions: {str(e)}"
        )


# Code Execution Endpoints
@judge_router.post("/execute", response_model=ExecutionResponse)
async def execute_code(
    request: ExecutionRequest,
    user_id: str = Query(..., description="User ID from authentication"),
    execution_usecase: CodeExecutionUseCase = Depends(),
) -> ExecutionResponse:
    """Execute code without submitting to a problem"""
    try:
        # Validate language
        try:
            language = ProgrammingLanguage(request.language.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported language: {request.language}"
            )

        result = await execution_usecase.execute_code(
            user_id=UUID(user_id),
            language=language,
            source_code=request.source_code,
            input_data=request.input_data,
            time_limit_ms=request.time_limit_ms,
            memory_limit_mb=request.memory_limit_mb
        )

        return ExecutionResponse(
            id=str(result.execution_id),
            language=request.language,
            status=result.status.value,
            output=result.output or "",
            error_message=result.error_message or "",
            execution_time_ms=result.execution_time_ms,
            memory_usage_kb=result.memory_usage_kb,
            exit_code=result.exit_code,
            created_at=result.created_at.isoformat(),
            completed_at=result.completed_at.isoformat() if result.completed_at else None,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid parameter: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute code: {str(e)}"
        )


@judge_router.get("/executions/{execution_id}", response_model=ExecutionResponse)
async def get_execution(
    execution_id: str,
    user_id: str = Query(..., description="User ID from authentication"),
    execution_usecase: CodeExecutionUseCase = Depends(),
) -> ExecutionResponse:
    """Get execution result"""
    try:
        result = await execution_usecase.get_execution_result(
            execution_id=UUID(execution_id),
            user_id=UUID(user_id)
        )

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Execution not found"
            )

        return ExecutionResponse(
            id=str(result.execution_id),
            language=result.language.value,
            status=result.status.value,
            output=result.output or "",
            error_message=result.error_message or "",
            execution_time_ms=result.execution_time_ms,
            memory_usage_kb=result.memory_usage_kb,
            exit_code=result.exit_code,
            created_at=result.created_at.isoformat(),
            completed_at=result.completed_at.isoformat() if result.completed_at else None,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid ID format: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get execution: {str(e)}"
        )


# System Status Endpoints
@judge_router.get("/status")
async def get_judge_status():
    """Get judge system status"""
    return {
        "status": "healthy",
        "service": "judge-system",
        "version": "1.0.0",
        "supported_languages": [lang.value for lang in ProgrammingLanguage],
        "endpoints": {
            "submit": "/api/judge/submit",
            "submissions": "/api/judge/submissions",
            "execute": "/api/judge/execute",
            "executions": "/api/judge/executions/{execution_id}",
        }
    }


@judge_router.get("/health")
async def judge_health_check():
    """Judge system health check"""
    return {
        "status": "healthy",
        "service": "judge-system",
        "timestamp": "2025-08-02T06:30:00Z",
        "checks": {
            "database": "healthy",
            "queue": "healthy",
            "workers": "healthy"
        }
    }