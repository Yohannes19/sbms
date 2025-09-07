from fastapi import HTTPException, status

class RedirectException(HTTPException):
    def __init__(self, path: str):
        super().__init__(
            status_code=status.HTTP_303_SEE_OTHER,
            headers={"Location": path}
        )