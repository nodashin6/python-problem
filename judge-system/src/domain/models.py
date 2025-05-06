from pydantic import BaseModel, Field


class Problem(BaseModel):
    id: str
    title: str | None = None
    markdown : str | None = None

class Stdin(BaseModel):
    id: str | None = None
    name: str | None = None
    content: str
    
class Stdout(BaseModel):
    id: str | None = None
    name: str | None = None
    content: str

class Testcase(BaseModel):
    id: str
    name: str
    problem: Problem
    stdin: Stdin
    stdout: Stdout

    model_config = {
        "arbitrary_types_allowed": True
    }


class JudgeRequest(BaseModel):
    id: str
    problem: Problem
    code: str
    
    
class JudgeResultMetadata(BaseModel):
    memory_used: int | None = None
    time_used: int | None = None
    compile_error: str | None = None
    runtime_error: str | None = None
    output: str | None = None


class JudgeResult(BaseModel):
    id: str
    problem: Problem
    test_case: Testcase
    status: str
    metadata: JudgeResultMetadata | None = None

    model_config = {
        "arbitrary_types_allowed": True
    }


class JudgeResponse(BaseModel):
    id: str
    problem: Problem
    code: str
    results: list[JudgeResult]

    model_config = {
        "arbitrary_types_allowed": True
    }